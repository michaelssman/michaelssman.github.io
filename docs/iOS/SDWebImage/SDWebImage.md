# SDWebImage

## 如何设计一个图片加载库

必须具备以下几个特点：

1. 给别人去用，提供一个入口，调用入口。

   提供入口的方式：

   分类

   面向对象的方式，让别人创建对象来调用库。

   分类更好一点，对业务没有打对入侵。

   SDWebImage也是提供分类的方式供使用。

2. 异步加载（加载图片使用网络）线程相关的知识点。

3. 速度快，用户体验，设计缓存。支持缓存模块。

   1. 内存
   2. 磁盘

4. 同一个UIImageView不能重复下载。

5. 对图片格式进行解码。

   图片存在目录下是一个二进制文件raw data。jpeg或png格式。 用UIImage读取到内存中（Data Buffer）。这个Data Buffer不能直接显示的，要把Data Buffer显示到屏幕上，通过UIIMageView做一些处理，这个处理就是对Data Buffer做解码操作，解码完成之后就变成了Image Buffer，也就是像素信息，绘制图片的时候必须知道像素点的信息。

   对于硬件GPU，CoreGraphics，OpenGLES来说，会通过读取Image Buffer来进行绘制。

   绘制并不是直接绘制到屏幕上，而是绘制到帧缓冲区。显示图片是一帧一帧的图片。屏幕上显示的信息就是帧缓冲区的信息。

   Data Buffer转成ImageBuffer是在主线程操作的。所以图片比较大的时候主线程压力大。所以在子线程中去转。

最上层是分类UIImageview UIButton等，所有的分类都是调用UIView+WebCache。

加载一张图片：

1. 请求
2. 缓存

UIView+WebCache把任务交给了SDWebImageManager。SDWebImageManager相当于中间者。

SDWebImageManager的作用是将任务交给对应的类，完成对应的职责。

- 加载缓存交给SDImageCache完成。
  - 磁盘缓存
  - 内存缓存

- 下载图片交给SDWebImageDownloader来完成。
  - 网络请求。

**模块间的解耦：通过协议，暴露依赖关系。**

不管加载缓存和下载图片底层怎么变，上层接口不变。

SDWebImageManager收集所需要完成的功能，分发给对应组件，对应组件完成核心逻辑的调用。

UIView+WebCache发起调用。

具体发起逻辑的地方就在`UIView+WebCache`的下面方法中：

```objective-c
- (void)sd_internalSetImageWithURL:(nullable NSURL *)url
                  placeholderImage:(nullable UIImage *)placeholder
                           options:(SDWebImageOptions)options
                      operationKey:(nullable NSString *)operationKey
             internalSetImageBlock:(nullable SDInternalSetImageBlock)setImageBlock
                          progress:(nullable SDWebImageDownloaderProgressBlock)progressBlock
                         completed:(nullable SDExternalCompletionBlock)completedBlock
                           context:(nullable NSDictionary<NSString *, id> *)context {
		//唯一标识
    NSString *validOperationKey = operationKey ?: NSStringFromClass([self class]);
    //类似字典的数据结构
    //点进去发现是NSMapTable
    //取消重复下载的任务
    [self sd_cancelImageLoadOperationWithKey:validOperationKey];
    objc_setAssociatedObject(self, &imageURLKey, url, OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    
    dispatch_group_t group = context[SDWebImageInternalSetImageGroupKey];
    if (!(options & SDWebImageDelayPlaceholder)) {
        if (group) {
            dispatch_group_enter(group);
        }
        dispatch_main_async_safe(^{
            [self sd_setImage:placeholder imageData:nil basedOnClassOrViaCustomSetImageBlock:setImageBlock cacheType:SDImageCacheTypeNone imageURL:url];
        });
    }
    
                             
    if (url) {
#if SD_UIKIT
        // check if activityView is enabled or not
        if ([self sd_showActivityIndicatorView]) {
            [self sd_addActivityIndicator];
        }
#endif
        
        // reset the progress
        self.sd_imageProgress.totalUnitCount = 0;
        self.sd_imageProgress.completedUnitCount = 0;
        
        SDWebImageManager *manager = [context objectForKey:SDWebImageExternalCustomManagerKey];
        if (!manager) {
            manager = [SDWebImageManager sharedManager];
        }
        
        __weak __typeof(self)wself = self;
        SDWebImageDownloaderProgressBlock combinedProgressBlock = ^(NSInteger receivedSize, NSInteger expectedSize, NSURL * _Nullable targetURL) {
            wself.sd_imageProgress.totalUnitCount = expectedSize;
            wself.sd_imageProgress.completedUnitCount = receivedSize;
            if (progressBlock) {
                progressBlock(receivedSize, expectedSize, targetURL);
            }
        };
        id <SDWebImageOperation> operation = [manager loadImageWithURL:url options:options progress:combinedProgressBlock completed:^(UIImage *image, NSData *data, NSError *error, SDImageCacheType cacheType, BOOL finished, NSURL *imageURL) {
            __strong __typeof (wself) sself = wself;
            if (!sself) { return; }
#if SD_UIKIT
            [sself sd_removeActivityIndicator];
#endif
            // if the progress not been updated, mark it to complete state
            if (finished && !error && sself.sd_imageProgress.totalUnitCount == 0 && sself.sd_imageProgress.completedUnitCount == 0) {
                sself.sd_imageProgress.totalUnitCount = SDWebImageProgressUnitCountUnknown;
                sself.sd_imageProgress.completedUnitCount = SDWebImageProgressUnitCountUnknown;
            }
            BOOL shouldCallCompletedBlock = finished || (options & SDWebImageAvoidAutoSetImage);
            BOOL shouldNotSetImage = ((image && (options & SDWebImageAvoidAutoSetImage)) ||
                                      (!image && !(options & SDWebImageDelayPlaceholder)));
            SDWebImageNoParamsBlock callCompletedBlockClojure = ^{
                if (!sself) { return; }
                if (!shouldNotSetImage) {
                    [sself sd_setNeedsLayout];
                }
                if (completedBlock && shouldCallCompletedBlock) {
                    completedBlock(image, error, cacheType, url);
                }
            };
            
            // case 1a: we got an image, but the SDWebImageAvoidAutoSetImage flag is set
            // OR
            // case 1b: we got no image and the SDWebImageDelayPlaceholder is not set
            if (shouldNotSetImage) {
                dispatch_main_async_safe(callCompletedBlockClojure);
                return;
            }
            
            UIImage *targetImage = nil;
            NSData *targetData = nil;
            if (image) {
                // case 2a: we got an image and the SDWebImageAvoidAutoSetImage is not set
                targetImage = image;
                targetData = data;
            } else if (options & SDWebImageDelayPlaceholder) {
                // case 2b: we got no image and the SDWebImageDelayPlaceholder flag is set
                targetImage = placeholder;
                targetData = nil;
            }
            
#if SD_UIKIT || SD_MAC
            // check whether we should use the image transition
            SDWebImageTransition *transition = nil;
            if (finished && (options & SDWebImageForceTransition || cacheType == SDImageCacheTypeNone)) {
                transition = sself.sd_imageTransition;
            }
#endif
            dispatch_main_async_safe(^{
                if (group) {
                    dispatch_group_enter(group);
                }
#if SD_UIKIT || SD_MAC
                [sself sd_setImage:targetImage imageData:targetData basedOnClassOrViaCustomSetImageBlock:setImageBlock transition:transition cacheType:cacheType imageURL:imageURL];
#else
                [sself sd_setImage:targetImage imageData:targetData basedOnClassOrViaCustomSetImageBlock:setImageBlock cacheType:cacheType imageURL:imageURL];
#endif
                if (group) {
                    // compatible code for FLAnimatedImage, because we assume completedBlock called after image was set. This will be removed in 5.x
                    BOOL shouldUseGroup = [objc_getAssociatedObject(group, &SDWebImageInternalSetImageGroupKey) boolValue];
                    if (shouldUseGroup) {
                        dispatch_group_notify(group, dispatch_get_main_queue(), callCompletedBlockClojure);
                    } else {
                        callCompletedBlockClojure();
                    }
                } else {
                    callCompletedBlockClojure();
                }
            });
        }];
        [self sd_setImageLoadOperation:operation forKey:validOperationKey];
    } else {
        dispatch_main_async_safe(^{
#if SD_UIKIT
            [self sd_removeActivityIndicator];
#endif
            if (completedBlock) {
                NSError *error = [NSError errorWithDomain:SDWebImageErrorDomain code:-1 userInfo:@{NSLocalizedDescriptionKey : @"Trying to load a nil url"}];
                completedBlock(nil, error, SDImageCacheTypeNone, url);
            }
        });
    }
}
```

这个方法是发起网络请求还是加载缓存最开始的地方。

### SDWebImageManager

调用SDWebImageManager发起一个请求（网络请求，缓存请求）。

获取 SDWebImageManager 中的单例调用`- (**id** <SDWebImageOperation>)loadImageWithURL:(**nullable** NSURL *)url options:(SDWebImageOptions)options progress:(**nullable** SDWebImageDownloaderProgressBlock)progressBlock completed:(**nullable** SDInternalCompletionBlock)completedBlock`方法来获取图片。

而这个 manager 获取图片的过程有大体上分为两部分

1. 它首先会在 SDImageCache 中寻找图片是否有对应的缓存, 它会以 url 作为 数据的索引先在内存中寻找是否有对应的缓存, 如果缓存未命中就 会在磁盘中利用 MD5 处理过的 key 来继续查询对应的数据, 如果 找到了, 就会把磁盘中的缓存备份到内存中。
2. 然而, 假设我们在内存和磁盘缓存中都没有命中, 那么 manager 就 会调用它持有的一个 SDWebImageDownloader 对象的方法`- (**nullable** SDWebImageDownloadToken *)downloadImageWithURL:(**nullable** NSURL *)url options:(SDWebImageDownloaderOptions)options progress:(**nullable** SDWebImageDownloaderProgressBlock)progressBlock completed:(**nullable** SDWebImageDownloaderCompletedBlock)completedBlock`来下载图片, 这个方法会在执行的过程 中调用另一个方法 addProgressCallback:andCompletedBlock:fotURL:createCallback: 来存储下载过程中和下载完成的回调, 当回调块是第一次添加的时 候, 方法会实例化一个 NSMutableURLRequest 和 SDWebImageDownloaderOperation , 并将后者加入 downloader 持 有的下载队列开始图片的异步下载.

而在图片下载完成之后, 就会在主线程设置 image, 完成整个图像 的异步下载和配置.

```
//id <SDWebImageOperation> operation代表缓存请求，网络请求 的任务
id <SDWebImageOperation> operation = [manager loadImageWithURL:url options:options progress:combinedProgressBlock completed:^(UIImage *image, NSData *data, NSError *error, SDImageCacheType cacheType, BOOL finished, NSURL *imageURL) {}
```

SDWebImageManager的loadImageWithURL方法中有一个SDWebImageCombinedOperation中间者。

- SDWebImageCombinedOperation
  - cacheOperation

先加载缓存。



下载的任务怎么取消

已经调度的任务 不能取消。



## 目录结构

- Downloader
   ○ SDWebImageDownloader：是专门用来下载图片和优化图片加载的，跟缓存没有关系
   ○ SDWebImageDownloaderOperation：继承于 NSOperation，用来处理下载任务的
- Cache
   ○ SDImageCache：用来处理内存缓存和磁盘缓存（可选)的，其中磁盘缓存是异步进行的，因此不会阻塞主线程
- Utils
   ○ SDWebImageManager：作为 UIImageView+WebCache 背后的默默付出者，主要功能是将图片下载（SDWebImageDownloader）和图片缓存（SDImageCache）两个独立的功能组合起来
   ○ SDWebImageDecoder：图片解码器，用于图片下载完成后进行解码
   ○ SDWebImagePrefetcher：预下载图片，方便后续使用，图片下载的优先级低。
- Categories
   ○ UIView+WebCacheOperation：用来记录图片加载的 operation，方便需要时取消和移除图片加载的 operation
   ○ UIImageView+WebCache：集成 SDWebImageManager 的图片下载和缓存功能到 UIImageView 的方法中，方便调用方的简单使用
   ○ UIImageView+HighlightedWebCache：跟 UIImageView+WebCache 类似，也是包装了 SDWebImageManager，只不过是用于加载 highlighted 状态的图片
   ○ UIButton+WebCache：跟 UIImageView+WebCache 类似，集成 SDWebImageManager 的图片下载和缓存功能到 UIButton 的方法中，方便调用方的简单使用
   ○ MKAnnotationView+WebCache：跟 UIImageView+WebCache 类似
   ○ NSData+ImageContentType：用于获取图片数据的格式（JPEG、PNG等）
   ○ UIImage+GIF：用于加载 GIF 动图
   ○ UIImage+MultiFormat：根据不同格式的二进制数据转成 UIImage 对象
   ○ UIImage+WebP：用于解码并加载 WebP 图片
- Other
   ○ SDWebImageOperation（协议）
   ○ SDWebImageCompat（宏定义、常量、通用函数）

## 工作流程

![工作流程](SDWebImage.assets/a127008dd74a4616b762e78ca2041244~tplv-k3u1fbpfcp-zoom-in-crop-mark:1304:0:0:0.awebp)

- 入口 setImageWithURL:placeholderImage:options: 会先把 placeholderImage 显示，然后 SDWebImageManager 根据 URL 开始处理图片。

- 进入 SDWebImageManager-downloadWithURL:delegate:options:userInfo:交给 SDImageCache 从缓存查找图片是否已经下载 queryDiskCacheForKey:delegate:userInfo:。

- 先从内存图片缓存查找是否有图片，如果内存中已经有图片缓存，SDImageCacheDelegate 回调 imageCache:didFindImage:forKey:userInfo: 到 SDWebImageManager。

- SDWebImageManagerDelegate 回调 webImageManager:didFinishWithImage: 到 UIImageView+WebCache 等前端展示图片。

- 如果内存缓存中没有，生成 NSInvocationOperation 添加到队列开始从硬盘查找图片是否已经缓存。

- 根据 URLKey 在硬盘缓存目录下尝试读取图片文件。这一步是在 NSOperation 进行的操作，所以回主线程进行结果回调 notifyDelegate:。

- 如果从硬盘读取到了图片，将图片添加到内存缓存中（如果空闲内存过小，会先清空内存缓存）。SDImageCacheDelegate 回调 imageCache:didFindImage:forKey:userInfo:进而回调展示图片。

- 如果从硬盘缓存目录读取不到图片，说明所有缓存都不存在该图片，需要下载图片，回调 imageCache:didNotFindImageForKey:userInfo:。

- 共享或重新生成一个下载器 SDWebImageDownloader 开始下载图片。

- 图片下载由NSURLSession，实现相关 delegate 来判断图片下载中、下载完成和下载失败。

  - 下载完成之后，会调用解码返回image，而不是直接返回的data。

  ```objective-c
  //下载完成
  - (void)URLSession:(NSURLSession *)session task:(NSURLSessionTask *)task didCompleteWithError:(NSError *)error {
      // If we already cancel the operation or anything mark the operation finished, don't callback twice
      if (self.isFinished) return;
      
      @synchronized(self) {
          self.dataTask = nil;
          __block typeof(self) strongSelf = self;
          dispatch_async(dispatch_get_main_queue(), ^{
              [[NSNotificationCenter defaultCenter] postNotificationName:SDWebImageDownloadStopNotification object:strongSelf];
              if (!error) {
                  [[NSNotificationCenter defaultCenter] postNotificationName:SDWebImageDownloadFinishNotification object:strongSelf];
              }
          });
      }
      
      // make sure to call `[self done]` to mark operation as finished
      if (error) {
          // custom error instead of URLSession error
          if (self.responseError) {
              error = self.responseError;
          }
          [self callCompletionBlocksWithError:error];
          [self done];
      } else {
          if ([self callbacksForKey:kCompletedCallbackKey].count > 0) {
              NSData *imageData = [self.imageData copy];
              self.imageData = nil;
              // data decryptor
              if (imageData && self.decryptor) {
                  imageData = [self.decryptor decryptedDataWithData:imageData response:self.response];
              }
              if (imageData) {
                  /**  if you specified to only use cached data via `SDWebImageDownloaderIgnoreCachedResponse`,
                   *  then we should check if the cached data is equal to image data
                   */
                  if (self.options & SDWebImageDownloaderIgnoreCachedResponse && [self.cachedData isEqualToData:imageData]) {
                      self.responseError = [NSError errorWithDomain:SDWebImageErrorDomain code:SDWebImageErrorCacheNotModified userInfo:nil];
                      // call completion block with not modified error
                      [self callCompletionBlocksWithError:self.responseError];
                      [self done];
                  } else {
                      // decode the image in coder queue
                      dispatch_async(self.coderQueue, ^{
                          @autoreleasepool {
                              UIImage *image = SDImageLoaderDecodeImageData(imageData, self.request.URL, [[self class] imageOptionsFromDownloaderOptions:self.options], self.context);
                              CGSize imageSize = image.size;
                              if (imageSize.width == 0 || imageSize.height == 0) {
                                  [self callCompletionBlocksWithError:[NSError errorWithDomain:SDWebImageErrorDomain code:SDWebImageErrorBadImageData userInfo:@{NSLocalizedDescriptionKey : @"Downloaded image has 0 pixels"}]];
                              } else {
                                  [self callCompletionBlocksWithImage:image imageData:imageData error:nil finished:YES];
                              }
                              [self done];
                          }
                      });
                  }
              } else {
                  [self callCompletionBlocksWithError:[NSError errorWithDomain:SDWebImageErrorDomain code:SDWebImageErrorBadImageData userInfo:@{NSLocalizedDescriptionKey : @"Image data is nil"}]];
                  [self done];
              }
          } else {
              [self done];
          }
      }
  }
  ```

- connection:didReceiveData: 中利用 ImageIO 做了按图片下载进度加载效果。connectionDidFinishLoading: 数据下载完成后交给 SDWebImageDecoder 做图片解码处理。

- 图片解码处理在一个 NSOperationQueue 完成，不会拖慢主线程 UI。如果有需要对下载的图片进行二次处理，最好也在这里完成，效率会好很多。

- 在主线程 notifyDelegateOnMainThreadWithInfo: 宣告解码完成，imageDecoder:didFinishDecodingImage:userInfo: 回调给 SDWebImageDownloader。

- imageDownloader:didFinishWithImage: 回调给 SDWebImageManager 告知图片下载完成。

- 通知所有的 downloadDelegates 下载完成，回调给需要的地方展示图片。

- 将图片保存到 SDImageCache 中，内存缓存和硬盘缓存同时保存。写文件到硬盘也在以单独 NSInvocationOperation 完成，避免拖慢主线程。

- SDImageCache 在初始化的时候会注册一些消息通知，在内存警告或退到后台的时候清理内存图片缓存，应用结束的时候清理过期图片。

- SDWebImagePrefetcher 可以预先下载图片，方便后续使用。

## 常见面试题

1. 图片文件缓存的时间有多长：1周

```
_maxCacheAge ＝ kDefaultCacheMaxCacheAge
```

1. SDWebImage 的内存缓存是用什么实现的？

```
NSCache
```

1. SDWebImage 的最大并发数是多少？

```
maxConcurrentDownloads ＝ 6
```

- 是程序固定死了，可以通过属性进行调整！

1. SDWebImage 支持动图吗？GIF

```
1. #import <ImageIO/ImageIO.h>
2. [UIImage animatedImageWithImages:images duration:duration];
```

1. SDWebImage是如何区分不同格式的图像的
   - 根据图像数据第一个字节来判断的！
   - PNG：压缩比没有JPG高，但是无损压缩，解压缩性能高，苹果推荐的图像格式！
   - JPG：压缩比最高的一种图片格式，有损压缩！最多使用的场景，照相机！解压缩的性能不好！
   - GIF：序列桢动图，特点：只支持256种颜色！最流行的时候在1998～1999，有专利的！

6.SDWebImage 缓存图片的名称是怎么确定的！

- `md5`
- 如果单纯使用 文件名保存，重名的几率很高！
- 使用 MD5 的散列函数！对完整的 URL 进行 md5，结果是一个 32 个字符长度的字符串！

### SDWebImage 的内存警告是如何处理的！

利用通知中心观察

- `- UIApplicationDidReceiveMemoryWarningNotification` 接收到内存警告的通知
- 执行 `clearMemory` 方法，清理内存缓存！
- `- UIApplicationWillTerminateNotification` 接收到应用程序将要终止通知
- 执行 `cleanDisk` 方法，清理磁盘缓存，将所有缓存目录中的文件，全部删除！
- `- UIApplicationDidEnterBackgroundNotification` 接收到应用程序进入后台通知
- 执行 `backgroundCleanDisk` 方法，后台清理磁盘！

通过以上通知监听，能够保证缓存文件的大小始终在控制范围之内！
