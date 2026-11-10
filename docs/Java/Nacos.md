# Nacos

Nacos 是微服务的**注册中心和配置中心**。可以把它理解成两本集中维护的册子：一本记录“服务在哪里”，另一本记录“服务使用什么配置”。Java 服务通过客户端连接 Nacos，App 不应直接访问 Nacos。

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

## 3. Java 服务如何接入

### 3.1 准备依赖

Spring Boot、Spring Cloud、Spring Cloud Alibaba 必须使用相互兼容的版本组合。hhjava 已在父 POM 管理版本，子模块按需声明依赖，不要为升级 Nacos 服务端随意修改整套 Java 框架版本。

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

### 3.2 在控制台创建一份学习配置

下面用独立学习服务 `demo-service` 说明最小配置流程，**不是让你覆盖 hhjava 现有的 application.yml**。

1. 打开 Nacos 控制台，进入“命名空间”，创建 ID 为 `dev`、显示名为“开发环境”的命名空间；若已经存在，不重复创建。
2. 进入“配置管理 → 配置列表”，选中“开发环境”。
3. 新建配置，填写 Data ID `demo-service-dev.yaml`、Group `demo`，格式选择 YAML。
4. 填入以下非秘密内容并发布：

   ```yaml
   demo:
     greeting: "你好，Nacos"
   ```

5. 回到列表，确认配置位于正确命名空间，Data ID 和 Group 与填写值一致。

### 3.3 在应用中显式导入

当前 Spring Cloud Alibaba 使用 Spring Boot 的 **ConfigData（配置数据加载机制）**，通过 `spring.config.import` 明确列出要读取的配置。可在学习服务的 `src/main/resources/application.yml` 使用下面的连接部分：[官方接入说明](https://sca.aliyun.com/docs/2025.x/user-guide/nacos/advanced-guide/)

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
        namespace: dev
        group: demo
      config:
        namespace: dev
        group: demo
  config:
    import:
      - "nacos:demo-service-dev.yaml"
```

启动前在 IDE 的运行环境或受限部署配置中提供 `NACOS_USERNAME`、`NACOS_PASSWORD`，其值来自已有 Nacos 账号；不要把真实值写到 YAML 示例里。ECS 运行时将 `NACOS_SERVER_ADDR` 设为 `127.0.0.1:8848`。如果某个环境尚未启用鉴权，应先核实实际策略，不能靠关闭鉴权来解决连接失败。

启动后检查两件不同的事情：

1. 在控制台“服务管理 → 服务列表”选择 `dev`，检查 `demo` 分组下是否出现 `demo-service`，实例 IP 和端口是否正确。
2. 在 IDE 调试器查看 Spring `Environment` 的 `getProperty("demo.greeting")`，应得到 `你好，Nacos`。不要用打印全部环境变量或开放公开 `/actuator/env` 的方式排查配置。

不带 `optional:` 的导入表示应用需要这份配置，读取失败时不能假装启动正常。只有确实可以缺少的配置才使用 `optional:nacos:...`。

### 3.4 多份配置、公共配置和优先级

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

### 3.5 hhjava 项目对应关系

项目通常使用 Namespace ID `dev`、Group `hhjava`，各服务显式导入自己的 `应用名-环境.yaml`；不要只改应用名称却保留另一个服务的 Data ID。

本机秘密目录为 `java_demo/.hhjava-dev-config/`，每个服务读取自己的文件。该目录虽然位于 Git 工作树中，但已被忽略。项目 user、gateway、backup-file 还具有按 profile 阶段加载的本机覆盖配置，fund 的导入方式不同，不能把某个服务的整个文件复制给另一个服务。

这些是仓库代码约定，不代表 ECS 的最终配置。ECS 可以使用专属配置覆盖发现行为和固定路由。各服务完整配置不在本文重复，详细流程分别维护在 hhjava 项目的 `docs/CODEBASE_BUSINESS_LOGIC.md`（第 3 节“启动与配置逻辑”）和 `docs/ECS_DEPLOYMENT_RECORD.md`。它们属于另一个本地仓库，不随本知识站发布；在 Mac 上可打开项目文档目录：

```bash
open "/Users/michael/Documents/java_demo/hhjava/docs"
```

## 4. ECS Docker 升级实战：2.0.3 → 2.5.5

本节记录这台 ECS 的实际升级流程。**已从 2.0.3 升级到 2.5.5：就绪、配置基线、隔离读写及重启验证通过；公网接口和容器重建记录已复核。** 冷备和旧容器仍保留用于回退，最新验收及未验证边界见第 4.7 节。

下面的命令在 **ECS 的 root 终端**执行，除特别说明外工作目录为：

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
```

这是本次专用的受控目录，权限为 `700`。其中的脚本和 Java 工具已经放在服务器上，不是 Docker 自带命令，也不是适用于任意版本的通用升级器。未来复用前，应受限备份本轮工具、环境文件及恢复材料，审查源码并重新核对目标版本，再创建新目录；不要覆盖本轮材料，或直接修改工具中的固定路径保护后盲目执行。

### 4.1 确认当前版本、数据和影响范围

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
curl -fsS --max-time 5 "http://127.0.0.1:8848/nacos/v1/console/server/state"
docker inspect --format '{{range .Mounts}}{{println .Type .Source "->" .Destination}}{{end}}' nacos-server
free -m
df -h /
docker stats --no-stream
```

本次确认的升级前条件：

- Nacos `2.0.3`，单机模式，容器名 `nacos-server`，不是 Compose 管理。
- 使用内置 Derby；原数据挂载为 `/opt/hhjava-nacos/data → /home/nacos/data`。服务器有 MySQL 容器，不代表 Nacos 使用 MySQL。
- `public` 有 1 份测试配置，`dev` 有 3 份 `hhjava` 配置，共 2 个命名空间、4 份配置。
- ECS 的 user、gateway、backup-file 关闭服务发现和动态配置刷新，fund 关闭配置读取与发现。因此服务注册列表为空是现行部署预期，本轮不要求四服务重新注册。
- 主机约 3.5 GiB 内存、无 swap，开始检查时可用约 253 MiB。旧 Nacos 默认堆为 1 GiB，必须串行操作，不能同时运行新旧 Nacos。

版本选择同属 2.x 的正式版 `2.5.5`，不直接跨到 3.x；升级前对照[正式发布记录](https://github.com/alibaba/nacos/releases/tag/2.5.5)和[对应升级手册](https://nacos.io/docs/v2.5/manual/admin/upgrading/)。本轮不清库、不升级 MySQL/MinIO、不发布 Java 服务、不发送真实短信。

### 4.2 取得并核对固定版本镜像

Docker Hub 直连超时后，本次通过 DaoCloud 维护的公开代理取得 `linux/amd64` 镜像，固定引用如下：

```bash
docker pull --platform linux/amd64 \
  m.daocloud.io/docker.io/nacos/nacos-server@sha256:b481c7aaec43c07536b304bb16039d2cd6de8ee45348ce4095be391bc1ccdf4f
docker image inspect --format 'ID={{.Id}} 平台={{.Os}}/{{.Architecture}}' \
  m.daocloud.io/docker.io/nacos/nacos-server@sha256:b481c7aaec43c07536b304bb16039d2cd6de8ee45348ce4095be391bc1ccdf4f
```

摘要是镜像内容的标识，固定它可以避免同名标签被更新后拉到不同内容。本次还核对了：

- 官方 ZIP 的 SHA-256：`149438cd47e2d106a9dd4cd6403d84fba33e734bc915bd5619b15d43986ae84d`。
- 镜像内 Nacos 主程序与官方发行包一致，JAR 的 SHA-256：`ae113daf4f695c442abcb6225dccaae328e71a25133003e9517b185058e2d752`。
- 启动脚本和默认配置与官方 tag 一致。

**没有独立比对整个镜像的上游 manifest（镜像内容清单）**，不能把主程序一致扩大为整张镜像逐层验证通过。正式环境可进一步使用组织控制的镜像仓库和签名验证流程。

本轮曾因校验程序把整个 JAR 读入内存，触发主机 OOM（Out Of Memory，内存不足），旧 Nacos 被系统终止后恢复；已向用户说明。这不是无停机升级。之后使用流式校验、限制编译及迁移工具的堆，并给新版容器设置资源边界，不再整包读入内存。

### 4.3 停旧实例，保存一致性冷备和候选副本

Derby 数据正在使用时，直接复制数据库文件可能得到不一致的备份。先保存容器参数和配置基线，再停止旧 Nacos，备份整个数据目录。

先在旧实例仍运行时保存参数和基线。下面的命令拒绝覆盖已有文件；本轮这些文件已存在，**不要重跑或删除它们来绕过检查**。`verify-nacos.py` 必须先放入本次受控目录：

```bash
(
  set -euo pipefail
  set -C
  umask 077
  cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
  docker inspect nacos-server > old-container.inspect.json
  python3 - <<'PY'
import json, os, runpy
manifest = runpy.run_path('verify-nacos.py')['manifest']('nacos-server')
fd = os.open('before-manifest.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w', encoding='utf-8') as file:
    json.dump(manifest, file, ensure_ascii=True)
PY
  test ! -e old-conf
  docker cp nacos-server:/home/nacos/conf old-conf
)
```

`set -C` 防止 Shell 重定向覆盖已有文件，`O_EXCL` 防止 Python 覆盖已有基线；配置正文和秘密不回显到终端。

以下展示本次冷备的执行顺序；现有备份已经完成，**不要重复运行覆盖它**。子 Shell 的退出处理仅在普通失败时尝试恢复旧容器；恢复也可能失败，必须查看最终就绪状态，不能代替主机断电或强制终止时的人工恢复：

```bash
(
  set -euo pipefail
  umask 077
  cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
  test ! -e data-before.tar
  test ! -e candidate-data
  trap 'docker update --restart=always nacos-server >/dev/null && docker start nacos-server >/dev/null' EXIT
  docker update --restart=no nacos-server
  docker stop --timeout 60 nacos-server
  tar -C /opt/hhjava-nacos -cpf data-before.tar data
  sha256sum data-before.tar > data-before.tar.sha256
  sha256sum -c data-before.tar.sha256
  mkdir candidate-data
  tar -xpf data-before.tar -C candidate-data --strip-components=1
)
```

检查应显示校验通过，原目录仍存在，旧容器恢复后 readiness 为 `OK`。备份摘要只能证明归档文件没有改变，真正的可用性还需要后面的副本启动和回退验证。

本轮目录内材料及用途：

| 材料 | 用途 |
| --- | --- |
| `data-before.tar` 及校验文件 | 升级前完整数据冷备，包含 Derby 和 protocol |
| `candidate-data/` | 迁移、演练及正式切换使用的新数据；原 `data/` 仅用于回退 |
| `old-conf/` | 旧配置副本；不要整个覆盖到新版镜像 |
| `old-container.inspect.json`、`before-manifest.json` | 原容器参数和命名空间/配置基线 |
| `nacos.env` | 新容器专用环境文件，包含必要秘密，禁止打印 |
| `DerbyUpgrade.java`、`DerbyGrayCheck.java`、`derby-10.14.2.0.jar` | 迁移和数据库结构检查工具 |
| `verify-nacos.py`、`trial-nacos.sh`、`promote-nacos.sh` | 数据核对、隔离演练、正式切换及失败回退 |
| `record-container.py` | 验证正式运行参数后，原子更新受限的容器重建记录 |

含秘密的参数、环境和基线文件为 `600`；整个目录仅 root 可访问。不要将它们提交到 Git 或当作普通附件分享。

本次 `nacos.env` 的受限生成方式如下。**原实例的鉴权未启用，本轮沿用这一现状，不是升级时新关闭鉴权，也不是建议其他环境关闭鉴权。** 只有核实为本次条件时才能使用下面的值；已启用鉴权的环境必须保留原策略并验证客户端身份。当前只开放回环端口和 SSH 隧道，后续正式扩大访问范围前还需专项完善鉴权。

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
python3 - <<'PY'
import base64, os, secrets
values = {
    'MODE': 'standalone',
    'NACOS_AUTH_ENABLE': 'false',
    'NACOS_AUTH_TOKEN': base64.b64encode(secrets.token_bytes(48)).decode('ascii'),
    'NACOS_AUTH_IDENTITY_KEY': 'hhjava-nacos-node',
    'NACOS_AUTH_IDENTITY_VALUE': secrets.token_hex(32),
    'JVM_XMS': '256m', 'JVM_XMX': '512m', 'JVM_XMN': '128m',
}
fd = os.open('nacos.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w', encoding='ascii') as file:
    for key, value in values.items():
        file.write(key + '=' + value + '\n')
PY
```

Token 使用 48 字节安全随机数后做 Base64 编码，节点身份值使用 32 字节安全随机数生成 64 个十六进制字符；代码不会打印它们。文件已存在就失败退出，不能为重跑命令而删除文件或重新生成秘密。

### 4.4 只迁移候选副本，不改原数据

DDL（Data Definition Language，数据定义语言）用于调整表结构。本次工具只补下面 6 列；`NACOS` 是 Derby 的数据库 schema（表所属名称空间），不是控制台的 `dev` 命名空间：

```sql
ALTER TABLE NACOS.CONFIG_INFO ADD COLUMN ENCRYPTED_DATA_KEY LONG VARCHAR DEFAULT NULL;
ALTER TABLE NACOS.CONFIG_INFO_BETA ADD COLUMN ENCRYPTED_DATA_KEY LONG VARCHAR DEFAULT NULL;
ALTER TABLE NACOS.HIS_CONFIG_INFO ADD COLUMN ENCRYPTED_DATA_KEY LONG VARCHAR DEFAULT NULL;
ALTER TABLE NACOS.HIS_CONFIG_INFO ADD COLUMN PUBLISH_TYPE VARCHAR(50) DEFAULT 'formal';
ALTER TABLE NACOS.HIS_CONFIG_INFO ADD COLUMN GRAY_NAME VARCHAR(128) DEFAULT NULL;
ALTER TABLE NACOS.HIS_CONFIG_INFO ADD COLUMN EXT_INFO CLOB DEFAULT NULL;
```

这些 SQL 用于理解工具行为，**不要另行对原库手工执行**。工具使用 `nacos` 用户，拒绝原目录、软硬链接和自动建库；已有列的类型、长度、可空性或默认值不符就失败回滚。迁移前后对 `NACOS` 内所有原用户表的旧列计算行数和流式摘要，不输出业务内容或密码摘要。

结构依据为[旧版 schema](https://github.com/alibaba/nacos/blob/2.0.3/distribution/conf/schema.sql)、[新版 schema](https://github.com/alibaba/nacos/blob/2.5.5/distribution/conf/derby-schema.sql)及[灰度兼容迁移实现](https://github.com/alibaba/nacos/blob/2.5.5/config/src/main/java/com/alibaba/nacos/config/server/service/ConfigGrayModelMigrateService.java)。

先确认没有容器打开候选副本，再执行：

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
/opt/hhjava/jdks/current/bin/javac -J-Xmx64m -encoding UTF-8 --release 17 DerbyUpgrade.java
/opt/hhjava/jdks/current/bin/java -Dfile.encoding=UTF-8 -Xms16m -Xmx64m \
  -cp '.:derby-10.14.2.0.jar' DerbyUpgrade \
  /opt/hhjava-nacos/upgrade-20261110.2jyDTn/candidate-data/derby-data
```

`-encoding UTF-8` 防止服务器默认编码无法读取中文注释；`-J-Xmx64m` 限制编译器堆，运行命令中的 `-Xmx64m` 限制迁移工具堆，均不等于整个进程最多占 64 MiB。

本次已在 ECS 副本实际新增 6 列；15 张原用户表的旧列摘要一致，配置 4 条、历史 19 条，用户/角色/权限各 2 条，旧 beta/tag/aggr 均为 0。原数据目录没有迁移。此前本机真实 Derby 10.14.2.0 下的 7 组合成数据回归及独立复核通过，不能用它代替这里的真实副本验收。

### 4.5 隔离演练：启动、配置读写、重启和恢复旧版

运行本次专用脚本：

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
bash -n trial-nacos.sh
bash trial-nacos.sh
```

脚本先严格核对旧容器身份和配置基线，停止旧实例，再启动 `nacos-upgrade-check-20261110`：

- 使用 `--network none`，不开放端口，只挂载候选副本。
- 为无网络试验设置 `NACOS_SERVER_IP=127.0.0.1`；这只用于隔离试验，不复制到正式 bridge 网络。
- 检查版本、就绪、命名空间和配置摘要；仅在这个无网络副本上新增随机探针配置，执行新增、修改、读取、删除，确保探针不存在且原配置未变化。配置发布存在异步写出阶段，探针最多读取 20 次、重试间隔 250 毫秒，每次 HTTP 请求另有超时；这不是严格 5 秒总截止时间。
- 重启副本，再次核对持久化结果。
- 无论成功或失败，退出处理都会尝试恢复旧版，但只有确认新版容器停止后才启动旧版，并检查就绪和原基线；不能确认新版已停止就中止，转人工处理，不能保证所有失败都自动恢复。

成功标准是出现 `isolated_trial_and_restart=passed`、`old_ready_and_baseline_restored=true` 且最终退出码为 0。本次最终一轮实际通过：配置增改读删完成，其中一次读取经过 13 次重试匹配精确值；重启后 2 个命名空间、4 份配置基线一致，旧版恢复检查通过。没有成功退出不能进入正式切换。

新版命名空间接口增加了官方 `namespaceDesc` 字段。比较时只兼容“旧响应没有这个新增字段”，原有字段仍逐项严格相同；不通过忽略配置数量、命名空间 ID 等差异来凑出成功。探针保护、该兼容逻辑和有界重试的 11 项本机测试通过。依据：[命名空间返回实现](https://github.com/alibaba/nacos/blob/2.5.5/core/src/main/java/com/alibaba/nacos/core/service/NamespaceOperationService.java)、[配置发布实现](https://github.com/alibaba/nacos/blob/2.5.5/config/src/main/java/com/alibaba/nacos/config/server/service/ConfigOperationService.java)、[异步缓存更新](https://github.com/alibaba/nacos/blob/2.5.5/config/src/main/java/com/alibaba/nacos/config/server/service/dump/DumpService.java)。

试验结束、候选副本已停止后，检查新版创建的灰度表：

```bash
/opt/hhjava/jdks/current/bin/javac -J-Xmx64m -encoding UTF-8 --release 17 DerbyGrayCheck.java
/opt/hhjava/jdks/current/bin/java -Xms16m -Xmx64m \
  -cp '.:derby-10.14.2.0.jar' DerbyGrayCheck \
  /opt/hhjava-nacos/upgrade-20261110.2jyDTn/candidate-data/derby-data
```

本次已核实 `config_info_gray` 的 14 列、主键、复合唯一约束和两个索引符合目标结构，beta/tag/gray 行数均为 0。此工具只读检查，不能在新版正在打开数据库时执行。

### 4.6 正式切换

**只有上一节全部成功，且旧实例未出现新的配置或账号权限修改时才执行。** 有新写入就先重新同步和验证，不能直接使用过期候选副本。

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
bash -n promote-nacos.sh
bash promote-nacos.sh
```

脚本停止旧容器，将它改名为 `nacos-server-rollback-2.0.3-20261110` 并保持 `restart=no`；新容器使用名称 `nacos-server`。正式创建参数为：

| 参数 | 本次值及含义 |
| --- | --- |
| 镜像 | 第 4.2 节固定摘要的 2.5.5 |
| 网络 | bridge；8848/9848/9849 只绑定宿主机 `127.0.0.1` |
| 数据 | `/opt/hhjava-nacos/upgrade-20261110.2jyDTn/candidate-data → /home/nacos/data` |
| 环境文件 | 同目录 `nacos.env`，不在命令行放秘密 |
| JVM 堆 | Xms 256m、Xmx 512m、Xmn 128m |
| 容器资源 | `--memory 1g --memory-swap 1g --cpus 1`；memory 与 memory-swap 相同表示不额外使用 swap |
| 重启策略 | 新版 `always`，旧版 `no` |

`candidate-data` 切换成功后就是正式运行数据目录，**不能因名称带有 candidate 或位于 upgrade 目录而删除它，也不要擅自换回原 data 挂载**。

脚本失败时会尝试停止新实例，只有确认停止后才恢复旧容器和原数据，并核对基线；无法确认新实例已停止时中止，交由人工处理，不承诺所有故障都能自动回退。它不会把已迁移副本交给旧版。本次正式切换已出现 `production_promotion_checks=passed` 且退出码为 0。

仅在正式切换通过后，单独更新容器重建记录；这一步不包含在 `promote-nacos.sh` 中：

```bash
python3 record-container.py
```

预期输出 `current_container_create_record=updated mode=600 boundaries_verified=true`。工具先检查实际镜像、端口、资源和挂载，再原子更新 `/opt/hhjava-nacos/container-create.json`，权限 `600`；升级前副本保存在 `upgrade-20261110.2jyDTn/old-container-create.json`。不要继续使用旧参数创建容器。

### 4.7 切换后验证

在 ECS 执行：

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
python3 verify-nacos.py nacos-server before-manifest.json
docker inspect --format '运行={{.State.Running}} OOM={{.State.OOMKilled}} 重启次数={{.RestartCount}}' nacos-server
docker stats --no-stream
free -m
systemctl show hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund \
  -p Id -p ActiveState -p MainPID -p NRestarts
curl -sS --max-time 8 --resolve 47.120.56.43:443:127.0.0.1 \
  -o /dev/null -w 'JWKS HTTP=%{http_code}\n' https://47.120.56.43/user/oauth2/jwks
```

应看到目标版本 `2.5.5`、readiness 为 `OK`、2 个命名空间、4 份配置、`baseline_match=true`。HTTP 401/404、端口能连接或容器显示 Up 不能单独证明 Nacos 就绪。

随后从 **Mac 或其他公网客户端**请求相同 HTTPS/JWKS 地址，不加 `--resolve`，正常校验证书，不使用 `-k`。ECS 回环成功不能代替公网验证；匿名业务接口的 401 也不能代替真实登录与业务读写验证。

检查服务 PID/重启数、新增 OOM、CPU 与可用内存，并确认没有同时运行新旧 Nacos。服务发现关闭时，注册列表为空是预期行为；本轮没有重启 Java 服务，因此没有验证它们的 Nacos 配置冷启动读取。完整 App 登录、真实短信和长期压力验收也未执行。

以下是一组实际验收快照，记录于 **2026-11-10 13:03:53 CST**，不是实时监控：

| 范围 | 实际结果 |
| --- | --- |
| Nacos 与数据 | 2.5.5、readiness 为 OK；2 个命名空间、4 份原配置基线一致，隔离增改读删及重启验证通过 |
| 容器安全边界 | 新版运行、`OOMKilled=false`、重启次数 0、策略 always；旧版停止、策略 no；三个映射端口均仅绑定 `127.0.0.1` |
| 重建记录 | `record-container.py` 成功核对边界，已原子更新 `container-create.json`，权限 600 |
| 四个 Java 服务 | user、gateway、backup-file、fund 均 active，PID 未变，`NRestarts=0` |
| Mac 公网请求 | 正常校验 TLS：JWKS HTTP 200，约 1.489 秒；匿名基金 HTTP 401，约 1.560 秒 |
| 资源短时快照 | Nacos 约 546.5 MiB / 1 GiB、CPU 1.15%；主机可用约 704 MiB、无 swap；12:00 后未查到新增内核 OOM 记录 |

资源数值只代表这次短时观察，不是长期容量保证；匿名 401 不代表认证业务通过，镜像整体上游 manifest 未独立核对的限制仍保留。

### 4.8 回退条件与操作

正式切换脚本内已有失败回退。下面是切换完成后需要人工回退时的顺序，**只适用于切换后没有新的 Nacos 配置、用户或权限写入**；否则原 data 已过期，应先保护新增数据并制定恢复方案。

在 ECS 核实旧容器和参数备份存在、新版名称与身份正确，并确认不会覆盖已有失败容器后执行。新版仍可读时，先运行前面的只读基线检查；新版无法访问时，必须从操作记录确认切换后没有新写入，不能把无法查询当作没有变更。出现任一步失败就停止，不盲目继续：

```bash
(
  set -euo pipefail
  cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
  test -f old-container-create.json
  test "$(docker inspect --format '{{.Config.Image}}' nacos-server)" = 'm.daocloud.io/docker.io/nacos/nacos-server@sha256:b481c7aaec43c07536b304bb16039d2cd6de8ee45348ce4095be391bc1ccdf4f'
  test "$(docker inspect --format '{{.State.Running}}' nacos-server-rollback-2.0.3-20261110)" = false
  if docker inspect nacos-server-failed-2.5.5-20261110 >/dev/null 2>&1; then exit 1; fi
  docker update --restart=no nacos-server
  docker stop --timeout 45 nacos-server
  test "$(docker inspect --format '{{.State.Running}}' nacos-server)" = false
  docker rename nacos-server nacos-server-failed-2.5.5-20261110
  docker rename nacos-server-rollback-2.0.3-20261110 nacos-server
  docker update --restart=always nacos-server
  docker start nacos-server
  cp -p old-container-create.json /opt/hhjava-nacos/container-create.json
)
```

等待旧版 readiness 为 `OK` 后，执行下面的旧版核对。不要直接调用 `verify-nacos.py` 的主入口，它强制要求 2.5.5；回退检查应复用其只读函数，并明确要求 2.0.3：

```bash
cd /opt/hhjava-nacos/upgrade-20261110.2jyDTn
python3 - <<'PY'
import json, runpy
m = runpy.run_path('verify-nacos.py')
state = m['get_json']('nacos-server', '/v1/console/server/state')
assert state.get('version') == '2.0.3', 'OLD_VERSION_MISMATCH'
status, body = m['request']('nacos-server', '/v1/console/health/readiness')
assert status == 200 and body.strip() == 'OK', 'OLD_NOT_READY'
with open('before-manifest.json', encoding='utf-8') as file:
    before = json.load(file)
assert m['manifest']('nacos-server') == before, 'OLD_BASELINE_MISMATCH'
print('old_version=2.0.3 readiness=OK baseline_match=true')
PY
```

之后复查 Java 服务和公网接口。新的候选数据和失败容器暂时保留用于排查，不要为“恢复干净”而删掉。

回退始终用“旧容器 + 未迁移的原 data”；原目录损坏时，先验证冷备校验值，再向新的受控恢复目录解包并检查，不能覆盖正在使用的数据。不要使用 `docker compose down -v`、`docker rm -v` 或清库作为升级、回退步骤。

## 5. 配置备份与跨服务器迁移

### 5.1 分清三类备份

| 备份 | 包含什么 | 不能替代什么 |
| --- | --- | --- |
| 配置导出 ZIP | 当前配置内容及相应 Data ID、Group 等信息 | 完整数据库、所有历史和权限 |
| Nacos 实例数据 | 数据库或内置数据目录、必要运行配置 | 不保证可直接恢复到任意新版本 |
| 应用侧秘密 | Nacos 凭据、数据库凭据、应用签名密钥等 | 不应混入公开配置包或 Git |

临时服务实例一般由服务重连后重新注册；持久实例和非默认服务元数据如果实际使用了，需要单独盘点，不能当成配置 ZIP 已经包含。

备份文件也可能包含秘密。使用仅管理员可访问的目录，限制权限并保留校验值；备份目录不是普通教程素材，也不应上传到公共仓库。

### 5.2 导出配置

在控制台逐个选择需要迁移的命名空间，进入配置列表，导出需要保留的全部配置。在受限清单中记录：

1. 源 Nacos 版本、Namespace ID 与显示名称。
2. 每份配置的 Group、Data ID、格式和内容摘要。
3. 配置数量，以及外部秘密和部署参数的保存位置。

若界面只选中了当前页，不代表导出了全部页；导出后必须核对数量和清单。不要为方便核对而把配置正文、密码或 Token 打印到日志。

### 5.3 恢复到另一台服务器

1. 准备目标 Nacos、受限网络访问和可恢复的数据备份；完整实例恢复先按相同版本演练。
2. 创建相同的 Namespace ID，不能只创建同名的显示名称。
3. 将配置 ZIP 导入空的目标命名空间。遇到同名冲突先核对，不直接覆盖已有配置。
4. 核对 Group、Data ID、类型、数量和内容摘要，重新建立未随 ZIP 恢复的用户与权限。
5. 在受限位置恢复应用凭据及签名密钥；hhjava 本机目录是 `java_demo/.hhjava-dev-config/`，服务器按其实际服务专属目录恢复，不混用两套路径。
6. 先用受控测试客户端确认读取和注册，再切换正式应用的 Nacos 地址；切换后再次验证服务注册、网关和业务接口。
7. 验证通过并确认无需回退后，再按备份保留策略清理旧资源。恢复失败时使用成套的镜像、数据和配置回退，而不是清库重试。

使用稳定私网域名可以减少服务器地址变化的影响，但客户端刷新 DNS 和连接重建仍需验证；不能承诺修改 DNS 后所有连接立即自动切换。

## 6. 常见问题

| 现象 | 先检查什么 |
| --- | --- |
| 浏览器能打开，Java 连不上 | 是否同时转发客户端 gRPC 端口；应用地址是否误用了另一台机器的 `127.0.0.1` |
| 找不到配置 | Namespace ID、Group、Data ID、格式是否一致；是否确实发布且具有读取权限 |
| 服务没有出现在列表 | 是否引入发现依赖、是否启用注册、是否查看了正确命名空间/分组；ECS 是否故意使用固定路由 |
| 修改配置没有立即生效 | 属性是否支持刷新、是否被其他配置来源覆盖；不要把“收到变更”当成“所有组件已重建” |
| 容器一直重启 | 先查失败原因、鉴权参数、数据目录权限、版本兼容和 OOM；不要反复重启或清库 |
| 升级后版本没变化 | 是否只拉了镜像或重启旧容器，没有按新镜像重建 |
| 无法回滚 | 是否误让旧版本读取已迁移的数据；是否有升级前一致性快照和原镜像 |

查看日志时只提取错误类型和必要上下文，分享前脱敏，不复制完整配置、凭据或个人数据。
