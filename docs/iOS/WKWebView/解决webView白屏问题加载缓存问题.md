# 问题描述：

问题一：
点击文章列表进入文章详情，会有几秒显示空白页面，之后才是加载请求数据。加载请求数据显示加载动画，这段时间是可以接受的。主要矛盾是解决加载动画显示之前的白屏问题。
问题二：
后台设置的过期时间还没到，但是版本更新修改比较大，加载缓存数据会有问题，需要header请求，请求头部信息，查找是否有修改，更新缓存文件。

# 解决方法：

把页面文件保存到本地， 加载的时候，加载本地的，因为文章详情里面html文件代码都一样，框架都是那样的。只要后台那边不改代码，一般情况下都不变，所以把那个文件存到本地，以后都读本地读文件即可。不用去请求服务器，不再受服务器响应速度影响。

### 1、 先判断是否修改过

#### 设置html文件过期时间

在请求数据的时候，header中有一个过期时间。header信息可以在WKNavigationDelegate的`- (void)webView:(WKWebView *)webView decidePolicyForNavigationResponse:(WKNavigationResponse *)navigationResponse decisionHandler:(void (^)(WKNavigationResponsePolicy))decisionHandler;`代理方法中获得。

在上面方法中打印`navigationResponse`可以看到header。
```
- (void)webView:(WKWebView *)webView decidePolicyForNavigationResponse:(WKNavigationResponse *)navigationResponse decisionHandler:(void (^)(WKNavigationResponsePolicy))decisionHandler
{
    NSString *cacheControl = [(NSHTTPURLResponse*)navigationResponse.response allHeaderFields][@"Cache-Control"]; // max-age, must-revalidate, no-cache
    NSArray *cacheControlEntities = [cacheControl componentsSeparatedByString:@","];

    for(NSString *substring in cacheControlEntities) {
        
        if([substring rangeOfString:@"max-age"].location != NSNotFound) {
            
            // do some processing to calculate expiresOn
            NSString *maxAge = nil;
            NSArray *array = [substring componentsSeparatedByString:@"="];
            if([array count] > 1)
                maxAge = array[1];
            
           NSDate * expiresOnDate = [[NSDate date] dateByAddingTimeInterval:[maxAge intValue]];

        //保存过期时间
            [[NSUserDefaults standardUserDefaults] setObject:expiresOnDate forKey:kHtml_gqsj];

        }
    }

    decisionHandler(WKNavigationResponsePolicyAllow);
}
```
问题：
当后台那边对html文件进行了修改之后，app内html文件还没到过期时间，那么就会出请求不到数据等等问题。
解决方法：
可以只请求该url地址的header头， 请求的数据也不多，响应相应的比其他的请求快些。

html文件不是永远不变的， 后台那边可能会调整一些样式等，所以需要先使用header请求去 请求header判断一下缓存的html文件有没有修改过。
对应的代码如下：
```
/**
 header请求，获取头部的信息

 @param block yes：读取本地缓存 no：重新缓存文件
 @param baseUrl html文件地址
 */
- (void)requestWebViewHeader:(void (^)(BOOL isLoadCache))block
                     baseUrl:(NSString *)baseUrl {
    AFHTTPSessionManager *manager = [AFHTTPSessionManager manager];
    [manager HEAD:baseUrl parameters:nil success:^(NSURLSessionDataTask * _Nonnull task) {
        NSUserDefaults *userDefaults = [NSUserDefaults standardUserDefaults];
        if ([[userDefaults objectForKey:kHtml_lastModified] isEqual:[(NSHTTPURLResponse*)task.response allHeaderFields][@"Last-Modified"]]) {
            block(YES);
        } else {
            block(NO);
            [userDefaults setObject:[(NSHTTPURLResponse*)task.response allHeaderFields][@"Last-Modified"] forKey:kHtml_lastModified];
        }
    } failure:^(NSURLSessionDataTask * _Nullable task, NSError * _Nonnull error) {
        block(YES);
    }];
}
```
#### 控制台输出：

```
(lldb) po task.response
<NSHTTPURLResponse: 0x60400082f480> { URL: http://apptest.ningmengyun.com/news/newsDetail.html?ArticleID=1159&withNavigationBar=true } { Status Code: 200, Headers {
    "Accept-Ranges" =     (
        bytes
    );
    "Content-Encoding" =     (
        gzip
    );
    "Content-Length" =     (
        1353
    );
    "Content-Type" =     (
        "text/html"
    );
    Date =     (
        "Mon, 23 Apr 2018 04:06:18 GMT"
    );
    Etag =     (
        "\"809d9cf9cbd7d31:0\""
    );
    "Last-Modified" =     (
        "Thu, 19 Apr 2018 10:48:39 GMT"
    );
    Server =     (
        "Microsoft-IIS/7.5"
    );
    Vary =     (
        "Accept-Encoding"
    );
    "X-Powered-By" =     (
        "ASP.NET"
    );
} }

(lldb) po lastModified
Thu, 19 Apr 2018 10:48:39 GMT

(lldb) 
```
##### 关于url的问题：

点击每条文章，传入的url为`https://app.ningmengyun.com/news/newsDetail.html?ArticleID=1034`，其中的ArticleID为每条文章的id，但是缓存html和请求header头的时候不需要整个url，只需要前面的地址即可。参数都不需要。即：`https://app.ningmengyun.com/news/newsDetail.html`

请求头的参考：
https://blog.csdn.net/u013583789/article/details/52129316

### 2、判断是否修改过， 提前载入内存
如果没修改的话 可以直接加载缓存文件到内存中
如果有修改的话，就重新下载缓存html文件并且缓存到内存中。

```
- (void)cacheHeadlineHtml {
    NSString *path;
    NSString *baseUrl;
    NSString *cachesPath = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];

        path = [cachesPath stringByAppendingString:kHtml_hcwz];
        baseUrl =LMURLHeader5(@"/news/newsDetail.html");

    [self requestWebViewHeader:^(BOOL isLoadCache) {
        if (isLoadCache) {
            //没修改
 self.htmlString_new = [NSString stringWithContentsOfFile:path encoding:NSUTF8StringEncoding error:nil];
        } else {
            //修改过
            [[NSFileManager defaultManager] removeItemAtPath:path error:nil];
            [self writeToCache:baseUrl];
        }
    } baseUrl:baseUrl];
}
```

## 3、在加载webView的时候改为下面方法：
```
- (void)loadHtml {
    NSString *cachesPath = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
   NSString *path = [cachesPath stringByAppendingString:[NSString stringWithFormat:@"/Caches/%lu.html",[@"huancunwenzhang" hash]]];
   NSString *htmlString = [NSString stringWithContentsOfFile:path encoding:NSUTF8StringEncoding error:nil];

//有缓存
    if (!(htmlString == nil || [htmlString isEqualToString:@""])) {
        [_wkWebview loadHTMLString:htmlString baseURL:[NSURL URLWithString:self.urlString]];
    }
//没缓存
 else {
        NSURL *url = [NSURL URLWithString:self.urlString];
        NSURLRequest *request = [NSURLRequest requestWithURL:url];
        [_wkWebview loadRequest:request];
//没有缓存需要缓存
        [self writeToCache];
    }
}
```
注：
还有优化的地方：
可以把上面htmlString读取到内存中，常驻内存中，app运行时使用同一个。减少一点读取文件的时间。

#### 将html文件保存到本地：

```
- (void)writeToCache {
//@"https://app.ningmengyun.com/news/newsDetail.html" 是html文件路径，后面不需要加某篇文章id等参数。
    NSString *htmlResponseStr = [NSString stringWithContentsOfURL:[NSURL URLWithString:@"https://app.ningmengyun.com/news/newsDetail.html"] encoding:NSUTF8StringEncoding error:nil];

    //创建文件管理器
    NSFileManager *fileManager = [NSFileManager defaultManager];
    //获取document路径
    NSString *cachesPath = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
//创建文件夹路径 
    [fileManager createDirectoryAtPath:[cachesPath stringByAppendingString:@"/Caches"] withIntermediateDirectories:YES attributes:nil error:nil];
    //写入路径
    NSString *path = [cachesPath stringByAppendingString:[NSString stringWithFormat:@"/Caches/%lu.html",[@"huancunwenzhang" hash]]];
    [htmlResponseStr writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];

        //缓存到内存  提高速度
        self.htmlString_course = htmlResponseStr;

}
```

##### 注：

这是读书详情的接口`http://apptest.ningmengyun.com/commodity/booksDetail.html?productId=100106`
可以使用接口`/commodity/booksDetail.html`直接去存储，路径和名称都使用接口的。