# MinIO：阿里云 Docker 部署与 hhjava 接入

MinIO 是兼容 S3 接口的对象存储：**桶（bucket）**装对象，**对象键（key）**标识文件。hhjava 通过 Java SDK 上传和删除；`mc` 是管理员使用的命令行客户端。

本文沿用已有 ECS `47.120.56.43`、Docker、Nacos 和 hhjava 登录服务，安装 **AIStor Free 单节点版**。许可证由本人申请并确认条款。[官方容器安装](https://docs.min.io/aistor/installation/container/install/)、[许可证](https://docs.min.io/aistor/operations/licenses/)。

## 1. 部署结构

```text
App → HTTPS :443 gateway → 127.0.0.1:63030 backup-file
                                      ├─ Nacos：读取连接配置
                                      ├─ user JWKS：验证 JWT
                                      └─ 127.0.0.1:9000 MinIO → 私有桶 hhjava-backup
```

| 项目 | 本实例约定 |
| --- | --- |
| Docker 与持久化数据 | `/opt/hhjava-minio/compose.yaml`、`/opt/hhjava-minio/data/` |
| 许可证与管理员凭据 | `/opt/hhjava-minio/minio.license`、`secrets/root_user`、`secrets/root_password` |
| 应用凭据 | `secrets/app_user`、`secrets/app_password`，仅有指定桶权限 |
| 文件服务配置 | `/etc/hhjava/backup-file/application.yml`、`secrets.properties` |
| 文件请求入口 | `https://47.120.56.43/backup/files/...` |

现有 MySQL/Nacos 的管理入口仍应由安全组限制来源。

## 2. Mac：上传许可证与安装脚本

先确认服务器 9000/9001 未占用，且没有同名 MinIO 数据目录。以下初始化步骤只执行一次。

```sh
cd /Users/michael/Documents/java_demo/hhjava
HHJAVA_KEY=/Users/michael/Downloads/ecs260818.pem
HHJAVA_SERVER=root@47.120.56.43
ssh -i "$HHJAVA_KEY" "$HHJAVA_SERVER" 'install -d -m 700 /opt/hhjava-minio'
scp -i "$HHJAVA_KEY" /Users/michael/Downloads/minio.license scripts/ecs/prepare-minio.py scripts/ecs/configure-minio.py scripts/ecs/minio-compose.yml "$HHJAVA_SERVER:/opt/hhjava-minio/"
ssh -i "$HHJAVA_KEY" "$HHJAVA_SERVER"
```

部署模板保存在 `hhjava/scripts/ecs/`。

## 3. ECS：启动 MinIO，创建私有桶

以下命令在 **ECS root 终端**执行，任一步失败先处理，不继续后面的步骤。

```sh
cd /opt/hhjava-minio
docker pull quay.io/minio/aistor/minio:latest
docker pull quay.io/minio/aistor/mc:latest

# 从官方客户端镜像取出 mc；提取容器不运行，也没有业务数据。
docker create --name hhjava-mc-extract quay.io/minio/aistor/mc:latest
docker cp hhjava-mc-extract:/usr/bin/mc /opt/hhjava-minio/mc-client
chmod 700 mc-client
docker rm hhjava-mc-extract
./mc-client --version

python3 prepare-minio.py
install -m 600 minio-compose.yml compose.yaml
docker compose config --quiet
docker compose up -d
curl --fail http://127.0.0.1:9000/minio/health/ready
python3 configure-minio.py
```

`prepare-minio.py` 把实际镜像摘要写入 `.env`，生成随机管理员/应用密码，凭据文件权限为 600。

`configure-minio.py` 创建私有桶、5 GiB 配额、最小权限应用账号，并验证上传内容、下载一致性、删除和匿名/管理操作拒绝。成功才生成 `configured` 标记。

本次服务器版本为 `RELEASE.2026-09-19T17-05-25Z`。重新启动使用 `.env` 中的固定摘要；升级前备份并重新验证，不直接用 `latest` 覆盖运行实例。禁止执行 `docker compose down -v` 或删除 `data/` 来排障。

## 4. Nacos：发布连接配置，不保存真实密钥

在 Nacos 配置管理中选择 `dev`，新建 `hhjava-backup-file-dev.yaml`，Group 为 `hhjava`，格式 YAML，内容采用项目的 `scripts/ecs/backup-file-nacos.yaml`。已有同名配置时先导出备份，再合并，不整份覆盖。

关键部分：

```yaml
minio:
  endpoint: ${HHJAVA_MINIO_ENDPOINT:http://127.0.0.1:9000}
  read-path: ${HHJAVA_MINIO_READ_PATH:http://127.0.0.1:9000}
  bucket: hhjava-backup
  access-key: ${HHJAVA_MINIO_ACCESS_KEY}
  secret-key: ${HHJAVA_MINIO_SECRET_KEY}
```

`endpoint` 是 Java 连接的 **API** 地址，不是控制台 9001；`read-path` 是返回给调用方的稳定对象定位前缀。`${…}` 由 Java 进程解析。模板还设置 10 MB 单文件、12 MB 整请求限制。发布后确认运行账号 `hhjava_dev_runtime` 能读回相同内容。

## 5. 部署文件服务并添加网关路由

**Mac，hhjava 根目录**：先测试再打包，上传到新的发布目录。`files-20261019-01` 是本次目录，后续发布改成新的唯一名称，不覆盖旧 JAR。

```sh
mvn -pl hhjava-service/hhjava-backup-file -am test
mvn -pl hhjava-service/hhjava-backup-file -am -DskipTests package
ssh -i "$HHJAVA_KEY" "$HHJAVA_SERVER" 'install -d -m 755 /opt/hhjava/releases/files-20261019-01/ecs'
scp -i "$HHJAVA_KEY" hhjava-service/hhjava-backup-file/target/hhjava-backup-file-1.0-SNAPSHOT.jar "$HHJAVA_SERVER:/opt/hhjava/releases/files-20261019-01/backup-file.jar"
scp -i "$HHJAVA_KEY" scripts/ecs/hhjava-backup-file.service scripts/ecs/backup-file-application.yml scripts/ecs/gateway-application.yml scripts/ecs/install-backup-file-secrets.py "$HHJAVA_SERVER:/opt/hhjava/releases/files-20261019-01/ecs/"
```

**ECS，首次安装**：

```sh
useradd --system --user-group --home-dir /var/lib/hhjava/backup-file --shell /sbin/nologin hhjava-backup-file
install -d -m 750 -o root -g hhjava-backup-file /etc/hhjava/backup-file
python3 /opt/hhjava/releases/files-20261019-01/ecs/install-backup-file-secrets.py
install -m 640 -o root -g hhjava-backup-file /opt/hhjava/releases/files-20261019-01/ecs/backup-file-application.yml /etc/hhjava/backup-file/application.yml
install -m 644 /opt/hhjava/releases/files-20261019-01/ecs/hhjava-backup-file.service /etc/systemd/system/hhjava-backup-file.service
ln -s /opt/hhjava/releases/files-20261019-01/backup-file.jar /opt/hhjava/current/backup-file.jar
systemctl daemon-reload
systemctl enable --now hhjava-backup-file
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:63030/files
```

最后一条预期 **401**：服务已响应，但匿名不能访问。该服务只持有 Nacos 与 MinIO 凭据，不持有 user 的 RSA 私钥、数据库密码或 OAuth 客户端秘密。

在 `/etc/hhjava/gateway/application.yml` 的 `spring.cloud.gateway.routes` 保留现有 user 路由，再加入：

```yaml
- id: hhjava-backup-file-ecs
  uri: http://127.0.0.1:63030
  predicates:
    - Path=/backup/files,/backup/files/**
  filters:
    - StripPrefix=1
```

项目 `scripts/ecs/gateway-application.yml` 已含此路由。在 ECS 对比差异，确认仅新增上述路由后执行：

```sh
diff -u /etc/hhjava/gateway/application.yml /opt/hhjava/releases/files-20261019-01/ecs/gateway-application.yml
cp -p /etc/hhjava/gateway/application.yml /etc/hhjava/gateway/application.before-minio.yml
install -m 640 -o root -g hhjava-gateway /opt/hhjava/releases/files-20261019-01/ecs/gateway-application.yml /etc/hhjava/gateway/application.yml
systemctl restart hhjava-gateway
```

备份文件已存在时另取新名称，不覆盖旧备份。`StripPrefix=1` 把 `/backup/files/database` 转为下游 `/files/database`。ECS 使用本地静态路由覆盖共享 Nacos 路由，因此只改远端网关配置不会生效。

检查 `https://47.120.56.43/user/oauth2/jwks` 仍为 200；失败时恢复网关备份并重启。MinIO 连接参数调整后重启文件服务，不假定已有 SDK 客户端会自动刷新。

## 6. 验收与使用

用 App/Reqable 按项目认证指南取得包含 `hhjava.api` scope 的 Access Token；每个文件请求带 `Authorization: Bearer <Access Token>`，不使用 Refresh Token 调业务。

| 请求 | 参数 / 预期 |
| --- | --- |
| `POST /backup/files/image` | multipart 的 `file` 字段；图片业务 |
| `POST /backup/files/html` | multipart 的 `file` 字段；HTML 业务 |
| `POST /backup/files/database` | multipart 的 `file` 字段；数据库文件业务 |
| `DELETE /backup/files?url=…` | Query 参数 `url` 填上传响应的 `data`，由工具编码；只能删除自己的对象 |

上传可带 `prefix`，例如 `backups/app`；每段只允许字母数字开头及字母数字、下划线、连字符。省略时分别使用 `images`、`htmls`、`databases`。对象按用户/服务客户端、issuer 和主体隔离，并使用 UUID 文件名；同名上传不会覆盖。

返回的 URL **只是私有对象定位值，不是浏览器可直接下载的公开链接**。当前没有 HTTP 下载接口；不能为了让链接可打开而把桶设为公开。也不检测文件真实内容类型。浏览器 H5 跨域访问需要单独配置精确 Origin；App/Reqable 不需要放宽 CORS。

验收至少覆盖：上传后内容一致、同名不覆盖、本人删除成功、跨主体删除 403、匿名 401、非法路径 400，以及 MinIO 匿名读取 403。检查完成后删除专用测试对象。

## 7. 控制台、日常检查与备份

### 7.1 打开控制台

通过 SSH（Secure Shell，安全外壳协议）隧道，把 Mac 本地端口转发到 ECS 上的 MinIO。Mac 与 ECS 之间的数据经过加密，只需已有 SSH 连接可用。

1. **Mac：建立隧道。** 新开一个 Mac 终端窗口，执行下面这一整条命令；可以整段复制，行尾的 `\` 表示命令继续到下一行。

   ```sh
   ssh -i "/Users/michael/Downloads/ecs260818.pem" \
     -N -o ExitOnForwardFailure=yes \
     -L 127.0.0.1:19000:127.0.0.1:9000 \
     -L 127.0.0.1:19001:127.0.0.1:9001 \
     root@47.120.56.43
   ```

   `-N` 表示只转发端口、不进入服务器命令行；`-L` 指定本地端口转发；`ExitOnForwardFailure=yes` 在本地转发监听无法建立时退出并报错。[SSH 官方说明](https://man.openbsd.org/ssh)

   | Mac 本地入口 | 转发到 ECS | 用途 |
   | --- | --- | --- |
   | `127.0.0.1:19000` | `127.0.0.1:9000` | MinIO API 调试 |
   | `127.0.0.1:19001` | `127.0.0.1:9001` | MinIO 网页控制台 |

2. **Mac：打开控制台。** 保持隧道终端运行，在 Chrome 打开 `http://127.0.0.1:19001`，应出现 MinIO 登录页面。终端没有输出、一直等待通常是正常的；如果提示端口已占用，先确认是否已有隧道，避免重复启动。

3. **登录 MinIO。** 使用 MinIO 管理员账号和密码，凭据保存在 ECS 的 `/opt/hhjava-minio/secrets/root_user` 和 `/opt/hhjava-minio/secrets/root_password`。需要查看时，另开 Mac 终端登录 ECS，登录后可查看存储桶和对象、进行管理。

4. **关闭隧道。** 在隧道终端按 `Control + C`。

### 7.2 日常检查与备份

**ECS** 常用检查：

```sh
cd /opt/hhjava-minio
docker compose ps
docker stats --no-stream hhjava-minio
curl --fail http://127.0.0.1:9000/minio/health/ready
systemctl is-active hhjava-backup-file hhjava-user hhjava-gateway
systemctl show hhjava-backup-file -p MemoryCurrent -p MemoryPeak -p NRestarts
```

启动失败先看服务状态和受控日志，排查许可证、未解析变量、Nacos 权限及内存限制；不要通过公开桶、放开所有端口或关闭 JWT 校验解决。持久化数据、许可证、MinIO 身份配置和服务秘密需要另做受控异地备份；单纯保留 Docker 镜像或复制 JAR 不能恢复文件。
