# Nacos 2.5.5 安装、配置与使用

Nacos 是微服务的**注册中心和配置中心**：记录“服务在哪里”和“服务使用什么配置”。Java 服务通过客户端连接它，App 不应直接访问 Nacos。

本文固定使用 **2.5.5**，按“安装 → 控制台配置 → Java 接入 → 备份维护”操作。新装部分面向全新实例；已有实例可以跳过安装，按实际账号、挂载目录和网络配置使用。

## 1. 先理解这些概念

| 概念 | 通俗解释 | 用途或例子 |
| --- | --- | --- |
| 注册中心 | 保存服务名称及实例地址 | `hhjava-user` 注册自己，调用方按服务名查地址 |
| 服务实例 | 一个正在运行的服务进程 | 同一个服务可以有多个实例，各自具有 IP 和端口 |
| 配置中心 | 集中存放环境配置 | 数据库地址、非秘密的功能开关、网关路由等 |
| Namespace（命名空间） | 一层资源隔离 | 常用来区分 `dev`、`test`、`prod` |
| Group（分组） | 命名空间内的业务分组 | 例如 `hhjava`；配置和服务注册都有自己的分组设置 |
| Data ID（配置标识） | 一份配置的名称 | 例如 `hhjava-user-dev.yaml` |
| Profile（运行环境配置） | Spring Boot 选用的一组配置 | `dev`、`prod` 是项目约定，不会自动替你创建 Nacos 命名空间 |
| 镜像 | 创建容器使用的软件模板 | `nacos/nacos-server:v2.5.5` 中 `v2.5.5` 是版本标签 |
| 容器 | 从镜像创建的运行实例 | 本文的容器名为 `nacos-server` |
| 挂载 | 将容器目录连接到宿主机目录或数据卷 | 容器重建后，已正确挂载的数据仍可保留 |
| Derby | Nacos 可使用的内置数据库 | 数据保存在文件中；备份运行中的数据库不能简单复制文件 |

一份配置由 **Namespace ID + Group + Data ID** 唯一定位。Namespace 的“显示名称”和“ID”不是一回事，Java 配置使用的是 ID。`应用名-环境.yaml` 是便于管理的命名习惯，不是 Nacos 强制要求。

服务发现的过程是：服务启动后登记地址，调用方查询可用实例，再向该实例发送业务请求。Nacos 不会替服务处理业务，也不会因为注册成功就自动生成所有网关路由。临时实例失联后会被剔除，不保证停止进程的一瞬间就在控制台消失。

配置中心把环境差异集中起来，但不是把所有内容都移到服务器：应用名称、Nacos 地址、认证信息来源和配置导入入口，必须在连接 Nacos 之前就能获得。数据库密码、私钥等秘密继续通过受限文件或部署环境提供，不写进公开教程、Git 或普通配置导出包。

## 2. 在 ECS 安装 Nacos 2.5.5

### 2.1 准备环境与确认安装范围

本文使用 **Linux x86_64 ECS + Docker + 单机模式 + 内置 Derby**，适合学习和单节点使用。Derby 无需额外创建 MySQL 数据库；需要高可用时，应另外设计集群和数据库部署，不能把单机教程当作高可用方案。

**第 2 节命令均在 ECS 的 root Bash 终端执行，初始工作目录不限。每块命令成功后再执行下一块。**

```bash
uname -m
docker version
command -v bash curl openssl tar sha256sum
free -h
df -h /opt
docker ps -a --filter 'name=^/nacos-server$'
ss -lnt | grep -E ':(8848|9848)[[:space:]]' || true
```

预期架构为 `x86_64`，Docker 的客户端与服务端均可用。**如果已存在 `nacos-server` 或端口已占用，停止新装步骤；已有实例直接从第 3 节开始使用。** 不要删除容器、移动挂载目录或清空数据来重新安装。已有实例的数据位置以 `docker inspect` 为准，不一定是本文的新装目录。

### 2.2 拉取固定版本镜像

```bash
docker pull --platform linux/amd64 nacos/nacos-server:v2.5.5
docker image inspect nacos/nacos-server:v2.5.5 \
  --format '平台={{.Os}}/{{.Architecture}} 摘要={{json .RepoDigests}}'
```

确认拉取成功、平台为 `linux/amd64`，记录返回的镜像摘要以便以后重建同一镜像。不要改用 `latest`。Docker 镜像内已包含运行环境，宿主机无需另装 Java 来启动这个容器。[2.5.5 发布记录](https://github.com/alibaba/nacos/releases/tag/2.5.5)、[Docker 部署说明](https://nacos.io/docs/v2.5/quickstart/quick-start-docker/)

### 2.3 创建数据目录与鉴权配置

以下整块命令只用于首次安装。目录存在就停止，防止覆盖配置。括号创建子 Shell，`set -e` 使其中命令失败时停止，`umask 077` 限制新文件权限。

```bash
(
  set -eu
  umask 077
  mkdir /opt/nacos-2.5.5
  mkdir /opt/nacos-2.5.5/data /opt/nacos-2.5.5/logs
  nacos_token=$(openssl rand -base64 48)
  nacos_identity=$(openssl rand -hex 32)
  cat > /opt/nacos-2.5.5/nacos.env <<EOF
MODE=standalone
NACOS_AUTH_ENABLE=true
NACOS_AUTH_TOKEN=$nacos_token
NACOS_AUTH_IDENTITY_KEY=nacos-node-identity
NACOS_AUTH_IDENTITY_VALUE=$nacos_identity
JVM_XMS=256m
JVM_XMX=512m
JVM_XMN=128m
EOF
  chmod 600 /opt/nacos-2.5.5/nacos.env
)
```

生成的文件：

| 路径 | 用途 |
| --- | --- |
| `/opt/nacos-2.5.5/data` | 保存 Derby 数据库及其他持久化数据 |
| `/opt/nacos-2.5.5/logs` | 保存 Nacos 日志 |
| `/opt/nacos-2.5.5/nacos.env` | Docker 读取的环境配置，含鉴权密钥，仅 root 可读写 |

`NACOS_AUTH_ENABLE=true` 开启鉴权；`NACOS_AUTH_TOKEN` 是用于签发登录令牌的随机密钥，**不是登录密码**。`NACOS_AUTH_IDENTITY_KEY/VALUE` 用于服务端身份识别。`JVM_XMS/XMX/XMN` 分别设置 Java 虚拟机的初始堆、最大堆和年轻代大小；堆外内存也占容器内存。[鉴权参数说明](https://nacos.io/docs/v2.5/manual/admin/auth/)

执行 `ls -ld /opt/nacos-2.5.5 /opt/nacos-2.5.5/nacos.env`，预期目录权限为 `drwx------`、配置文件为 `-rw-------`。不要输出或提交环境文件；重建容器应沿用它，不要重新生成密钥。

### 2.4 创建并启动容器

```bash
docker run -d \
  --name nacos-server \
  --restart unless-stopped \
  --env-file /opt/nacos-2.5.5/nacos.env \
  --memory 1g --memory-swap 1g --cpus 1 \
  --log-opt max-size=10m --log-opt max-file=3 \
  -p 127.0.0.1:8848:8848 \
  -p 127.0.0.1:9848:9848 \
  -v /opt/nacos-2.5.5/data:/home/nacos/data \
  -v /opt/nacos-2.5.5/logs:/home/nacos/logs \
  nacos/nacos-server:v2.5.5
```

- `-d`：后台运行；`unless-stopped`：异常退出或 Docker 重启后自动恢复，但保留人为停止状态。
- `-v`：将容器内的数据、日志保存到宿主机；删除容器不等于删除这些目录。
- `--memory` 与 `--memory-swap` 相同：不额外使用 swap；`--cpus 1` 限制最多使用一个 CPU 核心的计算额度。
- 两个 `--log-opt` 限制 Docker 标准输出日志大小，不负责清理挂载目录中的 Nacos 日志。

| 端口 | 用途 | 本教程是否映射到宿主机 |
| --- | --- | --- |
| `8848` | 控制台与 HTTP API（程序接口） | 是，仅回环地址 |
| `9848` | Java 客户端使用的 gRPC（远程过程调用）通信 | 是，仅回环地址 |
| `9849`、`7848` | 服务端节点间通信 | 否，本教程为单机 |

`127.0.0.1` 表示当前机器自己。此处只允许 ECS 本机连接；Mac 按 [SSH 隧道访问 ECS 服务](SSH隧道访问ECS服务.md#nacos-mysql)连接。不要直接改成对公网发布端口。

### 2.5 验证服务启动

```bash
docker ps --filter 'name=^/nacos-server$'
curl -fsS --max-time 5 http://127.0.0.1:8848/nacos/v1/console/health/readiness
curl -fsS --max-time 5 http://127.0.0.1:8848/nacos/v1/console/server/state
```

首次初始化需要时间；连接失败时稍后重试。预期 readiness 返回 `OK`，状态接口中的 `version` 为 `2.5.5`；这两个探活接口在该镜像默认配置中允许匿名访问。容器显示 `Up` 只代表进程还在，不代表服务已经可用。

若反复失败，在 ECS 查看 `docker logs --tail 80 nacos-server` 和 `docker stats --no-stream nacos-server`，按第 6 节排查。分享日志前先检查并遮盖敏感信息。

## 3. 打开控制台并创建配置

### 3.1 创建命名空间、配置和应用账号

在控制台用管理员完成以下步骤，使用独立学习资源，不覆盖 hhjava 的业务配置：

1. 打开“命名空间”，创建 **ID 为 `demo-dev`**、显示名为“学习环境”的命名空间；已有相同 ID 时复用。
2. 打开“配置管理 → 配置列表”，选择该命名空间，新增 Data ID 为 `demo-service-dev.yaml`、Group 为 `demo`、格式为 YAML 的配置：

   ```yaml
   demo:
     greeting: "你好，Nacos"
   ```

3. 点击“发布”，在配置列表重新打开，确认内容、Data ID、Group 和命名空间正确。Group 在创建配置时填写，无需另建分组目录。
4. 在“权限控制 → 用户列表”创建应用账号 `demo-app`，设置独立密码；账号存在时先核对，不重置现有密码。
5. 在“角色管理”创建 `demo-role` 并关联 `demo-app`；在“权限管理”给该角色授权 `demo-dev` 命名空间的读写权限。此学习服务既读取配置又注册服务，需要相应权限。控制台按命名空间授权，不要把它理解成只允许访问 `demo` 分组；因此学习资源使用独立命名空间。

不要给学习账号授予管理员角色或其他命名空间权限。退出管理员，用 `demo-app` 登录，确认能够查看学习配置，再进行 Java 接入。配置正文只放非秘密参数，密码和私钥由应用受限配置提供。[2.5.5 控制台授权实现](https://github.com/alibaba/nacos/blob/2.5.5/console-ui/src/pages/AuthorityControl/PermissionsManagement/NewPermissions.js)

## 4. Java 服务接入

### 4.1 准备依赖

本节在 **Mac 的现有 Spring Boot 学习项目**中操作：项目应已有 `pom.xml`、启动类和 `src/main/resources/application.yml`，能正常启动，且父 POM 已管理兼容的 Spring Cloud 与 Spring Cloud Alibaba 版本。IDE 是集成开发环境，例如 IntelliJ IDEA；POM 是 Maven 项目的依赖与构建配置文件。版本未管理时，先按 [Spring Cloud Alibaba 版本说明](https://sca.aliyun.com/docs/2025.x/overview/version-explain/) 配好对应 BOM（统一依赖版本清单）。hhjava 已有父 POM，不要给现有模块重复添加依赖或更换框架版本。

在学习项目 `pom.xml` 的 `<dependencies>` 中添加所需依赖，然后在 IDEA 的 Maven 面板重新加载项目：

需要服务注册时使用：

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
```

需要读取配置时使用：

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

两者职责不同：只引入配置依赖，不等于服务一定会注册。

### 4.2 在应用中显式导入

Spring Cloud Alibaba 2025.x 使用 Spring Boot 的 **ConfigData（配置数据加载机制）**，通过 `spring.config.import` 明确列出要读取的配置。可在学习服务的 `src/main/resources/application.yml` 使用下面的连接部分：[官方接入说明](https://sca.aliyun.com/docs/2025.x/user-guide/nacos/advanced-guide/)

```yaml
spring:
  application:
    name: demo-service
  profiles:
    active: dev
  cloud:
    nacos:
      server-addr: ${NACOS_SERVER_ADDR:127.0.0.1:18848}
      username: ${NACOS_USERNAME}
      password: ${NACOS_PASSWORD}
      discovery:
        namespace: demo-dev
        group: demo
      config:
        namespace: demo-dev
        group: demo
  config:
    import:
      - "nacos:demo-service-dev.yaml"
```

启动前在 IDE 的运行环境或受限部署配置中提供 `NACOS_USERNAME`、`NACOS_PASSWORD`，用户名使用第 3.1 节创建的 `demo-app`，密码使用你为它设置的密码；不要把真实值写到 YAML 示例里。ECS 运行时将 `NACOS_SERVER_ADDR` 设为 `127.0.0.1:8848`。如果某个环境尚未启用鉴权，应先核实实际策略，不能靠关闭鉴权来解决连接失败。

为了检查配置读取，在学习项目带 `@SpringBootApplication` 注解的启动类文件中加入以下 import：

```java
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.core.env.Environment;
```

在该类内部、`main` 方法之外添加以下方法。`Environment` 是应用的运行时配置集合，`ApplicationRunner` 会在应用启动后执行；这里仅打印学习用的非秘密属性，不打印全部配置：

```java
@Bean
ApplicationRunner showNacosGreeting(Environment environment) {
    return args -> System.out.println(
            "demo.greeting=" + environment.getRequiredProperty("demo.greeting"));
}
```

在 IDEA 打开启动类，运行其 `main` 方法；若隧道已断开，先按 [SSH 隧道文档](SSH隧道访问ECS服务.md#nacos-mysql)恢复连接。启动后检查两件不同的事情：

1. 在控制台“服务管理 → 服务列表”选择 `demo-dev`，检查 `demo` 分组下是否出现 `demo-service`，实例 IP 和端口是否正确。
2. 启动日志应显示 `demo.greeting=你好，Nacos`。在控制台把这个学习值改为“配置已更新”，发布后重新启动学习应用，应看到新值。此处验证重新读取，不把启动日志当成动态刷新验证。

不带 `optional:` 的导入表示应用需要这份配置，读取失败时不能假装启动正常。只有确实可以缺少的配置才使用 `optional:nacos:...`。

### 4.3 多份配置、公共配置和优先级

公共配置就是多项服务共用的一份配置，不需要为它引入另一套加载机制。比如先在 `demo` 分组创建 `common.yaml`，然后显式导入公共和服务专有配置：

```yaml
spring:
  config:
    import:
      - "nacos:common.yaml"
      - "nacos:demo-service-dev.yaml"
```

只有确实共用的非秘密配置才放入 `common.yaml`；不要让所有服务共享认证服务的私钥或数据库账号。

理解优先级时先记住三点：

- 导入内容通常可以覆盖声明导入的配置文档；同一导入列表中，后面的导入具有更高优先级。
- 命令行参数、Java 系统属性、操作系统环境变量和配置文件属于不同配置来源，不能简单概括成“Nacos 永远最高”或“本地永远最高”。
- Profile 激活阶段、多段 YAML 和扩展加载器也影响最终结果。排查时检查具体属性来源，不靠调整一个无关开关碰运气。[Spring Boot 外部配置说明](https://docs.spring.io/spring-boot/reference/features/external-config.html)

配置更新能否不停机生效，还取决于消费该属性的组件是否支持刷新；监听到配置变化不等于端口、数据库连接池等所有对象都会自动重建。

### 4.4 hhjava 项目对应关系

项目通常使用 Namespace ID `dev`、Group `hhjava`，各服务显式导入自己的 `应用名-环境.yaml`；不要只改应用名称却保留另一个服务的 Data ID。

hhjava 的本机秘密目录为 `java_demo/.hhjava-dev-config/`，已在该仓库的 `.gitignore` 中忽略。请沿用各模块自己的 `application.yml` 与启动配置，不要把上面的学习配置覆盖到业务模块。学习账号 `demo-app` 也不能代替有 `hhjava` 资源权限的业务账号。

各服务的启动配置和部署步骤分别见 hhjava 项目的 `docs/architecture.md` 与 `docs/deployment.md`。它们位于另一个本地仓库，不随本知识站发布；在 Mac 打开：

```bash
open "/Users/michael/Documents/java_demo/hhjava/docs"
```

## 5. 日常管理与备份

### 5.1 查看状态、停止和启动

以下在 **ECS root 终端**执行：

```bash
docker inspect --format '运行={{.State.Running}} OOM={{.State.OOMKilled}} 重启次数={{.RestartCount}}' nacos-server
docker stats --no-stream nacos-server
docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' nacos-server
```

`OOM=true` 表示曾被内存不足终止，应结合日志和主机内存排查。最后一条用于核对真实数据目录；已有容器的路径可能与新装示例不同。

维护窗口可执行 `docker stop --time 60 nacos-server` 停止，执行 `docker start nacos-server` 恢复。停止期间客户端无法正常访问配置中心；恢复后重新执行第 2.5 节检查，并验证应用能读取配置和注册服务。

修改 `nacos.env` 后，`docker restart` 不会重新读取宿主机环境文件。环境变量在创建容器时确定；需要变更时先备份，再在维护窗口按核实的原镜像、挂载和端口参数重建，不清空数据目录。

### 5.2 导出配置

在控制台逐个选择命名空间，进入配置列表，选中要保留的配置并导出 ZIP。核对是否只选了当前页，记录 Namespace ID、Group、Data ID、格式和数量。

配置 ZIP 适合迁移配置内容，**不等于完整数据库备份**，不能代替用户、权限、历史记录或应用密钥的备份。备份放在受限目录，不提交到 Git。

### 5.3 备份 Derby 实例

Derby 正在运行时不能直接复制数据库目录。安排停服窗口，在 **ECS root Bash** 中执行下面的整块命令：它自动读取容器实际的数据挂载，不假定现有实例使用新装目录。

```bash
(
  set -eu
  umask 077
  test "$(docker inspect -f '{{.State.Running}}' nacos-server)" = true
  nacos_data=$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/home/nacos/data"}}{{.Source}}{{end}}{{end}}' nacos-server)
  test -n "$nacos_data" && test -d "$nacos_data"
  nacos_backup=$(mktemp -d /var/backups/nacos-2.5.5.XXXXXX)
  printf '备份位置：%s\n' "$nacos_backup"
  docker inspect nacos-server > "$nacos_backup/container.json"
  docker cp nacos-server:/home/nacos/conf "$nacos_backup/conf"
  trap 'docker start nacos-server >/dev/null' EXIT
  docker stop --time 60 nacos-server
  tar -C "$nacos_data" -cpf "$nacos_backup/data.tar" .
  (cd "$nacos_backup" && sha256sum data.tar > SHA256SUMS && sha256sum -c SHA256SUMS)
)
```

预期摘要检查显示 `data.tar: OK`，随后容器恢复启动；再检查 readiness。退出处理会尝试恢复容器，但不能保证主机断电或强制终止时也能执行，必须检查最终状态。

`container.json` 含容器环境变量，可能包含密钥；整个备份目录保持仅 root 可访问。另行保存实际使用的环境文件和应用凭据；新装示例为 `/opt/nacos-2.5.5/nacos.env`。完整恢复需要相同镜像、数据库、配置及凭据，文件校验通过不代表已完成恢复演练。

### 5.4 迁移到另一台服务器

1. 在目标服务器安装同版本的 Nacos 2.5.5，完成管理员初始化，先保持独立访问。
2. 若只迁移配置，在空的目标命名空间中创建相同 Namespace ID，再导入配置 ZIP；同名冲突先核对，不直接覆盖。
3. 核对 Group、Data ID、格式、数量和内容，重新建立用户、角色与权限；恢复应用的外部凭据。
4. 若需要完整 Derby 恢复，在隔离实例中验证完整备份；恢复时目标容器必须停止，将归档解到新目录并挂载，不能覆盖正在运行的数据。
5. 用受控 Java 客户端确认配置读取和服务注册，再切换业务应用的 Nacos 地址。使用服务发现时还要验证服务实例地址能够被调用方访问。
6. 保留原实例和备份，直到配置、登录及业务接口验收完成。不要用删库或删除数据卷来排查恢复失败。

## 6. 常见问题

| 现象 | 先检查什么 |
| --- | --- |
| 容器名已存在或端口被占用 | 是否已有 Nacos；先查看现有实例，不重复安装或直接删除 |
| 浏览器能打开，Java 连不上 | SSH 隧道是否同时转发 `18848` 和 `19848`；应用地址是否正确 |
| 控制台要求设置密码 | 全新实例需要初始化管理员；不要尝试默认密码 |
| 403 或认证失败 | 应用用户名、密码、角色权限；服务端 Token 是否为有效 Base64 密钥，不通过关闭鉴权解决 |
| 找不到配置 | Namespace ID、Group、Data ID 是否一致，配置是否发布，账号是否有读取权限 |
| 注册成功但无法调用服务 | 注册的 IP/端口是否能被调用方访问；Nacos 隧道不转发业务接口流量 |
| 注册列表为空 | 是否添加发现依赖并启用注册，是否选对命名空间/分组；固定路由部署可能有意关闭注册 |
| 配置修改没有立即生效 | 消费属性的组件是否支持刷新，是否被其他配置来源覆盖；必要时安排应用重启 |
| 容器反复重启或 readiness 失败 | 查看日志、磁盘/目录权限、内存和鉴权参数；`Up` 不等于就绪 |
| 环境文件改了却未生效 | `docker restart` 不会重新读取 `--env-file`，需要保留数据后按计划重建容器 |

分享日志前先脱敏，不复制完整配置、凭据或个人数据。
