# OAuth2 与 OIDC：从委托授权到安全登录

本文讲协议原理：应用为什么要跳转登录、授权码怎样换成令牌、各类令牌交给谁，以及浏览器和移动端应守住哪些安全边界。

还不熟悉“认证、授权、Session、Cookie”的读者，先读[认证和授权](认证和授权.md#authentication-authorization)及其中的[浏览器会话](认证和授权.md#session-cookie)。JWT 的结构、签名和字段解释统一见 [JWT 与 JWKS](JWT与JWKS.md#jwt-fields)。

先记住三件事：OAuth2 主要解决“允许应用访问什么”，OIDC（OpenID Connect，建立在 OAuth2 之上的身份层）补充“这次登录的用户是谁”。

<a id="oauth-roles"></a>

## 1. 为什么需要 OAuth2，谁参与其中

假设“相册打印应用”要读取用户在“云相册”中的照片。如果用户直接把云相册密码交给打印应用，打印应用可能得到远超打印所需的权限；泄漏影响整个账号，用户也很难只撤销这一应用的访问权。

OAuth 2.0 是委托授权框架：用户在云相册的授权服务器完成认证与授权，打印应用取得有范围和有效期限制的 Access Token（访问令牌），凭它读取允许访问的资源，无需接触用户的云相册密码。机器调用也可以使用 OAuth2，但不一定有用户参与。[RFC 6749 §1](https://www.rfc-editor.org/rfc/rfc6749.html#section-1)

### 1.1 四个基本角色

| 角色 | 职责 | 相册例子 |
| --- | --- | --- |
| Resource Owner，资源所有者 | 有权同意他人访问资源的主体，通常是用户 | 照片所属用户 |
| Client，客户端 | 希望取得授权、调用受保护资源的应用 | 相册打印应用 |
| Authorization Server，授权服务器 | 核实授权请求，必要时认证用户，并签发令牌 | 云相册的授权中心 |
| Resource Server，资源服务器 | 提供受保护的应用程序接口（API），验证令牌并检查访问权限 | 云相册的照片 API |

“客户端”是协议角色，不只指手机或浏览器：Java 后端也可以是 OAuth2 客户端。浏览器经常只是帮用户打开页面、携带重定向结果；真正保存令牌并调用 API 的客户端可能在后端。

“资源”是被保护的数据或能力，不是第五个协议角色。同一系统可以同时承担授权服务器和资源服务器，但“能否发令牌”与“能否读这张照片”仍是不同职责。

### 1.2 公开客户端与机密客户端

| 类型 | 能否可靠保管长期凭据 | 常见形式 |
| --- | --- | --- |
| Public Client，公开客户端 | 不能把随应用分发的秘密可靠地藏起来 | 原生 App、纯浏览器单页应用（Single Page Application，SPA） |
| Confidential Client，机密客户端 | 可以在受控服务端保管凭据并认证自身 | Java 后端、带受控后端的 Web 应用 |

Client ID（客户端标识）是公开编号，告诉授权服务器“哪个应用在申请”；Client Secret（客户端秘密）是机密客户端认证自身的一种凭据，不是用户密码，也不证明当前用户是谁。写进 JavaScript 或 App 安装包的共享 Secret，不能因为代码混淆就变成可信秘密。[RFC 6749 §2.1](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.1)

### 1.3 对应到 Spring Security 的职责

读 Java 代码时，可以先按职责认组件：OAuth2 Client 支持应用发起授权与取得令牌；Authorization Server 支持授权端点和令牌签发；Resource Server 支持 API 验证访问令牌。添加资源服务器支持不会让应用自动获得签发令牌的能力，一个应用也可同时配置多个角色。

具体依赖和配置取决于项目采用的 Spring 版本；[Spring Authorization Server 官方 SPA 指南](https://docs.spring.io/spring-authorization-server/reference/guides/how-to-pkce.html)展示了公开客户端与 PKCE 的配置边界，不应把客户端 Secret 交给浏览器。

<a id="oauth-parameters"></a>

## 2. 读懂授权请求里的常用参数

授权端点是用户通过浏览器完成授权的入口；令牌端点是客户端提交授权码等凭据、取得令牌的接口。两者不是同一个步骤。

| 参数或概念 | 在本流程中的作用 |
| --- | --- |
| `client_id` | 标识已注册的客户端 |
| `redirect_uri` | 授权完成后，把浏览器送回客户端的回调地址 |
| `response_type=code` | 请求授权端点返回授权码 |
| `scope` | 申请的权限范围，多个值用空格分隔；`openid` 表示发起 OIDC 认证 |
| Consent，授权确认 | 用户确认应用申请的能力；是否再次展示页面取决于已有授权与服务端策略 |
| Authorization Code，授权码 | 短期、一次性的中间凭据，只用于兑换令牌，不能直接调用 API |
| `grant_type` | 令牌端点识别本次取令牌方式；例如 `authorization_code` 或 `client_credentials` |

回调地址由客户端注册时约定，不是访问者随意填写的“登录后跳哪里”。授权服务器应精确匹配已注册地址；原生 App 的本机回环回调端口有专门例外，见[原生 App 约束](#native-apps)。登录后返回某个业务页面，应由客户端另行保存、限制为允许的站内路径，不能把回调做成任意网址跳转器。[RFC 9700 §2.1](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1)

`state`、`nonce`、`code_challenge` 和 `code_verifier` 都与本次请求的安全绑定有关，下面放在实际流程中解释。

<a id="pkce"></a>

## 3. 授权码 + PKCE：按实际顺序理解

PKCE 的全称是 Proof Key for Code Exchange，可理解为“兑换授权码时出示一次性证明”。它让拿到授权码的一方还必须持有本次事务保存的原始随机值，降低授权码被截获或注入后的冒用风险。

### 3.1 流程开始前要具备什么

客户端应事先取得 Client ID，注册准确的回调地址，并知道可信授权服务器的端点及支持能力。不要从未经验证的外部输入选择令牌端点，否则可能把凭据发给攻击者。

下面以公开客户端使用 OIDC 为例，同时显式使用 `state`、`nonce` 和 PKCE，便于看清各自的位置；实际实现应交给成熟的 OAuth2/OIDC 客户端库维护事务和校验。纯 OAuth2 授权不使用 OIDC 的 `nonce` 和 ID Token。

### 3.2 一次完整请求

1. **客户端建立本次授权事务。** 分别生成新的、难以猜测的 `state`、`nonce` 和 `code_verifier`，安全绑定到发起流程的浏览器会话或 App 本次操作，设置有效期；不同用户、标签页或登录尝试不能混用同一份状态。
2. **生成 PKCE 挑战。** 客户端用 `S256` 方法从 `code_verifier` 计算 `code_challenge`，暂时保留原始 verifier，不把它放入授权请求。
3. **打开授权页面。** 浏览器访问授权端点，带上 `client_id`、`redirect_uri`、`response_type=code`、`scope`、`state`、`nonce`、`code_challenge` 和 `code_challenge_method=S256`。
4. **授权服务器认证用户并决定授权。** 用户在授权服务器的可信页面完成登录；已有有效会话时可能不必再输密码。需要确认权限时，用户同意或拒绝授权。用户密码不交给申请照片的客户端。
5. **浏览器回调客户端。** 成功时携带一次性 `code` 与原样返回的 `state`；失败时可能携带协议错误。客户端先检查回调对应当前事务，使用本例的 `state` 校验，拒绝不匹配、过期或重复回调。
6. **客户端兑换令牌。** 向可信令牌端点发送 `grant_type=authorization_code`、`code`、相同的 `redirect_uri`、`client_id` 和原始 `code_verifier`。机密客户端还须按注册方式认证自身；PKCE 不替代客户端认证。
7. **授权服务器校验。** 检查授权码是否有效、未被使用、属于该客户端及回调地址，再验证 verifier 与授权请求保存的 challenge 是否匹配；通过后返回 Access Token，本例的 OIDC 成功响应还含 ID Token（身份令牌）。是否返回用于续期的 Refresh Token取决于策略。
8. **分别使用结果。** 客户端验证 ID Token 和本次 `nonce` 后使用身份结果；向资源服务器发请求时使用 Access Token。资源服务器验证令牌，再检查 API 权限和具体照片的访问权。

这解释了“为什么不直接在回调 URL 发 Access Token”：浏览器回调只运输短期的一次性授权码，真正令牌通过独立的令牌端点取得，减少访问令牌进入地址、历史记录和相关泄漏路径的机会。[RFC 9700 §2.1.1–2.1.2](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1.1)

### 3.3 PKCE 的计算与检查点

```text
code_challenge = BASE64URL(SHA256(ASCII(code_verifier)))
```

这里 SHA-256 是摘要算法；Base64URL 是适合放入 URL 的编码，结果不带末尾的 `=` 填充。`code_verifier` 应由密码学安全随机数生成器产生，长度为 43～128 个允许字符；一种标准做法是生成 32 字节随机数后转成不带填充的 Base64URL。[RFC 7636 §4.1–4.2](https://www.rfc-editor.org/rfc/rfc7636.html#section-4.1)

可以把 challenge 想成“先登记证明的摘要”，verifier 是“兑换时出示原件”。

使用授权码流程的公开客户端必须使用 PKCE，机密客户端也推荐使用；选择 `S256`。服务端必须真正校验 verifier，并防止攻击者通过删除 challenge 降级绕过 PKCE。[RFC 9700 §2.1.1](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1.1)

<a id="state-nonce"></a>

### 3.4 state、nonce 和 PKCE 的区别

| 机制 | 谁在哪里检查 | 保护什么 |
| --- | --- | --- |
| `state` | 客户端处理授权回调时检查 | 关联请求与回调；与当前用户代理安全绑定的一次性随机值可防回调 CSRF |
| `nonce` | OIDC 客户端验证 ID Token 时检查 | 把身份结果绑定到这次认证请求，检测重放；满足协议条件时也可防回调 CSRF、授权码注入 |
| PKCE | 授权服务器在令牌端点验证 `code_verifier` | 将授权码兑换绑定到本次发起事务；确认服务端正确支持并执行时，也可承担回调 CSRF 防护 |

`state` 的基本往返关系如下，尖括号均为每次动态生成或收到的值：

```text
授权请求：...?state=<本次随机值>
授权回调：...?code=<一次性授权码>&state=<原来的随机值>
```

客户端不能只检查 `state`“非空”或“在全局表里存在”，还要检查它属于当前会话或授权事务、未过期且未使用；验证后使其失效。错误回调也应与原请求关联。可以在客户端保存 `state → 允许的登录后页面` 的映射，但不要把密码、令牌等秘密塞进会经过浏览器的 `state`。

三者不是机械叠加的固定公式。客户端必须防回调 CSRF：确认 PKCE 防护可靠时可以依赖 PKCE；OIDC 可使用正确绑定并校验的 `nonce`；没有这些可靠防护时，必须使用与当前用户代理绑定的一次性 `state`。发送了 `nonce` 就要检查 ID Token 中的对应值，不能换到令牌就提前建立登录状态。[RFC 9700 §2.1、§4.7](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1)、[OIDC Core §3.1.3.7](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation)

PKCE、state、nonce 都不替代 HTTPS，也无法让已经被恶意脚本控制的应用变安全。

<a id="native-apps"></a>

### 3.5 原生 App 的约束

原生 App 使用 OAuth2/OIDC 时，必须通过外部用户代理完成授权，例如系统浏览器或满足隔离要求的系统认证会话；不要在 App 可读取页面、密码或 Cookie 的内嵌 WebView 中完成授权。界面显示在 App 内，不一定就是 WebView，关键是 App 能否读取或改写认证环境。[RFC 8252 §4、§8.12](https://www.rfc-editor.org/rfc/rfc8252.html#section-4)

回调可按平台能力使用已验证归属的 HTTPS 链接、基于受控域名反写的私有 URI scheme，或本机 loopback IP（回环地址）。公网通信使用 HTTPS；HTTP 回调的例外仅适用于原生客户端的本机回环地址，不适用于公网网站。[RFC 8252 §7](https://www.rfc-editor.org/rfc/rfc8252.html#section-7)、[RFC 9700 §2.6](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.6)

### 3.6 不采用的 Grant

Grant 是协议规定的授权方式，不是“所有登录接口”的统称。现行安全基线要求：

- Resource Owner Password Credentials Grant（Password Grant，资源所有者密码凭据授权）不得使用；它把用户密码交给客户端，也难以适配多因素认证等交互。
- 不应使用 Implicit Grant（隐式授权）在授权响应中签发 Access Token。浏览器和原生 App 应采用授权码 + PKCE 主线。

这些约束来自 [RFC 9700 §2.4](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.4) 和 [§2.1.2](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1.2)。第一方应用的自有密码登录接口，不因接收密码就自动成为 OAuth2 Password Grant，也不因改名就天然安全；其密码暴露面、限流、多因素认证和会话管理仍需独立设计。Java 的密码核验职责见[标准认证链](认证和授权.md#password-authentication)。

<a id="oidc"></a>

## 4. OIDC 怎样补上“用户是谁”

OpenID Connect（OIDC）是在 OAuth2 之上的身份层。OAuth2 Access Token 表示访问授权，不能单凭“拿到了 Access Token”就认定客户端获得了标准的用户登录证明。

客户端在授权请求的 `scope` 中加入 `openid`，即发起 OIDC 认证。沿用授权码流程时，成功的令牌响应包含 ID Token（身份令牌），由客户端验证后了解本次认证结果。OIDC 中，提供认证结果的一方称为 OpenID Provider（OP，身份提供方），依赖这个结果的客户端称为 Relying Party（RP，依赖方）。[OIDC Core §1、§3.1](https://openid.net/specs/openid-connect-core-1_0.html#Introduction)

还会遇到两个入口：Discovery（发现元数据）告诉客户端可信提供方的端点和能力；UserInfo 是用 Access Token 获取已授权用户资料的端点。取得 UserInfo 后，其中的用户主体标识必须与已验证 ID Token 的主体一致，不能只按昵称或邮箱拼接身份。[OIDC Core §5.3.2](https://openid.net/specs/openid-connect-core-1_0.html#UserInfoResponse)

ID Token 的用途、接收者和本次请求绑定必须同时正确；“能 Base64 解码”不等于“身份可信”。字段含义与校验步骤统一见 [JWT 与 JWKS：验证流程](JWT与JWKS.md#jwt-validation)，使用成熟 OIDC 客户端库完成验证，不自己拼装一套只检查签名的登录协议。

<a id="tokens"></a>

## 5. 授权码与三种 Token，分别交给谁

| 凭据 | 接收者 | 用途 |
| --- | --- | --- |
| Authorization Code | 授权服务器的令牌端点 | 一次性兑换令牌 |
| Access Token | 预期的资源服务器 | 在授权范围内调用 API |
| ID Token | 发起 OIDC 认证的客户端 | 验证本次用户身份结果 |
| Refresh Token | 授权服务器的刷新入口 | 换取新的 Access Token |

Access Token 不一定是 JWT，OAuth2 不强制其编码格式；ID Token 是 OIDC 定义的 JWT。前者可以是不透明随机值，由资源服务器按部署协议核验。Cookie 所维持的浏览器会话也不等于这些令牌，见[Session 与 Cookie](认证和授权.md#session-cookie)。

### 5.1 Refresh Token 为什么需要额外保护

Access Token 通常有效期较短。Refresh Token 让客户端在获准的会话期限内取得新的 Access Token，避免每次过期都打断用户重新登录；是否签发它由服务端按风险决定，不是所有流程都会返回。

Refresh Token 泄漏可能让攻击者持续取到新令牌，因此必须保护传输和存储。对公开客户端，授权服务器必须采用发送方约束或轮换机制检测重放：

- **发送方约束**：除令牌外，还要求出示与该客户端实例绑定的密码学证明；不是只比较一个容易伪造的设备名称。
- **轮换**：每次刷新发出新 Refresh Token、使旧值失效并**保留关联关系**。再次使用旧值说明可能泄漏，服务端撤销关联的活动 Refresh Token，要求重新取得授权，不能只返回错误后让攻击者继续刷新。

这是 [RFC 9700 §4.14](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.14) 的重放防护要求。客户端也应协调并发刷新，避免多个请求同时拿旧值刷新而被判为重放。

浏览器公开客户端若获发 Refresh Token，还应设置最大总寿命或闲置超时；如果首枚令牌预设了到期时间，轮换不能把后续令牌延长到该时刻以后。[RFC 10017 §6.3.2.3](https://www.rfc-editor.org/rfc/rfc10017.html#section-6.3.2.3)

不透明随机 Refresh Token 在服务端只存不可逆摘要，是降低数据库泄漏后直接盗用风险的一种实现策略，不是 OAuth2 规定的唯一格式。具体存储、撤销粒度和到期策略应在实现文档中明确，不把某个项目的固定天数当作协议要求。

<a id="client-credentials"></a>

## 6. Client Credentials：服务代表自己调用

Client Credentials（客户端凭据授权）适合没有终端用户参与的机器间调用，例如定时任务读取被授权的统计数据。它只适用于机密客户端，不能把 Secret 分发到浏览器或原生 App 中。[RFC 6749 §4.4](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4)

流程只有三步：

1. 服务向令牌端点提交 `grant_type=client_credentials` 和所需 `scope`，按注册方式证明自身身份。
2. 授权服务器核对客户端凭据与允许的能力，返回 Access Token。
3. 服务携带 Access Token 调用目标 API；资源服务器按服务身份、权限范围和业务规则授权。

没有用户登录、浏览器回调、授权码或 PKCE；也不应签发 Refresh Token，服务需要新令牌时重新认证取令牌。[RFC 6749 §4.4.3](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4.3)

服务令牌不能冒充普通用户身份或偷偷继承其角色。Client Secret 只留在可信后端；条件允许时可采用证书或私钥签名等非对称客户端认证方式，避免共享秘密带来的泄漏风险。[RFC 9700 §2.5、§4.15](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.5)

<a id="permissions"></a>

## 7. scope、role、authority、audience 不是同一件事

| 概念 | 主要回答什么 | 示例含义 |
| --- | --- | --- |
| Scope，权限范围 | 此次授权允许客户端做什么 | `photos:read` 允许读取照片能力 |
| Role，业务角色 | 主体在业务中处于什么角色 | 普通用户、内容管理员；具体模型由应用定义 |
| Authority，框架权限项 | 安全框架最终用什么权限值做判断 | Spring Security 可将 scope 或角色映射为权限字符串 |
| Audience，预期接收方 | 这个令牌应交给谁消费 | Access Token 面向某资源服务器，ID Token 面向某客户端 |

Scope 不等于角色，角色也不自动意味着拥有所有业务对象；Audience 只限定接收方，不表示“可读”“可写”。`aud` 等 JWT 字段的完整解释见[字段说明](JWT与JWKS.md#jwt-fields)，这里关注其授权含义。

例如请求删除某张照片，资源服务器应依次判断：令牌可信且有效吗？是发给本站的吗？有删除能力吗？这张照片属于当前用户，或者满足管理员规则吗？任一步失败都不能继续。OAuth2 提供授权框架，但不会替应用自动完成对象所有权判断。[RFC 9700 §2.3](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.3)

<a id="csrf"></a>

## 8. CSRF：区分普通业务请求与授权回调

CSRF 是 Cross-Site Request Forgery（跨站请求伪造）。关键不是“请求从哪一页发出”这么简单，而是攻击者借用了浏览器会自动携带的认证凭据。

### 8.1 Cookie 会话下的业务 CSRF

典型过程是：用户登录可信站点后打开攻击者页面；攻击者诱导浏览器向可信站点提交修改操作；浏览器可能自动附带该站点 Cookie。如果服务端只看 Cookie 就执行，用户的登录身份被用于非本人意图的请求。

常见防护是 CSRF Token：让可信页面取得不可预测的校验值，修改状态的请求必须额外提交它，服务端核验后才执行。SameSite Cookie、Origin/Referer 来源检查可以组成额外防线，但不能跳过具体浏览器与部署条件分析。需要 Cookie 基础时回看[浏览器会话](认证和授权.md#session-cookie)。[Spring Security：CSRF](https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html)

若 API 仅接受由客户端主动设置的 `Authorization` 请求头，且不接受浏览器自动附加的其他认证凭据，传统 Cookie 型 CSRF 风险通常较低。是否叫“REST API”或是否无状态不是豁免依据；如果把认证令牌放入自动发送的 Cookie，仍需分析 CSRF，不能仅凭“用了 JWT”全局关闭防护。

### 8.2 OAuth2 回调 CSRF

攻击者也可能把自己的授权回调送到受害者浏览器，让客户端把受害者错误地关联到攻击者账号。防护重点是“返回结果确实属于本次授权事务”，对应 [state、nonce、PKCE](#state-nonce)，不能照搬普通业务表单的处理方式后就假定安全。

授权服务器自己的登录表单、授权确认页面以及采用 Cookie 会话的 BFF，仍有各自的业务 CSRF 边界。回调有 `state`，不意味着整个站点都不再需要 CSRF Token。

### 8.3 不能相互替代的机制

HTTPS 保护传输；CSRF 防护确认请求意图与会话或事务的绑定；XSS（Cross-Site Scripting，跨站脚本）防护阻止恶意脚本在可信页面执行。恶意脚本如果已控制页面，可能盗取可读令牌，或直接替用户操作。

CORS 的定义和配置统一见[网关：CORS](网关-认证过滤器-拦截器.md#cors)；它不替代身份认证、CSRF 防护或业务权限校验。不要把“配置了跨域”当成上述安全机制的总开关。

<a id="sso"></a>

## 9. OIDC 与单点登录

Single Sign-On（SSO，单点登录）指用户完成一次认证后，访问多个受信任应用时可以复用认证状态，而不必每个应用重复输入凭据。OIDC 可提供标准协议基础，但“接入 OIDC”不等于“完整 SSO 自动完成”。

一个典型过程是：

1. 用户访问应用 A，被送往身份提供方；完成登录后回到 A。
2. 用户访问应用 B，B 也发起自己的 OIDC 授权请求。
3. 浏览器访问同一身份提供方时，提供方识别已有会话，按策略完成本次认证与授权，再把 B 自己的授权码送回 B。
4. A、B 各自验证本次结果并维护自己的应用会话；不是让 B 直接拿走 A 的 ID Token 或共享 A 的所有 Cookie。

能否无交互完成还取决于提供方会话是否有效、是否需要重新认证或授权确认，以及浏览器 Cookie、域名和客户端配置。OIDC 定义了 `prompt`、`max_age` 等控制交互和认证时效的参数，客户端不能假定已有会话就永远免登录。[OIDC Core §3.1.2.1](https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest)

“退出当前应用”“退出身份提供方”“撤销已签发令牌”是不同动作。单点退出需要明确的会话与协议设计；只删除某个页面的本地令牌，不保证其他应用退出，也不保证尚未到期的 Access Token 立即失效。

<a id="browser-architectures"></a>

## 10. 浏览器应用：令牌放在哪一层

RFC 10017 按安全性由高到低介绍三种架构。差别不在页面用什么前端框架，而在 OAuth2 职责与令牌暴露给哪一层：

| 架构 | 令牌保存在哪里 | 浏览器怎样访问业务 API | 主要代价与风险 |
| --- | --- | --- | --- |
| Backend for Frontend（BFF，面向前端的专用后端） | Access/Refresh Token 都留在受控后端 | 浏览器带会话 Cookie 请求 BFF，由 BFF 携带令牌代理 API | 后端需维护会话、CSRF 防护和严格代理白名单 |
| Token-mediating Backend（令牌中介后端） | 后端保管 Refresh Token，Access Token 交给浏览器 | 浏览器携带 Access Token 直调 API | 前端恶意脚本仍可能取得 Access Token |
| Browser-based OAuth Client（纯浏览器 OAuth 客户端） | OAuth 流程与令牌由浏览器侧处理 | 浏览器自己换令牌并调用 API | 公开客户端必须使用 PKCE；脚本攻击暴露面更大 |

对业务系统、敏感应用和处理个人数据的应用，RFC 10017 强烈推荐 BFF。BFF 不是“加了一个网关就自动完成”：它作为机密客户端处理授权和令牌，且不能让前端指定任意代理目的地，否则可能把令牌转发给攻击者。[RFC 10017 §6.1](https://www.rfc-editor.org/rfc/rfc10017.html#section-6.1)

BFF 减少令牌暴露给浏览器脚本的机会，但不消灭 XSS；恶意脚本仍可能通过已登录浏览器调用 BFF。选择架构后仍需落实输入输出安全、会话保护、CSRF 和业务授权，不能只选一个名称就认定系统安全。

<a id="self-check"></a>

## 11. 自测：能否顺着凭据找到接收者

1. 相册打印例子里，谁是客户端，谁持有用户密码，谁决定能否读取某张照片？
2. 为什么原生 App 中的 Client Secret 不能作为可靠的共享秘密？
3. 授权码为什么不能直接调用 API？拿到授权码的人为什么不一定能换令牌？
4. state、nonce 和 PKCE 分别在哪里校验？它们是否所有流程都必须一起出现？
5. Access Token 和 ID Token 的接收者有什么区别？Refresh Token 能否当 Bearer Token 调普通 API？
6. 为什么通过 `aud` 检查并拥有 `photos:read`，仍不代表能读取所有用户的照片？
7. 机器间调用为什么不应伪装成某个普通用户登录？
8. 为什么 BFF 仍需 CSRF、XSS 防护，退出应用 A 也不一定让应用 B 退出？

核对要点：客户端是打印应用，用户在授权服务器认证，资源服务器落实对象权限；分发到不受控设备的共享秘密可以被提取；授权码只是一次性中间凭据，PKCE 绑定本次兑换；三种绑定机制校验位置和适用条件不同；API 用 Access Token，客户端用 ID Token，刷新只用 Refresh Token；令牌接收方、能力范围、业务对象权限是不同层次；服务身份与用户身份必须区分；BFF 与 SSO 都仍依赖明确的浏览器和会话安全设计。

<a id="references"></a>

## 12. 资料与后续阅读

协议结论以正式规范和官方文档为准：

- [RFC 6749：OAuth 2.0 授权框架](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 9700：OAuth 2.0 安全最佳实践](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 7636：PKCE](https://www.rfc-editor.org/rfc/rfc7636)
- [RFC 8252：原生 App 的 OAuth2](https://www.rfc-editor.org/rfc/rfc8252)
- [RFC 10017：浏览器应用的 OAuth2](https://www.rfc-editor.org/rfc/rfc10017)
- [OpenID Connect Core 1.0（Errata Set 2）](https://openid.net/specs/openid-connect-core-1_0.html)

视频用于建立直观认识，不作为安全结论的规范来源；本文也不是字幕整理：

- [深入浅出 OAuth2 和 OIDC 协议](https://www.bilibili.com/video/BV14RVbzLE3c/)
- [An Illustrated Guide to OAuth and OpenID Connect](https://www.youtube.com/watch?v=t18YB3xDfXI)
- [同一视频的图文版](https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc)

基础专题按职责继续读：[认证与标准密码链](认证和授权.md#password-authentication)、[JWT/JWKS 验证](JWT与JWKS.md#jwt-validation)、[网关与过滤链](网关-认证过滤器-拦截器.md)。

若同时克隆了示例工程，可在项目仓库打开 `hhjava/docs/AUTHENTICATION_GUIDE.md`。项目接口、配置和启动步骤以该实战指南及源码为准，不属于本文的通用协议约定；知识库网页不提供依赖本机目录布局的跨仓库链接。
