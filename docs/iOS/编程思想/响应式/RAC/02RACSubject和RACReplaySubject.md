# RACSubject

RACSignal是不具备发送信号的能力的，但是`RACSubject`这个类就可以做到订阅／发送为一体。
 之前还提到过RAC三部曲，在RACSuject中同样适用。

##### 然后我们先创建一个简单的代码段，然后接着分析分析。

```objective-c
    //1 创建信号
//创建一个数组
    RACSubject *subject = [RACSubject subject];

    //2 订阅信号
//创建一个订阅者0
//将block保存到o里面
//将订阅者保存到第一步创建的数组里面
    [subject subscribeNext:^(id  _Nullable x) {
        NSLog(@"订阅者%@",x);
    }];
    //3 发送数据
    [subject sendNext:@"发送数据第一个"];
```

##### 先看看创建信号会干啥吧

```objective-c
+ (instancetype)subject {
	return [[self alloc] init];
}

- (instancetype)init {
	self = [super init];
	if (self == nil) return nil;
	//干掉订阅，类似移除通知
	_disposable = [RACCompoundDisposable compoundDisposable];
  //可变数组
	_subscribers = [[NSMutableArray alloc] initWithCapacity:1];
	
	return self;
}
```

从上图中可以很直观的看到 调用`subject`方法内部事创建了一个`_disposable`取消信号和一个数组`_subscribers`，这个数组从命名上就可以看出来这个数组是用来保存订阅者。

```objective-c
- (void)dealloc {
	[self.disposable dispose];
}
```

在dealloc中调用干掉订阅方法。

##### 然后是订阅信号

参数是block，响应代码

```objective-c
- (RACDisposable *)subscribeNext:(void (^)(id x))nextBlock {
	NSCParameterAssert(nextBlock != NULL);
	//订阅者对象
	RACSubscriber *o = [RACSubscriber subscriberWithNext:nextBlock error:NULL completed:NULL];
	return [self subscribe:o];
}
```

```objective-c
+ (instancetype)subscriberWithNext:(void (^)(id x))next error:(void (^)(NSError *error))error completed:(void (^)(void))completed {
  //订阅者
	RACSubscriber *subscriber = [[self alloc] init];

	subscriber->_next = [next copy];//外面写的响应代码
	subscriber->_error = [error copy];
	subscriber->_completed = [completed copy];

	return subscriber;
}
```

这里很简单，创建一个订阅者，然后调用  `[self subscribe:o]`方法，细心的你可能还记得在`RACSignal`中也调用了这个方法，但是需要注意的是这两个方法并不是一个方法，内部实现不一样。

选中这个方法进去

```objective-c
- (RACDisposable *)subscribe:(id<RACSubscriber>)subscriber {
	NSCParameterAssert(subscriber != nil);

	RACCompoundDisposable *disposable = [RACCompoundDisposable compoundDisposable];
	subscriber = [[RACPassthroughSubscriber alloc] initWithSubscriber:subscriber signal:self disposable:disposable];

	NSMutableArray *subscribers = self.subscribers;
	@synchronized (subscribers) {
		[subscribers addObject:subscriber];//把订阅者保存到数组中
	}
	
	[disposable addDisposable:[RACDisposable disposableWithBlock:^{
		@synchronized (subscribers) {
			// Since newer subscribers are generally shorter-lived, search
			// starting from the end of the list.
			NSUInteger index = [subscribers indexOfObjectWithOptions:NSEnumerationReverse passingTest:^ BOOL (id<RACSubscriber> obj, NSUInteger index, BOOL *stop) {
				return obj == subscriber;
			}];

			if (index != NSNotFound) [subscribers removeObjectAtIndex:index];
		}
	}]];

	return disposable;
}
```

通过上面的代码得知：在订阅的时候会把订阅者保存到一开始创建`RACSubject`中的数组`_subscribers`中去。

##### 最后是发布信息

```objective-c
    [subject sendNext:@"发送数据第一个"];
```

遍历数组 发送消息

```objective-c
- (void)enumerateSubscribersUsingBlock:(void (^)(id<RACSubscriber> subscriber))block {
	NSArray *subscribers;
	@synchronized (self.subscribers) {//第一步的数组
		subscribers = [self.subscribers copy];
	}

	for (id<RACSubscriber> subscriber in subscribers) {//拿到订阅者对象 之前的o
		block(subscriber);
	}
}

#pragma mark RACSubscriber

- (void)sendNext:(id)value {
	[self enumerateSubscribersUsingBlock:^(id<RACSubscriber> subscriber) {
		[subscriber sendNext:value];
	}];
}
```

```objective-c
#pragma mark RACSubscriber
- (void)sendNext:(id)value {
	@synchronized (self) {
		void (^nextBlock)(id) = [self.next copy];
		if (nextBlock == nil) return;

		nextBlock(value);
	}
}
```

### 总结：

1. 创建的subject的是内部会创建一个数组`_subscribers`用来保存所有的订阅者
2. 订阅信息的时候会创建订阅者，并且保存到数组中
3. 遍历subject中`_subscribers`中的订阅者，依次发送信息

所以对于RACSignal不同的地方是：他可以被订阅多次，并且只能是先订阅后发布。

# RACReplaySubject

##### 如果非要先发送在订阅，并且也要能收到怎么处理呢？

可以使用RACReplaySubject

`RACReplaySubject`，他继承`RACSubject`，他的目的就是为了解决上面必须先订阅后发送的问题。

```objective-c
- (void)RACReplaySubjectTest {
    RACReplaySubject *replaySubject = [RACReplaySubject subject];
    [replaySubject sendNext:@"我先发送数据了，等你接受哦"];
    [replaySubject subscribeNext:^(id  _Nullable x) {
        NSLog(@"%@",x);
    }];
}
```

#### 创建信号

还记得RACSubject就是在init中做了初始化，不记得就到文章开头开开，所以我们直接看他对init做了啥处理吧

```objective-c
- (instancetype)init {
	return [self initWithCapacity:RACReplaySubjectUnlimitedCapacity];
}

- (instancetype)initWithCapacity:(NSUInteger)capacity {
	self = [super init];
	
	_capacity = capacity;
	_valuesReceived = (capacity == RACReplaySubjectUnlimitedCapacity ? [NSMutableArray array] : [NSMutableArray arrayWithCapacity:capacity]);
	
	return self;
}
```

#### 发送信号

```objective-c
- (void)sendNext:(id)value {
	@synchronized (self) {
		[self.valuesReceived addObject:value ?: RACTupleNil.tupleNil];
		
		if (self.capacity != RACReplaySubjectUnlimitedCapacity && self.valuesReceived.count > self.capacity) {
			[self.valuesReceived removeObjectsInRange:NSMakeRange(0, self.valuesReceived.count - self.capacity)];
		}
		
		[super sendNext:value];
	}
}
```

可以看到代码中在发送之前做了一件事情，把要发送的数据保存到数组中，然后调用父类的发送方法，发送玩了看发送成功了没，成功了就删除数据，避免一个数据多次发送。

#### 订阅信号

```objective-c
- (RACDisposable *)subscribe:(id<RACSubscriber>)subscriber {
	RACCompoundDisposable *compoundDisposable = [RACCompoundDisposable compoundDisposable];

	RACDisposable *schedulingDisposable = [RACScheduler.subscriptionScheduler schedule:^{
		@synchronized (self) {
      //订阅信号的时候会遍历一次数组，如果有数据就发送数据
			for (id value in self.valuesReceived) {//self.valuesReceived是在创建的时候保存的那个数组
				if (compoundDisposable.disposed) return;

				[subscriber sendNext:(value == RACTupleNil.tupleNil ? nil : value)];
			}

			if (compoundDisposable.disposed) return;

			if (self.hasCompleted) {
				[subscriber sendCompleted];
			} else if (self.hasError) {
				[subscriber sendError:self.error];
			} else {
				RACDisposable *subscriptionDisposable = [super subscribe:subscriber];
				[compoundDisposable addDisposable:subscriptionDisposable];
			}
		}
	}];

	[compoundDisposable addDisposable:schedulingDisposable];

	return compoundDisposable;
}
```

### 总结：

1. 创建的时候会在父类的基础之上多做一步，创建一个数组用来保存发送的数据
2. 发送数据，但是此时发送会失败啊，为什么？因为没有人订阅啊，我发给谁啊。
3. 订阅信号，先遍历一次保存数据的数组，如果有就执行 2 。