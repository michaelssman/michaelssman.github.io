# jwt令牌

## 普通令牌的问题

客户端申请到令牌，接下来客户端携带令牌去访问资源，到资源服务器将会校验令牌的合法性。

资源服务器如何校验令牌的合法性？

以OAuth2的密码模式为例进行说明：

![image-20240925140436592](./assets/image-20240925140436592.png)

从第4步开始说明：

1. 客户端携带令牌访问资源服务获取资源。
2. 资源服务远程请求认证服务校验令牌的合法性
3. 如果令牌合法资源服务向客户端返回资源。

这里存在一个问题：

就是校验令牌需要远程请求认证服务，客户端的每次访问都会远程校验，执行性能低。

如果能够让资源服务自己校验令牌的合法性将省去远程请求认证服务的成本，提高了性能。如下图：

![image-20240925140551475](./assets/image-20240925140551475.png)

**如何解决上边的问题，实现资源服务自行校验令牌。**

令牌采用JWT格式即可解决上边的问题，用户认证通过后会得到一个JWT令牌，JWT令牌中已经包括了用户相关的信息，客户端只需要携带JWT访问资源服务，资源服务根据事先约定的算法自行完成令牌校验，无需每次都请求认证服务完成授权。

## JWT

JSON Web Token（JWT）是一种使用JSON格式传递数据的网络令牌技术，它是一个开放的行业标准（RFC 7519），它定义了一种简洁的、**自包含**的协议格式，用于在通信双方传递json对象，传递的信息经过数字签名可以被验证和信任，它可以使用HMAC算法或使用RSA的公钥/私钥对来签名，防止内容篡改。

官网：https://jwt.io/

使用JWT可以实现无状态认证

用户在浏览器输入用户名和密码进行验证，服务器验证通过之后，服务器向用户返回唯一的sessionID。

传统的基于session的方式是有状态认证，**用户登录成功将用户的身份信息存储在服务端**，这样加大了服务端的存储压力，并且这种方式不适合在分布式系统中应用。

如下图，当用户访问应用服务，每个应用服务都会去服务器查看session信息，如果session中没有该用户则说明用户没有登录，此时就会重新认证，而解决这个问题的方法是Session复制、Session黏贴。

![image-20240925141120682](./assets/image-20240925141120682.png)

如果是基于令牌技术在分布式系统中实现认证则**服务端不用存储session**，可以将用户身份信息存储在令牌中，用户认证通过后认证服务颁发令牌给用户，用户将令牌存储在客户端，去访问应用服务时携带令牌去访问，服务端从jwt解析出用户信息。这个过程就是无状态认证。

![image-20240925141207939](./assets/image-20240925141207939.png)

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

内容也是一个json对象，它是存放有效信息的地方，它可以存放jwt提供的信息字段，比如：iss（签发者）,exp（过期时间戳）, sub（面向的用户）等，也可自定义字段。

此部分不建议存放敏感信息，因为此部分可以解码还原原始内容。

最后负载使用Base64Url编码，得到一个字符串就是JWT令牌的第二部分。

```JSON
  {
    "sub": "1234567890",
    "name": "456",
    "admin": true
  }
```

#### 3、Signature签名

此部分用于防止jwt内容被篡改。

这个部分使用base64url将前两部分进行编码，编码后使用点（.）连接组成字符串，最后使用header中声明的签名算法进行签名。

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

第三部分使用签名算法对第一部分和第二部分的内容进行签名，常用的签名算法是 HS256，md5，sha 等，签名算法需要使用密钥进行签名，密钥不对外公开，并且签名是不可逆的，如果第三方更改了内容那么服务器验证签名就会失败，要想保证验证签名正确必须保证内容、密钥与签名前一致。

![image-20240925142041822](./assets/image-20240925142041822.png)

认证服务和资源服务使用相同的密钥，这叫对称加密，对称加密效率高，如果一旦密钥泄露可以伪造jwt令牌。

可以使用非对称加密，认证服务自己保留私钥，将公钥下发给受信任的客户端、资源服务，公钥和私钥是配对的，成对的公钥和私钥才可以正常加密和解密，非对称加密效率低但相比对称加密非对称加密更安全一些。

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

因为JWT的信息是自包含的，非常适合**跨域认证**的场景。

客户端在登录之后会收到JWT的一个token，之后每次请求通过http头部来带上这个token，服务器来验证签名来确认用户是否有权限。