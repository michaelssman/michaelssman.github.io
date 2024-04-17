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

### `signal.h`中的`void(*signal(int, void (*)(int)))(int);`方法介绍

这行代码是C语言中的一个函数声明，它定义了`signal`函数的原型。这个函数用于设置一个信号处理函数，它是UNIX、Linux系统编程中用来处理异步事件的一个标准库函数。

让我们逐部分解析这个声明：

- `signal`：这是函数名。
- `int`：这是第一个参数的类型，表示信号的编号。在C语言中，不同的信号（如SIGINT, SIGTERM等）通常用整数常量来表示。
- `void (*)(int)`：这是第二个参数的类型，它是一个函数指针，指向一个返回类型为void、接受一个int参数的函数。这个函数指针指向的函数是当信号发生时将要被调用的信号处理函数。
- `void (*signal(int, void (*)(int)))(int)`：整个声明的返回类型是一个函数指针，这个函数指针指向的函数类型也是返回void、接受一个int参数的函数。这意味着`signal`函数返回的是另一个函数指针，这个返回的函数指针通常指向之前设置的旧的信号处理函数。

简单来说，`signal`函数的作用是设置一个信号的处理函数（即当信号发生时系统自动调用的函数）。当你调用`signal`函数时，你需要提供两个参数：一个是你想要处理的信号的编号，另一个是一个指向信号处理函数的指针。然后，`signal`函数会返回一个指向之前关联到该信号的旧处理函数的指针（如果有的话）。

使用`signal`函数的一个典型例子是捕获中断信号（如用户按下Ctrl+C产生的SIGINT信号），以确保程序可以以一种预定的方式响应这个信号，比如进行清理工作并优雅地退出。

下面是一个使用`signal`函数的简单例子：

```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

// 信号处理函数
void handle_sigint(int sig) {
    printf("Caught signal %d\n", sig);
}

int main() {
    // 设置SIGINT的处理函数为handle_sigint
    signal(SIGINT, handle_sigint);
    // 无限循环，等待信号
    while (1) {
        sleep(1);
    }
    return 0;
}
```
在这个例子中，当用户按下Ctrl+C时，程序不会立即退出，而是调用`handle_sigint`函数来处理信号。

### BSD和Mach

BSD和Mach是两种不同的内核，分别用于不同的操作系统。在macOS和iOS系统中，BSD是底层的网络和文件系统部分，而Mach是底层的进程管理和通信部分。

#### BSD崩溃

BSD崩溃通常指应用程序中的崩溃，例如访问无效的内存地址或执行非法指令等。在BSD崩溃发生时，**操作系统会发送一个信号给应用程序，称为SIGSEGV（Segmentation Violation）信号。应用程序可以使用信号处理机制来捕获和处理该信号，通常使用的方法是注册SIGSEGV信号的处理函数。**在处理函数中，您可以记录崩溃信息、生成崩溃报告或采取其他操作。

#### Mach崩溃

Mach崩溃通常指系统级别的崩溃，例如虚拟内存错误、线程死锁或异常信号等。Mach异常和信号是在内核级别处理的，应用程序无法直接捕获和处理这些异常。然而，您可以使用Mach异常处理机制来**注册异常处理器**，并对特定的Mach异常进行处理。通过注册异常处理器，您可以在Mach崩溃发生时收到通知，并进行一些操作，如记录日志、生成崩溃报告或采取其他措施。

对于应用程序的稳定性和崩溃处理，通常更关注的是应用程序级别的崩溃，即BSD崩溃。Mach崩溃通常是由于系统级别的问题，开发者很少需要直接处理这些崩溃。

上面两个可以看看用户态和内核态的知识。

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

## Bugly上传符号表

上传符号表（也称为符号文件，对于iOS是dSYM文件，对于Android是mapping文件）是Bugly崩溃分析的一个重要步骤，因为它可以将加密的崩溃日志还原为可读的堆栈信息。

CI（持续集成）流水线是自动化地集成和测试代码变更的一系列流程，确保新的代码提交不会破坏现有的功能。在CI流程中集成上传Bugly符号表的步骤可以自动化地处理符号文件的上传，提高效率并减少人为错误。

以下是通常的步骤来在CI流水线中上传符号表到Bugly：

1. **获取Bugly的API Key和App ID**：这两个值是在Bugly创建应用后获得的，用于鉴权和指定上传符号表到正确的应用。
2. **准备符号表**：对于iOS来说，需要生成dSYM文件；对于Android，需要生成mapping文件。
3. **编写上传脚本**：使用Bugly提供的API编写脚本来上传符号表。Bugly通常会提供上传符号表的工具或脚本。
4. **集成到CI流水线**：将上传脚本集成到CI流程中，通常是在构建后的步骤中执行。
5. **测试流水线**：确保在CI流程中上传符号表的步骤能够正确执行。

这里是一个简单的示例，假设你正在使用Jenkins作为CI工具，你可以在构建后的步骤中添加Shell脚本来上传符号表：

对于iOS的dSYM文件，使用curl上传可能如下所示：

```bash
curl -k "http://api.bugly.qq.com/openapi/file/upload/symbol?app_id=你的AppID&app_key=你的AppKey" \
-F "api_version=1" \
-F "app_id=你的AppID" \
-F "app_key=你的AppKey" \
-F "symbolType=2" \
-F "bundleId=你的BundleID" \
-F "productVersion=你的版本号" \
-F "fileName=文件名.dSYM.zip" \
-F "file=@文件路径.dSYM.zip"
```

对于Android的mapping文件，上传可能如下所示：

```bash
curl -k "http://api.bugly.qq.com/openapi/file/upload/symbol?app_id=你的AppID&app_key=你的AppKey" \
-F "api_version=1" \
-F "app_id=你的AppID" \
-F "app_key=你的AppKey" \
-F "symbolType=1" \
-F "bundleId=你的Package Name" \
-F "productVersion=你的版本号" \
-F "fileName=文件名.txt" \
-F "file=@文件路径.txt"
```

请注意，你需要将`你的AppID`、`你的AppKey`、`你的BundleID`、`你的版本号`和`文件路径`替换为实际的值。而且，对于iOS，通常需要先将dSYM文件压缩成zip格式。

确保在CI流水线中正确设置所有的环境变量，并且在上传前测试脚本的有效性。此外，Bugly的API和上传方式可能会随着时间而变化，因此请参考最新的Bugly文档来获取最准确的信息。

### bugly使用上传工具上传

```bash
KJXY：
java -jar buglyqq-upload-symbol.jar -appid bb45d2001f -appkey 12b7e14e-09b2-4d58-abc8-7f4145fe93be -bundleid com.ningmengyun.AccCollege -version 5.1.5 -buildNo 21 -platform IOS -inputSymbol /Users/michael/Downloads/bugly_dsym/柠檬会计学院测试.app.dSYM

YCW：
java -jar buglyqq-upload-symbol.jar -appid 90785b8889 -appkey 7d14b9a7-0790-44f4-bca6-e9dc02ea4593 -bundleid com.ningmengyun.lemonacc -version 5.1.10 -buildNo 1 -platform IOS -inputSymbol /Users/michael/Downloads/bugly_dsym/柠檬云财务.app.dSYM

SCM：
java -jar buglyqq-upload-symbol.jar -appid 497a888cf2 -appkey 057b79a8-2200-4742-b8bf-17381f46fd6d -bundleid com.ningmengyun.SCM -version 3.3.7 -buildNo 4 -platform IOS -inputSymbol /Users/michael/Downloads/bugly_dsym/柠檬云进销存.app.dSYM
```

