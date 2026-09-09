# MinIO：从服务器安装到 hhjava 文件接口联调

这是一篇从概念、准备到安装、联调的完整教程。第一次先读第 1～2 节确认各个程序装在哪里，再按第 3～14 节逐步操作。只有存储部署成功、客户端读写成功、Java 接口联调成功三个层次都确认，才算走通；不要只以容器处于 running 状态判断文件功能已完成。

## 1. 先知道要安装什么

MinIO 服务端保存文件；Java SDK（Software Development Kit，软件开发工具包）是 Java 程序调用服务端的工具；`mc` 是管理员在终端管理存储的客户端。给 Maven 添加 `io.minio:minio`，不会自动在 ECS（Elastic Compute Service，阿里云弹性计算服务器）安装 MinIO 服务端。

### 1.1 文件为什么不直接放进 Java 项目目录

源码目录用来开发，不是用户文件的可靠存储位置。应用可能重新打包、替换容器，或者扩展为两个实例；如果每个实例把上传文件存在自己的临时目录，另一个实例未必读得到，重建时还可能丢失。

| 方式 | 如何保存和访问 | 需要考虑什么 |
| --- | --- | --- |
| 服务器本地磁盘 | 应用读写操作系统路径 | 简单，但要处理持久化、磁盘容量、备份以及多实例共享 |
| 网络文件系统 | 把远端存储以文件目录语义提供给程序 | 要处理挂载、权限、网络及共享访问语义 |
| 自建对象存储（本文 MinIO） | 按桶和对象键通过 API 读写文件 | 由自己维护部署、权限、升级、容量和备份；不是装完就免运维 |
| 托管对象存储 | 使用云厂商提供的对象 API | 由服务方承担部分基础设施管理，同时考虑费用、权限、网络与数据迁移 |

S3 是 Amazon Simple Storage Service（简单存储服务），也常用来指其对象 API 生态。MinIO 提供 S3 兼容接口，因此 Java 可以使用相应 SDK 操作对象；兼容不代表任何云厂商扩展功能都完全相同。对象存储适合图片、视频、附件、备份等内容，不用来代替 MySQL 的关系查询和事务。

三个基础概念：

| 概念 | 可以怎样理解 | 本文例子 |
| --- | --- | --- |
| Bucket，存储桶 | 一组对象的容器 | `hhjava-backup` |
| Object，对象 | 文件内容及元数据 | 一份测试数据库文件 |
| Object key，对象键 | 桶内定位文件的字符串，不是本机文件路径 | `smoke/example.txt` |

桶内 `smoke/example.txt` 的斜杠便于按前缀组织，但不等于 ECS 真实存在一个 `smoke` 文件夹。完整定位需要桶名和对象键；文件 URL 还包含访问入口。`Content-Type` 是描述内容类型的元数据，例如 `image/png`，不是文件已经安全的证明。

### 1.2 “分布式”、纠删码和备份

分布式存储把数据和服务能力分布到多个节点或磁盘；本文选择**单节点个人开发部署**，不因此获得多节点高可用。高可用是发生部分故障后仍能继续服务的能力，需要部署拓扑、冗余和运维共同保证。

纠删码（Erasure Coding）把数据组织为数据片和校验片，在满足所选冗余与读写仲裁条件时应对一定数量的磁盘故障；能容忍多少故障取决于实际配置，不能笼统说“坏一半以上也一定恢复”。冗余也不能替代备份，误删除、账号滥用和整机故障仍需单独应对。[MinIO 纠删码说明](https://docs.min.io/aistor/operations/core-concepts/erasure-coding/)

性能取决于磁盘、网络、对象大小、并发及部署方式，不能拿一个公开测试数字当作自己的服务器保证。当前步骤只验证功能，不做吞吐量和故障恢复验收。

### 1.3 安装命令中会出现的词

| 词语 | 基础含义，以及本文中的作用 |
| --- | --- |
| Linux / 发行版 / 架构 | Linux 是服务器操作系统体系；Ubuntu、Alibaba Cloud Linux 是不同发行版；amd64/arm64 决定下载哪种可执行程序 |
| SSH（Secure Shell，安全外壳协议） | 加密登录远端服务器，也可转发端口；登录后的命令作用于 ECS，不是 Mac |
| sudo / root | sudo 按权限以其他身份执行命令；root 是 Linux 管理员，能影响整个服务器，不是 MinIO 管理员账号 |
| Docker 镜像（image） | 包含程序及运行文件的模板；pull 下载镜像，并不等于已经启动服务 |
| 容器（container） | 根据镜像启动的隔离进程环境；它不是另一台永久保存所有数据的虚拟机 |
| Compose | 使用 YAML 描述容器、端口、目录、秘密等配置的工具；本文 `docker compose` 根据 compose.yaml 管理 MinIO |
| 挂载（mount） / 数据卷（volume） | 把容器外的持久数据提供给容器；本文使用 ECS 目录的 bind mount，容器重建不应删除宿主机数据目录 |
| 端口映射 | 将宿主机地址端口转到容器端口；`127.0.0.1:9000:9000` 只监听 ECS 回环地址，不是开放公网 |
| API（Application Programming Interface） / Console | API 是程序读写对象的接口；Console 是管理网页，9000 与 9001 在本文职责不同 |
| endpoint | SDK 连接的服务入口地址，必须从 Java 运行的那台机器可达；不是桶名、密码或控制台页面地址 |
| Access Key / Secret Key | 对象存储客户端的访问标识与秘密，用于请求认证；不同于 hhjava 用户登录的 Access Token |
| Policy（权限策略） | 约定某个身份能对哪些桶/对象执行哪些动作；应用账号只授予需要的桶权限 |
| 环境变量 / `.env` / Compose secrets | 环境变量向进程提供配置；本文 `.env` 存非秘密镜像引用；secrets 从受限文件挂入容器，不能因此把源文件当公开资料 |
| digest（镜像摘要） | 标识镜像内容的摘要，比可移动的 latest 标签更适合记录本次部署所选内容 |

容器隔离不等于自动安全；持久化目录、监听地址与权限都需要明确配置。[Docker 容器概念](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)

### 本文选择的安装版本类型

本文的新安装主线使用 **MinIO AIStor Free 的单节点容器部署**。它需要自行注册并领取免费许可证，适用于符合该许可条件的个人开发等场景，不等于有企业支持或多节点高可用。必须自行阅读并接受许可；若不接受，不要执行 AIStor 安装部分，也不要用社区版命令混接下面的许可证配置。[官方许可证说明](https://docs.min.io/aistor/operations/licenses/)

## 2. 本文的机器与端口约定

主线假设：MinIO 装在阿里云 Linux ECS；IDEA、user、gateway、backup-file 和 Reqable 运行在同一台 Mac。Nacos/MySQL 沿用你已经准备的环境，本文不重装它们。

```text
Mac：Reqable → gateway → backup-file
                            ↓ http://127.0.0.1:19000
                         SSH 加密隧道
                            ↓
ECS：127.0.0.1:9000 → MinIO 容器 API → 持久化数据目录
     127.0.0.1:9001 → MinIO 管理控制台
```

| 地址或目录 | 用途 |
| --- | --- |
| ECS 的 9000 | 对象存储 API，只绑定 ECS 本机回环地址 |
| ECS 的 9001 | 管理控制台，只绑定 ECS 本机回环地址 |
| Mac 的 19000 | SSH 转发到 ECS 的 9000，供本机 Java 访问 |
| Mac 的 19001 | SSH 转发到 ECS 的 9001，供浏览器管理 |
| Mac 的 63030 | 本教程给 backup-file 选用的开发端口，不是仓库固定值 |
| `/opt/hhjava-minio` | ECS 上本教程专用的部署目录 |

`127.0.0.1` 永远表示“正在运行这个程序的那台机器”。本文地址不能原样用于其他手机、另一台服务器或 Java 容器。

本文不开放公网 9000/9001，不配置匿名公开桶。个人开发通过 SSH 访问；正式对外服务需另行准备可信网络、HTTPS、对象授权和备份方案。

## 3. 第一步：登录 ECS，检查环境

### 3.1 在 Mac 终端登录

先在阿里云 ECS 控制台确认公网 IP、登录用户名、SSH 端口和你已配置的登录方式。下面尖括号内容必须替换，不原样执行：

```sh
ssh -p <实际SSH端口> <实际登录用户名>@<ECS公网IP>
```

若使用密钥登录，可在 `ssh` 后追加 `-i "<本机私钥文件的绝对路径>"`；不要上传或输出 SSH 私钥正文。首次连接前通过阿里云可信控制台等渠道核对主机指纹，再接受连接，不能为了连通关闭主机密钥校验。

登录后看到的是 ECS 终端。后文标注“ECS”都在这里执行，标注“Mac”则另开本机终端。

### 3.2 在 ECS 检查系统、架构和 Docker

```bash
cat /etc/os-release
uname -m
df -h
free -h
command -v docker
sudo docker version
sudo docker ps
sudo ss -lntp
```

逐项检查：

1. 操作系统是 Ubuntu，还是 Alibaba Cloud Linux，版本是多少？不要把两套安装命令都执行。
2. `x86_64` 对应 amd64，`aarch64` 对应 arm64；后面下载 `mc` 要选对架构。
3. 磁盘和内存有无余量？单节点不提供硬件故障下的高可用，不能把唯一一份重要数据放进去。
4. 如果 Docker 已在运行 MySQL/Nacos 等容器，沿用现有 Docker，不先卸载、不删除镜像/卷、不重建其配置。
5. 9000/9001 是否已经被占用？若已占用，先确认现有服务，不停止不认识的进程。

成功标准：明确系统与架构，知道 Docker 是否已有业务运行，确定存储目录与端口没有冲突。

### 3.3 ECS 安全组

在阿里云控制台找到该 ECS 的安全组：SSH 端口只允许你的可信来源地址；本文不新增 9000/9001 的公网入站规则。也不要为排障把所有端口放开或关闭主机防火墙。

## 4. 第二步：只在没有 Docker 时安装

已有可用 Docker 和 Compose 插件时跳过安装，直接执行本节末尾的验证。若存在旧版 Docker、Moby、containerd 或其他业务依赖，先评估兼容性，不照搬卸载命令。

### 4.1 Ubuntu 24.04 的安装示例

以下在 ECS 执行。其他 Ubuntu 版本先核对官方支持范围。[Docker 官方 Ubuntu 安装文档](https://docs.docker.com/engine/install/ubuntu/)

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl nano
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
dpkg --print-architecture
```

执行 `sudo nano /etc/apt/sources.list.d/docker.sources`，只对这台确认是 Ubuntu 24.04 的新环境填写：

```text
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
```

`noble` 是 Ubuntu 24.04 的代号，不要把它写到其他发行版上。Nano 中按 `Control+O`、回车保存，再按 `Control+X` 退出。

然后执行：

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

### 4.2 Alibaba Cloud Linux 3 的安装示例

只在 `/etc/os-release` 确认是 Alibaba Cloud Linux 3、且没有已有容器运行环境冲突时执行；不适用于 Alibaba Cloud Linux 4。[阿里云 Docker 安装说明](https://help.aliyun.com/zh/ecs/user-guide/install-and-use-docker)

```bash
sudo dnf install -y dnf-plugins-core curl nano
sudo dnf config-manager --add-repo=https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo dnf install -y dnf-plugin-releasever-adapter --repo alinux3-plus
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

若软件源不可达或系统不是上述两种，不切换到来源不明的安装脚本。按实际系统选择官方对应分支，解决软件源/网络问题后继续。

### 4.3 验证

```bash
sudo docker version
sudo docker compose version
sudo systemctl is-active docker
```

应能看到客户端/服务端版本、Compose 插件版本，Docker 状态为 `active`。只有 `docker --version` 有输出，还不足以证明服务端已启动。

## 5. 第三步：申请许可证并准备目录

### 5.1 在 Mac 浏览器申请

打开 [MinIO 官方定价与申请入口](https://min.io/pricing)，选择 Free 对应入口，按官网完成账号验证、许可阅读和申请。将实际取得的许可证文件保存到本机安全位置；后续文件名统一使用 `minio.license`。

网页字段可能调整，以官方流程为准。没有拿到有效许可证文件之前，不继续启动 AIStor，也不使用别人的许可证。[官方容器安装流程](https://docs.min.io/aistor/installation/container/install/)

### 5.2 在 ECS 创建专用目录

后续服务器管理命令统一在管理员 Bash 终端执行：

```bash
sudo -i
```

确认 `/opt/hhjava-minio` 是本次新部署的目录；若已有内容，先检查并备份，不覆盖已有实例。

```bash
umask 077
install -d -m 0700 /opt/hhjava-minio
install -d -m 0700 /opt/hhjava-minio/secrets /opt/hhjava-minio/mc
install -d -m 0750 /opt/hhjava-minio/data
cd /opt/hhjava-minio
```

目录规划：

```text
/opt/hhjava-minio/
├── compose.yaml       # 容器启动规则
├── .env               # 固定镜像摘要，不放业务密码
├── minio.license      # 许可证
├── secrets/           # 管理员凭据，受限权限
├── mc/                # 管理客户端配置，含凭据，不能公开
├── data/              # 持久化对象数据，不能随意删除
└── hhjava-policy.json # 应用账号访问策略
```

### 5.3 把许可证传到 ECS

先在 Mac 终端通过 SSH 为原登录账户创建私有上传目录，再上传许可证。下列两条使用同一个实际 SSH 用户与 ECS 地址：

```bash
ssh "<ECS登录用户名>@<ECS公网IP>" 'umask 077; mkdir -p .hhjava-minio-upload; chmod 0700 .hhjava-minio-upload'
scp "/本机许可证的绝对路径/minio.license" "<ECS登录用户名>@<ECS公网IP>:.hhjava-minio-upload/minio.license"
```

另开一个以同一 SSH 用户登录的 ECS 终端（此终端先不要执行 `sudo -i`），将上传文件安装到目标位置：

```bash
sudo install -m 0600 "$HOME/.hhjava-minio-upload/minio.license" /opt/hhjava-minio/minio.license
sudo test -s /opt/hhjava-minio/minio.license
```

这里 `$HOME` 只读取原 SSH 登录用户的主目录，不要改写它。成功标准：目标是非空文件，不是同名目录。不要打印或截图许可证正文。完成后回到第 5.2 节保留的 ECS 管理员终端，继续后续步骤。

## 6. 第四步：准备管理员凭据

在密码管理器中准备独立的管理员用户名和足够长的随机密码，不使用默认凭据，不复用 MySQL、Nacos 或用户登录密码。

在同一个 ECS 管理员 Bash 终端执行。密码由终端隐藏输入，不写进命令历史；文件只存值，不存 `KEY=VALUE`：

```bash
cd /opt/hhjava-minio
umask 077
read -r -p 'MinIO管理员用户名: ' HHJAVA_MINIO_ROOT_INPUT
read -r -s -p 'MinIO管理员密码: ' HHJAVA_MINIO_ROOT_PASSWORD_INPUT
printf '\n'
if [ -z "$HHJAVA_MINIO_ROOT_INPUT" ] || [ ${#HHJAVA_MINIO_ROOT_PASSWORD_INPUT} -lt 32 ]; then
    unset HHJAVA_MINIO_ROOT_INPUT HHJAVA_MINIO_ROOT_PASSWORD_INPUT
    printf '用户名不能为空，本文要求管理员密码至少32个字符，请重新执行本步骤。\n'
else
    printf '%s' "$HHJAVA_MINIO_ROOT_INPUT" > secrets/root_user
    printf '%s' "$HHJAVA_MINIO_ROOT_PASSWORD_INPUT" > secrets/root_password
    chmod 0600 secrets/root_user secrets/root_password
    unset HHJAVA_MINIO_ROOT_INPUT HHJAVA_MINIO_ROOT_PASSWORD_INPUT
fi
```

只有成功生成两个非空文件才继续。它们用于容器的文件型凭据变量，不需要直接把秘密填在 Compose 中。[MinIO 文件型配置变量](https://docs.min.io/aistor/reference/aistor-server/settings/)

文件权限不等于加密。许可证、凭据文件、`mc` 配置和后续备份都应留在受控机器/加密存储中，不能提交 Git。Docker Compose 的本地文件型 secrets 也不是自动加密的密码保险箱。[Docker Compose secrets 说明](https://docs.docker.com/compose/how-tos/use-secrets/)

## 7. 第五步：准备镜像和 Compose

### 7.1 首次拉取，再固定镜像摘要

在 ECS 执行：

```bash
docker pull quay.io/minio/aistor/minio:latest
docker image inspect --format '{{index .RepoDigests 0}}' quay.io/minio/aistor/minio:latest
```

第二条输出类似 `quay.io/minio/aistor/minio@sha256:...`。这是镜像标识，不是密码。执行 `nano /opt/hhjava-minio/.env`，填写实际完整输出：

```dotenv
MINIO_IMAGE=quay.io/minio/aistor/minio@sha256:<这里替换成上一步的实际完整摘要>
```

只在首次选择版本时使用 `latest`；部署配置固定摘要，后续重新启动不会无意升级。镜像拉取失败先处理 ECS 到官方镜像仓库的网络，不替换成来源不明的镜像。

### 7.2 创建 compose.yaml

在 ECS 执行 `nano /opt/hhjava-minio/compose.yaml`，粘贴：

```yaml
name: hhjava-minio
services:
  minio:
    image: ${MINIO_IMAGE:?请先在.env中设置实际镜像摘要}
    container_name: hhjava-minio
    restart: unless-stopped
    command:
      - minio
      - server
      - /mnt/data
      - --address
      - ':9000'
      - --console-address
      - ':9001'
      - --license
      - /minio.license
    ports:
      - '127.0.0.1:9000:9000'
      - '127.0.0.1:9001:9001'
    environment:
      MINIO_ROOT_USER_FILE: /run/secrets/root_user
      MINIO_ROOT_PASSWORD_FILE: /run/secrets/root_password
    secrets:
      - root_user
      - root_password
    volumes:
      - ./data:/mnt/data
      - ./minio.license:/minio.license:ro
secrets:
  root_user:
    file: ./secrets/root_user
  root_password:
    file: ./secrets/root_password
```

这里的宿主机是 ECS，不是 Mac。左侧 `./data` 是 ECS 的实际持久化目录；容器重建不应该删除它。`:ro` 表示容器只读访问许可证。

不要增加 `privileged: true`、挂载 Docker socket，或把端口改成面向所有网卡。不同镜像用户设置可能影响文件权限，遇到权限错误先核对实际运行 UID/GID，不用 `chmod 777` 解决。

### 7.3 检查并启动

```bash
cd /opt/hhjava-minio
test -s minio.license
test -s secrets/root_user
test -s secrets/root_password
docker compose config --quiet
docker compose up -d
docker compose ps
```

`config --quiet` 不输出完整配置。只有前面检查成功，才执行 `up -d`。容器应为运行状态；若持续重启，在本机受控查看 `docker compose logs --tail=50 minio`，先检查许可证、参数和目录权限，不公开粘贴原始日志。

## 8. 第六步：确认 API 就绪，建立 SSH 隧道

### 8.1 先在 ECS 检查 API

```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9000/minio/health/live
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9000/minio/health/ready
```

期望两次均返回 `200`。这证明当前探测可达且服务就绪，不证明应用账号权限、上传内容或 Java 代码已经正确。[MinIO HTTP 健康端点](https://docs.min.io/aistor/reference/aistor-server/http-endpoints/)

### 8.2 在 Mac 另开终端保持隧道运行

```bash
ssh -N -T \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L 127.0.0.1:19000:127.0.0.1:9000 \
  -L 127.0.0.1:19001:127.0.0.1:9001 \
  "<ECS登录用户名>@<ECS公网IP>"
```

没有输出且一直占用终端通常是正常现象；该终端不要关闭。SSH 已加密跨机器传输，所以本教程的 HTTP 只在两端回环连接上使用。

若提示本机端口被占用，先检查已有隧道；若确需更换 19000/19001，同时修改本文后续所有相应本机地址。

在 Mac 的第三个终端检查：

```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:19000/minio/health/ready
```

返回 `200` 后，在 Chrome 打开 `http://127.0.0.1:19001`，使用第 6 节的管理员凭据登录。管理页面能打开不等于 SDK endpoint 应填 19001；SDK 始终连接 API 的 19000。

## 9. 第七步：安装 mc 管理客户端

在 ECS 管理员终端操作。先执行 `uname -m`；以下两条下载命令只选符合架构的一条。

amd64（`x86_64`）：

```bash
curl -fL --retry 3 https://dl.min.io/aistor/mc/release/linux-amd64/mc -o /opt/hhjava-minio/mc-download
```

arm64（`aarch64`）：

```bash
curl -fL --retry 3 https://dl.min.io/aistor/mc/release/linux-arm64/mc -o /opt/hhjava-minio/mc-download
```

下载成功后执行。使用专用命令名，避免覆盖系统中其他同名 `mc` 程序：

```bash
install -m 0755 /opt/hhjava-minio/mc-download /usr/local/bin/hhjava-mc
hhjava-mc --version
export MC_CONFIG_DIR=/opt/hhjava-minio/mc
```

客户端版本应与所选服务端版本尽量接近。`MC_CONFIG_DIR` 指定其凭据配置目录；重新登录 ECS 管理员终端后，先重新执行这条 export，再运行下文管理命令。[官方 AIStor Client 说明](https://docs.min.io/aistor/reference/cli/)

配置管理员别名 `hhjava-admin`：

```bash
read -r -p 'MinIO管理员用户名: ' HHJAVA_MC_ROOT_INPUT
read -r -s -p 'MinIO管理员密码: ' HHJAVA_MC_ROOT_SECRET_INPUT
printf '\n'
hhjava-mc alias set hhjava-admin http://127.0.0.1:9000 "$HHJAVA_MC_ROOT_INPUT" "$HHJAVA_MC_ROOT_SECRET_INPUT"
unset HHJAVA_MC_ROOT_INPUT HHJAVA_MC_ROOT_SECRET_INPUT
chmod 0600 /opt/hhjava-minio/mc/config.json
hhjava-mc admin info hhjava-admin
```

成功标准：能看到部署信息。别名是本机客户端给地址和账号起的名字，不是存储桶，也不需要在 Nacos 填这个名字。

隐藏输入可以避免密码出现在命令历史，但传给 `mc` 的参数可能被有权查看进程的本机用户看到；这些命令仅在你控制的管理环境执行。不要打印 `config.json`、导出别名或开 shell 调试跟踪。

## 10. 第八步：创建私有桶和应用专用账号

### 10.1 创建存储桶

以下只针对本次新建的测试桶；若同名桶已存有业务数据，先检查用途，不改变未知桶的策略。

```bash
hhjava-mc mb hhjava-admin/hhjava-backup
hhjava-mc anonymous set none hhjava-admin/hhjava-backup
hhjava-mc anonymous get hhjava-admin/hhjava-backup
hhjava-mc ls hhjava-admin/hhjava-backup
```

桶已存在时，`mb` 可能提示已存在，确认它属于本次部署即可，不要删除重建。新桶没有对象时列表为空是正常现象。匿名访问策略应为不允许匿名访问。[创建桶命令](https://docs.min.io/aistor/reference/cli/mc-mb/)、[匿名访问策略说明](https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-set/)

### 10.2 编写只针对这个桶的权限策略

执行 `nano /opt/hhjava-minio/hhjava-policy.json`，填写：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetBucketLocation", "s3:ListBucket", "s3:ListBucketMultipartUploads"],
      "Resource": ["arn:aws:s3:::hhjava-backup"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:AbortMultipartUpload", "s3:ListMultipartUploadParts"],
      "Resource": ["arn:aws:s3:::hhjava-backup/*"]
    }
  ]
}
```

第一组是桶级权限，第二组是桶内对象权限；`*` 只覆盖这个桶里的对象，不是所有桶。不授予管理员权限、创建其他桶或修改用户策略的权限。分片操作权限服务于上传流程，不代表 Java 现有上传实现已经正确处理所有大文件。[MinIO 权限动作说明](https://docs.min.io/aistor/administration/iam/access/)

创建策略：

```bash
hhjava-mc admin policy create hhjava-admin hhjava-backup-rw /opt/hhjava-minio/hhjava-policy.json
```

`hhjava-backup-rw` 是策略名，不是密码。[创建策略命令](https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-create/)

### 10.3 创建应用账号并绑定策略

在密码管理器中为应用生成另一份长随机密码，与管理员密码不同。下面用 `hhjava-file-app` 作为示例账号；若更换账号名，后续命令与 IDEA 配置必须同步修改。

```bash
read -r -s -p '应用账号密码（请先保存到密码管理器）: ' HHJAVA_MC_APP_SECRET_INPUT
printf '\n'
hhjava-mc admin user add hhjava-admin hhjava-file-app "$HHJAVA_MC_APP_SECRET_INPUT"
hhjava-mc admin policy attach hhjava-admin hhjava-backup-rw --user hhjava-file-app
hhjava-mc alias set hhjava-app http://127.0.0.1:9000 hhjava-file-app "$HHJAVA_MC_APP_SECRET_INPUT"
unset HHJAVA_MC_APP_SECRET_INPUT
chmod 0600 /opt/hhjava-minio/mc/config.json
hhjava-mc ls hhjava-app/hhjava-backup
```

新用户本来没有默认权限，只有用户创建成功且策略绑定成功后，最后的列桶内对象操作才应成功。中途失败就停止并排查，不跳到下一步。[创建用户](https://docs.min.io/aistor/reference/cli/admin/mc-admin-user/mc-admin-user-add/)、[绑定策略](https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-attach/)

这一套内置应用账号的 access key 是 `hhjava-file-app`，secret key 是刚才设置的应用密码。不要把 Java 用户登录 Token 或 MinIO 管理员密码填到这里。

### 10.4 先用 mc 独立验证存储

执行 `nano /opt/hhjava-minio/smoke.txt`，写入一行不含秘密的测试文字。只对本次测试对象执行：

```bash
hhjava-mc cp /opt/hhjava-minio/smoke.txt hhjava-app/hhjava-backup/smoke/install-check.txt
hhjava-mc stat hhjava-app/hhjava-backup/smoke/install-check.txt
hhjava-mc cp hhjava-app/hhjava-backup/smoke/install-check.txt /opt/hhjava-minio/smoke-downloaded.txt
cmp /opt/hhjava-minio/smoke.txt /opt/hhjava-minio/smoke-downloaded.txt
```

`cmp` 没有输出且退出成功表示内容一致。确认目标只含测试数据后清理该对象：

```bash
hhjava-mc rm hhjava-app/hhjava-backup/smoke/install-check.txt
```

不要使用递归删除整个桶的命令。这个验证能把“存储本身的问题”与“Java 服务问题”分开。[复制对象](https://docs.min.io/aistor/reference/cli/mc-cp/)、[删除对象](https://docs.min.io/aistor/reference/cli/mc-rm/)

## 11. 第九步：在 Nacos 配置文件服务

### 11.1 先确认 Data ID、Namespace 和 Group

在 Chrome 打开你的 Nacos 控制台，进入“配置管理 → 配置列表”，选择目标开发命名空间。显示名称“开发环境”和 Namespace ID 不一定相同，以实际 ID 为准。

当前源码约定：

| 项目 | 本教程开发值 | 来源 |
| --- | --- | --- |
| 应用名 | `hhjava-backup-file` | 文件服务本地 `application.yml` |
| profile | `dev` | `SPRING_PROFILES_ACTIVE` |
| Data ID | `hhjava-backup-file-dev.yaml` | 应用名 + profile + `.yaml` |
| Namespace ID | `dev`，若环境使用其他 ID 则替换 | `NACOS_NAMESPACE` |
| Group | `hhjava`，若环境使用其他组则替换 | `NACOS_GROUP` |
| 配置格式 | YAML | 本地 Nacos 配置约定 |

已有同名配置时先导出备份，并在原文件中合并，不整段覆盖未知配置。Nacos 备份方法见 [Nacos](Nacos.md)。

### 11.2 新开发配置的完整示例

新建相应 Data ID，选择 YAML，填写以下内容。若是在原配置中合并，同级不能出现两个 `spring:`。

```yaml
server:
  address: 127.0.0.1
  port: 63030
  servlet:
    context-path: /

spring:
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 12MB

minio:
  endpoint: http://127.0.0.1:19000
  read-path: http://127.0.0.1:19000
  bucket: hhjava-backup
  access-key: ${HHJAVA_MINIO_ACCESS_KEY}
  secret-key: ${HHJAVA_MINIO_SECRET_KEY}
```

各项含义：

- `server.address/port` 让文件服务只在当前 Mac 本机 63030 上监听。该端口是教程选择，先确认未占用；不适用于跨机器直连。
- `context-path: /` 明确内部接口从 `/files/...` 开始，避免继承远端旧上下文路径而重复加前缀。
- multipart 限制由 Web 层限制请求体大小；不替代文件内容、所有权或上传总长度正确性检查。
- `endpoint` 和 `read-path` 在这套开发方案中完全相同，均无末尾 `/`、均不包含桶名、均不是 19001 控制台地址。这是适配当前 URL 解析规则，不是已经修复了解析设计。
- `HHJAVA_MINIO_ACCESS_KEY` 与 `HHJAVA_MINIO_SECRET_KEY` 是本文通过上述占位符明确引入的进程环境变量，不是现有开发脚本自动生成的值。

Nacos 不会帮你生成应用密钥。这两个占位符最终由运行 backup-file 的 Java 进程环境解析。发布成功后重新打开配置确认保存正确；以后修改 MinIO 连接属性，重启文件服务，不假定已有 `MinioClient` 会自动重建。

## 12. 第十步：配置 IDEA 的文件服务启动项

### 12.1 为什么要单独配置

当前 backup-file 的 `application.yml` 只导入 Nacos，不像 user/gateway 那样自动导入父目录 `.hhjava-dev-config/application.properties`。仅执行 `scripts/setup-dev-config.sh` 不等于文件服务已经拿到了所需变量。

### 12.2 先确认认证服务可用

先正常启动现有 user 和 gateway。用 Reqable 访问开发网关对应的 OIDC discovery 地址，例如：

```http
GET http://127.0.0.1:63010/user/.well-known/openid-configuration
```

从实际响应读取 `issuer` 和 `jwks_uri`，不要凭空拼接 user 内部端口与上下文路径；JWKS 地址必须从运行 backup-file 的 Mac 可达。`issuer` 应与签发 JWT 的值完全一致。

### 12.3 创建或编辑运行配置

1. 在 IDEA 打开 hhjava 根工程并完成 Maven 导入。
2. 找到 `hhjava-service/hhjava-backup-file/src/main/java/com/hhjava/www/BackupFileApplication.java`。
3. 通过运行图标创建运行配置，再打开 **Run → Edit Configurations**；若已有对应配置直接编辑。
4. 主类使用 `com.hhjava.www.BackupFileApplication`，模块选择 `hhjava-backup-file`，JDK 使用项目要求的 Java 17。
5. 在 Environment variables 中逐项添加下表；没有看到该字段时，在 Modify options 中启用它。
6. 保持配置为本机私有，不勾选 Store as project file，不把包含真实密码的运行配置或截图提交 Git。

| 环境变量 | 怎么填写 |
| --- | --- |
| `SPRING_PROFILES_ACTIVE` | `dev` |
| `NACOS_SERVER_ADDR` | 与当前可用 user/gateway 一致的 Nacos 地址和端口 |
| `NACOS_USERNAME` | 实际 Nacos 登录账号 |
| `NACOS_PASSWORD` | 实际 Nacos 密码，仅在本机私有配置中填写 |
| `NACOS_NAMESPACE` | 第 11 节选择的 Namespace ID |
| `NACOS_GROUP` | 第 11 节选择的 Group |
| `HHJAVA_SECURITY_JWT_ISSUER` | discovery 响应中的实际 issuer |
| `HHJAVA_SECURITY_JWT_JWK_SET_URI` | 可达的实际 JWKS URI，可使用 discovery 返回地址 |
| `HHJAVA_SECURITY_JWT_AUDIENCE` | 与 user 签发规则一致，项目默认 `hhjava-api` |
| `HHJAVA_MINIO_ACCESS_KEY` | `hhjava-file-app`，或你实际创建的应用账号 |
| `HHJAVA_MINIO_SECRET_KEY` | 第 10 节应用账号的 secret，不是管理员密码 |

文件服务只验证 JWT，不需要 RSA 私钥、OAuth client secret 或直接读取用户数据库的密码。不要把 user 的整套秘密复制给它。

### 12.4 构建、启动和确认

在 Mac 终端的 hhjava 根目录运行代码测试：

```bash
cd /Users/michael/Documents/java_demo/hhjava
mvn -pl hhjava-service/hhjava-backup-file -am test
```

保持 SSH 隧道运行，再用 IDEA 启动 `BackupFileApplication`。确认没有未解析占位符、Nacos 拉取失败或 Bean 创建失败。

在浏览器/Reqable 打开 `http://127.0.0.1:63030/v3/api-docs`：应返回文件服务的 OpenAPI JSON。没有 Bearer Token 请求 `/files/image` 等业务端点应被拒绝，不能因为调试就改成匿名。

测试通过、进程启动、SDK 实际传输成功是三个不同检查点；最后一个要继续完成接口联调。

## 13. 第十一步：先用 Reqable 直连验证文件接口

直连只用于本机隔离排障；不会绕过文件服务自身 JWT 验证。

### 13.1 获取 Access Token

按照 [注册与登录](登录.md) 注册测试账号，再调用移动端密码登录接口：

```http
POST http://127.0.0.1:63010/user/auth/mobile/login/password
Content-Type: application/json
```

```json
{"username":"<测试用户名>","password":"<该用户的登录密码>"}
```

这里填写的是 Java 用户账号，不是 MinIO 应用账号。把响应 `data.accessToken` 保存到 Reqable 私有变量；不要使用 `refreshToken` 调文件接口，也不要把 Token 写到本文或公开截图。

### 13.2 测试上传

先准备很小、不含真实业务数据的测试文件，文件名使用简单英文并保证本次测试唯一，避免当前实现覆盖同路径对象。

在 Reqable 新建请求：

| 设置项 | 内容 |
| --- | --- |
| Method | POST |
| URL | `http://127.0.0.1:63030/files/database` |
| Authorization | Bearer Token，填写私有变量中的 Access Token |
| Body 类型 | multipart/form-data |
| 字段 `file` | File 类型，选择一份小型测试文件 |
| 字段 `prefix` | Text 类型，例如 `dev-check-unique`，可省略 |

不要选择 JSON Body，也不要手工写缺少 boundary 的 `Content-Type`；让 Reqable 根据 multipart 自动生成。

另外两种上传只更换路径：图片用 `/files/image`，HTML 用 `/files/html`。三者都使用字段 `file` 和可选的 `prefix`；先完成一种，不使用不可信 HTML 或真实数据库测试。

成功时返回 HTTP 200，`ResponseResult.data` 是包含桶名和对象键的 URL。对象键大致是 `[prefix/]yyyy/MM/dd/原文件名`，日期以服务运行环境为准。

### 13.3 验证真的存到了服务器

在 Chrome 的 MinIO 控制台找到 `hhjava-backup`，进入返回 URL 对应的对象路径，检查文件大小；下载测试对象，与原文件比较内容或 SHA-256。Mac 可分别执行 `shasum -a 256 "/实际文件路径"` 比较结果。

返回 URL 不是预签名 URL，桶仍为私有：直接在浏览器打开 API 文件地址出现 403 可以是正常的权限拒绝，不要把桶改为公开来“修复”。当前项目也没有实现 HTTP 下载 Controller；控制台或 `mc` 下载是存储验收手段，不是 App 下载能力已经完成。

### 13.4 测试删除

只删除本次测试上传得到的 URL。在 Reqable 新建：

| 设置项 | 内容 |
| --- | --- |
| Method | DELETE |
| URL | `http://127.0.0.1:63030/files` |
| Authorization | 同上，使用有效 Access Token |
| Query 参数名 | `url` |
| Query 参数值 | 原样粘贴本次上传响应的完整 URL，让 Reqable 负责 URL 编码 |
| Body | 留空 |

先在控制台确认对象确实存在，再发送删除，再确认对象消失。只收到“删除成功”不足以证明删的是期望对象；对象存储删除不存在对象也可能正常返回。

### 13.5 最少做两项失败测试

1. 不带 Token 上传，应被文件服务拒绝。
2. 对独立测试请求使用失效 Token，应认证失败；不要修改共享服务凭据制造故障。

存储不可达、账号权限不足等更多测试在受控环境进行，不通过改坏已有业务账号来测试。

## 14. 第十二步：接入 gateway 路由

只有直连文件服务成功后才做这一步，方便区分“文件服务失败”和“网关路由失败”。

进入 Nacos 的 `hhjava-gateway-dev.yaml`，先导出备份。下面是本教程新增的开发路由方案，不代表远端已经存在。把一个新的路由项合并到原来的 `spring.cloud.gateway.routes` 列表，保留 user 等原有路由：

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: hhjava-backup-file-dev
          uri: http://127.0.0.1:63030
          predicates:
            - Path=/backup/**
          filters:
            - StripPrefix=1
```

这里直接使用本机地址，是因为教程让 gateway 和文件服务都运行在同一台 Mac，且文件服务只绑定本机。先不把它改成 `lb://hhjava-backup-file`：服务发现中的注册地址需要真实网络可达，不能假定 ECS/Nacos 可以直接调用你的 Mac 回环地址。

路径转换：`/backup/files/database` 去掉第一段 `/backup` 后，交给下游的 `/files/database`。`StripPrefix=1` 不是再删除一次 `/files`。[Gateway StripPrefix 官方说明](https://docs.spring.io/spring-cloud-gateway/reference/4.1/spring-cloud-gateway/gatewayfilter-factories/stripprefix-factory.html)

发布配置后重启 gateway，并用相同请求验证：

| 操作 | 网关 URL（开发网关端口以实际环境为准） |
| --- | --- |
| 上传图片 | `http://127.0.0.1:63010/backup/files/image` |
| 上传数据库 | `http://127.0.0.1:63010/backup/files/database` |
| 上传 HTML | `http://127.0.0.1:63010/backup/files/html` |
| 删除 | `http://127.0.0.1:63010/backup/files`，仍带 Query 参数 `url` |

全部携带 Access Token，不能把 `/backup/**` 加到匿名白名单。gateway 和文件服务各自验签，路由前缀也不会改变 MinIO 返回的对象 URL。

Reqable 和原生 App 不受浏览器 CORS 同源策略限制；当前 gateway 的跨域配置主要覆盖 `/user/**`，不能据此认定浏览器 H5 已可以跨域调用新 `/backup/**`。若要 H5 上传，应另外配置精确 Origin 的 CORS，并完成浏览器验收。

## 15. 完成检查表

- [ ] ECS 已有可用 Docker/Compose，没有影响原有 MySQL/Nacos 容器。
- [ ] 已获得并使用有效许可证，镜像固定到实际摘要。
- [ ] 管理员凭据与应用凭据不同，未提交 Git 或输出到公开日志。
- [ ] API 和控制台只绑定 ECS 回环地址，公网 9000/9001 未开放。
- [ ] Mac 的 SSH 隧道可用，API readiness 返回 200。
- [ ] `hhjava-backup` 是私有桶，应用账号仅有指定桶权限。
- [ ] `mc` 上传、下载比较和测试对象删除成功。
- [ ] Nacos Data ID、Namespace ID、Group 与 IDEA 变量一致。
- [ ] `endpoint` 与 `read-path` 均为本机 API 隧道地址，且相同、无末尾斜杠。
- [ ] backup-file 测试通过并能启动，JWT 参数与签发方一致。
- [ ] Reqable 直连上传和删除成功，文件内容校验一致，无 Token 请求被拒绝。
- [ ] 合并网关路由后，经 gateway 的同一组请求也成功。

只有实际完成的项目才打勾。本教程没有代表你完成真实 ECS/MinIO 联调，也不能把小文件通过推断为所有大文件或多用户场景安全可用。

## 16. 日常启停、迁移与排障

### 16.1 日常操作

在 ECS 管理员终端进入 `/opt/hhjava-minio`：

```bash
docker compose ps
docker compose stop
docker compose start
```

`stop/start` 是停止/启动当前实例，执行前确认没有正在上传的请求。Mac 上重建 SSH 隧道后，Java 才能再次通过 19000 访问它。

不要为了重启而删除 `data`、执行清理所有 Docker 卷、重装 MySQL/Nacos 或改成开放全部端口。

### 16.2 换电脑与换服务器

只换 Mac：ECS 数据仍在服务器；重新准备 SSH 访问、IDEA 私有变量和隧道，确认项目配置文件的位置。不会因为复制项目源码就自动带上 MinIO 密钥。

换 ECS：需要迁移对象数据，还要保存或重建桶配置、IAM 用户/策略、许可证和部署配置。Nacos 备份只包含其配置条目，不包含 MinIO 对象和 IAM。活动数据目录不能简单边写边复制；停写后做一致性备份，或使用适合版本的迁移工具并验证完整性。升级镜像和迁移数据不要同时未经测试地进行。

### 16.3 常见问题

| 现象 | 优先检查 |
| --- | --- |
| Docker 命令存在但连接 daemon 失败 | 服务是否启动、当前账号权限；不要直接卸载 |
| 容器不断重启 | 许可证是否为文件且有效、镜像参数、凭据文件和数据目录权限 |
| `Permission denied` | 查看容器镜像运行用户与挂载目录 UID/GID；仅按实际用户修正专用目录权限，不用 777 |
| ECS 本机 API 正常，Mac 19000 失败 | SSH 隧道是否还在运行、登录用户是否允许转发、本机端口冲突 |
| Java 提示缺少占位符 | IDEA 是否设置对应变量；backup-file 不自动导入 user 的本机秘密文件 |
| Nacos 配置为空或超时 | Data ID 后缀、Namespace ID、Group、账号权限及 Nacos 客户端所需网络端口 |
| `AccessDenied` / `InvalidAccessKeyId` | 应用账号、secret、策略是否绑定到该账号与该桶 |
| `NoSuchBucket` | 桶是否创建，配置桶名大小写是否一致 |
| 请求提示应访问 API 端口 | endpoint 误填了控制台 9001/19001 |
| 接口 401 | Access Token 是否过期，issuer/audience/JWKS 是否与签发方一致 |
| 接口 404 | 是否混用了 `/backup`、服务 context-path 和 `/files`，网关是否正确 StripPrefix |
| 网关 502/503，直连正常 | 路由目的地址是否从 gateway 所在机器可达，别把另一台机器的 localhost 当成本机 |
| 上传 413 | multipart 大小限制；先用小测试文件，不一律调成无限制 |
| URL 打开 403 | 私有桶未授权访问属预期，不能直接开放数据库备份 |
| 文件长度或内容不一致 | 当前 `InputStream.available()` 长度缺陷，需要改代码，不能靠重装 MinIO 解决 |

## 17. 当前项目代码怎样接入

### 17.1 模块与自动装配

`hhjava-basic/hhjava-file-starter` 是普通组件 Jar，负责存储；`hhjava-backup-file` 是可启动业务服务。根 POM 管理 MinIO SDK 版本，消费方不必复制整份 SDK 实现。

`MinIOConfigProperties` 绑定 `minio` 下的 `endpoint`、`accessKey`、`secretKey`、`bucket`、`readPath`。YAML 的 `access-key`、`read-path` 通过 Spring 属性绑定对应 Java 驼峰字段。

`MinIOConfig` 的条件是存在 `MinioClient` 类且匹配 `minio.endpoint` 属性；它分别为 `MinioClient`、`FileStorageService` 提供默认 Bean，已有相应 Bean 时退让。

自动配置清单为 Starter 的 `src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，其中包含 `com.hhjava.www.config.MinIOConfig`。消费方不需要扩大包扫描；`MinIOFileStorageService` 由构造器接收客户端和配置，不用 `@Service` 等待扫描。

下面是 `MinIOConfig` 中创建默认存储实现的方法节选，不是单独可运行的类：

```java
@Bean
@ConditionalOnMissingBean(FileStorageService.class)
public FileStorageService fileStorageService(MinioClient minioClient) {
    // 应用没有提供自己的存储服务时，才创建默认 MinIO 实现。
    return new MinIOFileStorageService(minioClient, minIOConfigProperties);
}
```

缺少 endpoint 时不创建两个默认 Bean，但 FileController 仍依赖存储接口，所以这不等于文件服务可以不配置存储正常运行。原理见 [SpringBoot](SpringBoot.md)。

### 17.2 上传与错误传播

```text
FileController 接收 MultipartFile 并打开输入流
    → FileStorageService
    → MinIOFileStorageService
    → MinioClient 调用服务端
    → 返回文件 URL，由 Controller 包装 ResponseResult
```

Controller 使用 `try-with-resources` 关闭自己打开的上传流，存储层只读取；下载时存储层自己打开 SDK 响应流，也由它关闭。存储 SDK 故障转换为保留 cause 的 `FileStorageException`，不吞掉删除失败、不重复输出含秘密的 SDK 异常。

上传 Controller 的调用结构如下，实际方法允许抛出 `IOException`，由公共异常处理器处理：

```java
// 方法体节选：发生异常时也会尝试关闭自己打开的流。
try (InputStream inputStream = file.getInputStream()) {
    String url = fileStorageService.uploadDbFile(
            prefix != null ? prefix : "databases", file.getOriginalFilename(), inputStream);
    return ResponseEntity.ok(ResponseResult.success(url));
}
```

异常由 Servlet 公共处理器返回安全的服务错误，不在 Starter 耦合 HTTP 响应。详见 [异常处理](异常处理.md)。

### 17.3 配置完成也没有自动解决的边界

- 当前上传使用 `InputStream.available()` 估计长度，不能保证等于任意流总长度；正确实现仍需明确总长度或未知长度分片策略。[Java 17 InputStream 文档](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/io/InputStream.html)
- 上传用 `readPath` 拼接 URL，删除/内部下载用 `endpoint` 解析。教程令二者相同，只保证该配置不触发两者不一致问题，未完成 URL 解析与对象键模型的重构。
- 文件接口目前要求认证，但没有完整的对象所有权、目标范围、文件名唯一化和内容校验。MinIO 应用账号的桶级策略不能区分 hhjava 中不同登录用户；正式多用户使用前必须补齐业务授权。
- 相同日期、前缀、文件名可能覆盖同一对象，因此测试也必须选择独立文件名和测试前缀。
- 内部下载返回完整 `byte[]`，没有对外下载 Controller，不是已实现的大文件流式下载。
- HTML 主动内容、浏览器读取域隔离、私有文件授权下载需要单独设计和验证。

安装、配置、单元测试、真实小文件联调、业务安全验收是不同层次，不能把其中一步成功描述为全部完成。
