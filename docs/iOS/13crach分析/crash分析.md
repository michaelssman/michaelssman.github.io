# Crash
崩溃分析

异常
1. 捕捉
2. 处理
3. 上传
4. 线下的处理
5. runloop起死回生


## 添加分类，进行处理

## 通过消息转发
崩溃：
数组越界，KVO，内存
接口应该返回一个数组Data，结果返回一个字典Data，调用[NSMutableArray arrayWithArray:responseObject[@"Data"]]就会crash。
如果都处理的话分类比较多，代码量就会多，就会影响性能。

接口应该返回一个字典，但是没有数据或者出错的时候返回的是NSNull类型，如果对NSNull直接使用key取值就会崩溃，可以使用消息转发，对nil对象做操作不会crash。

通过消息发送
没有响应某一个方法的时候，通过invocation 进行消息的转发。防止崩溃。在消息转发滞留。也就是hook，切面 AOP。进行收集 统计 埋点。

## 可视化埋点

websocket

## 像友盟，bugly一样处理
添加分类侵入性还是有的，最好是无痕埋点。
整个项目的耦合度 侵入性减少。

## 1、exception

为什么是`NSSetUncaughtExceptionHandler`：
objc-os.mm文件中的exception_init函数。_objc_terminate回调。

```c++
static void (*old_terminate)(void) = nil;
static void _objc_terminate(void)
{
    if (PrintExceptions) {
        _objc_inform("EXCEPTIONS: terminating");
    }

    if (! __cxa_current_exception_type()) {
        // No current exception.
        (*old_terminate)();
    }
    else {
        // There is a current exception. Check if it's an objc exception.
        @try {
            __cxa_rethrow();
        } @catch (id e) {
            // It's an objc object. Call Foundation's handler, if any.
            (*uncaught_handler)((id)e);
            (*old_terminate)();
        } @catch (...) {
            // It's not an objc object. Continue to C++ terminate.
            (*old_terminate)();
        }
    }
}
```
catch到了就uncaught_handler回调。把e（exception）传出去。
uncaught_handler点击进去有一个默认值，防止没有值，
objc-exception文件中

```c++
/***********************************************************************
* _objc_default_uncaught_exception_handler
* Default uncaught exception handler. Expected to be overridden by Foundation.
**********************************************************************/
static void _objc_default_uncaught_exception_handler(id exception)
{
}
static objc_uncaught_exception_handler uncaught_handler = _objc_default_uncaught_exception_handler;
```

```c++
objc_uncaught_exception_handler 
objc_setUncaughtExceptionHandler(objc_uncaught_exception_handler fn)
{
    objc_uncaught_exception_handler result = uncaught_handler;
    uncaught_handler = fn;
    return result;
}
```
fn是外界传进来的block。fn给了uncaught_handler回调，一发生问题就调用。

## 2、signal

并不是所有的程序崩溃都是由于发生可以捕捉的异常的，有些时候引起崩溃的原因如：内存访问错误，重复释放等错误，这种错误它抛出的是Signal，所以必须要专门做Signal处理。
当应用发生错误而产生上述Signal后，就将会进入我们自定义的回调函数SignalExceptionHandler。为了得到崩溃时的信息，还可以加入一些获取CallTrace及设备信息的代码。

### BSD和Mach

BSD和Mach是两种不同的内核，分别用于不同的操作系统。在macOS和iOS系统中，BSD是底层的网络和文件系统部分，而Mach是底层的进程管理和通信部分。

#### BSD崩溃

BSD崩溃通常指应用程序中的崩溃，例如访问无效的内存地址或执行非法指令等。在BSD崩溃发生时，**操作系统会发送一个信号给应用程序，称为SIGSEGV（Segmentation Violation）信号。应用程序可以使用信号处理机制来捕获和处理该信号，通常使用的方法是注册SIGSEGV信号的处理函数。**在处理函数中，您可以记录崩溃信息、生成崩溃报告或采取其他操作。

#### Mach崩溃

Mach崩溃通常指系统级别的崩溃，例如虚拟内存错误、线程死锁或异常信号等。Mach异常和信号是在内核级别处理的，应用程序无法直接捕获和处理这些异常。然而，您可以使用Mach异常处理机制来**注册异常处理器**，并对特定的Mach异常进行处理。通过注册异常处理器，您可以在Mach崩溃发生时收到通知，并进行一些操作，如记录日志、生成崩溃报告或采取其他措施。

需要注意的是，对于应用程序的稳定性和崩溃处理，通常更关注的是应用程序级别的崩溃，即BSD崩溃。Mach崩溃通常是由于系统级别的问题，开发者很少需要直接处理这些崩溃。



runloop除了在异常时保持程序运行，还可以做：检测卡顿。优化页面

**runloop切换mode会卡顿。导致计时不准确。**

渲染不及时，大事务比较多，对大事务细化成小事务。


GCD和runloop是平级的。

## 通过Mac自带的命令行工具symbolicatecrash解析Crash文件

### dysm

里面有崩溃所在的行、文件、类

1、symbolicatecrash，Xcode自带的崩溃分析工具，使用这个工具可以更精确的定位崩溃所在的位置，将0x开头的地址替换为响应代码和具体行数。

获取symbolicatecrash工具，打开终端输入以下命令：

`find /Applications/Xcode.app -name symbolicatecrash -type f`

根据路径前往文件夹找到symbolicatecrash，将其复制到指定文件夹。

2、获打包时产生的dSYM文件。

3、崩溃时产生的Crash文件，xxx.crash。

只需要cd到崩溃日志所在的文件夹，然后在终端输入以下的命令。

symbolicatecrash xxxx.crash > xxxx.txt 或 symbolicatecrash -o xxxx.txt xxxx.crash

这样就会在.crash文件同目录下生成解析后的log文件.txt了。
