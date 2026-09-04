# OAuth2、OIDC、PKCE、JWT、JWKS 与认证安全学习笔记

> 本文只整理可跨项目复用的概念、原理和安全知识，不记录 hhjava 的端口、接口、类名或配置值。

## 1. 学习资料与阅读方法

协议结论优先依据下面的正式规范和官方文档：

- [RFC 6749：OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 9700：OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 7636：Proof Key for Code Exchange](https://www.rfc-editor.org/rfc/rfc7636)
- [RFC 8252：OAuth 2.0 for Native Apps](https://www.rfc-editor.org/rfc/rfc8252)
- [RFC 10017：OAuth 2.0 for Browser-Based Applications](https://www.rfc-editor.org/rfc/rfc10017)
- [OpenID Connect Core 1.0（Errata Set 2）](https://openid.net/specs/openid-connect-core-1_0.html)
- [RFC 7519：JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
- [RFC 7517：JSON Web Key](https://www.rfc-editor.org/rfc/rfc7517)
- [RFC 8725：JSON Web Token Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
- [Spring Authorization Server：SPA + PKCE](https://docs.spring.io/spring-authorization-server/reference/guides/how-to-pkce.html)

下面的视频适合先建立直观认识。本文是结合现行规范整理的复习笔记，不是逐字字幕；视频或旧文章与正式规范冲突时，以正式规范为准：

- [深入浅出 OAuth2 和 OIDC 协议](https://www.bilibili.com/video/BV14RVbzLE3c/)
- [An Illustrated Guide to OAuth and OpenID Connect](https://www.youtube.com/watch?v=t18YB3xDfXI)
- [An Illustrated Guide to OAuth and OpenID Connect（图文版）](https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc)

推荐按下面的顺序学习：

1. 先理解 OAuth2 为什么使用令牌，而不是把用户密码交给第三方应用。
2. 再区分 Authorization Code、Access Token、ID Token 和 Refresh Token。
3. 然后学习 OIDC、PKCE、JWT 与 JWKS 各自解决什么问题。
4. 最后把 state、nonce、CSRF、CORS、XSS 和 HTTPS 放在一起比较。

先记住六句话：

1. OAuth2 主要解决委托授权问题。
2. OIDC 在 OAuth2 之上补充用户身份认证。
3. Access Token 用于访问 API，ID Token 用于向客户端说明用户是谁。
4. PKCE 把授权码绑定到发起请求的客户端实例；它不能代替 HTTPS，但在满足 RFC 9700 条件时也能承担回调 CSRF 防护。
5. JWT 是令牌格式；资源服务器常通过公开 JWKS 取得验签公钥。
6. 登录成功只代表身份已确认，不代表拥有所有业务数据的权限。

## 2. OAuth2 为什么出现

假设一个应用需要读取用户存放在另一个系统中的数据。最直接但最危险的做法，是让用户把目标系统的账号和密码交给这个应用。

这种做法有几个明显问题：

- 应用获得的权限通常过大；
- 用户无法只授权某一小部分能力；
- 密码泄露后影响整个账号；
- 用户很难单独撤销某一个应用的访问权限；
- 密码一旦修改，所有依赖它的应用都会失效。

OAuth2 的核心思路是：

> 用户不把密码交给客户端，而是由授权服务器签发一个权限受限且会过期的令牌。

令牌能否立即撤销取决于实现：不透明 Token 可以通过服务端状态失效；自包含 JWT 如果没有黑名单、内省或其他状态检查，通常会一直有效到自身过期时间。

因此，OAuth2 首先是一套授权协议。它规定客户端怎样取得授权并获取令牌，以及资源服务器怎样依据令牌决定是否允许访问 API。代表用户的流程可能需要用户同意；Client Credentials 等机器流程没有终端用户参与。

### 2.1 认证与授权不是一回事

- **Authentication，认证**：确认当前主体是谁。
- **Authorization，授权**：确认这个主体被允许做什么。

先认证再授权是常见顺序，但两者不能合并成一个判断。账号密码正确只说明身份校验通过；接口权限和业务数据权限仍要单独判断。

## 3. 四个基本角色

| 角色 | 含义 | 常见例子 |
| --- | --- | --- |
| Resource Owner | 资源所有者，通常就是用户 | 某个账号的拥有者 |
| Client | 希望代表用户访问资源的应用 | Web、H5、桌面端、移动 App |
| Authorization Server | 处理授权并签发令牌；用户流程认证用户，机器流程认证客户端 | 统一身份与授权中心 |
| Resource Server | 保存业务数据并接受 Access Token 的 API | 用户、订单、文件服务 |

同一个系统可以同时承担授权服务器和资源服务器，但理解协议时仍要把两个职责分开：

- 授权服务器回答“能否签发令牌、给谁签发、授予哪些权限”；
- 资源服务器回答“这个令牌能否访问当前 API 或当前业务对象”。

### 3.1 公开客户端与机密客户端

OAuth2 客户端通常分为两类：

| 类型 | 能否安全保存长期秘密 | 常见形态 |
| --- | --- | --- |
| Public Client | 不能 | 纯浏览器 SPA/H5、原生移动 App |
| Confidential Client | 能 | 有受控服务端的 Web 应用、后端服务 |

安装到用户设备上的代码可以被分析，浏览器代码也可以被查看，因此不能把写进 App 或 JavaScript 的 Client Secret 当作秘密。

### 3.2 浏览器应用的三种架构

RFC 10017 把浏览器 OAuth 应用归纳为三种架构，并按安全性从高到低排列：

| 架构 | Token 放在哪里 | 浏览器怎样访问 API | 主要取舍 |
| --- | --- | --- | --- |
| Backend for Frontend（BFF） | Access/Refresh Token 都留在受控后端 | 浏览器带安全 Cookie 请求 BFF，由 BFF 代理 API | 安全性最高，但后端要维护 Session、CSRF 和严格的代理白名单 |
| Token-mediating Backend | Refresh Token 留在后端，Access Token 会交给浏览器 | 浏览器持 Access Token 直调资源服务器 | 比 BFF 简单，但恶意 JavaScript 仍可能窃取 Access Token |
| Browser-based OAuth Client | Token 和 OAuth 流程都在浏览器 | 浏览器直接带 Access Token 调 API | 部署最简单，但面对 XSS 时 Token 暴露面最大 |

纯浏览器客户端仍应使用 Authorization Code + PKCE，不能退回 Implicit Grant。对于业务系统、敏感应用或处理个人数据的应用，
RFC 10017 强烈推荐 BFF。BFF 使用 Cookie 后，必须重新认真处理 Session、Cookie、CSRF 和代理目标限制。

Spring Authorization Server 官方 SPA 指南也把 BFF 作为直接暴露公共客户端的替代方案。

### 3.3 Client ID 与 Client Secret

- **Client ID** 是客户端的公开标识，用于告诉授权服务器“谁在发起请求”。
- **Client Secret** 是机密客户端用于证明自身身份的凭据，只应保存在可信服务端。

Client Secret 不是用户密码，也不能证明当前终端用户是谁。

## 4. 常见协议参数

### 4.1 Redirect URI

授权服务器完成用户认证和授权后，把浏览器重定向回客户端的地址。

### 4.2 Response Type

它表示客户端希望授权端点返回什么。Authorization Code 流程通常请求 code。

### 4.3 Scope

Scope 表示客户端申请的权限范围，例如读取资料、写入资料等。

### 4.4 Consent

Consent 是授权服务器让用户确认客户端正在申请哪些权限。

### 4.5 Authorization Code

Authorization Code 是短期、一次性的中间凭据。客户端先从浏览器重定向中收到授权码，再通过独立的令牌端点请求把它兑换成令牌。

## 5. Authorization Code + PKCE

### 5.1 使用 state 的推荐示例流程

1. 客户端生成高熵随机字符串`code_verifier`。
2. 客户端根据`code_verifier`计算`code_challenge`。
3. 客户端把 code_challenge、redirect_uri、scope 和本例使用的 state 等参数发送到授权端点。
4. 授权服务器在浏览器中完成用户认证，并在需要时完成授权确认。
5. 授权服务器把浏览器重定向回客户端，同时返回一次性 code 和原来的 state。
6. 客户端先校验本例使用的 state。
7. 客户端把 code、redirect_uri 和原始 code_verifier 发送到令牌端点。
8. 授权服务器验证成功后签发相应令牌。

这是一条便于入门理解、显式使用 state 的流程。回调 CSRF 的具体防护组合并非永远固定，PKCE、state 和 OIDC nonce 的适用条件见 5.4 节。

### 5.2 PKCE 的计算关系

推荐使用 S256：

~~~text
code_challenge = BASE64URL(SHA256(code_verifier))
~~~

授权请求只携带 code_challenge，兑换令牌时才提交 code_verifier。截获授权码的一方如果没有原始 verifier，就不能完成兑换。

### 5.3 PKCE 解决什么问题

PKCE 主要降低授权码被截获后遭冒用的风险，尤其适合无法安全保存 Client Secret 的公开客户端。

PKCE 与客户端认证不是互斥方案：

- 使用 Authorization Code 的公开客户端必须使用 PKCE；
- 机密客户端仍推荐在客户端认证之外使用 PKCE。

### 5.4 state、nonce 与 PKCE 的区别

| 机制 | 主要保护对象 | 核心作用 |
| --- | --- | --- |
| PKCE | Authorization Code | 防止授权码截获或注入；确认授权服务器支持并正确执行 PKCE 时，也可承担回调 CSRF 防护 |
| state | 授权请求和回调 | 保存并校验应用状态；没有可靠 PKCE 或 OIDC nonce 时，用一次性 state 防回调 CSRF |
| nonce | OIDC ID Token | 把 ID Token 与本次认证请求绑定，降低重放、授权码注入和回调 CSRF 风险 |

三者验证位置不同，并不是所有流程都必须机械地同时使用。客户端必须确保回调 CSRF 得到防护，并根据所用协议、SDK 和应用状态选择正确组合；只要使用了 state 或 nonce，就必须校验返回值。授权端点、Token 端点和 API 应使用 HTTPS。
原生 App 回调按 RFC 8252 可采用 App-claimed HTTPS、基于受控域名反写的 private-use URI scheme，或 loopback IP；
只有 loopback 回调允许使用 HTTP，不能把这个例外扩大到公网地址。

### 5.5 不再使用的授权方式

根据 RFC 9700：

- **Resource Owner Password Credentials Grant（Password Grant）不得再使用。** 它让客户端直接接触用户密码，
  扩大凭据泄漏面，也难以支持多因素认证、Passkey 等现代认证方式。
- **Implicit Grant 不应继续用于签发 Access Token。** Access Token 不应出现在浏览器重定向 URL 中；
  浏览器和原生 App 应使用 Authorization Code + PKCE。

第一方 App 提供“用户名密码登录接口”并不自动等于 Password Grant。是否属于OAuth2 Grant，要看它是否实现OAuth2 Token Endpoint 的 grant 协议。自有接口仍必须评估密码暴露面、限流、MFA 扩展和会话安全。

原生 App 一旦采用 OAuth2/OIDC 授权流程，应遵循 RFC 8252 使用外部用户代理，例如系统浏览器或安全的系统认证会话，而不是在 App 内嵌 WebView 中收集授权服务器密码。

## 6. OAuth2 与 OIDC

### 6.1 OAuth2 主要回答授权问题

OAuth2 关注的是：

- 客户端能否获得 Access Token；
- Token 允许访问哪些资源；
- Token 何时过期；
- 资源服务器如何接受和校验 Token。

只拿到 OAuth2 Access Token，不代表客户端已经得到一套标准化、可信的用户登录信息。

### 6.2 OIDC 补充身份认证

OpenID Connect，简称 OIDC，是构建在 OAuth2 之上的身份层。

客户端要发起 OIDC 认证，就要在授权请求中加入 openid scope；授权服务器随后可以签发 ID Token。OIDC 主要回答：

> 当前完成认证的用户是谁，这次认证结果是否可以被客户端信任？

常见 OIDC 能力包括：

- ID Token；
- Discovery 元数据；
- UserInfo 端点；
- 标准 Claims；
- 登录请求与结果之间的 nonce 绑定。

### 6.3 OIDC 与单点登录

OIDC 可以作为单点登录的协议基础，但“用了 OIDC”不等于“自动拥有完整单点登录”。

真正的单点登录还依赖授权服务器会话、Cookie 策略、域名、客户端注册、退出策略和产品交互。

## 7. 各类凭据与登录会话

| 材料 | 主要用途 | 是否直接调用业务 API |
| --- | --- | --- |
| Authorization Code | 一次性兑换令牌 | 否 |
| Access Token | 访问资源服务器 API | 是 |
| ID Token | 客户端识别本次登录用户 | 否 |
| Refresh Token | 获取新的 Access Token | 否 |
| 浏览器 Session Cookie | 维持授权服务器浏览器会话 | 不是 Bearer Token |

### 7.1 Access Token

Access Token 是发给资源服务器消费的访问凭据。OAuth2 并未规定它必须采用 JWT：它既可以是自包含 JWT，也可以是不透明随机值。如果采用 JWT，资源服务器至少应检查：

- 签名与允许的算法；
- issuer；
- audience；
- 过期时间和生效时间；
- 当前接口要求的 scope 或 authority。

如果采用不透明 Token，资源服务器通常通过令牌内省或服务端会话查询取得并校验这些状态，而不是自行解析 JWT。

### 7.2 ID Token

ID Token 是发给客户端消费的身份声明。常见 Claims 包括：

- iss：签发者；
- sub：用户的稳定标识；
- aud：接收该 ID Token 的客户端；
- exp：过期时间；
- iat：签发时间；
- nonce：与认证请求绑定的随机值。

客户端不能只把 ID Token 解码后就相信其中内容。客户端或成熟的 OIDC SDK 还应验证签名与允许的算法、iss、aud、exp，以及认证请求中使用的 nonce；存在多 audience 等场景时还要按协议检查 azp。

验证通过的 ID Token 仍不能当作访问普通业务 API 的 Access Token。

### 7.3 Refresh Token

Access Token 通常较短命。Refresh Token 可以在不要求用户重新输入凭据的情况下换取新的 Access Token。

Refresh Token 必须在传输和存储中得到严格保护，不能当作 Bearer Token 调用业务 API。RFC 9700 要求给公开客户端签发Refresh Token 时，使用发送方约束或 Refresh Token 轮换来检测重放；采用轮换时，发现旧值重放后应撤销仍有效的关联凭据。

如果 Refresh Token 由服务端生成并以不透明随机值表示，数据库只保存不可逆摘要可以降低数据库泄漏后的直接滥用风险；
这是一种实现策略，不是 OAuth2 规定的唯一 Token 格式。对于浏览器客户端，RFC 10017 还要求 Refresh Token 每次轮换或采用发送方约束，并设置最大总寿命或闲置超时；轮换不能越过首枚 Token 已设定的到期点。具体时长、会话列表和主动退出能力再按产品风险设计。

## 8. Client Credentials

Client Credentials 用于“服务证明自己是谁”，适合没有终端用户参与的机器间调用。

它签发的是服务身份令牌，而不是用户登录令牌。因此：

- 不应把某个普通用户的角色偷偷放进服务令牌；
- Scope 应表达服务被允许执行的能力；
- Client Secret 只能保存在可信后端；可行时可以采用 mTLS 或 private_key_jwt 等非对称客户端认证；
- 浏览器、H5 和原生 App 不适合保存这种 Secret。

## 9. JWT、RS256 与 JWKS

### 9.1 JWT 是什么

常见的签名 JWT 使用 JWS Compact Serialization，由三部分组成：

~~~text
Header.Payload.Signature
~~~

- Header 描述令牌类型、签名算法、密钥编号等；
- Payload 保存 Claims；
- Signature 用于验证内容是否被篡改以及签发者是否持有对应密钥。

这种签名 JWT 的 Header 和 Payload 只是 Base64URL 编码，不是加密。JWT 也可以使用 JWE 加密表示，
但不能因为名称是 JWT 就假定内容保密。普通签名 JWT 中不要放密码、私钥或其他不应被客户端看到的秘密。

### 9.2 RS256 为什么适合多服务

RS256 使用 RSA 私钥签名、RSA 公钥验签：

- 签发方独占私钥；
- 资源服务器只拿公钥；
- 资源服务器即使被攻破，也不能仅凭公钥伪造令牌。

对称签名则要求签发方和验证方共享同一秘密，验证方数量增加时，秘密扩散风险也会增加。

### 9.3 JWKS 是什么

JWKS 通常指 JWK Set，即包含一个或多个 JSON Web Key 的 JSON 文档。JWK Set 本身不保证其中只有公钥；
对外提供的验签 JWKS 端点才应只发布公钥材料。

资源服务器通常这样验签：

1. 读取 JWT Header 中的 kid；
2. 从 JWKS 中找到相同 kid 的公钥；
3. 使用公钥校验签名；
4. 继续校验 issuer、audience、时间和权限声明。

公开验签 JWKS 不得出现 RSA 私钥参数。

### 9.4 为什么需要 kid

kid 是密钥编号。密钥轮换期间，JWKS 可以同时发布新旧公钥，资源服务器依据 JWT 中的 kid 选择正确公钥，因此旧令牌可以在合理过渡期内继续验证。

## 10. Scope、Role、Authority 与 Audience

| 概念 | 回答的问题 |
| --- | --- |
| Scope | 客户端或令牌被授予了哪些能力 |
| Role | 用户在业务系统中具有什么角色 |
| Authority | 安全框架最终用于授权判断的权限字符串 |
| Audience | 这个 Token 预期由哪个客户端或资源服务器消费 |

它们不能混成一个概念：

- Scope 不等于 Role；
- Role 不自动拥有所有业务对象；
- Audience 不表示具体操作权限；
- 通过签名校验不代表一定有权执行当前操作。

一个可靠的资源服务器往往要分层判断：

1. Token 是否可信且仍然有效；
2. Token 是否签发给当前资源服务器；
3. 当前主体是否拥有所需 scope、role 或 authority；
4. 当前主体是否拥有目标业务对象，或是否满足更细的领域规则。

## 11. CSRF 与相关安全机制

### 11.1 CSRF 是什么

CSRF 是 Cross-Site Request Forgery，中文常译为跨站请求伪造。

典型场景是：

1. 用户已经登录某网站，浏览器保存了 Session Cookie；
2. 用户又打开攻击者页面；
3. 攻击者页面诱导浏览器向已登录网站提交请求；
4. 浏览器自动携带 Cookie；
5. 如果服务端无法判断请求是否由可信页面发起，就可能执行用户并不知情的操作。

### 11.2 CSRF Token

服务端可以向可信页面发放攻击者无法读取的随机 Token。修改状态的请求必须同时携带 Cookie 和该 Token，服务端校验匹配后才处理。

SameSite Cookie、Origin 或 Referer 校验可以形成额外防线，但应结合具体浏览器和部署环境评估。

### 11.3 Bearer Token 接口是否需要 CSRF

如果 API 只从 Authorization 请求头读取 Bearer Token，而且浏览器不会自动附加该Token，传统 Cookie 型 CSRF 风险通常较低。

但只要同一应用仍使用 Cookie Session、表单登录或浏览器授权流程，就不能因为“系统也使用 JWT”而全局关闭 CSRF。应按过滤链和具体端点分析凭据是否会被浏览器自动携带。

### 11.4 常见机制对照

| 机制 | 主要防范的问题 |
| --- | --- |
| CSRF Token | 利用自动携带 Cookie 的跨站伪造请求 |
| state | 保存应用状态；在需要时防 OAuth2 回调 CSRF |
| nonce | OIDC ID Token 重放、授权码注入和回调 CSRF |
| PKCE | 授权码截获或注入；满足 RFC 9700 条件时也可防回调 CSRF |
| CORS | 浏览器中的跨源脚本读取或调用策略 |
| HTTPS | 网络传输被窃听或篡改 |
| XSS 防护 | 恶意脚本读取页面数据或以当前页面身份操作 |

CORS 不是身份认证，也不能代替 CSRF、权限校验或 HTTPS。

## 12. 一条完整的标准主线

下面用抽象流程串起这些概念：

~~~text
用户
  │
  │ 在客户端发起登录
  ▼
客户端生成 state、nonce、code_verifier
  │
  │ 浏览器访问授权端点，携带 code_challenge
  ▼
授权服务器认证用户并处理授权
  │
  │ 回调客户端，返回 code 和 state
  ▼
客户端校验 state，并用 code + code_verifier 换 Token
  │
  ├── ID Token：客户端确认用户身份
  │
  ├── Access Token：调用资源服务器
  │
  └── Refresh Token：在允许时刷新 Access Token
                         │
                         ▼
资源服务器通过 JWKS 获取公钥，校验签名、issuer、audience、时间和权限
~~~

图中 ID Token、Refresh Token 和 nonce 是否出现，取决于请求是否使用 OIDC 以及授权服务器的客户端与令牌策略；
通过 JWKS 本地验签这一段则适用于 JWT Access Token，不透明 Access Token 通常改用内省或服务端查询。

## 13. 常见误区

### 13.1 “OAuth2 就是登录协议”

不准确。OAuth2 主要处理授权；需要标准化用户登录身份时，通常使用 OIDC。

### 13.2 “JWT 加密了所有数据”

不准确。常见 JWT 是签名而非加密，Payload 可以被读取。

### 13.3 “拿到 ID Token 就能访问 API”

不应该。ID Token 的接收者是客户端；业务 API 应接受为资源服务器签发的 Access Token。

### 13.4 “有 PKCE 就一定不需要 state”

不能一概而论。RFC 9700 允许在确认授权服务器正确支持 PKCE 时依赖 PKCE 防回调 CSRF；但如果客户端还要携带
并校验应用状态，仍可使用 state。没有可靠 PKCE 或 OIDC nonce 时，必须使用与用户代理会话绑定的一次性 state。

### 13.5 “公开客户端也可以内置 Client Secret”

不安全。用户可控制的运行环境无法可靠保存长期共享秘密。

### 13.6 “验签成功就有全部权限”

不准确。验签只是确认 Token 的可信性，仍需校验 audience、时间、权限和业务对象所有权。

### 13.7 “用了 JWT 就可以关闭所有 Session 和 CSRF”

不准确。浏览器登录和授权流程仍可能依赖 Session Cookie；CSRF 是否需要保护取决于凭据的携带方式和端点用途。

## 14. 自测题

1. OAuth2 与 OIDC 分别主要解决什么问题？
2. Authorization Code 为什么不能直接调用业务 API？
3. Access Token 和 ID Token 的接收者有什么不同？
4. 为什么 SPA 和原生 App 不能安全保存 Client Secret？
5. code_verifier 与 code_challenge 有什么关系？
6. PKCE、state 和 nonce 分别在哪里校验，什么条件下可以承担回调 CSRF 防护？
7. JWT 为什么不适合存放密码？
8. 用于验签的公钥 JWKS 为什么可以公开，RSA 私钥为什么不能公开？
9. Resource Server 验证 JWT 时，为什么不能只验签名？
10. 登录成功后，为什么还要做业务对象所有权检查？

参考答案可以浓缩成下面五句话：

1. OAuth2 管授权，OIDC 补身份认证。
2. Authorization Code 是一次性中间凭据，Access Token 才用于 API。
3. PKCE、state、nonce 验证位置不同，应按协议与客户端场景组合，不能照抄固定公式。
4. JWT 负责承载 Claims，JWKS 负责让验证方安全取得公钥。
5. 认证、协议权限和业务数据权限是三层不同的判断。
