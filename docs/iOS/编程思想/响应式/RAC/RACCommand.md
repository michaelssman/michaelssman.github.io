# RACCommand

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        return nil;
    }];
    [command execute:@"起飞～～～～～"];
}
```

运行崩溃

**'nil signal returned from signal block for value: 起飞～～～～～'**

返回的信号不能为空，既然如此我们就放回一个信号给他呗。

于是代码变成了这样子的：

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            return nil;
        }];
    }];
    [command execute:@"起飞～～～～～"];
}
```

再次运行，这次没有奔溃，啥都没有，那我们发送的数据呢？`[command execute:@"开始飞起来"];`
没错就是在创建command的block中的input参数
我们可以打印一下

```objective-c
- (void)RACCommandTest {
    RACCommand *command = [[RACCommand alloc] initWithSignalBlock:^RACSignal * _Nonnull(id  _Nullable input) {
        NSLog(@"%@",input);
        return [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
            return nil;
        }];
    }];
    [command execute:@"起飞～～～～～"];
}
```

input打印出了**起飞～～～～～**

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





























































