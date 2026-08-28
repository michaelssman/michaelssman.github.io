# JWT 令牌

## 基本特性

JSON Web Token（JWT）是 RFC 7519 定义的紧凑声明格式。JWT 可以承载用户或客户端身份，但内容默认只经过 Base64Url 编码，并未加密，因此不能放入密码、密钥或其他敏感信息。

在 hhjava 中，JWT 用于无状态 Bearer 认证：

- user 服务使用 RSA 私钥和 RS256 签发；
- Gateway 与 backup-file 通过 JWKS 获取公钥并独立验签；
- user 自身使用本地 RSA 公钥验证资源请求；
- 资源服务不需要为每个请求回调签发服务，但仍要处理密钥轮换、Token 过期和撤销策略。

## JWT 结构

JWT 由 Header、Payload 和 Signature 三部分组成，中间使用 `.` 分隔。

### Header

Header 声明令牌类型、签名算法和密钥版本：

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "hhjava-rsa-key"
}
```

资源服务只能接受预期算法，不能信任客户端任意指定的 `alg`。

### Payload

Payload 保存声明，例如：

```json
{
  "iss": "https://issuer.example",
  "sub": "user-id",
  "aud": ["hhjava-api"],
  "iat": 1787880000,
  "nbf": 1787880000,
  "exp": 1787883600,
  "jti": "token-id"
}
```

项目自有 `/auth/login` Token 使用用户名作为 `sub`。OAuth2 access token 还可以包含协议 scope；当前 Gateway 尚未根据 scope 或角色进行业务授权。

### Signature

签发方使用 RSA 私钥对 Header 和 Payload 的编码结果签名。资源服务使用公钥验证签名和声明，公钥只能验签，不能伪造新 Token。

## RS256、kid 与 JWKS

- 私钥只保留在 user 服务；
- JWKS 只发布公钥材料；
- `kid` 用于在公钥集合中选择对应密钥；
- Gateway 与 backup-file 只获得验签能力。

### Resource Server 配置

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${HHJAVA_SECURITY_JWT_ISSUER}
          jwk-set-uri: ${HHJAVA_SECURITY_JWT_JWK_SET_URI}
          audiences:
            - ${HHJAVA_SECURITY_JWT_AUDIENCE:hhjava-api}
          jws-algorithms:
            - RS256
```

验签至少应覆盖：

| 校验项 | 目的 |
| --- | --- |
| `alg` | 只接受 RS256，避免算法降级 |
| `kid` | 从 JWKS 选择正确公钥 |
| `iss` | Token 必须来自预期签发者 |
| `aud` | Token 必须用于当前 API |
| `exp`、`nbf`、`iat` | 约束有效时间 |

### JWKS 验收与轮换

公开 JWK 通常包含 `kty`、`n`、`e`、`use`、`alg`、`kid`，不应出现 RSA 私钥字段 `d`、`p`、`q`、`dp`、`dq`、`qi`、`oth`。

轮换时先让 JWKS 同时发布新旧公钥，再让签发方切换到新 `kid`；等待旧 Token 过期和资源服务缓存刷新后再移除旧公钥。直接用同一个 `kid` 覆盖密钥可能在缓存期间造成批量 401。

完整实现与验证记录见 [hhjava 认证授权与配置安全整改实战](./hhjava认证授权与配置安全整改实战.md)。
