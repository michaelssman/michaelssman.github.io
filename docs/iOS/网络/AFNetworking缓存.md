# AFN缓存

## 使用AFN优化app

打开app加载列表数据有时候会比较慢，显示空白的不太好，所以可以在app第一次打开的时候先加载本地的缓存，然后自动刷新一下数据。这样以后打开app就不会显示空白界面的情况。

```
    AFHTTPSessionManager *manager = [AFHTTPSessionManager manager];
    manager.requestSerializer.cachePolicy = NSURLRequestReturnCacheDataElseLoad;
```

NSURLRequestReturnCacheDataElseLoad加载缓存数据。


##### 没网的时候 也加载缓存数据
```
    if (!(([Reachability reachabilityForLocalWiFi].currentReachabilityStatus != NotReachable) || ([Reachability reachabilityForInternetConnection].currentReachabilityStatus != NotReachable))) {
        manager.requestSerializer.cachePolicy = NSURLRequestReturnCacheDataElseLoad;
    }
```