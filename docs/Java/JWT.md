# JWT

用户在浏览器输入用户名和密码进行验证，服务器验证通过之后，用户信息在服务器保存，服务器向用户返回唯一的sessionID。

## 认证

认证即用户去访问系统资源时系统要求验证用户的身份信息，身份合法方可继续访问。

常见的用户身份认证的表现形式有：用户名密码登录，微信扫码等方式。

认证通过由认证服务向给用户颁发令牌，相当于访问系统的通行证，用户拿着令牌去访问系统的资源。

### 第三方认证

为了提高用户体验，很多网站有扫码登录的功能，如：微信扫码登录、QQ扫码登录等。扫码登录的好处是用户不用输入账号和密码，操作简便，另外一个好处就是有利于用户信息的共享，互联网的优势就是资源共享，用户也是一种资源，对于一个新网站如果让用户去注册是很困难的，如果提供了微信扫码登录将省去用户注册的成本，是一种非常有效的推广手段。

## 用户授权

用户认证通过后去访问系统的资源，系统会判断用户是否拥有访问资源的权限，只允许访问有权限的系统资源，没有权限的资源将无法访问，这个过程叫用户授权。

比如：用户去发布课程，系统首先进行用户身份认证，认证通过后继续判断用户是否有发布课程的权限，如果没有权限则拒绝继续访问系统，如果有权限则继续发布课程。

## 单点登录

项目基于微服务架构构建，微服务包括：内容管理服务、媒资管理服务、学习中心服务、系统管理服务等，为了提高用户体验性，用户只需要认证一次便可以在多个拥有访问权限的系统中访问，这个功能叫做单点登录。

> 单点登录（Single Sign On），简称为 SSO，是目前比较流行的企业业务整合的解决方案之一。SSO的定义是在多个应用系统中，用户只需要登录一次就可以访问所有相互信任的应用系统。

## Spring Security

认证功能几乎是每个项目都要具备的功能，并且它与业务无关，市面上有很多认证框架，如：Apache Shiro、CAS、Spring Security等。

Spring Security是spring家族的一份子且和Spring Cloud集成的很好，所以选用Spring Security作为认证服务的技术框架。

Spring Security 是一个功能强大且高度可定制的身份验证和访问控制框架，它是一个专注于为 Java 应用程序提供身份验证和授权的框架。

项目主页：https://spring.io/projects/spring-security

Spring cloud Security： https://spring.io/projects/spring-cloud-security

### Spring Security原理

Spring Security所解决的问题就是**安全访问控制**。

对所有进入系统的请求进行拦截，校验每个请求是否能够访问它所期望的资源。

Spring Security对Web资源的保护是靠Filter实现的。

初始化Spring Security时，会创建一个名为`SpringSecurityFilterChain`的Servlet过滤器，类型为`org.springframework.security.web.FilterChainProxy`，它实现了`javax.servlet.Filter`，因此外部的请求会经过此类。

Spring Security过虑器链结构图：

![image-20240911164023286](assets/image-20240911164023286.png)

FilterChainProxy是一个代理，真正起作用的是FilterChainProxy中SecurityFilterChain所包含的各个Filter，同时这些Filter作为Bean被Spring管理，它们是Spring Security核心，各有各的职责，但他们并不直接处理用户的**认证**和**授权**，而是把它们交给了认证管理器（AuthenticationManager）和决策管理器（AccessDecisionManager）进行处理。

spring Security功能的实现主要是由一系列过滤器链相互配合完成。

![image-20240913190122474](assets/image-20240913190122474.png)

下面介绍过滤器链中主要的几个过滤器及其作用：

- **SecurityContextPersistenceFilter**：这个Filter是整个拦截过程的入口和出口（也就是第一个和最后一个拦截器）
  - 请求开始时从配置好的 SecurityContextRepository 中获取 SecurityContext，然后把它设置给 SecurityContextHolder。
  - 在请求完成后将 SecurityContextHolder 持有的 SecurityContext 再保存到配置好的 SecurityContextRepository，同时清除 securityContextHolder 所持有的 SecurityContext。

- **UsernamePasswordAuthenticationFilter**：用于处理来自表单提交的认证。该表单必须提供对应的用户名和密码，其内部还有登录成功或失败后进行处理的 AuthenticationSuccessHandler 和 AuthenticationFailureHandler，这些都可以根据需求做相关改变。
- **FilterSecurityInterceptor**：是用于保护web资源的，使用AccessDecisionManager对当前用户进行授权访问。
- **ExceptionTranslationFilter** 能够捕获来自 FilterChain 所有的异常，并进行处理。但是它只会处理两类异常：AuthenticationException 和 AccessDeniedException，其它的异常它会继续抛出。

**Spring Security的执行流程如下：**

![image-20240913190052291](assets/image-20240913190052291.png)

1. 用户提交用户名、密码被SecurityFilterChain中的`UsernamePasswordAuthenticationFilter`过滤器获取到，封装为请求Authentication，通常情况下是UsernamePasswordAuthenticationToken这个实现类。
2. 过滤器将Authentication提交至认证管理器`AuthenticationManager`进行认证。
3. 认证成功后，`AuthenticationManager`身份管理器返回一个被填充满了信息的（包括上面提到的权限信息，身份信息，细节信息，但密码通常会被移除）`Authentication`实例。
4. `SecurityContextHolder`安全上下文容器将上面填充了信息的`Authentication`，通过`SecurityContextHolder.getContext().setAuthentication(…)`方法，设置到其中。
5. 可以看出AuthenticationManager接口（认证管理器）是认证相关的核心接口，也是发起认证的出发点，它的实现类为ProviderManager。而Spring Security支持多种认证方式，因此ProviderManager维护着一个`List<AuthenticationProvider>`列表，存放多种认证方式，最终实际的认证工作是由AuthenticationProvider完成的。
   1. web表单的对应的AuthenticationProvider实现类为DaoAuthenticationProvider，它的内部又维护着一个`UserDetailsService`负责UserDetails的获取。最终AuthenticationProvider将UserDetails填充至Authentication。

## OAuth2

微信扫码认证，是一种第三方认证的方式，这种认证方式是基于OAuth2协议实现，

OAUTH协议为用户资源的授权提供了一个安全的、开放而又简易的标准。同时，任何第三方都可以使用OAUTH认证服务，任何服务提供商都可以实现自身的OAUTH认证服务，因而OAUTH是开放的。业界提供了OAUTH的多种实现如PHP、JavaScript，Java，Ruby等各种语言开发包，大大节约了程序员的时间，因而OAUTH是简易的。互联网很多服务如Open API，很多大公司如Google，Yahoo，Microsoft等都提供了OAUTH认证服务，这些都足以说明OAUTH标准逐渐成为开放资源授权的标准。

参考：https://baike.baidu.com/item/oAuth/7153134?fr=aladdin

Oauth协议：https://tools.ietf.org/html/rfc6749

下边分析一个Oauth2认证的例子，黑马程序员网站使用微信认证扫码登录的过程：

![image-20240925110310039](assets/image-20240925110310039.png)

1. 用户进入黑马程序的登录页面，点击微信的图标开打微信扫码界面。

   微信扫码的目的是通过微信认证登录黑马程序员官网，黑马程序员网站需要从微信获取当前用户的身份信息才会让当前用户在黑马网站登录成功。

2. 用户授权黑马网站访问用户信息

   资源拥有者扫描二维码表示资源拥有者请求微信进行认证，微信认证通过向用户手机返回**授权页面**。

   询问用户是否授权黑马程序员访问自己在微信的用户信息，用户点击“确认登录”表示同意授权，**微信认证服务器颁发一个授权码给黑马程序员的网站**。

   只有资源拥有者同意微信才允许黑马网站访问资源。

3. 黑马程序员的网站获取到授权码
4. 携带授权码请求**微信认证服务器**申请令牌（此交互过程用户看不到）。
5. 微信认证服务器向黑马程序员的网站响应令牌（此交互过程用户看不到）。
6. 黑马程序员网站携带令牌请求**微信资源服务器**获取资源即用户信息。
7. 资源服务器返回受保护资源即用户信息。
8. 黑马网站接收到用户信息，此时用户在黑马网站登录成功。

接下来认识Oauth2.0的认证流程：

引自Oauth2.0协议rfc6749 https://tools.ietf.org/html/rfc6749

![image-20240925111524146](assets/image-20240925111524146.png)

Oauth2包括以下角色：

1. 客户端

   客户端会携带令牌请求微信获取用户信息，黑马程序员网站即客户端。

   本身不存储资源，需要通过资源拥有者的授权去请求资源服务器的资源，比如：手机客户端、浏览器等。

2. 资源拥有者

   通常用户是用户信息资源的拥有者，也可以是应用程序，即该资源的拥有者。

   A表示 客户端请求资源拥有者授权。

   B表示 资源拥有者授权客户端即黑马网站访问自己的用户信息。

3. 授权服务器（也称认证服务器）

   微信负责认证当前用户的身份，负责为客户端颁发令牌。

   C 客户端即黑马网站携带授权码请求认证。

   D认证通过颁发令牌。

4. 资源服务器

   存储资源的服务器。用户信息，在微信中存储。

   E表示客户端即黑马网站携带令牌请求资源服务器获取资源。

   F表示资源服务器校验令牌通过后提供受保护资源。

### OAuth2的授权模式

Spring Security支持OAuth2认证，OAuth2提供授权码模式、密码模式、简化模式、客户端模式等四种授权模式，微信扫码登录的例子就是基于授权码模式，这四种模式中授权码模式和密码模式应用较多。

### 1、授权码模式

OAuth2的几个授权模式是根据不同的应用场景以不同的方式去获取令牌，最终目的是要获取认证服务颁发的令牌，最终**通过令牌去获取资源**。

授权码模式简单理解是使用授权码去获取令牌，授权码的获取需要资源拥有者亲自授权同意才可以获取。

下图是授权码模式的交互图：

![image-20240925113752687](assets/image-20240925113752687.png)

还以微信扫码登录为例进行说明：

1. 用户打开浏览器。
2. 通过浏览器访问客户端即黑马网站。
3. 用户通过浏览器向认证服务请求授权，请求授权时会携带客户端的URL，此URL为下发授权码的重定向地址。
4. 认证服务向资源拥有者返回授权页面。
5. 资源拥有者亲自授权同意。
6. 通过浏览器向认证服务发送授权同意。
7. 认证服务向客户端地址重定向并携带授权码。
8. 客户端即黑马网站收到授权码。
9. 客户端携带授权码向认证服务申请令牌。
10. 认证服务向客户端颁发令牌。

### 2、密码模式

密码模式相对授权码模式简单，授权码模式需要借助浏览器供用户亲自授权，密码模式不用借助浏览器，如下图：

![image-20240925120249236](assets/image-20240925120249236.png)

1. 资源拥有者提供账号和密码。
2. 客户端向认证服务申请令牌，请求中携带账号和密码。
3. 认证服务校验账号和密码正确颁发令牌。

这种模式十分简单，但是却意味着直接将用户敏感信息泄漏给了client，因此这就说明这种模式只能用于client是我们自己开发的情况下。

**授权码模式适合客户端和认证服务非同一个系统的情况，所以本项目使用授权码模式完成微信扫码认证，采用密码模式作为前端请求微服务的认证方式。**

## 普通令牌的问题

客户端申请到令牌，接下来客户端携带令牌去访问资源，到资源服务器将会校验令牌的合法性。

资源服务器如何校验令牌的合法性？

以OAuth2的密码模式为例进行说明：

![image-20240925140436592](assets/image-20240925140436592.png)

从第4步开始说明：

1、客户端携带令牌访问资源服务获取资源。

2、资源服务远程请求认证服务校验令牌的合法性

3、如果令牌合法资源服务向客户端返回资源。

这里存在一个问题：

就是校验令牌需要远程请求认证服务，客户端的每次访问都会远程校验，执行性能低。

如果能够让资源服务自己校验令牌的合法性将省去远程请求认证服务的成本，提高了性能。如下图：

![image-20240925140551475](assets/image-20240925140551475.png)

如何解决上边的问题，实现资源服务自行校验令牌。

令牌采用JWT格式即可解决上边的问题，用户认证通过后会得到一个JWT令牌，JWT令牌中已经包括了用户相关的信息，客户端只需要携带JWT访问资源服务，资源服务根据事先约定的算法自行完成令牌校验，无需每次都请求认证服务完成授权。

## JWT

JSON Web Token（JWT）是一种使用JSON格式传递数据的网络令牌技术，它是一个开放的行业标准（RFC 7519），它定义了一种简洁的、**自包含**的协议格式，用于在通信双方传递json对象，传递的信息经过数字签名可以被验证和信任，它可以使用HMAC算法或使用RSA的公钥/私钥对来签名，防止内容篡改。

官网：https://jwt.io/

使用JWT可以实现无状态认证

传统的基于session的方式是有状态认证，用户登录成功将用户的身份信息存储在服务端，这样加大了服务端的存储压力，并且这种方式不适合在分布式系统中应用。

如下图，当用户访问应用服务，每个应用服务都会去服务器查看session信息，如果session中没有该用户则说明用户没有登录，此时就会重新认证，而解决这个问题的方法是Session复制、Session黏贴。

![image-20240925141120682](assets/image-20240925141120682.png)

如果是基于令牌技术在分布式系统中实现认证则服务端不用存储session，可以将用户身份信息存储在令牌中，用户认证通过后认证服务颁发令牌给用户，用户将令牌存储在客户端，去访问应用服务时携带令牌去访问，服务端从jwt解析出用户信息。这个过程就是无状态认证。

![image-20240925141207939](assets/image-20240925141207939.png)

JWT令牌的优点：

- jwt基于json，非常方便解析。
- 可以在令牌中自定义丰富的内容，易扩展。
- 通过非对称加密算法及数字签名技术，JWT防止篡改，安全性高。
- **资源服务**使用JWT可不依赖**认证服务**即可完成授权。

缺点：

- JWT令牌较长，占存储空间比较大。

### JWT组成

JWT令牌由三部分组成，每部分中间使用`.`分隔

#### 1、Header头部

头部包括令牌的类型（即JWT）及使用的签名哈希算法（如HMAC SHA256或RSA）

```JSON
 {
  "alg": "HS256",
  "typ": "JWT"
}
```

将上边的内容使用Base64Url编码，得到一个字符串就是JWT令牌的第一部分。

#### 2、Payload载荷

第二部分是负载，内容也是一个json对象，它是存放有效信息的地方，它可以存放jwt提供的信息字段，比如：iss（签发者）,exp（过期时间戳）, sub（面向的用户）等，也可自定义字段。

此部分不建议存放敏感信息，因为此部分可以解码还原原始内容。

最后将第二部分负载使用Base64Url编码，得到一个字符串就是JWT令牌的第二部分。

```JSON
  {
    "sub": "1234567890",
    "name": "456",
    "admin": true
  }
```

#### 3、Signature

第三部分是签名，此部分用于防止jwt内容被篡改。

这个部分使用base64url将前两部分进行编码，编码后使用点（.）连接组成字符串，最后使用header中声明的签名算法进行签名。

  一个例子：

```JSON
  HMACSHA256(
    base64UrlEncode(header) + "." +
    base64UrlEncode(payload),
    secret)
```

- base64UrlEncode(header)：jwt令牌的第一部分。
- base64UrlEncode(payload)：jwt令牌的第二部分。
- secret：签名所使用的密钥。

为什么JWT可以防止篡改？

第三部分使用签名算法对第一部分和第二部分的内容进行签名，常用的签名算法是 HS256，常见的还有md5,sha 等，签名算法需要使用密钥进行签名，密钥不对外公开，并且签名是不可逆的，如果第三方更改了内容那么服务器验证签名就会失败，要想保证验证签名正确必须保证内容、密钥与签名前一致。

![image-20240925142041822](assets/image-20240925142041822.png)

从上图可以看出认证服务和资源服务使用相同的密钥，这叫对称加密，对称加密效率高，如果一旦密钥泄露可以伪造jwt令牌。

JWT还可以使用非对称加密，认证服务自己保留私钥，将公钥下发给受信任的客户端、资源服务，公钥和私钥是配对的，成对的公钥和私钥才可以正常加密和解密，非对称加密效率低但相比对称加密非对称加密更安全一些。

### jwt的示例

```JSON
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicmVzMSJdLCJ1c2VyX25hbWUiOiJ6aGFuZ3NhbiIsInNjb3BlIjpbImFsbCJdLCJleHAiOjE2NjQzMzE2OTUsImF1dGhvcml0aWVzIjpbInAxIl0sImp0aSI6ImU5ZDNkMGZkLTI0Y2ItNDRjOC04YzEwLTI1NmIzNGY4ZGZjYyIsImNsaWVudF9pZCI6ImMxIn0.-9SKI-qUqKhKcs8Gb80Rascx-JxqsNZxxXoPo82d8SM",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicmVzMSJdLCJ1c2VyX25hbWUiOiJ6aGFuZ3NhbiIsInNjb3BlIjpbImFsbCJdLCJhdGkiOiJlOWQzZDBmZC0yNGNiLTQ0YzgtOGMxMC0yNTZiMzRmOGRmY2MiLCJleHAiOjE2NjQ1ODM2OTUsImF1dGhvcml0aWVzIjpbInAxIl0sImp0aSI6ImRjNTRjNTRkLTA0YTMtNDIzNS04MmY3LTFkOWZkMmFjM2VmNSIsImNsaWVudF9pZCI6ImMxIn0.Wsw1Jc-Kd_GFqEugzdfoSsMY6inC8OQsraA21WjWtT8",
  "expires_in": 7199,
  "scope": "all",
  "jti": "e9d3d0fd-24cb-44c8-8c10-256b34f8dfcc"
}
```

- access_token：生成的jwt令牌，用于访问资源使用。
- token_type：bearer是在RFC6750中定义的一种token类型，在携带jwt令牌访问资源时需要在head中加入`bearer 空格 令牌内容`。
- refresh_token：当jwt令牌快过期时使用刷新令牌可以再次生成jwt令牌。
- expires_in：过期时间（秒）
- scope：令牌的权限范围，服务端可以根据令牌的权限范围去对令牌授权。
- jti：令牌的唯一标识。

**因为JWT的信息是自包含的，非常适合跨域认证的场景，客户端在登录之后会收到JWT的一个token，之后每次请求通过http头部来带上这个token，服务器来验证签名来确认用户是否有权限。**

## 注册登录


整合Spring Security实现JWT资源访问的认证和权限控制。

- 实现注册接口，创建新用户
- 实现登录接口，用于下发JWT Token
- 使用JWT Filter验证带有Token的请求访问头
- 利用Spring Security保护应用的资源API

SpringBoot Security

- 使用MyBatisX插件生成数据访问层的代码
- Jwt跨域认证

整个流程确保了应用的安全性，通过对用户的身份验证和权限校验，来决定用户是否可以访问应用中特定的资源。

引入依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<!--jwt相关的依赖-->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.11.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.11.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.11.5</version>
</dependency>
```

### AuthController

```java
package com.example.demo.student.api;

import com.example.demo.student.dto.LoginDto;
import com.example.demo.student.dto.LoginResponseDto;
import com.example.demo.student.dto.RegisterDto;
import com.example.demo.student.dto.UserDto;
import com.example.demo.student.security.JwtUtil;
import com.example.demo.student.service.UserService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    @Resource
    private UserService userService;

    @Resource
    private AuthenticationManager authenticationManager;

    @Resource
    private JwtUtil jwtUtil;

    @PostMapping("register")
    public ResponseEntity<String> register(@RequestBody RegisterDto registerDto) {
        UserDto user = userService.getUserByUsername(registerDto.getUsername());
        if (user != null) {
            return new ResponseEntity<>("用户名已存在", HttpStatus.BAD_REQUEST);
        }
        userService.register(registerDto);
        return new ResponseEntity<>("用户注册成功", HttpStatus.OK);
    }

    /**
     * 使用 AuthenticationManager 来处理认证逻辑。
     * authenticationManager.authenticate 方法会接收一个 UsernamePasswordAuthenticationToken 对象，根据传入的用户名和密码进行认证。
     * 如果认证成功，SecurityContextHolder.getContext().setAuthentication(authenticate) 会将认证信息存储在安全上下文中，供后续的请求访问。
     * 最后，生成 JWT 令牌并返回给客户端。
     */
    @PostMapping("login")
    public ResponseEntity<LoginResponseDto> login(@RequestBody LoginDto loginDto) {
        Authentication authenticate = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken
                        (loginDto.getUsername(), loginDto.getPassword()));
        SecurityContextHolder.getContext().setAuthentication(authenticate);
        LoginResponseDto loginResponseDto = new LoginResponseDto();
        loginResponseDto.setToken(jwtUtil.generateToken(authenticate));
        return new ResponseEntity<>(loginResponseDto, HttpStatus.OK);
    }
}
```

### SecurityConfig

```java
package com.example.demo.student.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import javax.annotation.Resource;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Resource
    private AuthEntryPoint authEntryPoint;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
               	//开启跨域认证
                .csrf().disable()
               	//异常处理
                .exceptionHandling()
                .authenticationEntryPoint(authEntryPoint)
                .and()
        	     	//因为jwt是无状态的，所以session管理策略改为无状态的
                .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                .authorizeRequests()
                //api/auth/下面的接口都可以被访问到（注册登录不需要验证）
                .antMatchers("/api/auth/**").permitAll()
                .antMatchers("/v2/api-docs",
                        "/configuration/ui",
                        "/swagger-resources/**",
                        "/configuration/security",
                        "/swagger-ui.html",
                        "/webjars/**").permitAll()
              	//每一个请求都需要认证之后，才可以访问
                .anyRequest().authenticated()
                .and()
                .httpBasic();
        //JWT 过滤器：在用户名密码认证过滤器之前添加 JWT 认证过滤器。先对token进行有效性的验证。
        http.addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    //登录接口需要使用
    @Bean
    public AuthenticationManager authenticationManager
            (AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    //对用户密码进行加密
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public JWTAuthenticationFilter jwtAuthenticationFilter() {
        return new JWTAuthenticationFilter();
    }
}
```

### AuthenticationEntryPoint

没有权限时返回报错，而不是Spring Security默认的重定向登录页。需要添加登录异常的拦截处理类。

```java
package com.example.demo.student.security;

import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * 定义一个名为 AuthEntryPoint 的类，它实现了 AuthenticationEntryPoint 接口。这个类的作用是在用户尝试访问受保护的资源但未通过身份验证时，发送一个未授权的错误响应。
 * @Component 注解表明这个类是一个 Spring 组件，会被 Spring 容器管理。
 * commence 方法是 AuthenticationEntryPoint 接口中的方法，当用户未通过身份验证时会被调用。
 * commence 方法接收三个参数：HttpServletRequest、HttpServletResponse 和 AuthenticationException。
 * 在方法内部，调用 response.sendError(HttpServletResponse.SC_UNAUTHORIZED, authException.getMessage()) 发送一个 401 未授权的 HTTP 响应，并附带异常信息。
 */
@Component//注册到Spring容器中
public class AuthEntryPoint implements AuthenticationEntryPoint {
    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException, ServletException {
        response.sendError(HttpServletResponse.SC_UNAUTHORIZED, authException.getMessage());
    }
}
```

登录验证用户名和密码通过之后，生成jwt token返回给客户端，客户端之后的请求在请求头上面带上下发的JWT token，服务端验证这个token，实现jwt跨域认证的效果。

```java
package com.example.demo.student.security;

public class SecurityConstants {
    //token过期时间
    public static final long JWT_EXPIRATION = 7 * 24 * 60 * 60 * 1000L;
    //jwt的key
    public static final String JWT_SECRET_KEY = "askjjdkslajkdlkjaslkdjklasjdlkjasdkljaslkdjasdlkajsdsd";

}
```

```java
package com.example.demo.student.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.security.authentication.AuthenticationCredentialsNotFoundException;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import javax.xml.bind.DatatypeConverter;
import java.util.Date;

@Component//注入到容器中
public class JwtUtil {
    //生成加密key
    byte[] jwtSecretKey = DatatypeConverter.parseBase64Binary(SecurityConstants.JWT_SECRET_KEY);
		//生成token
    public String generateToken(Authentication authentication) {
        String username = authentication.getName();
        Date now = new Date();
        Date expireDate = new Date(now.getTime() + SecurityConstants.JWT_EXPIRATION);
        return Jwts.builder()
                .setSubject(username)
	          	  //token的下发时间是现在
                .setIssuedAt(now)
               	//过期时间
                .setExpiration(expireDate)
	        	    //加密算法HS256
                .signWith(Keys.hmacShaKeyFor(jwtSecretKey), SignatureAlgorithm.HS256)
                .compact();
    }
		//从token中解析用户名
    public String getUsernameFromToken(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(jwtSecretKey)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
    }
		//校验token有效性
    public boolean validateToken(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
              			.setSigningKey(jwtSecretKey)            
                   	.build()
              			.parseClaimsJws(token)
              			.getBody();
            return claims != null && claims.getExpiration().after(new Date());
        } catch (Exception e) {
            throw new AuthenticationCredentialsNotFoundException("Jwt 解析异常或已过期");
        }
    }
}
```

### UserDetailsService

创建UserDetailsService，Spring Security中的核心接口，用于提供用户的详细信息。Spring Security使用此接口来获取进行身份认证和授权的用户信息。

```java
package com.example.demo.student.security;

import com.example.demo.student.dto.UserDto;
import com.example.demo.student.service.UserService;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.Collection;
import java.util.stream.Collectors;

@Component//注册到Spring容器中
public class CustomUserDetailsService implements UserDetailsService {
    @Resource
    private UserService userService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        UserDto user = userService.getUserByUsername(username);
        if (user == null) {
            return null;
        }
        //import org.springframework.security.core.userdetails.User;
        return new User(user.getUsername(), user.getPassword(), getAuthorities(user));
    }

    //import org.springframework.security.core.GrantedAuthority;
    private Collection<? extends GrantedAuthority> getAuthorities(UserDto user) {
        return user.getRoles()
                .stream()
                .map(role -> new SimpleGrantedAuthority(role.getName()))
                .collect(Collectors.toList());
    }
}
```

### OncePerRequestFilter

验证token是否有效

JWTAuthenticationFilter 类是一个自定义的过滤器，用于在每次请求时验证 JWT 令牌。它继承自 OncePerRequestFilter，确保在每个请求中只执行一次过滤操作。 

通过AuthenticationFilter拦截用户请求并提取认证信息（用户名、密码、token），然后调用AuthenticationManager处理认证逻辑，认证逻辑会调用UserDetailsService来加载用户的详情信息（密码，用户名等），一旦认证成功，用户的信息会被设置到SecurityContext中，供后续的请求访问。

```java
package com.example.demo.student.security;

import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.annotation.Resource;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
//过滤器，每次http请求时检查http请求头是否有有效的jwt令牌，对用户认证
public class JWTAuthenticationFilter extends OncePerRequestFilter {
    @Resource
    private JwtUtil jwtUtil;
    @Resource
    private CustomUserDetailsService customUserDetailsService;

	  //doFilterInternal 方法是过滤器的核心逻辑
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
    	  //从请求中获取 JWT 令牌
        String token = getTokenFromRequest(request);
	      //验证令牌的有效性
        if (token != null && jwtUtil.validateToken(token)) {
	          //如果令牌有效，获取用户名
            String username = jwtUtil.getUsernameFromToken(token);
            //加载用户详细信息
            UserDetails userDetails = customUserDetailsService.loadUserByUsername(username);
	          //创建 UsernamePasswordAuthenticationToken 对象
            UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(userDetails,
                            null, userDetails.getAuthorities());
	          //设置认证详细信息
            authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
	          //将认证信息存储在安全上下文中
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
	      //继续过滤链
        filterChain.doFilter(request, response);
    }

    //从请求头里面获取token
    // Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTcxMjMxMjg5MCwiZXhwIjoxNzEyMzEzNDk1fQ
    // .7UhzQxpiyOqK9m3oUd2ZssvypVOUt1R9zK8-AtZ4qfU
    private String getTokenFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

## 网关认证

一个前端请求首先会经过网关，之后再路由到一个个的微服务。

API网关（Gateway）是应用程序客户端的单一入口点，它位于客户端和应用程序的后端服务集合之间。

![image-20240929210307018](assets/image-20240929210307018.png)

流程

1. 客户端向API网关发送请求，该请求通常基于HTTP协议。
2. API网关验证HTTP请求。
3. API网关根据其允许列表和拒绝列表检查调用者的IP地址和其它HTTP请求头，还可以针对IP地址和HTTP请求头等属性执行基本的速率限制检查。例如：它可以拒绝来自超过一定速率的IP地址的请求。
4. API网关将请求传递给身份验证服务，以进行身份验证和授权。API网关从身份验证服务处接收经过身份验证的会话，其中包含允许请求执行的操作范围。
5. 对经过身份验证的会话应用更高级别的速率限制检查，如果超过限制，此时请求将被拒绝。
6. 在服务发现组件的帮助下，API网关通过路径匹配找到适当的后端服务来处理请求。
7. 网关将请求转换为适当的协议，并将转换后的请求发送到后端服务（例如gRPC）。当响应从后端服务返回时，网关会将响应转换回面向公众的协议，并将响应返回给客户端。

网关作用：

- **网站白名单维护**：针对不用认证的URL全部放行。
- **身份验证和安全性**：进行身份验证和授权，保护后端服务。除了白名单剩下的就是需要认证的请求，网关需要验证jwt的合法性，jwt合法则说明用户身份合法，否则说明身份不合法则拒绝继续访问。

- **请求路由**：将请求转发到合适的微服务。
- **协议转换和服务发现**：处理不同协议之间的转换，例如从 HTTP 到 MQTT。
- **负载均衡**：分配请求到多个实例，以提高性能和可用性。
- **断路**：网关应跟踪错误，并提供断路功能以防止服务过载。
- **监控与日志记录**：收集和分析流量数据，以便于监控和故障排查。
- **分析和计费**。
- **缓存**。

所有访问微服务的请求都要经过网关。在网关进行用户身份的认证可以将很多非法的请求拦截到微服务以外，这叫做网关认证。

网关是基础设置的关键部分，应将其部署到多个区域以提高可用性。

**网关不负责授权**，对请求的授权操作在各个微服务进行，因为微服务最清楚用户有哪些权限访问哪些接口。

在网关工程添加依赖

```XML
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-oauth2</artifactId>
</dependency>
```

由于是在网关处进行令牌校验，所以在微服务处不再校验令牌的合法性。
