# https认证

https就是披了一件ssl（加密）外套的http

http网络协议：
缺点：
数据不安全，数据不完整性（中间人（钓鱼网站）攻击，篡改数据），数据不真实

https解决上面的缺点。

https 既然已经是加密了，为什么还要认证验证服务器的证书。

加密了是安全的，验证服务器是安全的，确认是想请求的服务器。
服务器是客户端想要的服务器，客户端是服务器想要的客户端。这是双向的。
单向  验证服务器。

## AFSecurityPolicy证书验证

- ca机构颁布的证书 （我们代码中不需要做修改，只需要http后面加个s）

- 自签证书 需要手动验证合法性。

  ```objective-c
  - (void)test{
      NSString *urlStr = @"http://www.12306.cn/mormhweb/";
      AFHTTPSessionManager *manager = [AFHTTPSessionManager manager];
      manager.securityPolicy = [self securityPolicy];
      [manager GET:urlStr parameters:nil headers:nil progress:nil success:^(NSURLSessionDataTask * _Nonnull task, id  _Nullable responseObject) {
          //
      } failure:^(NSURLSessionDataTask * _Nullable task, NSError * _Nonnull error) {
          //
      }];
  }
  - (AFSecurityPolicy *)securityPolicy {
      NSString *cerPath = [[NSBundle mainBundle] pathForResource:@"scra" ofType:@"cer"];
      NSData *cerData = [NSData dataWithContentsOfFile:cerPath];
      NSSet *set = [NSSet setWithObject:cerData];
      AFSecurityPolicy *securityPolicy = [AFSecurityPolicy policyWithPinningMode:AFSSLPinningModeCertificate withPinnedCertificates:set];
      securityPolicy.allowInvalidCertificates = YES;
      securityPolicy.validatesDomainName = NO;
      return securityPolicy;
  }
  ```

`NSURLSessionTaskDelegate`的代理方法`- (void)URLSession:(NSURLSession *)session
              task:(NSURLSessionTask *)task
didReceiveChallenge:(NSURLAuthenticationChallenge *)challenge
 completionHandler`

设置了验证策略
请求之后会有一个回调，验证证书是否可信。
接受挑战
服务器给你传证书  你验证证书
验证核心方法：
`- (BOOL)evaluateServerTrust:(SecTrustRef)serverTrust
                  forDomain:(NSString *)domain`

项目里面的证书和服务器里面的证书对比。可能有很多证书（子证书），只要有一个和服务器匹配，则通过。

还有一种：
证书中获取公钥， 本地公钥和服务器端公钥的匹配。

总结：
校验证书或者公钥。