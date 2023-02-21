# RACCommand

```objective-c
- (void)RACCommandTest {
  
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        NSLog(@"%@",input);//input打印出：起飞～～～～～
      
      //里面需要返回一个信号
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            return nil;
        }];
      
    }];
  
    [command execute:@"起飞～～～～～"];
}
```

既然返回的是一个信号，那我们就尝试着发布信息

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
//        NSLog(@"%@",input);
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            [subscriber sendNext:@"发布信息"];
            return nil;
        }];
    }];
    [command execute:@"起飞～～～～～"];
}
```

这个时候问题来了，发送的信息谁去接收呢？？？

这个时候我们注意一下`execute`这个方法

```objective-c
- (RACSignal *)execute:(id)input {
	// `immediateEnabled` is guaranteed to send a value upon subscription, so
	// -first is acceptable here.
	BOOL enabled = [[self.immediateEnabled first] boolValue];
	if (!enabled) {
		NSError *error = [NSError errorWithDomain:RACCommandErrorDomain code:RACCommandErrorNotEnabled userInfo:@{
			NSLocalizedDescriptionKey: NSLocalizedString(@"The command is disabled and cannot be executed", nil),
			RACUnderlyingCommandErrorKey: self
		}];

		return [RACSignal error:error];
	}

	RACSignal *signal = self.signalBlock(input);
	NSCAssert(signal != nil, @"nil signal returned from signal block for value: %@", input);

	// We subscribe to the signal on the main thread so that it occurs _after_
	// -addActiveExecutionSignal: completes below.
	//
	// This means that `executing` and `enabled` will send updated values before
	// the signal actually starts performing work.
	RACMulticastConnection *connection = [[signal
		subscribeOn:RACScheduler.mainThreadScheduler]
		multicast:[RACReplaySubject subject]];
	
	[self.addedExecutionSignalsSubject sendNext:connection.signal];

	[connection connect];
	return [connection.signal setNameWithFormat:@"%@ -execute: %@", self, RACDescription(input)];
}
```

最终代码

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        NSLog(@"%@",input);
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            [subscriber sendNext:@"发布信息"];
            return nil;
        }];
    }];
    
    [command.executionSignals subscribeNext:^(id  _Nullable x) {
        [x subscribeNext:^(id  _Nullable x) {
            NSLog(@"订阅一次 - %@",x);
        }];
        NSLog(@"接收数据 - %@",x);//x打印是一个信号
    }];
    [command execute:@"起飞～～～～～"];

}
```

### switchToLatest

上面代码订阅了两次，可以使用下面的方法

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        NSLog(@"%@",input);
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            [subscriber sendNext:@"发布信息"];
            return nil;
        }];
    }];
    
//    [command.executionSignals subscribeNext:^(id  _Nullable x) {
//        [x subscribeNext:^(id  _Nullable x) {
//            NSLog(@"订阅一次 - %@",x);
//        }];
//        NSLog(@"接收数据 - %@",x);//x打印是一个信号
//    }];
    //等于下面这句
    [command.executionSignals.switchToLatest subscribeNext:^(id  _Nullable x) {
        NSLog(@"接收数据 - %@",x);//x打印是一个信号
    }];
    [command execute:@"起飞～～～～～"];
}
```

其中`switchToLatest`表示的是最新发送的信号

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        NSLog(@"%@",input);
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            [subscriber sendNext:@"发布信息"];
            [subscriber sendCompleted];//告诉外界发送完成了
            return nil;
        }];
    }];
    
//    [command.executionSignals subscribeNext:^(id  _Nullable x) {
//        [x subscribeNext:^(id  _Nullable x) {
//            NSLog(@"订阅一次 - %@",x);
//        }];
//        NSLog(@"接收数据 - %@",x);//x打印是一个信号
//    }];
    //等于下面这句
    [command.executionSignals.switchToLatest subscribeNext:^(id  _Nullable x) {
        NSLog(@"接收数据 - %@",x);//x打印是一个信号
    }];
  	//监听执行状态
    [[command.executing skip:1] subscribeNext:^(NSNumber * _Nullable x) {
        if ([x boolValue]) {
            NSLog(@"还在执行");
        } else {
            NSLog(@"执行结束");
        }
    }];
    [command execute:@"起飞～～～～～"];
}
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



## RACCommand网络请求

实例演示：有一个接口从服务端读取团队列表，开始读取的时候显示加载状态。读取完成后更新页面。

### 1、在ViewModel中将接口声明成一个RACCommand

```objective-c
@property (nonatomic, strong) RACCommand *fetchTeamListCommand;
// 读取我的团队列表
- (RACCommand *)fetchTeamListCommand {
    if (!_fetchTeamListCommand) {
        _fetchTeamListCommand = [[RACCommand alloc] initWithSignalBlock:^RACSignal *(id input) {
            
            return [RACSignal createSignal:^RACDisposable *(id<RACSubscriber> subscriber) {
                
                [TeamApi fetchTeamListWithResult:^(BOOL isSuccess, id data, NSError *error) {
                    
                    if (isSuccess) {
                        self.teamList = [TeamModel mj_objectArrayWithKeyValuesArray:data];
                                          
                        [subscriber sendNext:self.teamList];
                    }
                    else {
                        [subscriber sendNext:@(NO)];
                    }
                    // 一定要记得发送完成消息，不然不能再次执行
                    [subscriber sendCompleted];
                }];
                
                return nil;
            }];
        }];
    }
    
    return _fetchTeamListCommand;
}
```

1. 在Controller中订阅信号

```objective-c
[[self.viewModel.fetchTeamListCommand executionSignals] subscribeNext:^(id x) {
        // 这里的x是一个RACSignal，即执行Command时返回的那个Signal，所以x也是可以订阅的。收到这个信号，说明网络请求开始。
        [MBProgressHUD showHUDAddedTo:self.view animated:YES];
        // 这里收到信号是开始发送网络请求
        [x subscribeNext:^(id x) {
            // 这里收到信号是网络请求返回
            [MBProgressHUD hideHUDForView:self.view animated:YES];
            
            // do something            
        }];
        
    }];
```

在要读取的地方执行command

```objective-c
// 执行请求
    [self.viewModel.fetchTeamListCommand execute:nil];
```

如果不用在发送网络请求前做什么事，也可以这样订阅：

```objective-c
[[[self.viewModel.fetchTeamListCommand executionSignals] switchToLatest] subscribeNext:^(id x) {
        
    }];
```

## 注意的点

- 在Command返回的Signal里面一定要记得发送Completed信号，不能这个Command的不能重复执行。
- 上面的订阅方式只要订阅一次，每次执行Command都会接收到。还有一种在execute方法后面直接订阅的方式。那样每次execute都得订阅。个人更喜欢上面这种订阅方式。

























































