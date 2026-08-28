# Nacos

Nacos 是一个开源的动态服务发现、配置管理和服务管理平台，由阿里巴巴开源。Nacos 是 "Dynamic Naming and Configuration Service" 的缩写，它为微服务架构提供了关键的基础设施支持。

Nacos 的主要功能：

- **服务发现中心（注册中心）**
  - Nacos 可以帮助服务在注册中心进行注册和发现。服务实例可以通过 Nacos 注册自己，并且其他服务（网关）可以通过 Nacos 查找这些服务实例。

- **动态配置管理**

  - Nacos 提供集中化的配置管理功能，允许开发者在一个地方（Nacos）管理所有的配置项。配置的变更可以实时推送到应用程序中。

  - 支持配置的版本管理和灰度发布，方便进行配置的管理和控制。

- **动态 DNS 服务**
  - Nacos 提供 DNS 服务，可以将服务发现和 DNS 解析结合起来，方便服务的调用。

- **服务健康监测**
  - Nacos 提供了服务健康检查机制，确保服务实例的可用性。
- **服务管理**
  - 提供服务的元数据管理、流量管理、熔断降级等功能，帮助提升系统的稳定性和可靠性。

Nacos 支持多种服务发现协议（如 HTTP、gRPC、Dubbo 等）和多种配置格式（如 YAML、Properties、JSON 等），并且可以与 Spring Cloud、Kubernetes 等生态系统集成。

**Nacos 的典型应用场景包括微服务架构中的服务注册与发现、配置管理，以及分布式系统中的服务治理。**

Nacos通常安装在Linux服务器上。

## Nacos安装

> 生产环境不要直接使用 `latest`，也不要把管理端口无条件开放到公网。应固定经过测试的版本、先完成升级兼容验证，并通过内网、安全组、防火墙或 VPN 只允许可信来源访问。

1、docker拉取镜像 

```shell
docker pull nacos/nacos-server:<经过验证的固定版本>
```

2、创建容器

针对nacos镜像创建容器

```shell
docker run --env MODE=standalone -d --name nacos-server --restart=always \
  -p 8848:8848 -p 9848:9848 -p 9849:9849 \
  nacos/nacos-server:<经过验证的固定版本>
```

- docker run 启动容器
- MODE=standalone 单机版
- --restart=always 开机启动

`8848` 是主 HTTP 端口，Nacos 2.x 客户端还会使用相对主端口偏移的 gRPC 端口，例如默认 `9848`。安全组只应对应用所在内网或明确的可信来源放行这些必要端口，不能直接对整个互联网开放。

3、访问nacos地址：http://服务器ip:8848/nacos 
## 当前 Spring Cloud Config Import 配置

2021.0.5版本的 Spring Cloud 默认不再启用 bootstrap 包，因此应该将配置文件写在 application.yml 中。

```yaml
#微服务配置
spring:
  cloud:
    nacos:
      config:
        namespace: dev
        group: hhjava
        file-extension: yaml
  config:
    import: "nacos:hhjava-user-dev.yaml?group=hhjava"
```

在当前 Spring Cloud Alibaba 版本中，import URI 的查询参数使用 `group`；namespace 从 `spring.cloud.nacos.config.namespace` 读取，文件后缀已经包含在 data-id 中。不要把 `config.namespace`、`config.group`、`config.file-extension` 写进 URI，它们不是当前 resolver 识别的参数。

## 生产安全与 hhjava 实践

### 当前配置装配差异（2026-08-28）

三个运行服务都按 `${spring.application.name}-${spring.profiles.active}.yaml` 计算 data-id，且 Nacos import 都没有声明 `optional:`。这表示配置没有主动设计本地降级路径，但不能简单推导成“data-id 不存在就中止启动”：当前版本对空/不存在的 data-id 记录警告后继续。三个服务的本地秘密配置加载方式如下：

| 服务 | 本地外部 properties | Nacos data-id 只读复核 | 当前影响 |
| --- | --- | --- | --- |
| `hhjava-gateway` | 先可选加载 `HHJAVA_DEV_CONFIG_LOCATION`，再导入 Nacos | `hhjava-gateway-dev.yaml` 存在 | 路由等运行配置依赖 Nacos；连接/读取故障没有显式降级方案 |
| `hhjava-user` | 先可选加载 `HHJAVA_DEV_CONFIG_LOCATION`，再导入 Nacos | `hhjava-user-dev.yaml` 存在 | 数据源等运行配置仍依赖 Nacos |
| `hhjava-backup-file` | 没有上述本地文件导入 | `hhjava-backup-file-dev.yaml` 缺失 | 空配置警告后继续；随后因缺少 `minio.endpoint` 和 `MinioClient` Bean 启动失败 |

`scripts/setup-dev-config.sh` 会从本机受控目录读取 Nacos、MySQL、OAuth 和 RSA 材料，原子生成权限为 `600` 的 `application.properties`。该脚本不生成 MinIO 参数，也不会被文件服务自动加载，因此不能把“脚本执行成功”理解为三个服务都具备启动条件。

Gateway 当前远端路由为 `/user/** -> lb://hhjava-user` 与 `/backup/** -> lb://hhjava-backup-file`，没有 `StripPrefix`、重试、熔断或 fallback。文件服务无配置/无实例时，`/backup/**` 只会进入 Gateway 默认失败路径。

### 1、应用账号与管理员账号分离

业务应用不应使用 Nacos 管理员账号。推荐为每套环境创建独立运行账号，并把权限限制在该环境、项目的配置和服务发现资源。

`hhjava` 开发环境采用的权限边界是：

- 配置读取只覆盖 `dev:hhjava:*`。
- 服务发现只覆盖 `dev:hhjava:naming/*`。
- 应用运行账号与管理员账号分离。
- 管理员密码轮换后验证旧密码失效。

最小权限不能代替服务端升级。旧版本如果存在认证绕过或管理接口授权缺陷，即使应用 ACL 配置正确，也不能视为基础设施风险已经关闭。

### 2、不要把秘密保存在源码或 Nacos 普通配置中

本地配置只引用部署环境变量：

```yaml
spring:
  cloud:
    nacos:
      server-addr: ${NACOS_SERVER_ADDR}
      username: ${NACOS_USERNAME}
      password: ${NACOS_PASSWORD}
```

数据库密码在 Nacos 中也只保存变量占位符：

```yaml
spring:
  datasource:
    password: ${HHJAVA_DATASOURCE_PASSWORD}
```

真实密码由容器、systemd、IDE 私有运行配置或秘密管理系统注入。`.env` 必须加入 `.gitignore`，仓库只能提交没有真实值的 `.env.example`。

### 3、按应用名和 Profile 动态生成 data-id

```yaml
spring:
  application:
    name: hhjava-user
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  cloud:
    nacos:
      config:
        namespace: ${NACOS_NAMESPACE:dev}
        group: ${NACOS_GROUP:hhjava}
        file-extension: yaml
  config:
    import:
      - "optional:file:${HHJAVA_DEV_CONFIG_LOCATION:${user.home}/.config/hhjava/dev/application.properties}"
      - "nacos:${spring.application.name}-${spring.profiles.active}.yaml?group=${NACOS_GROUP:hhjava}"
```

这样会读取 `hhjava-user-dev.yaml`，切换 profile 时远端配置文件名会同步变化。

当前 user、gateway 和 backup-file 源码的 import URI 仍使用 `config.namespace`、`config.group`、`config.file-extension`。现环境之所以能工作，是因为 namespace/group 同时配置在 `spring.cloud.nacos.config` 下，data-id 自身也带 `.yaml` 后缀；后续应把源码 URI 收敛为上面的受支持写法，避免误以为这些查询参数生效。

### 4、轮换与验收

轮换凭据不能只修改新值，还要验证旧值确实失效：

1. 生成新随机密码并写入受控秘密存储。
2. 更新 Nacos 或数据库账号。
3. 使用新值启动应用，确认配置读取、服务注册和数据库连接成功。
4. 使用旧值发起只读登录，必须明确失败。
5. 检查源码、构建产物、日志和 Git 历史中是否仍有旧值。

### 5、版本与网络收口

`hhjava` 本次验证时服务端仍为 Nacos 2.0.3，且公网 `8848` 尚未完成访问范围收敛，因此只能标记为“凭据已轮换，基础设施待收口”。后续需要：

- 备份配置和服务数据后升级到经过兼容验证的维护版本。
- 收敛 `8848` 到内网或可信来源。
- 同时检查 9848 等客户端必需 gRPC 端口，避免只开放 HTTP 后服务注册不稳定。
- 升级后重新验证登录、最小权限、配置读取、监听推送和服务注册。

参考：

- [Nacos 身份认证文档](https://nacos.io/en/docs/v2.3/guide/user/auth/)
- [Nacos 认证绕过问题记录](https://github.com/alibaba/nacos/issues/10060)
- [Nacos 2.5 升级指南](https://nacos.io/en/docs/v2.5/manual/admin/upgrading/)
- [hhjava 认证授权与配置安全整改实战](./认证授权和网关/hhjava认证授权与配置安全整改实战.md)
