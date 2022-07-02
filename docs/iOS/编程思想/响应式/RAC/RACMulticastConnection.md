# RACMulticastConnection

## 使用

在项目中我们一般都会涉及网络请求，在使用RAC进行网络请求的时候我们可以这样子写：

```objective-c
- (void)RACMulticastConnectionTest {
    RACSignal *signal = [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
        NSLog(@"发送网络请求");
        [subscriber sendNext:@"得到网络请求数据"];
        return nil;
    }];
    //普通的订阅
    [signal subscribeNext:^(id  _Nullable x) {
        NSLog(@"1 - %@",x);
    }];
    [signal subscribeNext:^(id  _Nullable x) {
        NSLog(@"2 - %@",x);
    }];
    [signal subscribeNext:^(id  _Nullable x) {
        NSLog(@"3 - %@",x);
    }];
    
    //MulticastConnection
    RACMulticastConnection *connect = [signal publish];
    [connect.signal subscribeNext:^(id  _Nullable x) {
            NSLog(@"11 - %@",x);
    }];
    [connect.signal subscribeNext:^(id  _Nullable x) {
            NSLog(@"22 - %@",x);
    }];
    [connect.signal subscribeNext:^(id  _Nullable x) {
            NSLog(@"33 - %@",x);
    }];
    [connect connect];
}
```

打印结果

```
发送网络请求
1 - 得到网络请求数据
发送网络请求
2 - 得到网络请求数据
发送网络请求
3 - 得到网络请求数据
发送网络请求
11 - 得到网络请求数据
22 - 得到网络请求数据
33 - 得到网络请求数据
```

# 内部实现

1. 创建信号这个步骤就不用在多说了（保存了一个block，didSubscribe）
2. 把信号转化成为一个连接类`[signal publish]`

​		在`publish`方法中首先创建了一个`subject`然后调用`multicast`创建了一个连接类，在创建连接类的时候把`signal`和`subject`保存了起来。

```objective-c
- (RACMulticastConnection *)publish {
	RACSubject *subject = [[RACSubject subject] setNameWithFormat:@"[%@] -publish", self.name];
	RACMulticastConnection *connection = [self multicast:subject];
	return connection;
}

- (RACMulticastConnection *)multicast:(RACSubject *)subject {
	[subject setNameWithFormat:@"[%@] -multicast: %@", self.name, subject.name];
	RACMulticastConnection *connection = [[RACMulticastConnection alloc] initWithSourceSignal:self subject:subject];
	return connection;
}
```

```objective-c
- (instancetype)initWithSourceSignal:(RACSignal *)source subject:(RACSubject *)subject {
	NSCParameterAssert(source != nil);
	NSCParameterAssert(subject != nil);

	self = [super init];

	_sourceSignal = source;
	_serialDisposable = [[RACSerialDisposable alloc] init];
	_signal = subject;
	
	return self;
}
```

3. 在调用的时候就不是调用原来的`signal`了，而是调用`connect`连接类的信号，但是在`publish`这个方法中我们把`subject`保存了起来，所以还是在调用`subject`。
    在init方法中赋值`_signal = subject;`
4. 在最后的`connect`方法中，在用之前保存的`signal`订阅我们保存的`subject`,也就是说在这里才是真正的订阅了我们的信号，这个时候才会去调用我们最开始保存的`didSubscribe`这个block，而发送数据的其实是我们在`publish`中保存的`subject`，所以就完成了一次创建多次订阅了。

```objective-c
- (RACDisposable *)connect {
	BOOL shouldConnect = OSAtomicCompareAndSwap32Barrier(0, 1, &_hasConnected);

	if (shouldConnect) {
		self.serialDisposable.disposable = [self.sourceSignal subscribe:_signal];
	}

	return self.serialDisposable;
}
```









































