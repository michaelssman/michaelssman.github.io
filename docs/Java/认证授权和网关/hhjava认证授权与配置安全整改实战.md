# hhjava 认证授权与配置安全整改实战

> 整改日期：2026-08-27
>
> 源码与配置复核：2026-08-28
>
> 适用项目：`hhjava`
>
> 技术基线：Java 17、Spring Boot 3.3.7、Spring Security 6.3.6、Spring Authorization Server 1.3.4、Spring Cloud Gateway、Nacos、MySQL

本文记录一次真实的微服务认证与配置安全整改。内容覆盖源码、Nacos、MySQL、OAuth2、RSA/JWKS、Gateway、文件服务、Reqable 调试和验证结果。

文中的账号、密码、客户端密钥、Token 和 RSA 私钥全部使用变量或占位符，不记录任何真实秘密。当前 `.env.example` 与开发脚本仍包含固定的开发环境 Nacos 地址；它不是认证秘密，但形成环境耦合，后续应改为显式注入。

本文只统计本次实际实施的改造；工作区中用户原有的 `.idea/dataSources.xml` 修改不属于本次内容，也未被覆盖。

## 一、整改目标与边界

本次优先处理代码评审问题 R001：JWT、Nacos 和 OAuth 客户端凭据曾进入版本库。采用的方案是：

1. 先把所有运行凭据从源码和远端普通配置中移出。
2. 轮换已经暴露或可能暴露的 Nacos、MySQL 和 OAuth 凭据。
3. 将共享 HMAC JWT 改成认证服务持有 RSA 私钥、资源服务通过 JWKS 公钥验签。
4. Gateway、用户服务、文件服务全部使用 Spring Security Resource Server。
5. 用单元测试和真实运行请求验证签发、验签、拒绝篡改 Token 等关键链路。

MinIO 尚未部署，因此此前只用临时占位配置验证过文件服务安全过滤链，没有执行真实上传、删除、Bucket 策略或返回地址验证。2026-08-28 复核还确认 Nacos 缺少 `hhjava-backup-file-dev.yaml`；实跑时空 data-id 只产生警告，随后因没有 `minio.endpoint`，`MinIOConfig` 不生效并缺少 `MinioClient` Bean，文件服务因此启动失败。

## 二、整改前后的架构变化

### 2.1 整改前

- JWT 使用仓库内固定 HMAC 密钥，拿到密钥的任意服务都能伪造 Token。
- 用户服务、Gateway、文件服务各自维护自定义 Filter 或 Interceptor，行为不一致。
- 文件服务在缺少 Token 时仍可能继续放行。
- Gateway 白名单覆盖整个 `/user/**`，新增接口容易被意外匿名开放。
- Nacos、OAuth 客户端等凭据存在源码默认值或硬编码。
- OAuth 客户端声明了没有完整 converter/provider 支持的 password grant。
- Spring Authorization Server 版本脱离 Spring Boot 依赖管理，存在兼容性风险。

### 2.2 整改后

```text
Reqable / App / Browser
          │ 注册、登录、Bearer Token
          ▼
Spring Cloud Gateway（Reactive Resource Server）
          ├──────────────────────┐
          ▼                      ▼
hhjava-user                 hhjava-backup-file
Authorization Server       Resource Server
+ Resource Server                 │
    │ 发布 JWKS                   │ 按 kid 获取公钥
    ├───────────────► RSA 公钥 ◄──┘
    │
    └───────────────► MySQL app

Gateway / user / backup-file ───► Nacos 配置与服务发现
本地外部 properties ────────────► Gateway / user
部署环境变量 ───────────────────► backup-file
```

认证服务是唯一 JWT 私钥持有者和签发方。Gateway 负责入口认证与路由，下游服务仍独立验签，避免绕过 Gateway 直连服务时失去安全边界。

## 三、仓库修改清单

### 3.1 用户认证服务 `hhjava-user`

新增 `com.hh.security.jwt`：

- `RsaKeyConfiguration`
  - 从外部资源读取 PKCS#8 私钥和 X.509 公钥。
  - 校验公私钥模数一致。
  - 强制 RSA 位数不低于 2048；开发环境实际生成 3072 位密钥。
  - 创建 `RSAKey`、`JWKSource`、`JwtEncoder` 和 `JwtDecoder`。
  - Decoder 限制为 RS256，并校验 issuer、audience 和标准时间声明。
- `JwtTokenService`
  - 项目自有 `/auth/login` 不再调用旧 `JwtUtil`。
  - 使用授权服务器共享的 `JwtEncoder` 签发 RS256 Token。
  - Header 写入 `kid`；Claims 写入 `iss`、`sub`、`aud`、`iat`、`nbf`、`exp`、`jti`。

新增类型安全配置：

- `JwtProperties`：绑定密钥路径、`kid`、issuer、audience、访问令牌 TTL，并校验 URI 和 TTL。
- `OAuthClientProperties`：绑定 client id、client secret、redirect URI，校验密钥最小长度和绝对回调 URI。

修改 `AuthorizationServer`：

- OAuth 客户端信息全部由外部配置注入。
- client secret 只在进程启动时读取，写入内存仓库前使用 BCrypt 哈希。
- 保留 authorization code、client credentials、refresh token。
- 删除当前工程没有正确实现的 password grant。
- OAuth access token 与项目自有登录 Token 共用 RSA、issuer、audience、`kid` 和 TTL。
- 授权服务器安全链使用 `@Order(1)`，启用 OIDC/JWKS。
- Token、introspection、revocation 等协议端点使用 OAuth2 自身客户端认证，不要求浏览器 CSRF Token。

修改 `WebSecurityConfig`：

- 普通应用安全链使用 `@Order(2)`。
- 只精确公开 `POST /auth/register`、`POST /auth/login`、登录页、错误页和 API 文档。
- 其他请求默认要求认证。
- Bearer Token 由标准 OAuth2 Resource Server 处理，不再注册手写 JWT Filter。
- 会话策略使用 `IF_REQUIRED`，为后续授权码浏览器流程保留会话能力。

`AuthController` 改用 `JwtTokenService` 签发登录 Token；`CustomUserDetailsService` 只有格式整理，没有借本次整改改变原有认证策略行为。

删除：

- `JWTAuthenticationFilter`
- 用户模块中的 JJWT 依赖

Spring Authorization Server 不再硬编码版本，由 Spring Boot 3.3.7 统一管理，实际解析为 1.3.4。

### 3.2 Gateway

修改 `SecurityConfig`：

- 使用 Reactive OAuth2 Resource Server 验证 Bearer JWT。
- JWKS 选择 `kid` 对应的公钥，限制 RS256，并验证 issuer、audience 和时间声明。
- 只按 HTTP 方法精确公开注册、登录。
- OAuth2/OIDC 协议端点和文档端点单独列入白名单。
- 其他请求全部使用 `authenticated()`。
- 未认证返回 401，无权限返回 403。

删除：

- `GatewayAuthFilter`：它只重复读取并写回已有 `Authorization` Header，没有完成真实认证。
- 过时的 `spring-cloud-starter-security:2.2.4.RELEASE`。

Gateway 默认会继续把标准 `Authorization: Bearer <token>` 转发给下游，不需要自定义 Filter 复制 Header。

### 3.3 文件服务 `hhjava-backup-file`

新增无状态 `SecurityFilterChain`：

- 仅公开 Swagger/OpenAPI。
- 其他请求全部要求认证。
- 通过认证服务的 JWKS 独立验证 JWT。
- 即使文件服务端口被直连，也不会因为绕过 Gateway 而匿名访问业务接口。

`SecurityUtil` 改为从标准 `SecurityContextHolder` 获取当前身份，不再依赖 request attribute。

删除旧 `WebMvcConfig` 和 `FileTokenInterceptor`。旧拦截器在缺少 Token 的分支中仍继续执行链路，不能作为安全边界。

### 3.4 公共模块与仓库配置

`hhjava-unify` 删除：

- `JwtUtil`
- `SecurityConstants`
- 全部 JJWT 依赖
- 仅为旧 JWT 代码引入的 Spring Security Core 依赖
- 测试目录中的临时密钥生成器

仓库根目录新增：

- `.env.example`：只列出变量名、空值和非敏感示例。
- `.gitignore`：忽略 `.env`、`.env.*`，但允许提交 `.env.example`。
- `CODEBASE_BUSINESS_LOGIC.md`：完整业务逻辑和代码逻辑梳理。
- `CODE_REVIEW_ISSUES.md`：12 项代码评审问题及确认状态。

## 四、配置和秘密外置

### 4.1 应用必须注入的变量

| 分类 | 变量 | 说明 |
| --- | --- | --- |
| Nacos | `NACOS_SERVER_ADDR` | 应用 YAML 无默认值；当前开发模板/脚本仍有固定地址，生产必须显式覆盖 |
| Nacos | `NACOS_USERNAME`、`NACOS_PASSWORD` | 应用最小权限账号 |
| Nacos | `NACOS_NAMESPACE`、`NACOS_GROUP` | 环境和项目隔离 |
| Profile | `SPRING_PROFILES_ACTIVE` | 决定远端 data-id 的环境后缀 |
| MySQL | `HHJAVA_DATASOURCE_PASSWORD` | 用户服务数据库密码 |
| JWT | `HHJAVA_SECURITY_JWT_PRIVATE_KEY_LOCATION` | 仅认证服务使用 |
| JWT | `HHJAVA_SECURITY_JWT_PUBLIC_KEY_LOCATION` | 用户服务本地 Decoder 使用 |
| JWT | `HHJAVA_SECURITY_JWT_KEY_ID` | JWT Header 与 JWKS 的密钥版本 |
| JWT | `HHJAVA_SECURITY_JWT_ISSUER` | 所有签发方与资源服务必须完全一致 |
| JWT | `HHJAVA_SECURITY_JWT_JWK_SET_URI` | Gateway、文件服务获取公钥的地址 |
| JWT | `HHJAVA_SECURITY_JWT_AUDIENCE` | 目标 API 标识 |
| JWT | `HHJAVA_SECURITY_JWT_ACCESS_TOKEN_TTL` | ISO-8601 Duration，例如 `PT1H` |
| OAuth | `HHJAVA_SECURITY_OAUTH_CLIENT_ID` | 内置客户端 ID |
| OAuth | `HHJAVA_SECURITY_OAUTH_CLIENT_SECRET` | 外部随机密钥 |
| OAuth | `HHJAVA_SECURITY_OAUTH_REDIRECT_URI` | 授权码回调地址 |

本地秘密文件集中存放在用户目录下的受控配置目录：目录权限为 `700`，秘密文件权限为 `600`。仓库、Nacos 普通配置和本文均不保存真实值。

### 4.2 动态导入 Nacos 配置

三个服务都通过本地 `application.yml` 定位 Nacos，但导入链并不完全相同：Gateway 和 user 会先可选加载 `HHJAVA_DEV_CONFIG_LOCATION` 指向的外部 properties，再通过未声明 `optional:` 的 import 读取 Nacos；backup-file 当前只有 Nacos import，不会自动加载该本地文件。下面按当前 resolver 实际支持的参数给出可复制的 user/gateway 配置形态：

```yaml
spring:
  application:
    name: hhjava-user
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  cloud:
    nacos:
      server-addr: ${NACOS_SERVER_ADDR}
      username: ${NACOS_USERNAME}
      password: ${NACOS_PASSWORD}
      config:
        namespace: ${NACOS_NAMESPACE:dev}
        group: ${NACOS_GROUP:hhjava}
        file-extension: yaml
  config:
    import:
      - "optional:file:${HHJAVA_DEV_CONFIG_LOCATION:${user.home}/.config/hhjava/dev/application.properties}"
      - "nacos:${spring.application.name}-${spring.profiles.active}.yaml?group=${NACOS_GROUP:hhjava}"
```

实际 data-id 会按应用名和 profile 生成，例如 `hhjava-user-dev.yaml`，避免本地 profile 与远端文件名脱节。namespace 从 `spring.cloud.nacos.config.namespace` 读取，import URI 只需使用 resolver 支持的 `group` 查询参数；`.yaml` 已经是 data-id 后缀。当前源码 URI 仍携带不被该 resolver 读取的 `config.namespace`、`config.group`、`config.file-extension`，现环境依靠上层全局配置生效，后续应按上例收敛。

本次在开发命名空间、`hhjava` Group 中核验的远端配置边界：

| data-id | 本次确认内容 |
| --- | --- |
| `hhjava-gateway-dev.yaml` | `/user/**` 路由到 `hhjava-user`，`/backup/**` 路由到 `hhjava-backup-file`，没有 `StripPrefix` |
| `hhjava-user-dev.yaml` | 用户服务端口、`/user` context path、MySQL/MyBatis 结构配置；数据库密码改为环境变量占位符 |
| `hhjava-backup-file-dev.yaml` | 2026-08-28 只读复核为缺失；当前版本对空配置记录警告后继续，随后文件服务因缺少 MinIO 配置和 `MinioClient` Bean 启动失败 |

因此开发入口 `/user/auth/login` 会由 Gateway 原样转发，并匹配用户服务 context path 下的 `/auth/login`。如果其他环境启用 `StripPrefix` 或改变 context path，需要同步调整路由和接口地址。

远端数据源配置只引用变量：

```yaml
spring:
  datasource:
    password: ${HHJAVA_DATASOURCE_PASSWORD}
```

这样 Nacos 配置内容本身也不再保存数据库真实密码。

### 4.3 Nacos 与 MySQL 轮换

本次外部环境操作包括：

- 创建 Nacos 应用运行账号，不再让应用使用管理员账号。
- 配置读取权限限制在 `dev:hhjava:*`。
- 服务发现权限限制在 `dev:hhjava:naming/*`。
- 轮换 Nacos 管理员密码，并验证旧密码失效。
- 轮换 MySQL `app@%` 密码，并验证旧密码失效。
- 初始化开发库 `app` 的 `user`、`role`、`user_role` 表、用户名唯一约束和源码当前依赖的默认角色记录。
- 联调完成后删除临时测试用户和对应角色关联。

## 五、RSA、JWT 与 JWKS

### 5.1 为什么从 HMAC 改为 RSA

HMAC 需要签发方和验签方共享同一个秘密。一旦 Gateway 或某个资源服务泄漏该秘密，攻击者既能验签也能伪造 Token。

RSA 模式中：

- 用户服务持有私钥并签发 Token。
- JWKS 只发布公钥。
- Gateway 和文件服务只有验签能力，没有签发能力。
- `kid` 用于选择具体公钥，为以后平滑轮换预留入口。

### 5.2 Token 约束

| 字段 | 作用 |
| --- | --- |
| `alg=RS256` | 防止接受未配置的签名算法 |
| `kid` | 指向当前密钥版本 |
| `iss` | 限定唯一签发者 |
| `sub` | 当前认证主体 |
| `aud` | 限定 Token 只能用于目标 API |
| `iat`、`nbf`、`exp` | 签发、生效和过期时间 |
| `jti` | Token 唯一标识，为审计或撤销扩展预留 |

本次运行验证确认访问令牌有效期为 3600 秒。Payload 可以被 Base64Url 解码，所以不得写入密码、客户端密钥或其他敏感内容。

### 5.3 JWKS 暴露边界

JWKS 验收项：

- 只有 1 枚用于签名的 RSA 公钥。
- `use=sig`、`alg=RS256`、`kid` 与 Token Header 一致。
- 不包含 `d`、`p`、`q`、`dp`、`dq`、`qi`、`oth` 等私钥字段。

## 六、OAuth2 授权服务器

### 6.1 当前支持的授权模式

| 模式 | 当前状态 | 使用场景 |
| --- | --- | --- |
| authorization code | 已配置，浏览器端到端流程待验收 | 有用户参与的网页登录 |
| client credentials | 已真实验证 | 服务到服务调用 |
| refresh token | 已配置，待独立集成测试 | 延长用户会话 |
| password grant | 已删除 | 当前工程没有完整实现，不继续声明 |

项目仍保留自定义 `/auth/login`，它与标准 OAuth2/OIDC 是两个认证入口，但已共用同一组 RSA 密钥、issuer、audience、`kid` 和 TTL。

### 6.2 client secret 的编码问题

Spring Authorization Server 1.3.4 会读取容器中的 `PasswordEncoder` 并注入 `ClientSecretAuthenticationProvider`。项目的全局编码器是 `BCryptPasswordEncoder`，因此注册客户端时必须使用同一个编码器生成 BCrypt 原生哈希，不能再人为拼接与该编码器不匹配的 `{bcrypt}` 前缀。

真实联调还发现：使用 HTTP Basic 发送包含 `+`、`/` 等字符的 client secret 时，手工调试工具如果没有先按 `application/x-www-form-urlencoded` 规则编码，服务端可能把 `+` 解码成空格，最终返回 `invalid_client`。

本次将尚未对外使用的 OAuth 密钥轮换为 64 位十六进制随机值。它仍有 256 位随机熵，同时能减少 Reqable、curl 或其他手工客户端的编码歧义。服务端只保存 BCrypt 哈希。

## 七、Gateway 与下游服务的纵深防御

### 7.1 精确白名单

Gateway 只精确公开：

- `POST /user/auth/register`
- `POST /user/auth/login`
- OAuth2/OIDC 协议端点

Gateway 源码虽然还列有 `/v3/api-docs/**`、`/swagger-ui/**` 等根路径白名单，但当前 Nacos 只有 `/user/**`、`/backup/**` 路由。真实的 `/user/v3/api-docs`、`/user/swagger-ui/**` 不匹配根路径白名单，经 Gateway 访问时仍需要 JWT；直连用户服务时才由下游自己的文档白名单匿名放行。

不能使用 `/user/**` 这类服务级通配符，否则未来新增用户接口会默认匿名公开。

用户服务也使用相同原则：只公开注册、登录、协议和文档端点，其他请求默认认证。

文件服务只公开文档端点，所有文件上传和删除请求都必须携带合法 Token。

### 7.2 为什么下游还要验签

只在 Gateway 验签依赖一个很强的前提：下游端口永远不能被绕过。但开发环境、安全组误配、服务网格旁路、内部横向访问都可能破坏这个前提。

当前方案让 Gateway、用户服务、文件服务都成为 Resource Server：

- Gateway 可以尽早拒绝非法流量。
- 下游服务仍保留自身安全边界。
- 身份通过标准 `SecurityContext` 获取，不信任客户端可伪造的 `userId` Header。
- 合法 Bearer Token 默认由 Gateway 原样转发，无需自定义 Header Filter。

## 八、使用 Reqable 调试

建议先在 Reqable 环境变量中定义：

| 变量 | 开发环境示例 |
| --- | --- |
| `gateway_base_url` | `http://127.0.0.1:63010` |
| `user_base_url` | `http://127.0.0.1:8080/user` |
| `username` | 自行创建的测试用户名 |
| `password` | 仅保存在 Reqable 私有环境中 |
| `oauth_client_id` | 从部署环境取得 |
| `oauth_client_secret` | 从部署环境取得 |
| `access_token` | 登录后临时保存，不写进文档或 Git |

### 8.1 注册

```http
POST {{gateway_base_url}}/user/auth/register
Content-Type: application/json
```

```json
{
  "username": "{{username}}",
  "password": "{{password}}"
}
```

### 8.2 登录

```http
POST {{gateway_base_url}}/user/auth/login
Content-Type: application/json
```

```json
{
  "username": "{{username}}",
  "password": "{{password}}",
  "authType": "password"
}
```

成功时从响应的 `data.token` 取出 JWT，保存到 Reqable 私有环境变量 `access_token`。

调用受保护接口时设置：

```http
Authorization: Bearer {{access_token}}
```

调用注册或登录接口时不要附带过期 Bearer Token。即使路径允许匿名访问，Resource Server 看到主动提交的无效 Token 时仍可能先返回 401。

### 8.3 client credentials

```http
POST {{user_base_url}}/oauth2/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic <由 Reqable 根据 client id 和 client secret 生成>
```

Body 选择 Form URL Encoded：

```text
grant_type=client_credentials
scope=all
```

不要手工把 `client_id:client_secret` 明文写进文档、脚本或公共环境。Reqable 中选择 Basic Auth，由工具生成 Header。

### 8.4 JWKS

```http
GET {{user_base_url}}/oauth2/jwks
```

只检查 `kty`、`use`、`alg`、`kid` 以及是否存在私钥字段，不要复制完整 modulus 到公开问题记录中。

### 8.5 常见失败判断

| 现象 | 优先检查 |
| --- | --- |
| 连接失败 | 服务是否启动、端口、Gateway 路由、Nacos 9848 是否可达 |
| 404 | `/user` context path 是否重复或缺失 |
| 400 | JSON/Form 类型、必填字段、`authType=password` |
| 401 | Token 缺失、过期、篡改，issuer/audience/JWKS 不匹配 |
| 403 | 已认证但没有满足授权规则，或协议端点 CSRF/客户端认证配置错误 |
| `invalid_client` | client id/secret、Basic 编码、服务是否已用新秘密重启、BCrypt 编码器是否一致 |
| 500 | 请求已通过认证但进入业务层失败，应结合服务日志继续定位；不能简单判断为 Token 失败 |

## 九、验证结果

### 9.1 自动化测试与构建

- `mvn clean test`：9 个 Reactor 模块全部 `BUILD SUCCESS`。
- Surefire 共执行 6 个测试，6/6 通过：
  - `JwtTokenServiceTest`：2 个。
  - `RsaKeyConfigurationTest`：3 个。
  - `AuthorizationServerTest`：1 个。
- 随后完整 Reactor package 成功。
- `git diff --check` 通过。
- 当前源码敏感信息扫描未发现 RSA 私钥、JWT、旧数据库密码等已知秘密模式。

### 9.2 2026-08-27 真实运行验证

| 验证项 | 结果 |
| --- | --- |
| 用户服务加载 Nacos 配置 | 成功 |
| 用户服务连接轮换后的 MySQL | 成功 |
| 用户服务注册到 Nacos | 成功 |
| 注册和自定义登录 | 成功 |
| 自定义登录 JWT | RS256、正确 `kid`/issuer/audience、TTL 3600 秒 |
| OAuth2 client credentials | 成功签发 Bearer JWT |
| JWKS | 只有公钥，无私钥字段 |
| Gateway 合法 Token | 通过安全链并到达下游 |
| Gateway 缺失/篡改 Token | 401 |
| 文件服务合法 Token | 通过安全链并进入业务请求处理 |
| 文件服务缺失/篡改 Token | 401 |
| 旧 Nacos 管理员密码 | 失效 |
| 旧 MySQL 应用密码 | 失效 |
| 临时联调账号 | 验证后已删除 |

文件服务验证使用了进程级临时 MinIO 占位参数，没有进行真实对象存储操作。

## 十、仍未关闭的风险

R001 当前应保持“部分修复/待基础设施收口”，不能仅因为代码通过测试就标记为完全关闭。

### 10.1 Nacos 基础设施

- 2026-08-27 验证时公网 Nacos 为 2.0.3，需要先备份再按官方升级指南升级。
- `8848` 不应无条件向公网开放，应通过安全组、防火墙、VPN、堡垒机或内网化收敛到可信来源。
- Nacos 2.x 客户端还依赖偏移后的 gRPC 端口；当前 9848 出现过超时，需要结合版本升级和安全组规则一起检查。
- 最小权限应用账号仍能访问用户枚举接口，说明旧版本服务端风险不能只靠应用 ACL 解决。

### 10.2 Git 历史

当前工作树已不再保存旧秘密，但旧密码和旧 HMAC 代码可能仍在 Git 历史中。历史清理会改写提交 ID、影响所有协作者，必须单独确认后执行。无论是否改写历史，已暴露秘密都必须先轮换，本次已经完成当前可操作的轮换。

### 10.3 OAuth2/OIDC

- authorization code 的浏览器端到端流程尚未验收。
- `CustomUserDetailsService` 当前只接受项目自有 JSON 登录参数，默认表单登录传入普通用户名时协议不一致，此问题继续归入 R009。
- refresh、introspection、revocation、UserInfo 等端点仍需独立测试。
- 项目长期保留 `/auth/login` 还是完全收敛到 OAuth2/OIDC，仍需产品和架构决策。

### 10.4 文件业务

- MinIO 尚未安装，真实上传、删除、下载未验证。
- 文件没有元数据表、所有权模型和对象级授权。
- 删除目标仍由客户端 URL 控制。
- `InputStream.available()` 不能可靠代表对象总长度。
- 删除异常可能被吞掉并返回假成功。

## 十一、关联代码评审问题状态

| 编号 | 问题摘要 | 本次结果 |
| --- | --- | --- |
| R001 | JWT、Nacos、OAuth 凭据进入版本库 | 已完成源码、轮换和运行验证；Nacos 基础设施与 Git 历史待收口 |
| R002 | 文件服务没有强制认证 | 已改为 Resource Server；待用户单独确认关闭 |
| R003 | 文件没有所有权模型 | 未处理 |
| R004 | 登录 JWT 回放协议不兼容 | 删除手写回放 Filter，改为标准 JWT 认证；待用户确认 |
| R005 | 注册两次写库没有事务 | 未处理 |
| R006 | Gateway、用户服务放行范围过大 | 已改为精确白名单；待用户确认 |
| R007 | 认证输入与失败信息保护不足 | 登录 Validation 运行基础已补，注册约束和账号枚举仍未处理 |
| R008 | 全局异常体系不统一 | 未处理 |
| R009 | 自定义登录与 OAuth2 两套入口 | 签名体系已经统一，长期入口和授权码流程仍待确认 |
| R010 | MinIO 完整性与假成功 | MinIO 延期，未处理 |
| R011 | 重复、命名、调试代码 | 未处理 |
| R012 | HTML 上传主动内容风险 | 等 MinIO 部署和 Bucket 策略后确认 |

“源码已经改变”不等于“用户已经逐项验收”。R002、R004、R006、R007、R009 的联动改造仍应保留独立确认状态。

## 十二、后续执行顺序

1. 备份并升级 Nacos，验证配置、服务发现、权限模型兼容性。
2. 收敛 `8848`，并为可信客户端正确配置 9848 等必要端口。
3. 重新执行用户服务、Gateway、文件服务的 Token 矩阵。
4. 单独确认是否清理 Git 历史。
5. 处理 R002、R003、R004、R005、R006、R007、R008、R009 等剩余评审项。
6. 安装 MinIO 后再完成文件所有权、完整性和真实业务测试。

## 十三、关键源码索引

| 功能 | 项目内路径 |
| --- | --- |
| 授权服务器 | `hhjava-service/hhjava-user/src/main/java/com/hh/security/AuthorizationServer.java` |
| 用户服务安全链 | `hhjava-service/hhjava-user/src/main/java/com/hh/security/WebSecurityConfig.java` |
| RSA/JWKS | `hhjava-service/hhjava-user/src/main/java/com/hh/security/jwt/RsaKeyConfiguration.java` |
| 自定义登录签发 | `hhjava-service/hhjava-user/src/main/java/com/hh/security/jwt/JwtTokenService.java` |
| JWT 属性 | `hhjava-service/hhjava-user/src/main/java/com/hh/security/properties/JwtProperties.java` |
| OAuth 客户端属性 | `hhjava-service/hhjava-user/src/main/java/com/hh/security/properties/OAuthClientProperties.java` |
| Gateway 安全链 | `hhjava-gateway/src/main/java/com/hh/gateway/config/SecurityConfig.java` |
| 文件服务安全链 | `hhjava-service/hhjava-backup-file/src/main/java/com/hhjava/www/config/SecurityConfig.java` |
| 环境变量样例 | `.env.example` |
| 业务逻辑文档 | `CODEBASE_BUSINESS_LOGIC.md` |
| 问题清单 | `CODE_REVIEW_ISSUES.md` |

## 十四、参考资料

- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [Spring Security Resource Server JWT](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)
- [Spring Authorization Server 配置模型](https://docs.spring.io/spring-authorization-server/reference/configuration-model.html)
- [Nacos 身份认证文档](https://nacos.io/en/docs/v2.3/guide/user/auth/)
- [Nacos 认证绕过问题记录](https://github.com/alibaba/nacos/issues/10060)
- [Nacos 2.5 升级指南](https://nacos.io/en/docs/v2.5/manual/admin/upgrading/)

相关专题：

- [OAuth2 协议](./OAuth2协议.md)
- [JWT 令牌](./jwt令牌.md)
- [网关、认证过滤器与拦截器](./网关-认证过滤器-拦截器.md)
- [认证和授权](./认证和授权.md)
- [Nacos](../Nacos.md)
- [接口测试工具](../接口测试工具.md)
- [hhjava 项目业务与代码逻辑](../hhjava项目业务与代码逻辑.md)
