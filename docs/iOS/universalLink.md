# Universal Link

通用链接，唤起APP的功能。

`Universal Link`是`Apple`在`iOS 9`推出的一种能够方便的通过传统`HTTPS`链接来启动`APP`的功能。如果你的应用支持`Universal Link`，当用户点击一个链接时可以跳转到你的网站并获得无缝重定向到对应的`APP`，且不需要通过`Safari`浏览器。如果你的应用不支持的话，则会在`Safari`中打开该链接。

## 支持`Universal Link`

先决条件：必须有一个支持`HTTPS`的域名，并且拥有该域名下上传到根目录的权限（为了上传`Apple`指定文件）

## 集成步骤

### 1、开发者中心配置

找到对应的`App ID`，在`Application Services`列表里有`Associated Domains`一条，把它变为`Enabled`就可以了 

### 2、工程配置

`targets->Capabilites->Associated Domains`，在其中的`Domains`中填入你想支持的域名，必须以`applinks:`为前缀，如：`applinks:domain` 

配的universalLink是https://m.nmkjxy.com/app/

则project配置Signing&capabilities下的`Associated Domains`设置applinks:m.nmkjxy.com。

`applinks:`是固定的，后面的要和universalLink的地址保持一致

举个例子：
你的域名是：[https://xxx.com](https://xxx.com/) 你要匹配的是：https://xxx.com/app/link/
1、微信开发者 Universal Link 填写：https://xxx.com/app/link/
2、xcode 的` Associated Domains` 添加 applinks:xxx.com

### 3、配置指定文件

在你关联的域根目录下 创建 apple-app-site-association 文件，文件格式参照https://developer.apple.com/documentation/safariservices/supporting_associated_domains 。这里我们使用：{&quot;applinks&quot;:{&quot;apps&quot;:[],&quot;details&quot;:[{&quot;appID&quot;:&quot;teamID.bundleID&quot;,&quot;paths&quot;:[&quot;/app/link/*&quot;]}]}}

创建一个内容为`json`格式的文件，苹果将会在合适的时候，从我们在项目中填入的域名请求这个文件。这个文件名必须为`apple-app-site-association`，切记没有`后缀名`，文件内容大概是这样子：

```
{
    "applinks": {
        "apps": [],
        "details": [
            {
                "appID": "9JA89QQLNQ.com.apple.wwdc",
                "paths": [ "/wwdc/news/", "/videos/wwdc/2015/*"]
            },
            {
                "appID": "ABCD1234.com.apple.wwdc",
                "paths": [ "*" ]
            }
        ]
    }
}
```

`appID`：组成方式是`TeamID.BundleID`。如上面的`9JA89QQLNQ`就是`teamId`。登陆开发者中心，在`Account -> Membership`里面可以找到`Team ID` `paths`：设定你的`app`支持的路径列表，只有这些指定路径的链接，才能被`app`所处理。`*`的写法代表了可识别域名下所有链接

- 注意：苹果是根据域名下的`paths`处理要打开的应用的，所以要避免相同的`paths`对应多个`appID`

### 4、上传该文件

上传该文件到你的域名所对应的`根目录`或者`.well-known目录`下，这是为了苹果能获取到你上传的文件。上传完后，先访问一下，看看是否能够获取到，当你在浏览器中输入这个文件链接后，应该是直接下载`apple-app-site-association`文件

### 5、代码中的相关支持

当点击某个链接，可以直接进我们的`app`，但是我们的目的是要能够获取到用户进来的链接，根据链接来展示给用户相应的内容，我们需要在工程里实现`AppDelegate`对应的方法：

```objective-c
- (BOOL)application:(UIApplication *)application continueUserActivity:(NSUserActivity *)userActivity restorationHandler:(void (^)(NSArray * _Nullable))restorationHandler {
    // NSUserActivityTypeBrowsingWeb 由Universal Links唤醒的APP
    if ([userActivity.activityType isEqualToString:NSUserActivityTypeBrowsingWeb]){
        NSURL *webpageURL = userActivity.webpageURL;
        NSString *host = webpageURL.host;
        if ([host isEqualToString:@"api.r2games.com.cn"]){
            //进行我们的处理
            NSLog(@"TODO....");
        }else{
            NSLog(@"openurl");
            [[UIApplication sharedApplication] openURL:webpageURL options:nil completionHandler:nil];
            // [[UIApplication sharedApplication] openURL:webpageURL];
        }
    }
    return YES;
}
```

苹果为了方便开发者，提供了一个[网页验证](https://link.juejin.cn?target=https%3A%2F%2Fsearch.developer.apple.com%2Fappsearch-validation-tool%2F)我们编写的这个`apple-app-site-association`是否合法有效，但是苹果官方给的检测接口不靠谱，可以把通用链接地址在浏览器或者记事本上填写访问，能拉起应用就是配置成功了，不能就说明配置有问题或者还没有生效，一般配置完成最快要`30分钟后`才能生效

- 注意如果挂了代理，SSL的设置一定不要监控苹果的这个`https://app-site-association.cdn-apple.com`域名，可能会导致访问通用链接无效

## Universal Link（通用链接）注意点

### `Universal Link`跨域

`Universal Link`必须要求跨域，如果不跨域，就不会跳转。

假如当前网页的域名是`A`，当前网页发起跳转的域名是`B`，必须要求`B`和`A`是不同域名才会触发`Universal Link`，如果`B`和`A`是相同域名，只会继续在当前`WebView`里面进行跳转，哪怕你的`Universal Link`一切正常，根本不会打开`App` 

### `Universal Link`请求`apple-app-site-association`时机

- 当我们的`App`在设备上第一次运行时，如果支持`Associated Domains`功能，那么`iOS`会自动去`GET`定义的`Domain`下的`apple-app-site-association`文件
- `iOS`会先请求`https://domain.com/.well-known/apple-app-site-association`，如果此文件请求不到，再去请求`https://domain.com/apple-app-site-association`，所以如果想要避免服务器接收过多`GET`请求，可以直接把`apple-app-site-association`放在`./well-known`目录下
- 服务器上`apple-app-site-association`的更新不会让`iOS`本地的`apple-app-site-association`同步更新，即`iOS`只会在`App`第一次启动时请求一次，以后除非`App`更新或重新安装，否则不会在每次打开时请求`apple-app-site-association`

### Universal Link的好处

1. 之前的`Custom URL scheme`是自定义的协议，因此在没有安装该`app`的情况下是无法直接打开的。而`Universal Links`本身就是一个能够指向`web`页面或者`app`内容页的标准`web link`，因此能够很好的兼容其他情况
2. `Universal links`是从服务器上查询是哪个`app`需要被打开，因此不存在`Custom URL scheme`那样名字被抢占、冲突的情况
3. `Universal links`支持从其他`app`中的`UIWebView`中跳转到目标`app`
4. 提供`Universal link`给别的`app`进行`app`间的交流时，对方并不能够用这个方法去检测你的`app`是否被安装（之前的`custom scheme URL`的`canOpenURL`方法可以）