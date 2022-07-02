# RACDisposable

创建RACSignal的时候上次我们选择直接返回nil，这次我们返回一个`RACDisposable`对象

```objective-c
    //1、创建信号量
    RACSignal * signal = [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
        
        NSLog(@"创建信号量");
        
        //3、发布信息
        [subscriber sendNext:@"I'm send next data"];
        
        NSLog(@"那我啥时候运行");
        
        return [RACDisposable disposableWithBlock:^{
            NSLog(@"RACDisposable");
        }];
    }];
    
    //2、订阅信号量
    [signal subscribeNext:^(id  _Nullable x) {
        NSLog(@"%@",x);
    }];
```

看下内部做了什么，点进去看看

```objective-c
+ (instancetype)disposableWithBlock:(void (^)(void))block {
	return [(RACDisposable *)[self alloc] initWithBlock:block];
}
//这里代码就简单了，创建这个对象的时候保存block
```

##### 然后在创建`RACDisposable`对象劈头盖脸的就是一个block，但是这个block啥时候调用呢？

1. 订阅者被销毁
2.  `RACDisposable` 调用`dispose`取消订阅

##### 然后我们就试验证明情况

订阅者被销毁

在运行上面的代码之后`RACDisposable`的block也如期而至的调用了，然后我么仔细观察一下代码，
发生订阅者没有强引用，所以会调用`RACDisposable`的block，
现在我们把订阅者强引用，不让他销毁，看会发生什么。

```objective-c
    //1、创建信号量
    RACSignal * signal = [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
        
        NSLog(@"创建信号量");
        
        //3、发布信息
        [subscriber sendNext:@"I'm send next data"];
        
      //强引用 RACDisposable不会走释放方法
        self.subscriber = subscriber;
        
        NSLog(@"那我啥时候运行");
        
        return [RACDisposable disposableWithBlock:^{
            NSLog(@"RACDisposable");
        }];
    }];
    
    //2、订阅信号量
    [signal subscribeNext:^(id  _Nullable x) {
        NSLog(@"%@",x);
    }];
```

由此可以得知

订阅者销毁会调用`RACDisposable`的block
然后我们接着证明第二点，就算在强引用订阅者的情况下，主动调用`dispose`也会调用block

```objective-c
    //1、创建信号量
    RACSignal * signal = [RACSignal createSignal:^RACDisposable * _Nullable(id<RACSubscriber>  _Nonnull subscriber) {
        
        NSLog(@"创建信号量");
        
        //3、发布信息
        [subscriber sendNext:@"I'm send next data"];
        
        self.subscriber = subscriber;
        
        NSLog(@"那我啥时候运行");
        
        return [RACDisposable disposableWithBlock:^{
            NSLog(@"RACDisposable");
        }];
    }];
    
    //2、订阅信号量
    RACDisposable *disposable = [signal subscribeNext:^(id  _Nullable x) {
        NSLog(@"%@",x);
    }];
    
    //主动出发取消订阅
    [disposable dispose];
```

