# RACCommand

### 1、创建RACCommand

`#import <ReactiveObjC.h>`

在ViewModel中将接口声明成一个RACCommand

```objective-c
@property (nonatomic, strong)RACCommand *fetchListCommand;

// 读取我的团队列表
- (RACCommand *)fetchListCommand {
    if (!_fetchListCommand) {
        //创建command，init方法传block，block返回一个RACSignal
	      //block实现传过去：网络请求
        _fetchListCommand = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
            NSLog(@"%@",input);//input打印出：起飞～～～～～
            //返回一个信号
            return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
                // 1.开始网络请求
                NSLog(@"开始网络请求");
                
                // 2.1网络请求成功
                [subscriber sendNext:@"网络请求成功，对外发布数据信息"];//sendNext会调起subscribeNext
                [subscriber sendCompleted];//告诉外界发送完成了。一定要记得发送完成消息，不然不能再次执行
                
                // 2.2网络请求失败
                [subscriber sendError:nil];
                
                return [RACDisposable disposableWithBlock:^{
                    // 取消网络请求
                    NSLog(@"取消网络请求");
                }];
            }];
        }];
    }
    return _fetchListCommand;
}
```

### 2、订阅command

在Controller中订阅信号

```objective-c
    //订阅命令发出的信号
    //    [self.viewModel.fetchListCommand.executionSignals subscribeNext:^(id  _Nullable x) {
        			// 这里的x是一个RACSignal，即执行Command时返回的那个Signal，所以x也是可以订阅的。收到这个信号，说明网络请求开始。
		//        [MBProgressHUD showHUDAddedTo:self.view animated:YES];
    //        [x subscribeNext:^(id  _Nullable x) {
            // 这里收到信号是网络请求返回
		//            [MBProgressHUD hideHUDForView:self.view animated:YES];
    //            NSLog(@"订阅一次 - %@",x);
			            // do something            
    //        }];
    //        NSLog(@"接收数据 - %@",x);//x打印是一个信号
    //    }];

    //上面代码订阅了两次，可以使用下面的方法`switchToLatest`表示的是最新发送的信号
    [self.viewModel.fetchListCommand.executionSignals.switchToLatest subscribeNext:^(id  _Nullable x) {
        NSLog(@"接收数据 - %@",x);//x打印是一个信号
    }];
    

    [self.viewModel.fetchListCommand.errors subscribeNext:^(NSError * _Nullable x) {
        NSLog(@"出错");
    }];
    
    
    //监听命令执行状态
    [[self.viewModel.fetchListCommand.executing skip:1] subscribeNext:^(NSNumber * _Nullable x) {
        if ([x boolValue]) {
            NSLog(@"还在执行");
        } else {
            NSLog(@"执行结束");
        }
    }];
```

### 3、执行command

在Controller中需要读取的地方执行command请求

```objective-c
//开始所有动作的导火线 执行命令 会调起RACCommand创建时候的回调
[self.viewModel.fetchListCommand execute:@"起飞～～～～～"];
```

1. 没有打印`执行结束`需要发送完消息之后调用`[subscriber sendCompleted];`告诉外界发送完成了。
2. 第一次就打印执行结束，这次的判断不是我们想要的， 需要跳过第一步。这个时候我需要用到一个方法`skip`，这个方法后面有一个参数，填的就是忽略的次数，我们这个时候只想忽略第一次， 所以就填1

既然提到了`skip`那就随便可以提提其它的类似的方法
 `filter`过滤某些
 `ignore`忽略某些值
 `startWith`从哪里开始
 `skip`跳过（忽略）次数
 `take`取几次值 正序
 `takeLast`取几次值 倒序

## 注意的点

- 在Command返回的Signal里面一定要记得发送Completed信号，不然这个Command的不能重复执行。
- 上面的订阅方式只要订阅一次，每次执行Command都会接收到。还有一种在execute方法后面直接订阅的方式，这种的每次execute都得订阅。
