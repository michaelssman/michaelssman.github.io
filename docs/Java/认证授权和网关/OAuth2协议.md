# OAuth2 协议

OAuth 2.0 是授权框架，用于让客户端在限定范围内访问受保护资源；用户身份登录语义由 OpenID Connect 等协议补充。当前项目同时承担授权服务器和资源服务器职责，协议能力以实际注册的客户端、授权类型和安全过滤链为准。

## spring-boot-starter-oauth2-resource-server

用来保护资源，比如API端点，让它们需要OAuth2的令牌才能访问。

## spring-security-oauth2-authorization-server

`spring-security-oauth2-authorization-server` 是用于处理 OAuth2 认证和授权的组件。

- **用途**: 用于构建 OAuth2 授权服务器。
- **功能**:
  - 提供 OAuth2 授权服务，管理和颁发访问令牌。
  - 支持多种授权模式（如授权码、客户端凭证等）。
  - 适用于需要提供 OAuth2 授权服务的应用。

## 客户端凭证模式

client credentials 用于“应用代表自己”访问资源，不包含最终用户身份。典型场景是定时任务、内部服务或 CI 系统调用受保护 API。

请求 Token：

```http
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic <由客户端根据 client id 和 client secret 生成>
```

```text
grant_type=client_credentials
scope=all
```

注意：

- client secret 只能保存在服务端或受控部署环境，不能放在浏览器、移动 App 安装包或 Git 中。
- 服务端注册客户端时应保存 secret 的单向哈希，不保存明文。
- HTTP Basic 中的 client id 和 secret 按 OAuth2 规则需要先做表单编码，再拼接和 Base64；手工拼 Header 容易让 `+` 等字符被错误解码。
- `invalid_client` 应优先检查客户端 ID、密钥、Basic 编码、服务是否已加载轮换后的配置，以及服务端 `PasswordEncoder` 是否一致。

## Spring Authorization Server 当前实践

Spring Boot 应统一管理 Spring Authorization Server 的兼容版本，不要在子模块中随意覆盖一个与 Boot/Security 不匹配的版本。

`hhjava` 当前只声明真正配置的模式：

- authorization code
- client credentials
- refresh token

password grant 已从注册客户端中删除。授权服务器和项目自有登录虽然暂时并存，但两条签发路径共用 RSA `JwtEncoder`、issuer、audience、`kid` 和访问令牌 TTL。

OAuth access token 应由资源服务验证 RS256、issuer、audience 和时间声明；JWKS 只负责发布公钥，不应包含私钥参数。

实现、Reqable 请求方式和真实验证矩阵见 [hhjava 认证授权与配置安全整改实战](./hhjava认证授权与配置安全整改实战.md)。
