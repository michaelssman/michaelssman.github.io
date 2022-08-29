# CFRunLoopObserverRef

## Observer监听RunLoop状态变化

runloop有`source` `timer` `observer`，Observer用来监听RunLoop状态的。

(kCFRunLoopBeforeWaiting,kCFRunLoopAfterWaiting等)

## CFRunLoopObserverRef

**CFRunLoopObserverRef**：是观察者，我们可以通过CFRunLoopObserverCreateWithHandler函数来创建一个观察者（函数会有一个block回调），来对RunLoop进行观察，当RunLoop状态变化时，会触发block回调，回调会返回对应的状态，我们可以在回调里做相应做的操作。

（1）CFRunLoopObserverRef是观察者，能够监听RunLoop的状态改变

（2）如何监听

```objective-c
//创建一个runloop监听者
CFRunLoopObserverRef observer = CFRunLoopObserverCreateWithHandler(CFAllocatorGetDefault(),kCFRunLoopAllActivities, YES, 0, ^(CFRunLoopObserverRef observer, CFRunLoopActivity activity) {
NSLog(@"监听runloop状态改变---%zd",activity);
});
//为runloop添加一个监听者
CFRunLoopAddObserver(CFRunLoopGetCurrent(), observer, kCFRunLoopDefaultMode);
//释放Observer
CFRelease(observer);
```

（3）状态

## 监听的几个状态：

整个事务的执行状况。

kCFRunLoopBeforeWaiting和kCFRunLoopAfterWaiting关于事务生命周期。runloop会休眠。

kCFRunLoopBeforeWaiting和kCFRunLoopAfterWaiting之间是休息。

kCFRunLoopAfterWaiting和kCFRunLoopBeforeWaiting之间是在run，可以知道做一次事情需要的时间。这是一次循环。

```c
/* Run Loop Observer Activities */
typedef CF_OPTIONS(CFOptionFlags, CFRunLoopActivity) {
    kCFRunLoopEntry = (1UL << 0),					//1 即将进入RunLoop
    kCFRunLoopBeforeTimers = (1UL << 1),	//2 即将处理NSTimer
    kCFRunLoopBeforeSources = (1UL << 2), //4 即将处理Sources
    kCFRunLoopBeforeWaiting = (1UL << 5),	//32 即将进入休眠，休眠之前
    kCFRunLoopAfterWaiting = (1UL << 6),	//64 唤醒之前
    kCFRunLoopExit = (1UL << 7),					//128 即将退出runloop
    kCFRunLoopAllActivities = 0x0FFFFFFFU //所有状态改变
};
```

监听RunLoop的状态变化可以用于优化程序，比如表格要加载大量数据、图片、处理耗时操作、会造成UI卡顿，这时就可以利用监听RunLoop，**在他休眠时唤醒它去处理这些任务**。

点击CFRunLoopRef到API中发现定义了Observer的相关声明CFRunLoopObserverRef,这正是我们想要的:

```
typedef struct CF_BRIDGED_MUTABLE_TYPE(id) __CFRunLoop * CFRunLoopRef;

typedef struct CF_BRIDGED_MUTABLE_TYPE(id) __CFRunLoopSource * CFRunLoopSourceRef;

typedef struct CF_BRIDGED_MUTABLE_TYPE(id) __CFRunLoopObserver * CFRunLoopObserverRef;

typedef struct CF_BRIDGED_MUTABLE_TYPE(NSTimer) __CFRunLoopTimer * CFRunLoopTimerRef;
```

找到了CFRunLoopObserverRef之后就是要创建一个Observer了,在API中找到如下函数声明:

```
CF_EXPORT CFRunLoopObserverRef CFRunLoopObserverCreate(CFAllocatorRef allocator, CFOptionFlags activities, Boolean repeats, CFIndex order, CFRunLoopObserverCallBack callout, CFRunLoopObserverContext *context);
```

这正是我们想要的创建OBserver的方法,看看它需要的参数:

- CFAllocatorRef allocator 
- CFOptionFlags activities 表示要监听RunLoop的变化的状态(kCFRunLoopAfterWaiting等)
- Boolean repeats 表示是否重复监听
- CFIndex order 这个传0即可暂时没研究
- CFRunLoopObserverCallBack callout 表示监听的回调方法(C语言的方法)
- CFRunLoopObserverContext *context 表示上下文环境,用于C语言的方法与OC的互传传值

既然如此现在来创建一个CFRunLoopObserverContext,在API中也找到一个CFRunLoopObserverContext的声明

```
typedef struct {

CFIndex  version; //暂时传0不研究

void *  info; //重要就是C语言要与OC传递数据的引用.void *表示可以传递任何类型的数据

const void *(*retain)(const void *info);//引用

void  (*release)(const void *info);//回收

CFStringRef  (*copyDescription)(const void *info);//描述,暂时没用

} CFRunLoopObserverContext;
```

### 创建一个CFRunLoopObserverContext

```
CFRunLoopObserverContext context = {
0,
(__bridge void *)(self),//OC对象传递过去
&CFRetain,
&CFRelease,
NULL
};
```

点击上面的CFRunLoopObserverCallBack是API跳到这样的一个声明,即告诉我们监听的回调方法的参数怎么定义

```
typedef void (*CFRunLoopObserverCallBack)(CFRunLoopObserverRef observer, CFRunLoopActivity activity, void *info);
```

接下来新建一个C语言用于回调方法

```
static void runLoopOserverCallBack(CFRunLoopObserverRef observer, CFRunLoopActivity activity, void *info){

//void *info正是我们要用来与OC传值的,这边可以转成OC对象,前面我们传进来的时候是self

}
```

### 创建observer

```
//创建一个监听
static CFRunLoopObserverRef observer;
observer = CFRunLoopObserverCreate(NULL, kCFRunLoopAfterWaiting, YES, 0, &runLoopOserverCallBack,&context);

//注册监听
CFRunLoopAddObserver(runLoopRef, observer, kCFRunLoopCommonModes);

//销毁
CFRelease(observer);
```

### 到此结束,完整代码如下:

###### 为了让RunLoop一直工作,这边添加了一个NSTimer,不过他什么都没做,只是为了让RunLoop一直工作

```objective-c
@interface ViewController ()

@property (nonatomic, strong)NSTimer *runLoopObServerTimer;

@property (nonatomic, copy)NSString *name;

@end

@implementation ViewController

- (void)viewDidLoad {

[super viewDidLoad];

[self addRunLoopObserver];

[self initData];

}

- (void)initData{

_name = @"piaojin";

//默认会添加到当前的runLoop中去,不做任何事情,为了让runLoop一直处理任务而不去睡眠

_runLoopObServerTimer = [NSTimer scheduledTimerWithTimeInterval:0.001 target:self selector:@selector(timerMethod) userInfo:nil repeats:YES];

}

- (void)addRunLoopObserver{

//获取当前的CFRunLoopRef
CFRunLoopRef runLoopRef = CFRunLoopGetCurrent();

//创建上下文,用于控制器数据的获取
CFRunLoopObserverContext context = {
0,
(__bridge void *)(self),//self传递过去
&CFRetain,
&CFRelease,
NULL
};

//创建一个监听
static CFRunLoopObserverRef observer;
observer = CFRunLoopObserverCreate(NULL, kCFRunLoopBeforeWaiting, YES, 0, &runLoopOserverCallBack,&context);

//注册监听
CFRunLoopAddObserver(runLoopRef, observer, kCFRunLoopCommonModes);

//销毁
CFRelease(observer);
}

//监听CFRunLoopRef回调函数

static void runLoopOserverCallBack(CFRunLoopObserverRef observer, CFRunLoopActivity activity, void *info){
ViewController *viewController = (__bridge ViewController *)(info);//void *info即是我们前面传递的self(ViewController)
NSLog(@"runLoopOserverCallBack -> name = %@",viewController.name);
}

- (void)timerMethod{
//不做任何事情,为了让runLoop一直处理任务而不去睡眠
}
@end
```

至此当前的RunLoop一当进入休眠后都会被监听到并且调用runLoopOserverCallBack回调方法