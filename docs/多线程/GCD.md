# GCD

全称是Grand Central Dispatch，纯C语言，提供了非常多强大等函数

GCD是苹果公司为多核的并发运算提出的解决方案

GCD会自动利用更多的CPU内核（比如双核，四核）

GCD会自动管理线程的生命周期（创建线程，调度任务，销毁线程）

程序员只需要告诉GCD想要执行什么任务，不需要编写任何线程管理代码

## 多线程控制最大并发数

需要控制最大并发数和控制状态时选择封装NSOperation(SDWebImage和AFN也是封装的NSOperation)

NSThread一般和常驻线程使用(如AFN框架)。

NSOperation直接使用系统提供的maxConcurrentOperationCount可设置最大并发数。

GCD使用信号量手动去控制并发数。

## barrier

把异步任务分开两半，前面的先执行，后面的后执行。起到控制流程效果。

最直接的作用: 控制任务执行顺序，起到同步加锁效果。

dispatch_barrier_async 前面的任务执行完毕才会来到这里

dispatch_barrier_sync 作用相同，**但是这个会堵塞线程，影响后面的任务执行，后面的任务会等待栅栏函数。**

判断队列queue中有没有栅栏函数，没有的话就是普通的执行流程，一旦有栅栏函数，就会发生等待，把队列中的任务都执行完毕，等待栅栏函数执行完，然后才会走后面的任务。

执行barrier任务，必须把队列中的前面任务清空，所以前面的任务全部执行完毕才会执行barrier任务。

### 注：

1. 全局并发队列不能使用barrier。全局并发队列并不只是自己使用，系统后台可能也会使用，所以不能堵塞。所以只能使用自定义的并发队列。

2. 栅栏函数只能控制同一队列

   例：AFN封装了一层session。用barrier不能控制，不是一个队列。

### 用处

### 1、加载完两张图片，合成一张图片。

### 2、读写锁

需要实现功能

1. 多读单写
2. 写写互斥
3. 读写互斥
4. 不能阻塞任务执行（子线程，不能阻塞主线程）

#### 使用栅栏函数实现 

通过栅栏函数（自定义并发队列）实现写任务，如果队列前面**读写**操作没回来，后面的写不能执行。（2和3）

setter写操作：`dispatch_barrier_async`主线业务逻辑可以正常执行（4）

getter读操作：`dispatch_sync`同步。

读写操作是同一个并发队列。

```objective-c
#import "ViewController.h"
 
@interface ViewController ()
 
@property (nonatomic, copy) NSString *text;
@property (nonatomic, strong) dispatch_queue_t concurrentQueue;
@end
 
@implementation ViewController
 
- (void)viewDidLoad {
    [super viewDidLoad];
 
    [self readWriteLock];
}
 
- (void)readWriteLock {
    // 使用自己创建的并发队列
    self.concurrentQueue = dispatch_queue_create("aaa", DISPATCH_QUEUE_CONCURRENT);
    // 使用全局队列,必定野指针崩溃
//    self.concurrentQueue = dispatch_get_global_queue(0, 0);
 
    // 测试代码,模拟多线程情况下的读写
    for (int i = 0; i<10; i++) {
        // 创建10个线程进行写操作
        dispatch_async(dispatch_get_global_queue(0, 0), ^{
            [self updateText:[NSString stringWithFormat:@"噼里啪啦--%d",i]];
        });
 
    }
 
    for (int i = 0; i<50; i++) {
        // 50个线程进行读操作
        dispatch_async(dispatch_get_global_queue(0, 0), ^{
            NSLog(@"读 %@ %@",[self getCurrentText],[NSThread currentThread]);
        });
 
    }
 
    for (int i = 10; i<20; i++) {
        // 10个进行写操作
        dispatch_async(dispatch_get_global_queue(0, 0), ^{
            [self updateText:[NSString stringWithFormat:@"噼里啪啦--%d",i]];
        });
 
    }
}
 
// 写操作,栅栏函数是不允许并发的,所以"写操作"是单线程进入的,根据log可以看出来
- (void)updateText:(NSString *)text {
    // block内不需要使用weakSelf, 不会产生循环引用
    dispatch_barrier_async(self.concurrentQueue, ^{
        self.text = text;
        NSLog(@"写操作 %@ %@",text,[NSThread currentThread]);
        // 模拟耗时操作,打印log可以放发现是1个1个执行,没有并发
        sleep(1);
    });
}
// 读操作,这个是可以并发的,log在很快时间打印完
- (NSString *)getCurrentText {
    __block NSString * t = nil;
    // block内不需要使用weakSelf, 不会产生循环引用
    dispatch_sync(self.concurrentQueue, ^{
        t = self.text;
        // 模拟耗时操作,瞬间执行完,说明是多个线程并发的进入的
        sleep(1);
    });
    return t;
}
 
@end
```

## group

调度组

最直接的作用: 控制任务执行顺序

- dispatch_group_create 创建组 

- dispatch_group_notify 进组任务执行完毕通知 

- dispatch_group_wait 进组任务执行等待时间

- dispatch_group_async 进组任务 

  里面封装了dispatch_group_enter和dispatch_group_leave（callout执行完毕）

  - dispatch_group_enter 进组     --
  - dispatch_group_leave 出组 	++

  类似信号量的加减，搭配使用。

每次dispatch_group_leave会wakeup-->dispatch_group_notify判断是否等于0，等于0就会callout唤醒notify的block任务。

## dispatch_semaphore_t

信号量

作用：同步->当锁，控制GCD最大并发数，也可以控制流程。

```
dispatch_semaphore_create		创建信号量
dispatch_semaphore_wait			信号量等待 -- do while死循环 等待信号量为正
dispatch_semaphore_signal		信号量释放 ++
```

信号量是几，就可以执行几个任务。

```objective-c
- (void)semaphoreDemo {
    
    ///执行结果：
    /// 睡2秒后
    /// 执行任务2
    /// 任务2完成
    /// 执行任务1
    /// 任务1完成
    dispatch_queue_t queue = dispatch_get_global_queue(0, 0);
    dispatch_semaphore_t sem = dispatch_semaphore_create(0);
    dispatch_queue_t queue1 = dispatch_queue_create("cooci", NULL);
    
    //任务1
    dispatch_async(queue, ^{
        //会等待，因为信号量开始是0
        //第二个参数 是等待时间 DISPATCH_TIME_FOREVER一直等，do while循环
        dispatch_semaphore_wait(sem, DISPATCH_TIME_FOREVER); // 等待
        
        NSLog(@"执行任务1");
        NSLog(@"任务1完成");
    });
    
    //任务2
    //会先执行任务2 任务2执行完之后会释放信号 然后执行任务1
    dispatch_async(queue, ^{
        sleep(2);
        
        NSLog(@"执行任务2");
        NSLog(@"任务2完成");
        dispatch_semaphore_signal(sem); // 发信号
    });
    
    //任务3
    dispatch_async(queue, ^{
        dispatch_semaphore_wait(sem, DISPATCH_TIME_FOREVER);
        sleep(2);
        
        NSLog(@"执行任务3");
        NSLog(@"任务3完成");
        dispatch_semaphore_signal(sem);
    });
    
    //任务4
    dispatch_async(queue, ^{
        dispatch_semaphore_wait(sem, DISPATCH_TIME_FOREVER);
        sleep(2);
        
        NSLog(@"执行任务4");
        NSLog(@"任务4完成");
        dispatch_semaphore_signal(sem);
    });
}
```

控制一次最多上传或下载多少个任务：

```objective-c
///2最先打印，1最后打印，3和4顺序不一定。
- (void)gcdConcurrentCount
{
    //并发队列
    dispatch_queue_t queue = dispatch_queue_create("haha", DISPATCH_QUEUE_CONCURRENT);
    dispatch_semaphore_t semaphore = dispatch_semaphore_create(2);
  
    dispatch_async(queue, ^{
        dispatch_semaphore_wait(semaphore, DISPATCH_TIME_FOREVER);
        sleep(5);
        NSLog(@"1");
        dispatch_semaphore_signal(semaphore);
    });
    
    dispatch_async(queue, ^{
        dispatch_semaphore_wait(semaphore, DISPATCH_TIME_FOREVER);
        sleep(3);
        NSLog(@"2");
        dispatch_semaphore_signal(semaphore);
    });
    
    dispatch_async(queue, ^{
        dispatch_semaphore_wait(semaphore, DISPATCH_TIME_FOREVER);
        NSLog(@"3");
        dispatch_semaphore_signal(semaphore);
    });
    
    dispatch_async(queue, ^{
        dispatch_semaphore_wait(semaphore, DISPATCH_TIME_FOREVER);
        NSLog(@"4");
        dispatch_semaphore_signal(semaphore);
    });
}
```

## Dispatch_Source

- 其 CPU 负荷非常小，尽量不占用资源

- 联结的优势

通过条件控制block执行。

在任一线程上调用它的的一个函数 dispatch_source_merge_data 后，会执行 Dispatch Source 事先定义好的句柄(可以把句柄简单理解为一个 block ) 这个过程叫 Custom event 用户事件。是 dispatch source 支持处理的一种事件

句柄是一种指向指针的指针 它指向的就是一个类或者结构，它和系统有很密切的关系 HINSTANCE(实例句柄)，HBITMAP(位图句柄)，HDC(设备表述句柄)，HICON (图标句柄)等。这当中还有一个通用的句柄，就是HANDLE

- dispatch_source_create 创建源 
- dispatch_source_set_event_handler 设置源事件回调
- dispatch_source_merge_data 源事件设置数据
- dispatch_source_get_data  获取源事件数据
- dispatch_resume 继续 
- dispatch_suspend 挂起

底层封装的是pthread，不受runloop影响。
