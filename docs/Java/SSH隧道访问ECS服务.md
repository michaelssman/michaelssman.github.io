# SSH 隧道访问 ECS 服务

在 Mac 上通过 SSH（Secure Shell，安全外壳协议）隧道访问 ECS 的 MinIO、Nacos 和 MySQL，无需将这些服务端口向公网开放。隧道把 Mac 本地端口转发到 ECS，Mac 与 ECS 之间的数据经过 SSH 加密。

## 1. 使用前确认

- 安全组需允许可信来源访问 SSH `22`。
- 下文命令均在 **Mac 新终端窗口**执行，不是在已登录 ECS 的终端中执行。每个代码块是一条完整命令，可以整段复制；行尾的 `\` 表示续行。

命令中的 `-i` 指定 SSH 私钥；`-N` 表示只转发端口、不进入服务器命令行；`-L` 的格式为 `Mac监听地址:Mac端口:ECS可访问的目标地址:目标端口`。两个 `127.0.0.1` 分别指 Mac 和 ECS 自己，不是同一台机器。

`ExitOnForwardFailure=yes` 在本地转发监听无法建立时退出，但不保证 ECS 上的目标服务已启动。[SSH 端口转发](https://man.openbsd.org/ssh)、[转发失败处理](https://man.openbsd.org/ssh_config#ExitOnForwardFailure)。

## 2. MinIO：控制台与 API

**Mac：建立隧道。**

```sh
ssh -i "/Users/michael/Downloads/ecs260818.pem" \
  -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:19000:127.0.0.1:9000 \
  -L 127.0.0.1:19001:127.0.0.1:9001 \
  root@47.120.56.43
```

保持终端运行，在 Mac 上使用：

| 本地入口 | ECS 目标 | 用途 |
| --- | --- | --- |
| `http://127.0.0.1:19001` | `127.0.0.1:9001` | Chrome 打开 MinIO 控制台 |
| `http://127.0.0.1:19000` | `127.0.0.1:9000` | SDK 或存储工具连接 MinIO API |

控制台使用 **MinIO 管理员账号和密码**。凭据位于 ECS 的 `/opt/hhjava-minio/secrets/root_user` 和 `/opt/hhjava-minio/secrets/root_password`。需要查看时另开 Mac 终端正常登录 ECS；隧道窗口不能执行服务器命令。

看到登录页面并成功进入存储桶列表，即完成控制台访问验证。API 使用 MinIO 应用凭据，不使用 hhjava 的 Bearer Token。部署与权限说明见 [MinIO](分布式文件系统MinIO.md)。

<a id="nacos-mysql"></a>

## 3. Nacos 与 MySQL

**Mac：建立隧道。** 可以与上面的 MinIO 隧道分别运行在两个终端窗口中。

```sh
ssh -i "/Users/michael/Downloads/ecs260818.pem" \
  -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:18848:127.0.0.1:8848 \
  -L 127.0.0.1:19848:127.0.0.1:9848 \
  -L 127.0.0.1:13306:127.0.0.1:3306 \
  root@47.120.56.43
```

| Mac 本地入口 | ECS 目标 | 用途 |
| --- | --- | --- |
| `http://127.0.0.1:18848/nacos/` | `127.0.0.1:8848` | Nacos 2.x 控制台、HTTP 接口 |
| `127.0.0.1:19848` | `127.0.0.1:9848` | Nacos 客户端 gRPC 通信，不是网页地址 |
| `127.0.0.1:13306` | `127.0.0.1:3306` | MySQL 数据库工具或本机 Java 连接 |

1. **查看 Nacos 配置：** Chrome 打开上表控制台地址，用已有 Nacos 管理账号登录。
2. **连接 MySQL：** 数据库工具填写 Host `127.0.0.1`、Port `13306`，沿用已有业务账号、数据库名和 TLS（Transport Layer Security，传输层安全）配置，不使用 root。IDEA 的字段与连接验证见 [环境搭建](环境搭建.md#mysql-via-ssh)。

只查看 Nacos 网页时，只需要 `18848 → 8848`；本机 Java 使用 Nacos 2.x 客户端时还需要 `19848 → 9848`。客户端按主端口 **加 1000** 计算 gRPC（远程过程调用框架）端口，所以 `18848` 必须配套 `19848`，不能误配成本机 `9848`。[Nacos 2.x 端口规则](https://www.nacos.io/en/docs/v2/upgrading/version2-compatibility/)

<a id="local-java"></a>

## 4. Mac 本机运行 hhjava

先保持对应隧道运行，再在 **IDEA 的运行配置 → Environment variables** 中按服务设置以下变量；这些是配置项，不是直接粘贴到终端的命令。

| 本机服务 | 覆盖变量 |
| --- | --- |
| 需要连接 Nacos 的 hhjava 服务 | `NACOS_SERVER_ADDR=127.0.0.1:18848` |
| `hhjava-user` | `SPRING_DATASOURCE_URL=jdbc:mysql://127.0.0.1:13306/app?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&sslMode=REQUIRED` |
| `hhjava-backup-file` | `HHJAVA_MINIO_ENDPOINT=http://127.0.0.1:19000` |

数据库 URL 示例对应 `app` 库；已有数据库名或其他连接参数不同时保留其原值，只替换主机和端口。Nacos、数据库和 MinIO 的凭据继续使用各服务已有的受限配置，不写入本指南。MinIO 的 `read-path` 仍按对象定位约定配置，不因 API 走隧道就变成公开下载地址。

上述变量只用于 **Mac 进程**，不要修改共享 Nacos 配置或 ECS 的 systemd 参数。ECS 宿主机服务仍连接本机 `8848`、`3306`、`9000`；同 Docker 网络中的服务使用容器服务名。项目开发模板可能仍默认公网 Nacos 地址，修改 `.env.example` 本身不会改变正在运行的进程。

重启本机应用后确认 Nacos 配置能加载，数据库或文件业务能正常调用。隧道只解决这些基础服务的连接，不会自动打通其他微服务之间的访问。

## 5. 关闭隧道与收紧公网入口

- **关闭：** 在对应隧道终端按 `Control + C`。
- **端口占用：** 出现 `Address already in use` 时，先确认是否已有相同隧道，不要重复启动。端口转发后仍连接失败时，检查 ECS 上目标服务是否运行、回环端口是否已发布。
- **收紧前：** 先验证网页、数据库工具和本机 Java 都能通过隧道连接，再确认没有其他客户端依赖公网直连。
- **安全组：** 保留可信来源的 SSH `22` 和业务所需 HTTPS `443`。跨 ECS 的必要连接走私网并精确授权。[阿里云安全组建议](https://www.alibabacloud.com/help/en/ecs/user-guide/start-using-security-groups)
- **Docker：** 对仅供宿主机和 SSH 隧道访问的端口，使用 `127.0.0.1:宿主机端口:容器端口`，不绑定所有网卡。既有实例修改映射前先确认数据卷、容器网络和其他客户端；不要删除数据卷重建。MySQL 示例见 [环境搭建](环境搭建.md#mysql-via-ssh)。[Docker 端口发布说明](https://docs.docker.com/engine/network/port-publishing/)

以上是访问和收紧方案，不表示服务器的容器映射或安全组已经完成修改。
