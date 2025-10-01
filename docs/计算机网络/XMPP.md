# XMPP

## XMPP的基本结构

- XMPP是一个典型的C/S架构
- XMPP中定义了三个角色，客户端，服务器，网关
- 服务器同时承担了客户端信息记录，连接管理和信息的路由功能
- 基本的网络形式是单客户端通过TCP/IP连接到单服务器，然后在之上传输XML流

## XMPP工作原理

1. 节点连接到服务器
2. 服务器利用本地目录系统中的证书对其认证
3. 节点指定目标地址，让服务器告知目标状态
4. 服务器查找、连接并进行相互认证
5. 节点之间进行交互

## XMPP的优缺点

1. 优点：开放、安全、分散、可扩展
2. 缺点：数据负载过重XML、没有二进制传输

## Openfire

1. XMPP协议的服务器实现开源框架

2. 通过配置Openfifire服务器管理平台实现XMPP协议中的功能

3. Openfire服务器管理平台需要配置⼀个进⾏数据存储的数据库

## 注册、登录、好友、聊天

1. XMPPStream(通信管道管理对象) 
2. XMPPRoster(好友花名册管理对象) 
3. XMPPJID(账号对象) 
4. XMPPPresence(上线状态对象)
5. XMPPMessageArchivingCoreDataStorage(聊天消息持久化存储对象)

## XMPPFramwork中使用的多播代理GCDMulticastDelegate

iOS中通常的delegate模式只能有一个被委托的对象，这样当需要有多个被委托的对象时，实现起来就略为麻烦，在开源库XMPPFramework中提供了一个GCDMulticastDelegate类，使用它可以为一个对象添加多个被委托的对象，用起来也比较方便，用法简单小结如下：

```objective-c
#import "HHMulDelegateVC.h"
#import <GCDMulticastDelegate.h>
#import "PersonOne.h"
#import "PersonTwo.h"

//1、定义一个协议
@protocol MyDelegate
@optional
- (void)runTo:(NSString *)string;
@end

@interface HHMulDelegateVC ()
{
    //2、在需要使用delegate的类中定义一个GCDMulticastDelegate变量
    GCDMulticastDelegate<MyDelegate> *multiDelegate;
}
@end

@implementation HHMulDelegateVC

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.
    GCDMulticastDelegate<MyDelegate> *multiDelegate = (GCDMulticastDelegate <MyDelegate> *)[[GCDMulticastDelegate alloc] init];

    //3、定义多个实现了协议MyDelegate的类，如Object1和Object2；
    PersonOne *o1 = [[PersonOne alloc]init];
    PersonTwo *o2 = [[PersonTwo alloc]init];

    //4、在需要使用delegate的地方使用如下代码，将多个被委托的对象，添加到multiDelegate的delegate链中。
    [multiDelegate addDelegate:o1 delegateQueue:dispatch_get_main_queue()];
    [multiDelegate addDelegate:o2 delegateQueue:dispatch_get_main_queue()];

    [multiDelegate runTo:@"多播"];
}

@end
```

多播的delegate与通常的delegate不同，multiDelegate并没有实现协议中的方法，而是将协议中的方法转发到自己delegate链中的对象。  对multiDelegate对象调用`runTo`方法时，由于GCDMulticastDelegate没有实现`runTo`方法，因此该类的`methodSignatureForSelector`和`forwardInvocation`函数会被触发，在该函数中会遍历delegate链，对每一个delegate对象调用`runTo`方法，从而实现了多个delegate。

同时，在对multiDelegate调用协议方法时，采用的是异步的方式，协议方法会立刻返回，不会阻碍当前函数。

## 多账号登录：source
