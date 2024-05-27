# JWT

整合Spring Security实现JWT资源访问的认证和权限控制。

- 实现注册接口，创建新用户
- 实现登录接口，用于下发JWT Token
- 使用JWT Filter验证带有Token的请求访问头
- 利用Spring Security保护应用的资源API

SpringBoot Security

- 使用MyBatisX插件生成数据访问层的代码
- 使用Spring Security实现用户登录注册
- Jwt跨域认证

## Spring Security

Spring Security整体架构：

![image-20240525202632689](assets/image-20240525202632689.png)

SecurityFilter有下面几个主要的类

- AuthenticationFilter
- AuthenticationManager
- UserDetailsService
- SecurityContext

通过AuthenticationFilter拦截用户请求并提取认证信息（用户名、密码、token），然后调用AuthenticationManager处理认证逻辑，认证逻辑会调用UserDetailsService来加载用户的详情信息（密码，用户名等），一旦认证成功，用户的信息会被设置到SecurityContext中，供后续的请求访问。

整个流程确保了应用的安全性，通过对用户的身份验证和权限校验，来决定用户是否可以访问应用中特定的资源。

## JWT

jwt是一种开放的标准，定义了一种紧凑且自包含的方式，用于在各方之间以json对象的形式来安全的传输信息。

jwt由下面三个部分构成：

- Header头部
- payload载荷
- signature签名

Header包含令牌的类型和使用的签名算法

payload包含过期时间

signature是对header和signature的数字验证，验证消息的发送者是谁和**确保消息没有被篡改**。由头部指定的签名算法和密钥生成。

因为JWT的信息是自包含的，非常适合跨域认证的场景，客户端在登录之后会收到JWT的一个token，之后每次请求通过http头部来带上这个token，服务器来验证签名来确认用户是否有权限。

## 登陆注册

添加Spring Security和JWT的依赖：
