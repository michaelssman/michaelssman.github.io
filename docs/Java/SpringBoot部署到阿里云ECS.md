# Spring Boot 部署到阿里云 ECS

本文配合 hhjava 的 `scripts/ecs/` 模板部署到 `47.120.56.43`。这是单机个人联调方案：沿用 `app` 数据库及账号、Nacos 的 `dev` Namespace / `hhjava` Group 和已有 OAuth 服务客户端秘密，并非生产隔离环境。正式业务还需分库、独立配置环境、分离迁移与运行账号并完善限流、监控和备份。

只想连接 App，先看第 8.2、8.3 节；以后更新代码，看第 8.4 节；首次搭建服务器，再从第 3 节按顺序操作。

## 1. 部署完成后是什么效果

手机不再请求开发电脑，而是访问 ECS 的 HTTPS 地址。本教程只部署注册登录需要的 `hhjava-user` 和 `hhjava-gateway`，复用已有 MySQL、Nacos，不安装文件服务、MinIO 或 Nginx。

```text
App / API 调试工具
  │ HTTPS，https://47.120.56.43:443
  ▼
hhjava-gateway（公网入口、TLS、路由与 JWT 验签）
  │ 服务器本机连接
  ▼
hhjava-user（127.0.0.1:8080，注册、登录、刷新与退出）
  ├─ MySQL：用户、角色、OAuth2 与移动会话数据
  └─ Nacos：读取本环境配置

Certbot → 临时监听 80 完成证书验证 → 更新 HTTPS 证书 → 通知 gateway 加载
```

443 是 HTTPS 默认端口，访问时可以不写 `:443`。`127.0.0.1` 表示当前机器自己：在 ECS 上指 ECS，在手机上指手机，不能把它填为 App 的服务器地址。

本文选择 Alibaba Cloud Linux 4、x86_64、Dragonwell 17 Headless、systemd 托管 Java 进程。MySQL/Nacos 即使运行在 Docker 容器里，也不要求 Java 服务一起容器化；但它们的访问地址必须以实际容器网络和端口映射为准。

## 2. 先认识会用到的东西

| 名称 | 用途及本文中的作用 |
| --- | --- |
| Dragonwell / Headless | Dragonwell 是阿里巴巴提供的 OpenJDK 发行版；Headless 不依赖桌面显示环境，适合服务器 |
| systemd | Linux 的服务管理器；负责启动、停止、开机运行和按配置恢复进程 |
| Certbot / ACME | Certbot 是证书客户端；ACME（Automatic Certificate Management Environment，自动证书管理环境）是申请和续期证书的协议 |
| Flyway | 按版本执行数据库结构变更的工具；本项目由 user 启动时执行迁移 |

## 3. 第一步：准备信息，确认操作位置

### 3.3 服务器只读检查通过后再安装

在 ECS 确认系统、CPU 架构、内存与磁盘、已有 Java、80/443/8080 端口占用、已有 systemd 服务，以及 MySQL/Nacos 容器和数据目录。

**Mac 终端**设置变量；`<release>` 换成本次唯一名称，例如 `app-login-001`，只使用字母、数字、短横线和下划线。SSH 私钥路径按实际机器替换：

```sh
HHJAVA_RELEASE="<release>"
HHJAVA_SSH_KEY="/Users/michael/Downloads/ecs260818.pem"
HHJAVA_SERVER="root@47.120.56.43"
ssh -i "$HHJAVA_SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes "$HHJAVA_SERVER"
```

**ECS 终端**重新设置相同发布名，之后在这个终端继续：

```sh
HHJAVA_RELEASE="<release>"
cat /etc/os-release
uname -m
free -h
df -h / /opt
ss -lntp
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

每个命令块失败后先停止排查，不继续后面的操作。管理命令以 root 执行，Java 进程使用后面创建的受限用户。

## 4. 第二步：在本机测试并打包

操作位置：**Mac 终端，hhjava 仓库根目录**。把第一条路径替换为实际目录：

```sh
cd "<本机hhjava绝对路径>"
java -version
mvn -version
mvn clean test
mvn -pl hhjava-service/hhjava-user,hhjava-gateway -am -DskipTests package
```

参数含义：`-pl` 选择两个部署模块，`-am` 同时构建它们依赖的公共模块，`-DskipTests` 只在前面已经完成测试后跳过重复执行。所有 Maven 命令仍从根目录运行，不进入子模块单独猜依赖。

产物位置：

```text
hhjava-service/hhjava-user/target/hhjava-user-1.0-SNAPSHOT.jar
hhjava-gateway/target/hhjava-gateway-1.0-SNAPSHOT.jar
```

这是两个独立服务，需要分别启动。`hhjava-unify` 等公共模块被打进服务依赖中，不作为第三个 Java 服务运行。

上传时只上传选定产物；在本机和 ECS 比较 SHA-256 摘要，确认文件完整且确为本次打包结果。这里的产物摘要不是密码，可以记录；不要把 Refresh Token 摘要当成同类可公开信息。

**Mac，hhjava 根目录**先记录两个摘要：

```sh
shasum -a 256 hhjava-service/hhjava-user/target/hhjava-user-1.0-SNAPSHOT.jar hhjava-gateway/target/hhjava-gateway-1.0-SNAPSHOT.jar
```

文件稍后上传至 `/opt/hhjava/releases/<release>/user.jar`、`gateway.jar`；先完成第 5 节数据库检查（需保留数据时先备份）与第 6 节目录准备，再上传。

## 5. 第三步：检查数据库并准备迁移

操作位置：**ECS，通过已确认的 MySQL 管理入口操作**。

### 5.1 确认不是连错库

先检查数据库名、业务表结构、索引与角色，不查询或输出用户密码及会话凭据。注册需要 `user`、`role`、`user_role` 三张表；源码注册固定关联 `role_id=2`，因此角色必须实际存在。用户名唯一约束也要在真实 MySQL 中确认，不能把 Java 先查重当作数据库约束。

仓库的 V1～V4 不负责建立这三张业务表。**没有业务表的全新数据库，不属于本教程“复用已有数据库”的直接适用范围**；先准备经过审查的业务表建表迁移和角色数据，不能删库后只启动应用。短信注册还要求 `username` 至少容纳 38 字符，密码字段至少容纳 60 字符的 BCrypt 哈希。

### 5.2 需要保留数据时，建立能恢复的备份

当前项目尚未上线、数据均为可丢弃的测试业务数据，不强制备份，也不为旧版本增加兼容分支；结构满足要求时直接迁移，不为更新短信功能清空数据。确需重建时先确认本项目 `app` 库及基础三表，不清理 Nacos、凭据或其他服务数据。

将来需要保留数据时，在启动 user 新版本之前备份目标数据库的结构与数据，并确认恢复方案。以下备份步骤仅在这种情况下执行；备份可能含用户密码哈希、OAuth2 Token 和移动会话信息，不能公开。

1. 明确目标库与备份位置，使用受限账号和目录，不把密码写进命令行。
2. 确认备份工具退出成功、文件非空；若压缩，还要校验压缩文件完整性。
3. 在隔离测试库或实例进行恢复验证，核对表结构和必要数据；不能用覆盖正式库的方式做“恢复测试”。
4. 将备份放入加密且独立于原 ECS 的受控存储，并限制访问。

MySQL 的 `mysqldump --single-transaction` 可为 InnoDB 数据提供一致性快照，但备份期间仍需避免并发结构变更；不应把这一参数当成所有存储引擎、所有操作都安全的承诺。[MySQL 8.0 备份说明](https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html)

以下适用于 MySQL 容器名 `mysql`，容器内已有 `MYSQL_ROOT_PASSWORD` 的环境；其他配置先调整，不输出环境变量全文。**ECS**执行；括号中的失败会立即停止，不覆盖同名备份：

```sh
(
set -euo pipefail
install -d -o root -g root -m 700 /var/backups/hhjava
HHJAVA_BACKUP="/var/backups/hhjava/app-before-${HHJAVA_RELEASE}.sql.gz"
test ! -e "$HHJAVA_BACKUP"
umask 077
docker exec mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -uroot --single-transaction --routines --triggers --events --no-tablespaces --set-gtid-purged=OFF app' | gzip > "$HHJAVA_BACKUP"
gzip -t "$HHJAVA_BACKUP"
stat -c '%a %s %n' "$HHJAVA_BACKUP"
)
```

预期权限 600、非空，`gzip -t` 无错误；已经存在时换唯一名称。压缩完整性不是隔离恢复验证，也不是异地加密备份；后两项未完成时必须写“未验证”，不能在正式库尝试恢复。

### 5.3 按 Flyway 历史判断下一步

Flyway 使用 `flyway_schema_history` 记录版本。先查历史，再选择对应情况：

| 数据库情况 | 应如何处理 |
| --- | --- |
| 已有成功的迁移，尚未到 V4 | 保持 `HHJAVA_FLYWAY_BASELINE_ON_MIGRATE=false`；新版 user 校验历史并按顺序补齐迁移，已有 V1/V2 时追加 V3/V4 |
| 已有成功的 V1～V4 | 仍保留校验，不重复手工创建表，不修改已执行迁移 |
| 有业务表但没有 Flyway 历史 | 确认库与结构后，仅首次接管临时打开版本 0 基线开关；完成后恢复 `false` |
| 有失败记录、校验和不一致，或表存在但版本不对应 | 暂停启动，核对迁移原因；不直接删历史表或用 repair 掩盖问题 |

V1 创建 OAuth2 表；V2 创建 `mobile_refresh_session`，保存 Refresh Token 摘要和轮换状态；V3 创建手机号关联表 `user_phone_identity`；V4 创建短信挑战表 `sms_verification` 与发送配额锁表 `sms_send_guard`，并初始化固定锁行。**不要手工导入迁移 SQL 后再让 Flyway 重复执行。**

启动后的检查只看迁移版本、成功标记和目标表结构，不打印 Token、`token_hash` 或整表数据。H2 单元测试通过不等于真实 MySQL 迁移已经通过。

MySQL 的建表等 DDL（Data Definition Language，数据定义语言）不等于可以随应用事务任意回滚；不能认为换回旧 JAR 就能恢复数据库。回退前必须确认旧代码是否兼容新结构，需要数据库恢复时另行安排维护窗口和数据恢复方案。[MySQL 8.0 原子 DDL 说明](https://dev.mysql.com/doc/refman/8.0/en/atomic-ddl.html)

**ECS**查看迁移、业务表、默认角色和用户名索引：

```sh
docker exec mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -e "SELECT version,description,success FROM app.flyway_schema_history ORDER BY installed_rank; SELECT table_name FROM information_schema.tables WHERE table_schema=\"app\"; SELECT id,name FROM app.role WHERE id=2; SELECT index_name,non_unique,GROUP_CONCAT(column_name ORDER BY seq_in_index) FROM information_schema.statistics WHERE table_schema=\"app\" AND table_name=\"user\" GROUP BY index_name,non_unique;"'
```

当前模板复用 `app` 账号对 `app.*` 的权限，没有实现独立 DDL 迁移账号；上线前按真实授权重新设计。检查失败先停，不为了消除报错修改历史迁移。

## 6. 第四步：准备运行配置与服务权限

操作位置：**ECS**。安装本方案所需 Dragonwell 17 Headless，然后确认实际 Java 路径与主版本。user 和 gateway 由 systemd 以受限身份运行，不以 root 长期运行业务进程；443 的监听权限仅授予需要它的网关服务。

### 6.1 两类私钥不是同一个东西

- **JWT RSA 私钥**：由 user 独占，用于签发 Access Token；gateway 通过 JWKS 公钥验签，不获得该私钥。
- **HTTPS 私钥**：与 Let's Encrypt 证书配套，由 gateway 用于建立 TLS 连接；不能拿它代替 JWT RSA 密钥。

配置按服务分开，不能把包含 user 私钥权限与数据库秘密的整套开发配置共享给 gateway。`HHJAVA_DEV_CONFIG_LOCATION` 指向应用要导入的完整文件路径；`HHJAVA_DEV_CONFIG_DIR` 只是本地生成脚本所用的目录变量，两者不可混用，也不要让 ECS 依赖 Mac 的默认目录。

### 6.2 核对彼此一致的地址与配置

| 配置项 | 本方案的约束 |
| --- | --- |
| App API 根地址 | `https://47.120.56.43`；业务路径另加 `/user/...` |
| 公开 issuer | `https://47.120.56.43/user`；user 签发值、gateway 校验值与公开元数据必须完全一致 |
| user 监听 | 仅 `127.0.0.1:8080`，不开放公网直连 |
| gateway 监听 | 公网 443，直接加载 TLS 证书 |
| JWKS 获取地址 | `http://127.0.0.1:8080/user/oauth2/jwks`；user 的 context-path 为 `/user` |
| API audience | 所有签发方和消费方一致；仓库默认 `hhjava-api` |
| profile / Namespace / Group | `dev` / `dev` / `hhjava`；只读既有配置，关闭 discovery 和动态 refresh，不向共享 Nacos 注册 ECS 实例 |
| gateway 本机静态路由 | `/user/**` 到 `http://127.0.0.1:8080`，保留 `/user`，不能加 `StripPrefix`；覆盖共享 Nacos 的 `lb://` 路由 |
| MySQL | `app` 库 / `app` 账号；`sslMode=REQUIRED` 要求加密，但不等于校验数据库服务器身份 |

Nacos 必须已经存在 Namespace ID `dev`、Group `hhjava` 下的 `hhjava-user-dev.yaml` 和 `hhjava-gateway-dev.yaml`，运行账号须有读取权限。关闭服务发现不等于移除配置中心依赖：启动仍需读取这两份配置。换服务器前先迁移 Nacos 配置和数据库，Nacos 操作见 [Nacos](Nacos.md)；不能只复制两个 JAR 就期待所有依赖自动出现。

### 6.3 ECS：首次安装目录、用户与模板

```sh
dnf install -y java-17-alibaba-dragonwell-headless
/usr/bin/java -version
getent passwd hhjava-user hhjava-gateway
```

`getent` 没有输出表示相应用户不存在，才可创建；已有用户或目录先核对归属，不重复初始化：

```sh
useradd --system --user-group --home-dir /var/lib/hhjava/user --no-create-home --shell /sbin/nologin hhjava-user
useradd --system --user-group --home-dir /var/lib/hhjava/gateway --no-create-home --shell /sbin/nologin hhjava-gateway
install -d -m 755 /opt/hhjava /opt/hhjava/releases /etc/hhjava /var/lib/hhjava
install -d -o root -g hhjava-user -m 750 /etc/hhjava/user
install -d -o root -g hhjava-gateway -m 750 /etc/hhjava/gateway
install -d -o hhjava-user -g hhjava-user -m 700 /var/lib/hhjava/user
install -d -o hhjava-gateway -g hhjava-gateway -m 700 /var/lib/hhjava/gateway
(set -eu; test ! -e "/opt/hhjava/releases/$HHJAVA_RELEASE"; install -d -m 755 "/opt/hhjava/releases/$HHJAVA_RELEASE")
```

**Mac，hhjava 根目录**，沿用前述 Mac 变量上传：

```sh
scp -i "$HHJAVA_SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes hhjava-service/hhjava-user/target/hhjava-user-1.0-SNAPSHOT.jar "$HHJAVA_SERVER:/opt/hhjava/releases/$HHJAVA_RELEASE/user.jar"
scp -i "$HHJAVA_SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes hhjava-gateway/target/hhjava-gateway-1.0-SNAPSHOT.jar "$HHJAVA_SERVER:/opt/hhjava/releases/$HHJAVA_RELEASE/gateway.jar"
scp -r -i "$HHJAVA_SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes scripts/ecs "$HHJAVA_SERVER:/opt/hhjava/releases/$HHJAVA_RELEASE/"
```

**ECS**先比较两个 SHA-256 与 Mac 一致：

```sh
sha256sum "/opt/hhjava/releases/$HHJAVA_RELEASE/user.jar" "/opt/hhjava/releases/$HHJAVA_RELEASE/gateway.jar"
HHJAVA_TEMPLATES="/opt/hhjava/releases/$HHJAVA_RELEASE/ecs"
```

模板源位于仓库 `scripts/ecs/`，不用手工重写两份 YAML 和四个 unit。下列只适用于首次部署，目标已有文件时停止，先备份和对比，不覆盖已有配置：

```sh
(
set -eu
for file in /etc/hhjava/user/application.yml /etc/hhjava/gateway/application.yml /etc/systemd/system/hhjava-user.service /etc/systemd/system/hhjava-gateway.service /etc/systemd/system/hhjava-certbot-renew.service /etc/systemd/system/hhjava-certbot-renew.timer /usr/local/sbin/hhjava-deploy-certificate /opt/hhjava/current; do
  test ! -e "$file"
  test ! -L "$file"
done
install -o root -g hhjava-user -m 640 "$HHJAVA_TEMPLATES/user-application.yml" /etc/hhjava/user/application.yml
install -o root -g hhjava-gateway -m 640 "$HHJAVA_TEMPLATES/gateway-application.yml" /etc/hhjava/gateway/application.yml
install -m 644 "$HHJAVA_TEMPLATES/hhjava-user.service" /etc/systemd/system/hhjava-user.service
install -m 644 "$HHJAVA_TEMPLATES/hhjava-gateway.service" /etc/systemd/system/hhjava-gateway.service
install -m 750 "$HHJAVA_TEMPLATES/deploy-certificate.sh" /usr/local/sbin/hhjava-deploy-certificate
install -m 644 "$HHJAVA_TEMPLATES/hhjava-certbot-renew.service" /etc/systemd/system/hhjava-certbot-renew.service
install -m 644 "$HHJAVA_TEMPLATES/hhjava-certbot-renew.timer" /etc/systemd/system/hhjava-certbot-renew.timer
ln -s "/opt/hhjava/releases/$HHJAVA_RELEASE" /opt/hhjava/current
)
```

在受控编辑器逐项核对 6.2 表格。两个 unit 的 Nacos 地址为 `127.0.0.1:8848`、用户名 `hhjava_dev_runtime`；换环境时一起调整。unit 使用 `SPRING_CONFIG_ADDITIONAL_LOCATION` 在已有配置后加载 ECS YAML，不在 YAML 再声明 Nacos `spring.config.import`，避免远端子导入覆盖本机边界。模板关闭 Swagger 和 SQL 参数日志，不修改远端 Nacos。

### 6.4 Mac：加密传送三个秘密，ECS：生成独立 JWT 密钥

**Mac，hhjava 根目录**，确认 `../.hhjava-dev-config/` 已有下列三个秘密文件，不输出其内容：

```sh
set -o pipefail
COPYFILE_DISABLE=1 tar -C ../.hhjava-dev-config -cf - nacos-password mysql-app-password oauth-client-secret | ssh -i "$HHJAVA_SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes "$HHJAVA_SERVER" "python3 /opt/hhjava/releases/$HHJAVA_RELEASE/ecs/install-secrets.py"
```

脚本仅接收允许的成员，经 SSH 管道分别写入两个服务的 `secrets.properties`，权限 root:对应服务组 640；gateway 只取得 Nacos 密码。拒绝重复初始化，失败时检查是否部分生成，不盲目删除重跑。共享 OAuth 客户端秘密，不代表生产隔离；不随意更改 client-id/secret 影响既有客户端。

**ECS**生成新 RSA，不复制本机开发密钥；已有密钥时以下检查停止，不覆盖：

```sh
(
set -eu
test ! -e /etc/hhjava/user/jwt-private.pem
test ! -e /etc/hhjava/user/jwt-public.pem
umask 077
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out /etc/hhjava/user/jwt-private.pem
openssl pkey -in /etc/hhjava/user/jwt-private.pem -pubout -out /etc/hhjava/user/jwt-public.pem
chown root:hhjava-user /etc/hhjava/user/jwt-private.pem /etc/hhjava/user/jwt-public.pem
chmod 640 /etc/hhjava/user/jwt-private.pem /etc/hhjava/user/jwt-public.pem
openssl pkey -in /etc/hhjava/user/jwt-private.pem -check -noout
)
```

### 6.5 ECS：启动 user 后再进入证书步骤

```sh
systemd-analyze verify /etc/systemd/system/hhjava-user.service /etc/systemd/system/hhjava-gateway.service
systemctl daemon-reload
systemctl enable --now hhjava-user.service
```

等待服务初始化和 Flyway 完成，再检查：

```sh
systemctl show hhjava-user.service -p ActiveState -p SubState -p NRestarts
ss -lntp 'sport = :8080'
curl --noproxy '*' --silent --output /dev/null --write-out 'user_jwks_http=%{http_code}\n' http://127.0.0.1:8080/user/oauth2/jwks
docker exec mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -e "SELECT version,description,success FROM app.flyway_schema_history ORDER BY installed_rank;"'
```

预期 user 稳定运行、仅监听 `127.0.0.1:8080`、JWKS 200、V1～V4 均为 `success=1`。失败停在此处，受控查看 `journalctl -u hhjava-user.service -n 80 --no-pager`，分享前脱敏。user 就绪不是公网或 App 已通过。

## 7. 第五步：启用公网 IP 的 HTTPS 与自动续期

### 7.1 为什么没有域名也能用 HTTPS

TLS 证书可以证明服务器对一个 IP 地址的控制权，不一定只支持域名。Let's Encrypt 已提供 IPv4/IPv6 地址证书；它们必须使用 `shortlived` 配置，证书有效期为 160 小时，不能按常见的数十天证书手工维护。[Let's Encrypt IP 证书说明](https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability)

App 访问的 IP 必须与证书中的 IP 对应。公网 IP 变化时，证书、issuer 和 App 地址都要重新核对；不能只改 App 地址继续使用原 IP 证书。

### 7.2 本方案为什么让 gateway 自己处理 TLS

当前 gateway 会检查 `/user/**` 的请求协议、Host 和端口是否与公开 issuer 一致，并删除公网请求中伪造的转发头。因此本方案让 gateway 直接接收 HTTPS，作为第一层可信入口。不能未经适配就在前面放 Nginx/负载均衡终止 TLS，再把明文 HTTP 当成原始 HTTPS 请求。

### 7.3 证书验证、安装与续期是三件事

1. **验证与签发**：Certbot 使用 `standalone` 模式临时监听 TCP 80，让证书机构通过 HTTP-01 验证对该 IP 的控制权。80 不能被其他进程占用，ECS 安全组和系统防火墙也必须允许验证连接。
2. **安装使用**：正式签发后，让 gateway 加载证书链及配套私钥。测试环境签发的 staging 证书不被手机正常信任，不能作为交付证书。
3. **自动续期**：systemd timer 定期运行续期检查；成功取得新证书后，deploy-hook 更新 gateway 使用的文件并触发其加载。只更新磁盘证书而不更新服务内存中的证书，不算完成。

支持 IP 参数的 Certbot 版本和插件须核实；官方说明 `--ip-address` 从 5.3 起提供，教程执行时使用经过验证的支持版本。standalone 可以不安装 Nginx。[Let's Encrypt 的 Certbot IP 证书指南](https://letsencrypt.org/2026/03/11/shorter-certs-certbot.html)

这里的 80 仅用于 ACME 验证，不提供明文登录；App 永远使用 443 HTTPS。安全组持续允许所选验证方式的必要流量，避免首次成功后关闭 80 导致后续续期失效。SSH 只允许管理来源，8080、MySQL 和 Nacos 不作为本流程的新公网入口。

### 7.4 怎样才算自动续期验收通过

- 正式证书的 IP 标识、证书链和有效期正确，外部客户端无需关闭证书校验。
- timer 已启用，能看到下一次执行安排；验证服务和部署钩子的日志无错误。
- 完成续期演练；注意普通 `--dry-run` 默认不运行 deploy-hook，须按所用 Certbot 版本明确验证钩子。
- 从外部重新建立 TLS 连接，确认 gateway 实际使用的证书和预期一致。
- 监控续期失败及对外证书到期，不能只看定时器“运行成功”。

`certbot renew` 返回成功也可能只是“本次无需续期”。成功后才执行的 deploy-hook、磁盘证书和对外 TLS 证书应分别检查。[Certbot 续期与部署钩子说明](https://eff-certbot.readthedocs.io/en/stable/using.html#renewing-certificates)

### 7.5 ECS：安装、测试签发和正式启用

确认 `/opt/hhjava-certbot` 尚不存在且专用于本部署；已有安装先检查版本，不重复初始化。venv 是独立的 Python 包环境：

```sh
python3 -m venv /opt/hhjava-certbot
/opt/hhjava-certbot/bin/pip install --index-url https://pypi.org/simple 'certbot>=5.4'
/opt/hhjava-certbot/bin/certbot --version
/opt/hhjava-certbot/bin/certbot certonly --standalone --preferred-profile shortlived --ip-address 47.120.56.43 --cert-name hhjava-ip --agree-tos --register-unsafely-without-email --non-interactive --dry-run
```

执行者必须先阅读并同意 [Let's Encrypt 订户协议](https://letsencrypt.org/repository/)，才使用 `--agree-tos`。不填邮箱不能依赖邮件提醒，需要自己监控。缺 Python/venv 支持时按系统软件源补齐，不改用未知软件源。

**测试签发必须成功才继续**。超时通常需要核对安全组 80、系统防火墙、实际 IP、80 是否被其他进程占用；必须让证书机构从公网访问，ECS 自己请求成功不等于验证通过。停在本步修复，不反复申请正式证书。通过后去掉 `--dry-run`：

```sh
/opt/hhjava-certbot/bin/certbot certonly --standalone --preferred-profile shortlived --ip-address 47.120.56.43 --cert-name hhjava-ip --agree-tos --register-unsafely-without-email --non-interactive
env RENEWED_LINEAGE=/etc/letsencrypt/live/hhjava-ip /usr/local/sbin/hhjava-deploy-certificate
systemctl enable --now hhjava-gateway.service
```

等待 gateway 就绪，执行内部 HTTPS 检查。`--resolve` 仅让连接走回环，仍验证真实 IP 与公信证书：

```sh
systemctl show hhjava-gateway.service -p ActiveState -p SubState -p NRestarts
curl --noproxy '*' --resolve 47.120.56.43:443:127.0.0.1 --silent --output /dev/null --write-out 'gateway_jwks_http=%{http_code}\n' https://47.120.56.43/user/oauth2/jwks
```

预期 HTTP 200。脚本先验证 CA 信任链、IP、至少一天有效期及公私钥匹配，再创建受限证书目录、原子切换 `/etc/hhjava/gateway/tls`，必要时重启 gateway 并验 HTTPS JWKS；失败尝试恢复旧指针，旧证书目录保留。重启会短暂影响连接，不影响 user/数据库。材料相同且 gateway 正常运行时直接退出。

### 7.6 ECS：续期演练与完整任务检查

```sh
systemd-analyze verify /etc/systemd/system/hhjava-certbot-renew.service /etc/systemd/system/hhjava-certbot-renew.timer
systemctl enable --now hhjava-certbot-renew.timer
systemctl list-timers hhjava-certbot-renew.timer --all
/opt/hhjava-certbot/bin/certbot renew --cert-name hhjava-ip --dry-run --run-deploy-hooks --no-random-sleep-on-renew --deploy-hook /usr/local/sbin/hhjava-deploy-certificate
systemctl start hhjava-certbot-renew.service
systemctl show hhjava-certbot-renew.service -p Result -p ExecMainStatus
```

timer 每天 00/12 点加最多一小时随机延迟检查；renew 禁用自己的随机等待，避免重复等待。普通 dry-run 不执行 deploy-hook，上述参数用当前正式证书验钩子，不安装临时 staging 证书。预期演练成功、`Result=success`、`ExecMainStatus=0`，并再次检查公网入口。

renew unit 还有 `ExecStartPost`：即使无需续签也对齐证书，补偿上次“签发成功但部署失败”；不要只依赖 hook。失败时受控查看 `journalctl -u hhjava-certbot-renew.service`，修复后重跑，不只清掉失败状态。模板不包含外部到期/失败告警，需要另行配置。IP 改变时同步修改 issuer、两个 YAML 和证书脚本的 IP 校验/访问地址，并重新申请证书。

## 8. 第六步：按层验收，最后接 App

### 8.1 先检查服务器内部，再检查公网

| 检查位置 | 要确认的内容 | 通过标准 |
| --- | --- | --- |
| ECS | Java 与两个服务状态 | 进程稳定运行，无反复重启；user 只监听回环，gateway 监听 TLS 443 |
| ECS / MySQL | Flyway 与业务前置表 | V1～V4 成功；移动会话表、手机号关联表、短信挑战/配额表存在，基础业务表及默认角色完整 |
| ECS | JWKS 与路由 | 能取得公钥，不能取得私钥；gateway 正确到达 user |
| 服务器外部 | HTTPS | 证书可信、IP 匹配、证书链正常，不使用 `curl -k` 或 App 的跳过证书验证功能 |
| 服务器外部 | 公开元数据 | issuer、授权/Token/JWKS 地址使用预期公网入口，不泄露内部 8080 地址 |

**Mac**从公网检查，不使用 `-k`：

```sh
curl --noproxy '*' --silent --show-error --connect-timeout 5 --max-time 10 --output /dev/null --write-out 'public_jwks_http=%{http_code} tls_verify=%{ssl_verify_result}\n' https://47.120.56.43/user/oauth2/jwks
```

预期 `public_jwks_http=200`、`tls_verify=0`。内部通过但公网失败先查 443 安全组和系统防火墙，不降低证书校验要求。公开发现地址为 `https://47.120.56.43/user/.well-known/openid-configuration`，核对其中 issuer 及各协议端点使用外部 HTTPS。

### 8.2 注册、登录、刷新与退出

操作位置：**本机 API 调试工具或真实 App**。URL 以 `https://47.120.56.43` 为根地址；下表接口均使用 `POST` 和 `Content-Type: application/json`，不靠浏览器 Cookie 登录，也不需要 OAuth client secret。先确认已部署与当前接口一致的 user/gateway 版本，不能把本地代码更新当成服务器已更新。

手机号采用一次验证码验证后注册或登录，新号码自动创建账号并返回 Token；不再提供用户名密码独立注册。阿里云开通、凭据、已有账号绑定及登录后设置密码，统一按 [hhjava 项目认证指南](https://github.com/michaelssman/java_demo/blob/main/hhjava/docs/AUTHENTICATION_GUIDE.md)第 12.5 节操作。真实短信按量计费。本机文件是 `java_demo/hhjava/docs/AUTHENTICATION_GUIDE.md`；网页对应已推送版本，本地修改需同步推送后才能在网页查看。

| 操作 | 请求路径 | JSON 参数 |
| --- | --- | --- |
| 获取登录验证码 | `/user/auth/mobile/sms/code` | `phoneNumber` |
| 统一注册/登录 | `/user/auth/mobile/login/sms` | `phoneNumber`、`challengeId`、`code` |
| 密码登录 | `/user/auth/mobile/login/password` | `phoneNumber` 或 `username` 二选一，再加 `password` |
| 刷新 | `/user/auth/mobile/token/refresh` | `refreshToken` |
| 退出 | `/user/auth/mobile/logout` | `refreshToken` |

在 Reqable 新建请求，选 `POST`，填写“根地址 + 请求路径”；Body 选择 JSON。先获取短信验证码：

```json
{"phoneNumber":"<你自己的11位手机号>"}
```

再向统一登录入口提交返回的 `challengeId` 和手机收到的验证码：

```json
{"phoneNumber":"<同一手机号>","challengeId":"<本次发送返回的ID>","code":"<收到的6位验证码>"}
```

刷新和退出使用下面结构，值来自登录或最近一次刷新响应；占位符不能原样提交，实际 Token 不要复制到公开文档：

```json
{"refreshToken":"<最近一次返回的 Refresh Token>"}
```

按顺序操作，并只保留脱敏验收结论：

1. **首次短信登录**：使用自己的测试号码，正确验证码应直接返回 HTTP 200、`code: 200`，`data` 含 `tokenType`、`accessToken`、`expiresIn`、`refreshToken`、`refreshExpiresIn`。未关联号码自动创建账号，不再取第二条短信。Token 字段是凭据，不复制到截图或报告。
2. **再次登录**：按发送冷却重新获取验证码；成功后仍是同一账号，原备份归属不变。错误/过期码应拒绝，参数不合法返回 400；不要重复发送来做限流实验。
3. **密码入口**：使用已设置密码的手机号，正文为 `{"phoneNumber":"<已绑定手机号>","password":"<当前密码>"}`；旧账号可改传 `username`，不能同时传两个身份字段。正确密码成功，错误密码或不存在账号均返回 401。
4. **正常刷新**：把最近一次返回的 `refreshToken` 发送给刷新接口；成功取得新的一对 Token 后一起替换旧值。不得并发用同一旧 Refresh Token 刷新。
5. **验证退出**：使用最新 Refresh Token 退出，预期 HTTP 200、`data: "退出登录成功"`；重复退出仍成功。之后再次用该会话刷新应返回 401。
6. **独立验证旧 Token 重放**：重新登录建立单独测试会话，刷新一次，再重放旧 Refresh Token；旧 Token 与此会话的新 Token 随后均不能继续刷新。不要用正式正在使用的会话做此实验。

Access Token 用于受保护业务请求的 `Authorization: Bearer <accessToken>`；Refresh Token 只能用于刷新/退出，不能当作 Bearer 凭据。当前 JWT 没有即时撤销黑名单，退出撤销的是刷新会话，已发出的 Access Token 仍可能在到期前通过验证，这是当前实现边界。

### 8.3 App 侧还要做什么

将 App 实际使用的 API 根地址改为 `https://47.120.56.43`，核对不要重复拼出 `/user/user/...`。使用平台安全存储保存凭据，不在请求日志中打印登录响应；正常刷新后替换旧 Token，退出时清理本地凭据。

必须保持系统证书校验开启，不接受所有证书、不改成明文 HTTP。后端通过接口测试不代表 App 已修改，也不代表 iOS/Android 真机完成验收；应在实际目标设备、实际网络上验证注册、登录、刷新和退出。

本实例 API 根地址是 `https://47.120.56.43`。本教程不修改 App 工程，也不嵌入 OAuth service client secret；原生 App 连接失败不通过放开浏览器 CORS 解决。完整验收还应检查伪造 Host 返回 400、Refresh Token 不能作为 Bearer、JWKS 不含私钥。专用测试账号若要清理，应精确核对账号及会话 ID，不批量删除现有用户。

### 8.4 日常更新和回退

完成测试/打包，使用新发布名创建目录、上传两包并比较 SHA-256；保留原有秘密和 JWT 密钥，不重跑首次初始化。配置变化先备份并逐项比较。若已部署文件服务，它也通过 `/opt/hhjava/current/backup-file.jar` 启动，新目录必须保留该文件，否则后续重启文件服务会失败。以下在 **ECS** 核对旧指针，按需复制未改动的文件服务 Jar，确认内容一致且服务账号可读后再切换：

若同时更新文件服务，先在 **Mac 的 hhjava 根目录**执行 `mvn -pl hhjava-service/hhjava-user,hhjava-gateway,hhjava-service/hhjava-backup-file -am package`（包含测试），将 `hhjava-service/hhjava-backup-file/target/hhjava-backup-file-1.0-SNAPSHOT.jar` 上传为新目录的 `backup-file.jar`，按第 4 节方式核对 SHA-256。下方已有新 Jar 时不再复制旧文件；从未安装文件服务的服务器仍先按 [MinIO 部署教程](分布式文件系统MinIO.md)准备依赖与 unit。

```sh
readlink /opt/hhjava/current
(
set -eu
test -f "/opt/hhjava/releases/$HHJAVA_RELEASE/user.jar"
test -f "/opt/hhjava/releases/$HHJAVA_RELEASE/gateway.jar"
if systemctl cat hhjava-backup-file.service >/dev/null 2>&1; then
  if [ ! -e "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar" ]; then
    test ! -L "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar"
    test -r /opt/hhjava/current/backup-file.jar
    cp -p /opt/hhjava/current/backup-file.jar "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar"
    cmp -s /opt/hhjava/current/backup-file.jar "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar"
  fi
  test -f "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar"
  runuser -u hhjava-backup-file -- test -r "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar"
  sha256sum "/opt/hhjava/releases/$HHJAVA_RELEASE/backup-file.jar"
fi
test ! -e "/opt/hhjava/current-$HHJAVA_RELEASE"
test ! -L "/opt/hhjava/current-$HHJAVA_RELEASE"
ln -s "/opt/hhjava/releases/$HHJAVA_RELEASE" "/opt/hhjava/current-$HHJAVA_RELEASE"
mv -Tf "/opt/hhjava/current-$HHJAVA_RELEASE" /opt/hhjava/current
systemctl restart hhjava-user.service
)
```

user 的迁移和 JWKS 通过后，再 `systemctl restart hhjava-gateway.service`，重做公网与认证检查。若更新了文件服务 Jar，还需 `systemctl restart hhjava-backup-file.service`，使用 ECS 签发的令牌验收上传、分页、下载内容一致、跨账号拒绝和测试对象删除；不改动原有 MinIO 数据。回退按相同指针方式选择已验证旧目录，但必须先确认新数据库结构兼容旧代码；JAR 回退不撤销 Flyway。此方案有短暂停机，不承诺高可用或零停机。

## 9. 故障定位与交付边界

| 现象 | 先检查什么 |
| --- | --- |
| SSH 超时 | 实例运行状态、IP、实际 SSH 端口、安全组来源，不直接放开所有端口 |
| HTTPS 无法连接 | 443 监听、网关状态、安全组和系统防火墙 |
| 证书不被信任 | 是否误用 staging、是否匹配 IP、链是否完整、是否过期；不关闭校验 |
| `/user/**` 返回 400 | 请求协议/Host/端口是否与 issuer 一致，是否擅自增加 TLS 终止代理 |
| 返回 404 | Nacos 路由、前缀处理、user context-path，不先归因于密码 |
| 登录返回 500 | 数据库连接、业务表/默认角色、V1～V4 迁移、JWT 密钥；仅查看受控脱敏日志 |
| 登录成功但业务请求 401 | 是否使用 Access Token，issuer/audience/算法/时间是否匹配，JWKS 是否可达 |
| 首次 HTTPS 正常，之后突然失败 | timer、80 验证通路、证书到期、deploy-hook 与 gateway 实际证书 |
| 进程被系统结束 | 内存与系统日志，核对两个 Java 进程和既有容器总资源，不只反复重启 |

上线验收应分别记录“已验证 / 未验证及原因”：构建测试、产物校验、数据库备份及恢复（有保留要求时）、真实迁移、内部路由、外部 TLS、证书续期、认证正常与失败路径、真实 App。不要用一个“部署成功”掩盖未完成项目。

当前已有短信验证码及手机号/IP/全局发送限额、挑战核验次数限制，但密码登录入口仍缺少账号级限流，尚无完整风控、Access Token 即时撤销和平滑 JWT 密钥轮换；公开服务必须配套适合实际场景的抗滥用措施。本文完成单机部署与验收，不等于自动具备完整生产安全和高可用能力。

本文的备份操作只覆盖同机受限备份和压缩完整性检查；没有完成隔离恢复演练、异地加密备份或外部到期告警。真实 App 工程也不在本教程的服务端验收范围，须单独连接并验证。

详细项目实现以 `hhjava/docs/AUTHENTICATION_GUIDE.md` 为准；运维更新保留上一版本产物，数据库变更独立评估。JWT 私钥、数据库备份和证书续期配置需要受控备份，不能只保存在同一块 ECS 云盘上。正式公网使用前还需复核 Spring/Nacos 等依赖的维护状态与安全更新，不能把“能够启动”当作安全审查已经完成。
