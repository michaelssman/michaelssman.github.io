# PDF显示CGPDFDocumentRef

摘要: 学习使用自定义view加载显示pdf；

前言

在IOS中预览pdf文件，显示pdf文件一般使用两种方式，一种是UIWebView，这种方式怎么说呢优点就是除了简单还是简单，直接显示pdf文件；另外的一种是自定义UIView，配合CGPDFDocumentRef读取pdf文件里面的内容，在自定义的drawRect方法中描绘获取的pdf内容；其实还有一种的方式，就是苹果在IOS4.0后，apple推出新的文件预览控件：QLPreveiewController,支持pdf文件阅读。今天我主要写的是自定义View+CGPDFDocumentRef显示pdf文件；

 

（一）先运用CGPDFDocumentRef获取指定的pdf内容；下面是我写出的获取内容的方法；

```
 1 //用于本地pdf文件
 2 - (CGPDFDocumentRef)pdfRefByFilePath:(NSString *)aFilePath {
 3     CFStringRef path;
 4     CFURLRef url;
 5     CGPDFDocumentRef document;
 6     
 7     path = CFStringCreateWithCString(NULL, [aFilePath UTF8String], kCFStringEncodingUTF8);
 8     url = CFURLCreateWithFileSystemPath(NULL, path, kCFURLPOSIXPathStyle, NO);
 9     document = CGPDFDocumentCreateWithURL(url);
10     
11     CFRelease(path);
12     CFRelease(url);
13     
14     return document;
15 }
16 
17 - (NSString *)getPdfPathByFile:(NSString *)fileName {
18     return [[NSBundle mainBundle] pathForResource:fileName ofType:@".pdf"];
19 }
20 
21 //用于网络pdf文件
22 - (CGPDFDocumentRef)pdfRefByDataByUrl:(NSString *)aFileUrl {
23     NSData *pdfData = [NSData dataWithContentsOfFile:aFileUrl];
24     CFDataRef dataRef = (__bridge_retained CFDataRef)(pdfData);
25     
26     CGDataProviderRef proRef = CGDataProviderCreateWithCFData(dataRef);
27     CGPDFDocumentRef pdfRef = CGPDFDocumentCreateWithProvider(proRef);
28     
29     CGDataProviderRelease(proRef);
30     CFRelease(dataRef);
31     
32     return pdfRef;
33 }
```

 

通过文件路径解析pdf文件，返回文件内容。

 

（二）第二步就是在自定义的View中绘制pdf内容；``

```
- (void)drawRect:(CGRect)rect {
    CGContextRef context = UIGraphicsGetCurrentContext();
    CGPDFPageRef pageRef = CGPDFDocumentGetPage([self createPDFFromExistFile], _pageNumber);//获取指定页的内容如_pageNumber=1，获取的是pdf第一页的内容
    CGRect mediaRect = CGPDFPageGetBoxRect(pageRef, kCGPDFCropBox);//pdf内容的rect
    
    CGContextRetain(context);
    CGContextSaveGState(context);
    
    [[UIColor whiteColor] set];
    CGContextFillRect(context, rect);//填充背景色，否则为全黑色；
    
    CGContextTranslateCTM(context, 0, rect.size.height);//设置位移，x，y；
    
    CGFloat under_bar_height = 64.0f;
    CGContextScaleCTM(context, rect.size.width / mediaRect.size.width, -(rect.size.height + under_bar_height) / mediaRect.size.height);
    
    CGContextSetInterpolationQuality(context, kCGInterpolationHigh);
    CGContextSetRenderingIntent(context, kCGRenderingIntentDefault);
    CGContextDrawPDFPage(context, pageRef);//绘制pdf
    
    CGContextRestoreGState(context);
    CGContextRelease(context);
}
```

 

以上就是绘制pdf的内容的代码，代码每行我都写了注释，其实都是很好了解的。

当然上面的只是显示pdf指定页的逻辑，要想显示整个pdf文件的内容，需要配合UIScrollView或者是UIPageViewController去实现，原理也很简单，结合上述的逻辑只要传入一个pageIndex的值，刷新页面内容就可以实现。下面是我写的一个列子，pageviewcontroller实现；

```
- (void)viewDidLoad {
    [super viewDidLoad];
    self.pdfArr = [NSMutableArray array];
    NSDictionary *options = [NSDictionary  dictionaryWithObject:[NSNumber numberWithInteger:UIPageViewControllerSpineLocationMin] forKey:UIPageViewControllerOptionSpineLocationKey];
    self.pageVC = [[UIPageViewController alloc]initWithTransitionStyle:UIPageViewControllerTransitionStylePageCurl navigationOrientation:UIPageViewControllerNavigationOrientationHorizontal options:options];
    _pageVC.view.frame = self.view.bounds;
    _pageVC.delegate = self;
    _pageVC.dataSource = self;
    [self addChildViewController:_pageVC];
    
    PDFView *testPdf = [[PDFView alloc]initWithFrame:self.view.frame atPage:1 andFileName:@"Reader"];
    CGPDFDocumentRef pdfRef = [testPdf createPDFFromExistFile];
    size_t count = CGPDFDocumentGetNumberOfPages(pdfRef);//这个位置主要是获取pdf页码数；
    
    for (int i = 0; i < count; i++) {
        UIViewController *pdfVC = [[UIViewController alloc] init];
        PDFView *pdfView = [[PDFView alloc] initWithFrame:self.view.frame atPage:(i+1) andFileName:@"Reader"];
        [pdfVC.view addSubview:pdfView];
        
        [_pdfArr addObject:pdfVC];
    }
    
    
    [_pageVC setViewControllers:[NSArray arrayWithObject:_pdfArr[0]] direction:UIPageViewControllerNavigationDirectionForward animated:YES completion:nil];
    [self.view addSubview:_pageVC.view];
    
}
//委托方法；
- (UIViewController *)viewControllerAtIndex:(NSInteger)index
{
    //Create a new view controller and pass suitable data.
    
    if (([_pdfArr count] == 0 )|| (index > [_pdfArr count]) ) {
        return nil;
    }
    
    
    NSLog(@"index = %ld",(long)index);
    
    return (UIViewController *)_pdfArr[index];
}


- (NSUInteger) indexOfViewController:(UIViewController *)viewController
{
    return [self.pdfArr indexOfObject:viewController];
}


- (UIViewController *)pageViewController:(UIPageViewController *)pageViewController viewControllerAfterViewController:(UIViewController *)viewController
{
    NSUInteger index = [self indexOfViewController:(UIViewController *)viewController];
    if (index == NSNotFound) {
        return nil;
    }
    
    index++;
    
    if (index == [_pdfArr count]){
        return  nil;
    }
    
    return [self viewControllerAtIndex:index];
}

- (UIViewController *)pageViewController:(UIPageViewController *)pageViewController viewControllerBeforeViewController:(UIViewController *)viewController
{
    NSUInteger index = [self indexOfViewController:(UIViewController *)viewController];
    if ((index == 0 ) || (index == NSNotFound)){
        return nil;
    }
    
    index--;
    
    return [self viewControllerAtIndex:index];
}
```

 

以上就是简单的实现；

 

（三）对于第三种方法，使用QLPreveiewController去预览pdf，我就没有具体的通过代码去实现pdf的预览，在网络上应该有资源可查；

[QLPreveiewController的用法；](http://wanggp.iteye.com/blog/1129059)已经简单的说了一下怎么去预览pdf内容，也是很简单的，如果想要自定义显示的话，需要自己花时间去研究了。

 

总结

不管是选用哪一种方式，都可以实现加载pdf文件；webview除了简单粗暴但是只能作为简单的浏览，CGPDFDocumentRef需要开发者自己去实现显示的逻辑，但这样可控性会比较好，显示的效果也是可以自定义，QLPreveiewController的话，我没有自己去实现过，所以大家可以去试试。