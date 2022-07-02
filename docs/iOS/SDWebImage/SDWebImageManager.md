# SDWebImageManager

中心管理类，

管理不同的操作：

- 异步下载。
- 缓存。SDImageCache
- 解码。SDWebImageCodersManager 调用不同的实现。



## 多选选项NS_OPTIONS

```objective-c
typedef NS_OPTIONS(NSUInteger, SDWebImageOptions) {
    //不会重新下载已经失败过的图片
    SDWebImageRetryFailed = 1 << 0,

    //默认情况下，图像下载是在UI交互期间启动的，此标志禁用此功能，
    //导致延迟下载UIScrollView减速为例。
    SDWebImageLowPriority = 1 << 1,

   //禁止在磁盘缓存，只在缓存中存在
    SDWebImageCacheMemoryOnly = 1 << 2,

    //此标志支持逐行下载，图像在下载过程中逐步显示，就像浏览器所做的那样。
    //默认情况下，图像只显示一次，完全下载。
    SDWebImageProgressiveDownload = 1 << 3,

    //任何图片都从新下载，不使用http cache，比如一个图片发送变化，但是url没有变化，用该options刷新数据
    SDWebImageRefreshCached = 1 << 4,

    //后台下载
    SDWebImageContinueInBackground = 1 << 5,

    //存储在cookie nshttpcookiestore
    SDWebImageHandleCookies = 1 << 6,

    //允许不信任的ssl证书
    SDWebImageAllowInvalidSSLCertificates = 1 << 7,

    //默认情况下，图像按它们排队的顺序加载。这个标志是将图片放在队列的最前面
    SDWebImageHighPriority = 1 << 8,
    
    //占位符图像是在图像加载时加载的，完全加载完才展示
    SDWebImageDelayPlaceholder = 1 << 9,

    //转换图像
    SDWebImageTransformAnimatedImage = 1 << 10,
    
    //默认情况下，image是在下载完成后加载，但是在一些情况下，我们想要在设置图像之前使用（例如应用过滤器或添加交叉淡入淡出动画），如果您想在成功完成时手动设置图像，请使用此标志
    SDWebImageAvoidAutoSetImage = 1 << 11,
    
    //默认情况下，图像是进行解码的，这个标志是按比例缩小images的尺寸，来缩小占用的手机内存，如果` sdwebimageprogressivedownload `标志设置的情况下被停用。，压缩大的图片
    SDWebImageScaleDownLargeImages = 1 << 12,
    
    /**
     * By default, we do not query disk data when the image is cached in memory. This mask can force to query disk data at the same time.
     * This flag is recommend to be used with `SDWebImageQueryDiskSync` to ensure the image is loaded in the same runloop.
     */
    SDWebImageQueryDataWhenInMemory = 1 << 13,
    
    /**
     * By default, we query the memory cache synchronously, disk cache asynchronously. This mask can force to query disk cache synchronously to ensure that image is loaded in the same runloop.
     * This flag can avoid flashing during cell reuse if you disable memory cache or in some other cases.
     */
    SDWebImageQueryDiskSync = 1 << 14,
    
    /**
     * By default, when the cache missed, the image is download from the network. This flag can prevent network to load from cache only.
     */
    SDWebImageFromCacheOnly = 1 << 15,
    /**
     * By default, when you use `SDWebImageTransition` to do some view transition after the image load finished, this transition is only applied for image download from the network. This mask can force to apply view transition for memory and disk cache as well.
     */
    SDWebImageForceTransition = 1 << 16
};
```

## SDWebImageManagerDelegate代理方法

```objective-c
@protocol SDWebImageManagerDelegate <NSObject>

@optional

//当缓存没有发现当前图片，那么会查看调用者是否实现改方法，如果return一个no，则不会继续下载这张图片
- (BOOL)imageManager:(nonnull SDWebImageManager *)imageManager shouldDownloadImageForURL:(nullable NSURL *)imageURL;

- (BOOL)imageManager:(nonnull SDWebImageManager *)imageManager shouldBlockFailedURL:(nonnull NSURL *)imageURL withError:(nonnull NSError *)error;

//当图片下载完成但是未添加到缓存里面，这时候调用该方法可以给图片旋转方向，注意是异步执行， 防止阻塞主线程
- (nullable UIImage *)imageManager:(nonnull SDWebImageManager *)imageManager transformDownloadedImage:(nullable UIImage *)image withURL:(nullable NSURL *)imageURL;

@end
```

## SDWebImageManager属性和方法

```objective-c
@interface SDWebImageManager : NSObject

@property (weak, nonatomic, nullable) id <SDWebImageManagerDelegate> delegate;

@property (strong, nonatomic, readonly, nullable) SDImageCache *imageCache;
@property (strong, nonatomic, readonly, nullable) SDWebImageDownloader *imageDownloader;

//这个缓存block的作用是，在block内部进行缓存key的生成并return，key就是根据图片url根据规则生成，sd的缓存策略就是key是图片url，value就是image
@property (nonatomic, copy, nullable) SDWebImageCacheKeyFilterBlock cacheKeyFilter;

@property (nonatomic, copy, nullable) SDWebImageCacheSerializerBlock cacheSerializer;

+ (nonnull instancetype)sharedManager;

//根据特定的cache和downloader生成一个新的SDWebImageManager
- (nonnull instancetype)initWithCache:(nonnull SDImageCache *)cache downloader:(nonnull SDWebImageDownloader *)downloader NS_DESIGNATED_INITIALIZER;

//下载图片的关键方法，第一个参数图片url，第二个参数设置下载多样操作，第三个参数下载中进度block，第四个参数下载完成后回调
- (nullable id <SDWebImageOperation>)loadImageWithURL:(nullable NSURL *)url
                                              options:(SDWebImageOptions)options
                                             progress:(nullable SDWebImageDownloaderProgressBlock)progressBlock
                                            completed:(nullable SDInternalCompletionBlock)completedBlock;

//缓存图片根据指定的url和image
- (void)saveImageToCache:(nullable UIImage *)image forURL:(nullable NSURL *)url;

//取消所有当前的operation
- (void)cancelAll;

//检查是否有图片正在下载
- (BOOL)isRunning;

//异步检查图片是否已经缓存
- (void)cachedImageExistsForURL:(nullable NSURL *)url
                     completion:(nullable SDWebImageCheckCacheCompletionBlock)completionBlock;

//检查图片是否缓存 在磁盘中
- (void)diskImageExistsForURL:(nullable NSURL *)url
                   completion:(nullable SDWebImageCheckCacheCompletionBlock)completionBlock;


//给定一个url返回缓存的字符串key
- (nullable NSString *)cacheKeyForURL:(nullable NSURL *)url;

@end
```





对动图加载的支持：

FLAnimatedImage

## 加载图片流程

1. 加载图片

   SDWebImageManager

   ​	缓存

   ​	异步加载图片

2. 加载完成之后（raw Data）

   解码

   block

   flag

3. 取消重复下载任务 每个对象一个NSMapTable

   1. key-value
   2. key：当前Class
   3. value：当前对象

4. NSMapTable

