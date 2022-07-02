# AFNetworking源码分析

AFNetworking基于urlsession封装

目录：
包括三个部分：

1. NSURLSession
   这两个是网络通信的核心类
   *   `AFURLSessionManager`
   *   `AFHTTPSessionManager`
   AFHTTPSessionManager继承于AFURLSessionManager
   其他类都是围绕这两个类去做
2. Serialization  
   序列化
   包括两部分
   一部分是请求部分，一部分是响应部分
   *   `<AFURLRequestSerialization>`  请求时候Request的设置处理
       *   `AFHTTPRequestSerializer`
       一般请求的时候是AFHTTPRequestSerializer 数据流 nsdata
       *   `AFJSONRequestSerializer`
       *   `AFPropertyListRequestSerializer`
   *   `<AFURLResponseSerialization>`
       *   `AFHTTPResponseSerializer`
       *   `AFJSONResponseSerializer`
       一般响应的是AFJSONResponseSerializer afn自动转json
       *   `AFXMLParserResponseSerializer`
       *   `AFXMLDocumentResponseSerializer` *(macOS)*
       *   `AFPropertyListResponseSerializer`
       *   `AFImageResponseSerializer`
       *   `AFCompoundResponseSerializer`
3. Additional Functionality

其他功能类

1. `AFSecurityPolicy`  https验证
   安全策略
2. `AFNetworkReachabilityManager`
   网络状态监听 wifi 蜂窝网络

![image.png](https://upload-images.jianshu.io/upload_images/1892989-083f9afd625b3d09.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

1. 网络通信核心类分析
2. https认证
3. 序列化

url-request-session-task-resume
session通过request生成一个task

- requestSerializer：请求之前的操作都在这个类中完成
  请求之前传一个字典参数  其实是个表单形式 key=value&
- responseSerializer：请求之后的数据处理

- AFHTTPSessionManager请求的封装  get post等 更加简单  具体实现在AFURLSessionManager中

- NSParameterAssert(<#condition#>)
  断言  后面的值不能为空 

AFURLRequestSerialization.m文件 `NSArray * AFQueryStringPairsFromKeyAndValue(NSString *key, id value)` 参数设置。

序列化
字典变参数字符串

![
](https://upload-images.jianshu.io/upload_images/1892989-4eeaf9afb101a1da.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

染后生成一个NSURLRequest
然后生成一个NSURLSessionDataTask任务

任务task添加代理
代理和任务绑定在一起

上传下载进度 使用观察者监听
系统原生的是使用代理获取进度，AFN使用block（还有通知）。

通过AFURLSessionManagerTaskDelegate代理类 一个数据的处理的类
1. 以block形式返回进度，用户不需要再写代理获取。
2. 拼接服务器返回数据。服务器返回的数据是一块一块的，需要拼接。

请求前：nsurlsessionmanager （仅仅使用网络请求）减少主类的复杂程度
请求中：进度 代理 AFURLSessionManagerTaskDelegate 通知 block
请求后：数据的处理 json xml list AFURLSessionManagerTaskDelegate

![image.png](https://upload-images.jianshu.io/upload_images/1892989-34159ee4b09ddf69.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)