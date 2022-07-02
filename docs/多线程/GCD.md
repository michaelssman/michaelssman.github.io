# GCD

全称是Grand Central Dispatch，纯C语言，提供了非常多强大等函数

## GCD的优势

GCD是苹果公司为多核的并发运算提出的解决方案

GCD会自动利用更多的CPU内核（比如双核，四核）

GCD会自动管理线程的生命周期（创建线程，调度任务，销毁线程）

程序员只需要告诉GCD想要执行什么任务，不需要编写任何线程管理代码

## GCD坑点

## GCD原理

libdispatch 队列 线程 同步异步函数 栅栏函数

并不是真正的并发，而是**调度**。

真正的并发建立在多核上。

- 任务

  block的代码块，包括大括号在内。

  任务使用block封装

  任务的block没有参数也么没有返回值

  执行任务的函数

- 函数（同步函数，异步函数）

  能够开辟线程

  任务的回调是否具备异步性 - 同步性：同步函数会立马执行，异步函数会根据业务需求系统调度情况异步回调。

  1. 同步

     会阻塞当前线程，且不会开启新线程

     **同步函数阻塞的是同步函数下面的所有代码，包括`}`，和同步函数前面的代码没有任何关系。**

     同步`dispatch_sync`

     必须等待当前语句执行完毕，才会执行下一条语句

     在当前执行block的任务

  2. 异步

     不会阻塞当前线程（比如：main队列）.具备开辟新线程的能力，可能会开启新的线程

     异步不会阻塞线程，但是调度函数会耗时。

     异步`dispatch_async`

     不用等待当前语句执行完毕，就可以执行下一条语句

     会开启线程执行block的任务

     异步是多线程的代名词

- 队列

  队列本身就是一种数据结构，FIFO。

  1. 串行队列

     顺序执行。执行完前一个任务之后，再执行后一个任务。只有一个任务

     并发量等于1，一次只能执行一个，先调度进来的任务优先执行。所以绝大部分串行队列顺序执行。

  2. 并发队列

     一次可以调度很多个，并不是执行多个。执行前一个任务后，就可以执行下一个任务。可以有多个任务。

     一次能调度多个任务，虽然也是FIFO先进来的任务先处理，但任务执行完的时间不确定，还和任务的复杂度有关系。

## 资源抢夺 - 锁

互斥锁 同步锁 递归锁

死锁的必要条件：

1. 串行队列
2. 同步任务

#### 死锁

```objective-c
- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.    
    
    /**
     viewDidLoad整个代码块和下面的同步代码块都是在主队列主线程，相互等待。
     viewDidLoad先添加到队列，下面的任务后添加，下面的任务要等viewDidLoad整个执行结束才执行，但是下面的任务块是在viewDidLoad代码块中的。形成死锁。
     如果下面的同步任务不是主队列就不会死锁。不在同一个队列。
     */
    dispatch_sync(dispatch_get_main_queue(), ^{
        NSLog(@"---%@--", [NSThread currentThread]);
    });
    NSLog(@"123");
}
```

#### 多线程控制最大并发数

GCD使用信号量控制

#### 锁

1. NSCondition条件锁

  生产者消费者。

# barrier

最直接的作用: 控制任务执行顺序，起到同步加锁效果。

dispatch_barrier_async 前面的任务执行完毕才会来到这里

dispatch_barrier_sync 作用相同,但是这个会堵塞线程，影响后面的任务执行。后面的任务会等待栅栏函数

判断队列queue中有没有栅栏函数，没有的话就是普通的执行流程，一旦有栅栏函数，就会发生等待，把队列中的任务都执行完毕，等待栅栏函数执行完，然后才会走后面的任务。

执行barrier任务，必须把队列中的前面任务清空，所以前面的任务全部执行完毕才会执行barrier任务。

##### 注：

1. 全局并发队列不能使用barrier。队列没有处理，全局并发队列并不只是自己使用，系统后台可能也会使用，所以不能堵塞。所以只能使用自定义的并发队列。

2. 栅栏函数必须是同一个队列。栅栏函数只能控制同一并发队列

   例：AFN封装了一层session。用barrier不能控制，不是一个队列。

##### 栅栏函数

把异步任务 分开两半，前面的先执行，后面的后执行。起到控制流程效果。

用处：

加载完两张图片，合成一张图片。

# group

调度组

最直接的作用: 控制任务执行顺序

- dispatch_group_create 创建组 

- dispatch_group_notify 进组任务执行完毕通知 

- dispatch_group_wait 进组任务执行等待时间

- dispatch_group_async 进组任务 

  里面封装了dispatch_group_enter和dispatch_group_leave（callout执行完毕）

- dispatch_group_enter 进组     --

- dispatch_group_leave 出组 	++

类似信号量的加减

注意搭配使用

每次dispatch_group_leave会wakeup-->dispatch_group_notify判断是否等于0，等于0就会callout唤醒notify的block任务。

# 信号量

信号量**dispatch_semaphore_t**

同步->当锁，控制GCD最大并发数，也可以控制流程。

```
dispatch_semaphore_create		创建信号量
dispatch_semaphore_wait			信号量等待 -- do while死循环 等待信号量为正
dispatch_semaphore_signal		信号量释放 ++
```

信号量**大于等于**0才会正常执行，小于0就不会执行。

用处：

1. 控制一次最多上传或下载多少个任务
2. 

# Dispatch_Source

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





























































