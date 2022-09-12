# Crash
崩溃分析

异常
1. 捕捉
2. 处理
3. 上传
4. 线下的处理
5. runloop起死回生


## 添加分类，进行处理

## 通过消息发送
崩溃：
数组越界，KVO，内存
接口应该返回一个数组Data，结果返回一个字典Data，调用[NSMutableArray arrayWithArray:responseObject[@"Data"]]就会crash。
如果都处理的话分类比较多，代码量就会多，就会影响性能。

接口应该返回一个字典，但是没有数据或者出错的时候返回的是NSNull类型，如果对NSNull直接使用key取值就会崩溃，可以使用消息转发，对nil对象做操作不会crash。

通过消息发送
没有响应某一个方法的时候，通过invocation 进行消息的转发。防止崩溃。在消息转发滞留。也就是hook，切面 AOP。进行收集 统计 埋点。

## 像友盟，bugly一样处理
添加分类侵入性还是有的，最好是无痕埋点。
整个项目的耦合度 侵入性减少。
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


异常包括
1. exception
2. signal
并不是所有的程序崩溃都是由于发生可以捕捉的异常的，有些时候引起崩溃的大多数原因如：内存访问错误，重复释放等错误就无能为力了，因为这种错误它抛出的是Signal，所以必须要专门做Signal处理。
当应用发生错误而产生上述Signal后，就将会进入我们自定义的回调函数SignalExceptionHandler。为了得到崩溃时的现场信息，还可以加入一些获取CallTrace及设备信息的代码

runloop除了在异常时保持程序运行，还可以做什么：检测卡顿。优化页面

**runloop切换mode会卡顿。导致计时不准确。**

渲染不及时，大事务比较多，对大事务细化成小事务。


GCD和runloop是平级的。

