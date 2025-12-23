# CFRunLoopObserverRef

runloop有`source` `timer` `observer`，**Observer用来监听RunLoop状态变化**。

通过CFRunLoopObserverCreateWithHandler函数来创建一个观察者（函数会有一个block回调），对RunLoop进行观察，当RunLoop状态变化时，会触发block回调，回调会返回对应的状态，在回调里做相应操作。

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

## RunLoop状态与唤醒机制

RunLoop 的**核心状态**是由 Core Foundation 框架定义的 `CFRunLoopActivity` 枚举来表示的。

```c
/* Run Loop Observer Activities */
typedef CF_OPTIONS(CFOptionFlags, CFRunLoopActivity) {
    kCFRunLoopEntry = (1UL << 0),			//1 即将进入RunLoop
    kCFRunLoopBeforeTimers = (1UL << 1),	//2 即将处理NSTimer
    kCFRunLoopBeforeSources = (1UL << 2), //4 即将处理Sources
    kCFRunLoopBeforeWaiting = (1UL << 5),	//32 即将进入休眠，休眠之前
    kCFRunLoopAfterWaiting = (1UL << 6),	//64 唤醒之前
    kCFRunLoopExit = (1UL << 7),			//128 即将退出runloop
    kCFRunLoopAllActivities = 0x0FFFFFFFU //所有状态改变
};
```

这些状态描述了 RunLoop 在单个循环中所处的不同阶段。理解这些状态对于理解 RunLoop 何时工作、何时休眠以及如何被唤醒至关重要。

**RunLoop 的六种主要状态 (`CFRunLoopActivity`):**

1.  **`kCFRunLoopEntry` (进入循环):**
    *   表示 RunLoop 即将开始执行一个循环。
    *   **状态性质:** **活动状态** (RunLoop 正在工作)
    *   **任务执行:** 不直接执行用户任务，但这是循环开始的信号。注册的 Observers 可以在这个点执行回调。

2.  **`kCFRunLoopBeforeTimers` (即将处理 Timers):**
    *   表示 RunLoop 即将检查是否有基于 Timer 的源需要触发。
    *   **状态性质:** **活动状态** (RunLoop 正在工作)
    *   **任务执行:** 不直接执行 Timer 回调，但这是 RunLoop 准备处理 Timer 源的标志。注册的 Observers 可以在这个点执行回调。如果此时有到期的 Timer，RunLoop 会在后续阶段处理它。

3.  **`kCFRunLoopBeforeSources` (即将处理 Sources):**
    *   表示 RunLoop 即将检查是否有非 Timer 的源（主要是 Input Sources，如基于端口的源 `CFSocketRef`, `CFMachPortRef` 或自定义源 `CFRunLoopSourceRef`）有事件需要处理。
    *   **状态性质:** **活动状态** (RunLoop 正在工作)
    *   **任务执行:** 不直接执行 Source 回调，但这是 RunLoop 准备处理非 Timer 源的标志。注册的 Observers 可以在这个点执行回调。如果此时有准备好的 Source，RunLoop 会在后续阶段处理它。

4.  **`kCFRunLoopBeforeWaiting` (即将休眠):**
    *   表示 RunLoop 已经检查了所有源（Timers 和 Sources），**没有发现任何需要立即处理的事件**。RunLoop **即将进入休眠状态**。
    *   **状态性质:** **活动状态** (RunLoop 正在做休眠前的最后工作) -> **即将转变为休眠状态**。
    *   **任务执行:** RunLoop 在这个状态本身不执行用户任务（Timer/Source 回调），但它会执行注册的 Observer 回调。这是进入休眠前的最后一个活动点。

5.  **`kCFRunLoopAfterWaiting` (刚从休眠中唤醒):**
    *   表示 RunLoop **刚刚被某个事件唤醒**。这个事件可能是：
        *   一个 Timer 到时间了。
        *   一个基于端口的 Input Source 收到了消息（例如：用户触摸屏幕、网络数据到达、其他线程通过端口发送消息）。
        *   一个手动唤醒的调用（如 `CFRunLoopWakeUp`）。
        *   一个 `performSelector:onThread:...` 请求被调度到该 RunLoop。
    *   **状态性质:** **活动状态** (RunLoop 被唤醒，即将开始处理触发唤醒的事件)
    *   **任务执行:** **这是 RunLoop 被唤醒后进入的第一个状态**。注册的 Observers 可以在这个点执行回调。紧接着，RunLoop 会根据唤醒原因跳转到处理相应事件的状态（如处理 Timer 或 Source），并执行对应的回调函数（真正的用户任务会在处理 Source 或 Timer 时执行）。

6.  **`kCFRunLoopExit` (退出循环):**
    *   表示 RunLoop **即将退出整个循环**。这通常发生在：
        *   给 RunLoop 设置了超时时间并且超时了。
        *   使用 `CFRunLoopStop` 显式停止了 RunLoop。
        *   RunLoop 管理的所有 Sources 和 Timers 都被移除了。
    *   **状态性质:** **活动状态** (RunLoop 正在结束工作)
    *   **任务执行:** 不执行用户任务（Timer/Source 回调），但注册的 Observers 可以在这个点执行回调。RunLoop 退出后，如果其运行模式中还有事件需要处理，它可能会在将来再次被启动（对于主线程 RunLoop 来说，它几乎不会真正退出）。

**关键问题解答：**

1.  **什么状态表示 RunLoop 在休眠？**
    *   **休眠发生在 `kCFRunLoopBeforeWaiting` 和 `kCFRunLoopAfterWaiting` 之间。** 当 RunLoop 进入 `kCFRunLoopBeforeWaiting` 状态，执行完相关的 Observer 回调后，如果确实没有事件需要处理，它会调用底层的 `mach_msg()` 函数。这个函数会使当前线程在内核态挂起（睡眠），**此时线程不消耗 CPU 时间，这就是休眠的本质**。
    
2.  **什么状态表示 RunLoop 被唤醒执行任务？**
    *   **`kCFRunLoopAfterWaiting` 是 RunLoop 被唤醒后进入的第一个状态。** 它标志着休眠的结束。
    *   唤醒的原因（Timer 到期、端口消息到达等）决定了 RunLoop 接下来要处理什么。
    *   唤醒后，RunLoop 会从 `kCFRunLoopAfterWaiting` 状态开始，**根据唤醒源的类型，跳转到对应的处理阶段**：
        *   如果是 Timer 唤醒，接下来会进入 `kCFRunLoopBeforeTimers` 状态，然后处理到期的 Timer 回调（执行任务）。
        *   如果是 Source (如端口事件) 唤醒，接下来会进入 `kCFRunLoopBeforeSources` 状态，然后处理有事件的 Source 回调（执行任务）。
        *   如果是手动唤醒 (`CFRunLoopWakeUp`) 或 `performSelector:`，处理逻辑类似 Source 唤醒。
    *   **因此，虽然任务回调本身不是直接在 `kCFRunLoopAfterWaiting` 状态执行的，但这个状态是唤醒发生的明确信号，并且紧跟着唤醒事件的处理（任务执行）就开始了。**

**总结状态流转与休眠/唤醒的关系：**

1.  **活动 (处理事件/准备):** `Entry` -> `BeforeTimers` (可能处理Timer) -> `BeforeSources` (可能处理Source) -> ... 如果期间有事件处理完且暂无新事件...
2.  **准备休眠:** 进入 `BeforeWaiting` (执行Observer回调) -> 调用 `mach_msg()` 线程挂起 -> **休眠 (线程挂起，不消耗CPU)**。
3.  **唤醒:** 被事件 (Timer到期/端口消息/手动唤醒) 中断休眠 -> 线程恢复执行 -> 进入 `AfterWaiting` (执行Observer回调) -> 根据唤醒原因跳转 (`BeforeTimers` 或 `BeforeSources`) -> 处理事件 (执行Timer/Source回调，即**执行任务**) -> ... 处理完可能再次进入 `BeforeWaiting` 休眠或进入 `Exit`。
4.  **退出:** 进入 `Exit` (执行Observer回调)。

**简单记忆：**

*   **`kCFRunLoopBeforeWaiting`：** 是 RunLoop **准备去睡觉** 的信号。
*   **`kCFRunLoopAfterWaiting`：** 是 RunLoop **刚被叫醒** 的信号。醒来后马上就要根据谁叫醒它（Timer 还是 Source）去干活了。
*   **真正的休眠：** 发生在 `BeforeWaiting` (调用了 `mach_msg()`) 之后，`AfterWaiting` 之前，这个等待期间线程在内核挂起。

理解这些状态及其转换对于调试 RunLoop 相关问题（如任务不执行、卡顿、线程保活）、优化性能（避免唤醒过于频繁，列表要加载大量数据、图片、处理耗时操作等）以及实现高级的线程间通信机制都至关重要。你可以通过添加 `CFRunLoopObserver` 来观察这些状态的实时变化。

**在休眠时唤醒它去处理这些任务**。

点击CFRunLoopRef到API中发现定义了Observer的相关声明CFRunLoopObserverRef：

```c++
typedef struct CF_BRIDGED_MUTABLE_TYPE(id) __CFRunLoop * CFRunLoopRef;

typedef struct CF_BRIDGED_MUTABLE_TYPE(id) __CFRunLoopSource * CFRunLoopSourceRef;

typedef struct CF_BRIDGED_MUTABLE_TYPE(id) __CFRunLoopObserver * CFRunLoopObserverRef;

typedef struct CF_BRIDGED_MUTABLE_TYPE(NSTimer) __CFRunLoopTimer * CFRunLoopTimerRef;
```

创建Observer，在API中找到如下函数声明:

```c++
// 它需要的参数:
// CFAllocatorRef allocator 
// CFOptionFlags activities 表示要监听RunLoop的变化的状态(kCFRunLoopAfterWaiting等)
// Boolean repeats 表示是否重复监听
// CFIndex order 这个传0即可暂时没研究
// CFRunLoopObserverCallBack callout 表示监听的回调方法(C语言的方法)
// CFRunLoopObserverContext *context 表示上下文环境,用于C语言的方法与OC的互传传值
CF_EXPORT CFRunLoopObserverRef CFRunLoopObserverCreate(CFAllocatorRef allocator, CFOptionFlags activities, Boolean repeats, CFIndex order, CFRunLoopObserverCallBack callout, CFRunLoopObserverContext *context);
```

既然如此现在来创建一个CFRunLoopObserverContext,在API中也找到一个CFRunLoopObserverContext的声明

```c++
typedef struct {

  CFIndex  version; //暂时传0不研究

  void *  info; //重要就是C语言要与OC传递数据的引用.void *表示可以传递任何类型的数据

  const void *(*retain)(const void *info);//引用

  void  (*release)(const void *info);//回收

  CFStringRef  (*copyDescription)(const void *info);//描述,暂时没用

} CFRunLoopObserverContext;
```

### CFRunLoopObserverContext

```c++
CFRunLoopObserverContext context = {
  0,
  (__bridge void *)(self),//OC对象传递过去
  &CFRetain,
  &CFRelease,
  NULL
};
```

### CFRunLoopObserverCallBack

点击上面的CFRunLoopObserverCallBack是API跳到这样的一个声明,即告诉我们监听的回调方法的参数怎么定义

```c++
typedef void (*CFRunLoopObserverCallBack)(CFRunLoopObserverRef observer, CFRunLoopActivity activity, void *info);
```

接下来新建一个C语言用于回调方法

```c++
static void runLoopOserverCallBack(CFRunLoopObserverRef observer, CFRunLoopActivity activity, void *info){

	//void *info正是我们要用来与OC传值的,这边可以转成OC对象,前面我们传进来的时候是self

}
```

### CFRunLoopObserverRef

```c++
//创建一个监听
static CFRunLoopObserverRef observer;
observer = CFRunLoopObserverCreate(NULL, kCFRunLoopAfterWaiting, YES, 0, &runLoopOserverCallBack,&context);

//注册监听
CFRunLoopAddObserver(runLoopRef, observer, kCFRunLoopCommonModes);

//销毁
CFRelease(observer);
```

### 完整代码

添加了一个NSTimer，timer什么都没做，只是为了让RunLoop一直工作。

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