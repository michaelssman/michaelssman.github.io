# JWT（JSON Web Token）与 JWKS（JSON Web Key Set）

> 本文集中记录令牌格式、签名、验签、密钥管理和使用边界，核对时间：2026-09-05。
> 授权流程与令牌用途见 [OAuth 2.0、OIDC 与 PKCE 学习笔记](OAUTH2_OIDC_VIDEO_STUDY_NOTES.md)。

## 术语速查

| 术语 | 英文全称 | 中文解释 |
| --- | --- | --- |
| JWT | JSON Web Token | JSON Web 令牌，用于承载声明的令牌格式 |
| Claim | Claim | 声明，对主体或上下文信息的一项断言 |
| JWS | JSON Web Signature | JSON Web 签名，使用数字签名或消息认证码保护内容完整性 |
| JWE | JSON Web Encryption | JSON Web 加密，用于加密并保护内容 |
| JWK | JSON Web Key | JSON Web 密钥，使用 JSON 表示密码学密钥 |
| JWKS | JSON Web Key Set | JSON Web 密钥集 |
| OAuth 2.0 | The OAuth 2.0 Authorization Framework | OAuth 2.0 授权框架，用于委托访问资源 |
| OIDC | OpenID Connect | OpenID Connect 身份认证协议，是建立在 OAuth 2.0 之上的身份层 |
| PKCE | Proof Key for Code Exchange | 授权码交换证明密钥，用于降低授权码被截获后遭滥用的风险 |
| Access Token | Access Token | 访问令牌，用于访问受保护资源 |
| Refresh Token | Refresh Token | 刷新令牌，用于按授权服务器策略获取新的访问令牌 |
| ID Token | ID Token（ID 表示 Identity） | 身份令牌，OIDC 用它向客户端传递用户认证结果和相关声明 |
| MAC | Message Authentication Code | 消息认证码，使用共享秘密验证数据完整性和来源 |
| HMAC | Hash-based Message Authentication Code | 基于哈希函数的消息认证码 |
| SHA-256 | Secure Hash Algorithm 256-bit | 256 位安全散列算法 |
| HS256 | HMAC using SHA-256 | 使用 SHA-256 的 HMAC 算法 |
| RSA | Rivest-Shamir-Adleman | 以三位发明者姓氏命名的非对称密码算法 |
| RSASSA | RSA Signature Scheme with Appendix | RSA 附录式签名方案 |
| PKCS | Public-Key Cryptography Standards | 公钥密码学标准系列 |
| CRT | Chinese Remainder Theorem | 中国剩余定理，可用于优化 RSA 私钥运算 |
| RS256 | RSASSA-PKCS1-v1_5 using SHA-256 | 使用 SHA-256 的 RSA PKCS #1 v1.5 签名算法 |
| Base64URL | Base 64 Encoding with URL and Filename Safe Alphabet | 使用 URL 与文件名安全字符表的 Base64 编码 |
| Base64URLUInt | Base64urlUInt-Encoded Integer | 使用 Base64URL 编码的无符号整数 |
| UTF-8 | Unicode Transformation Format - 8-bit | Unicode 的 8 位可变长度字符编码 |
| ASCII | American Standard Code for Information Interchange | 美国信息交换标准代码 |
| UTC | Coordinated Universal Time | 协调世界时 |
| API | Application Programming Interface | 应用程序编程接口 |
| SDK | Software Development Kit | 软件开发工具包 |
| URL | Uniform Resource Locator | 统一资源定位符 |
| URI | Uniform Resource Identifier | 统一资源标识符，URL 是其常见形式 |
| HTTP | Hypertext Transfer Protocol | 超文本传输协议 |
| HTTPS | Hypertext Transfer Protocol Secure | 受加密连接保护的 HTTP |
| X.509 | X.509（标准编号，不是缩写） | 定义公钥证书及相关验证机制的标准 |
| CSRF | Cross-Site Request Forgery | 跨站请求伪造 |
| RFC | Request for Comments | 请求评议文档，互联网标准和技术规范的文档系列 |

## 1. JWT 的定位

JWT 是一种承载 Claims（声明）的格式。它可以用 JWS 提供数字签名或 MAC 保护，也可以用 JWE 加密；本文重点介绍常见的 JWS 形式。

OAuth 2.0 的 Access Token 可以采用 JWT，也可以是不透明随机值；Refresh Token 也不要求采用 JWT。OIDC 的 ID Token 使用 JWT，但不能作为普通业务 API 的 Access Token。

| 方式 | 常见验证方式 | 主要取舍 |
| --- | --- | --- |
| 自包含 JWT | 使用可信密钥在本地验证，再检查声明 | 减少逐次远程验证的依赖，但要处理密钥轮换、权限更新和撤销 |
| 不透明 Token | 内省或查询服务端状态，也可按策略缓存 | 便于集中管理状态，但依赖服务端查询及缓存策略 |

本地验签不等于整个登录系统无状态。登录会话、刷新令牌和撤销记录仍可能保存在服务端；共享会话存储也可以用于分布式系统。

## 2. 结构与 Claims（声明）

### 2.1 签名 JWT（JWS）的三段结构

常见的签名 JWT 采用以下形式，三段之间用 `.` 分隔：

```text
BASE64URL(Header) . BASE64URL(Payload) . BASE64URL(Signature)
```

- Header（头部）：描述算法、令牌类型和密钥编号。
- Payload（载荷）：保存身份、有效期、接收方等声明。
- Signature（签名）：数字签名或 MAC，用于检测篡改并验证密钥持有关系。

Header 和 Payload 的 Base64URL 编码可直接还原，不提供保密性。JWE 是加密表示，不能把所有 JWT 都理解为三段式签名令牌。

### 2.2 字段示例

以下是虚构的业务令牌字段，不是可直接使用的令牌。实际时间应由签发端生成，示例只演示 Unix 时间戳（从 1970-01-01 00:00:00 UTC 起计算的秒数）及 900 秒有效期。

Header：

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "signing-key-1"
}
```

Header 常见字段：

| 字段 | 英文全称 | 中文解释 |
| --- | --- | --- |
| `alg` | Algorithm | 保护令牌所使用的算法 |
| `typ` | Type | 对象类型，JWT 中通常写作 `JWT` |
| `kid` | Key ID（Key Identifier） | 密钥编号，用于从可信密钥集合中选择密钥 |

Payload：

```json
{
  "iss": "https://auth.example.com",
  "sub": "user-123",
  "aud": "orders-api",
  "iat": 1800000000,
  "exp": 1800000900,
  "scope": "orders:read"
}
```

常用 Claims：

| 字段 | 英文全称 | 中文解释 | 校验重点 |
| --- | --- | --- | --- |
| `iss` | Issuer | 签发者 | 与预期可信签发者匹配 |
| `sub` | Subject | 主体标识，不一定是用户 | 按签发者和业务约定识别主体 |
| `aud` | Audience | 预期接收者，可为字符串或数组 | 必须包含当前客户端或资源服务器的预期标识 |
| `exp` | Expiration Time | 过期时间 | 当前时间必须早于该时间 |
| `nbf` | Not Before | 最早生效时间 | 当前时间早于该时间时不能接受 |
| `iat` | Issued At | 签发时间 | 用于按策略检查令牌年龄，不代替 `exp` |
| `jti` | JWT ID | 令牌唯一标识 | 可关联撤销或重放记录，本身不会自动防重放 |
| `scope` | Scope | 授权范围 | 必须包含接口所需权限，并遵循签发方约定 |

JWT 基础规范不要求所有场景都携带上述全部字段；必需字段由具体协议和应用确定。`scope`、角色等声明也要遵循各自约定，不能仅凭字段存在就授权。

### 2.3 签名输入

下面的 `header` 和 `payload` 表示 JSON 文本，Base64URL 编码省略末尾填充符：

```text
signing_input = BASE64URL(UTF-8(header)) + "." + BASE64URL(UTF-8(payload))
signature = SIGN_OR_MAC(ASCII(signing_input), key)
jwt = signing_input + "." + BASE64URL(signature)
```

`SIGN_OR_MAC` 由约定算法决定。验证时使用收到的前两段原文，而不是把 JSON 解码、重新排版后再计算。实际签发和校验使用成熟库，不手写密码学实现。

## 3. HS256 与 RS256

| 对比项 | HS256（HMAC using SHA-256） | RS256（RSASSA-PKCS1-v1_5 using SHA-256） |
| --- | --- | --- |
| 算法 | HMAC-SHA-256，生成 MAC | RSA PKCS #1 v1.5 与 SHA-256，生成数字签名 |
| 密钥 | 签发方与验证方共享秘密 | 私钥签名，公钥验签 |
| 权限边界 | 持有共享秘密的一方也能生成有效 MAC | 仅持有公钥的一方不能生成有效签名 |
| 密钥要求 | 至少 256 位，并使用高熵随机密钥 | RSA 密钥至少 2048 位 |

两者都不是内容加密。多服务场景采用 RS256，可以让资源服务器只持有公钥，避免向所有验证方分发签名秘密；算法选择仍要匹配协议、库和部署要求。

验证端必须预先限制允许的算法，并检查算法与密钥类型、用途一致，不能由收到的 `alg` 自行决定接受范围。业务认证场景应拒绝未签名令牌和不符合策略的算法。

## 4. JWK、JWKS 与密钥轮换

JWK 是密钥的 JSON 表示；JWKS 是包含 `keys` 数组的 JWK 集合。它们可以表示公钥、私钥或对称秘密，**公开验签端点只能发布所需的公钥材料**。

在非对称签名场景中，认证服务器使用私钥签发 JWT，并在 Header 中写入 `kid`；验证端从预先信任的地址获取 JWKS，根据 `kid` 选择公钥并验证签名。OIDC Discovery（OpenID Connect Discovery，OpenID Connect 发现机制）使用 `jwks_uri`（JWK Set URI，JWK 集合地址）声明该地址，`/.well-known/jwks.json` 是常见路径，但不是必须采用的固定路径。这样可以集中分发公钥，并支持多个密钥并存和密钥轮换。

典型的 RSA 公钥 JWKS：

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "signing-key-1",
      "use": "sig",
      "alg": "RS256",
      "n": "<base64url-encoded-modulus>",
      "e": "AQAB"
    }
  ]
}
```

RSA 验签公钥常见字段：

| 字段 | 英文全称 | 中文解释 |
| --- | --- | --- |
| `kty` | Key Type | 密钥类型，例如 `RSA` |
| `kid` | Key ID（Key Identifier） | 密钥编号，用于匹配令牌 Header |
| `use` | Public Key Use | 公钥用途，`sig`（Signature）表示签名验证 |
| `alg` | Algorithm | 预期算法，例如 `RS256` |
| `n` | Modulus | RSA 公钥模数，以 Base64URLUInt 编码 |
| `e` | Exponent | RSA 公钥指数，以 Base64URLUInt 编码 |

Base64URLUInt 是使用 Base64URL 表示无符号整数的编码方式。示例中的 `AQAB` 对应常用公钥指数 65537。

`kid`、`use`、`alg` 是否必需取决于应用约定。公开 JWKS 不应包含以下 RSA 私钥参数，也不能发布对称密钥的 `k`（Key Value，密钥值）：

| 字段 | 英文全称 | 中文解释 |
| --- | --- | --- |
| `d` | Private Exponent | 私钥指数 |
| `p` | First Prime Factor | 第一个素因子 |
| `q` | Second Prime Factor | 第二个素因子 |
| `dp` | First Factor CRT Exponent | 第一个素因子的中国剩余定理指数 |
| `dq` | Second Factor CRT Exponent | 第二个素因子的中国剩余定理指数 |
| `qi` | First CRT Coefficient | 第一个中国剩余定理系数 |
| `oth` | Other Primes Info | 多素数 RSA 的其他素数信息 |

JWKS 只提供验签所需的密钥材料，不存放 JWT，也不会自动完成令牌校验。签名通过后，验证端仍须检查 `iss`、`aud`、`exp`、`nbf` 等声明以及业务权限。

密钥轮换通常按以下顺序进行：

1. 发布新公钥，为新旧密钥分配不同 `kid`。
2. 使用新私钥签发令牌，并在 Header 中携带新 `kid`。
3. 在正常轮换的过渡期保留旧公钥，让尚未过期的旧令牌继续验证。
4. 结合旧令牌的最长寿命、时钟偏差和缓存策略退役旧公钥。

验证端可缓存可信 JWKS。遇到未知 `kid` 时，只从预先信任的来源按受控策略刷新；仍无法找到合适密钥时拒绝令牌，不能跳过验证。私钥泄漏属于紧急事件，不能等待正常过渡期结束才处理。

## 5. 验证流程

### 5.1 JWT Access Token（访问令牌）

```text
收到 Access Token
  -> 使用预配置的令牌类型、可信签发者和算法策略
  -> 从可信密钥集合中选择匹配的验签密钥
  -> 验证签名或 MAC
  -> 检查必需声明、iss、aud、exp，以及存在时的 nbf
  -> 检查接口权限与业务数据权限
  -> 允许请求；任一必需检查失败则拒绝
```

关键约束：

- 解析出的 Header 和 Payload 在验证前都是不可信输入，`kid` 匹配也不代表令牌可信。
- 密钥来源必须由可信配置或经过验证的 Discovery 确定，不能直接请求令牌中任意指定的 `jku`（JWK Set URL，JWK 集合地址）、`x5u`（X.509 URL，证书链地址）或 `iss` 地址。
- 按所采用的令牌规范验证类型及必需声明，时间字段使用秒级时间，并设置有限的时钟偏差。
- 签名通过后仍需检查当前 API 的权限及业务对象所有权；令牌中的角色也可能需要结合实时授权状态判断。

### 5.2 OIDC ID Token（身份令牌）

ID Token 应交给成熟 OIDC SDK 按协议验证，不能与 Access Token 共用不加区分的接受规则：

- 检查 `iss`、`sub`、`aud`、`exp`、`iat` 等必需声明；`aud` 必须包含当前客户端的 `client_id`（Client Identifier，客户端标识），其他受众也须符合信任策略。
- 使用签发者提供的可信密钥，按协议和客户端协商配置验证密码学保护；接入时优先采用 SDK 的完整验签流程。
- 请求使用了 `nonce`（一次性随机值）时，必须检查返回值存在且与本次请求一致，并防止重放。
- 使用定义了 `azp`（Authorized Party，被授权方）的扩展时，按该扩展规则验证授权方；请求了 `auth_time`（Authentication Time，认证时间）或 `max_age`（Maximum Authentication Age，最长认证时效）时检查认证时间和重新认证要求。

JWT 也能承载 `private_key_jwt`（使用私钥签名 JWT 的客户端认证方式）等客户端断言。其用途是客户端认证，不是用户登录或访问业务 API，必须使用对应协议的独立验证规则。

## 6. 使用、过期与撤销

采用 Bearer Token（持有者令牌）认证时，通过 HTTPS 在请求头发送 Access Token：

```http
GET /orders HTTP/1.1
Host: api.example.com
Authorization: Bearer <ACCESS_TOKEN>
```

- 不把密码、私钥等秘密放进可读取的 Payload；声明只保留接收方需要的数据。
- 不把真实令牌写入 URL、日志或示例，也不上传到不受信任的在线解码网站。
- 本地验签不会自动获知退出登录、账号禁用或权限变更。需要立即失效时，必须配合撤销状态、内省或其他实时检查。
- 删除客户端保存的 Token，不会让已泄漏的副本失效；停止刷新也不会自动撤销已签发的 Access Token。
- 仅从 JWKS 删除公钥不能保证立即撤销，因为验证端可能持有缓存；密钥泄漏处置需要协调缓存和拒绝策略。
- JWT 可以与 Session（会话）、Cookie（浏览器状态数据）同时使用。CSRF 风险取决于浏览器是否自动携带认证凭据，不能由令牌格式单独决定。

## 7. 自测

| 问题 | 核心答案 |
| --- | --- |
| 为什么普通签名 JWT 中不能放密码？ | Header 和 Payload 可被解码，签名不提供内容保密性 |
| 公钥为什么可以公开？ | 公钥能验签，但不能代替私钥签名；公开端点必须排除秘密材料 |
| 为什么验签后还要检查 `iss`、`aud` 和权限？ | 签名只是一项信任检查，还需确认用途、接收方、有效期和业务授权 |
| JWT 能否在退出登录后立即失效？ | 取决于服务端是否执行撤销或其他实时状态检查，单纯本地验签无法感知退出 |

## 8. 参考资料

- [RFC 7519：JWT 格式与 Claims](https://www.rfc-editor.org/rfc/rfc7519.html)
- [RFC 7515：JWS 结构与签名输入](https://www.rfc-editor.org/rfc/rfc7515.html)
- [RFC 7518：HMAC、RSA 与密钥参数](https://www.rfc-editor.org/rfc/rfc7518.html)
- [RFC 7517：JWK 与 JWK Set](https://www.rfc-editor.org/rfc/rfc7517.html)
- [RFC 8725：JWT 安全实践](https://www.rfc-editor.org/rfc/rfc8725.html)
- [RFC 6750：Bearer Token 使用方式](https://www.rfc-editor.org/rfc/rfc6750.html)
- [OpenID Connect Core：ID Token 校验](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation)
