## 监听方法

rac_signalForSelector

```objective-c
RACView *v = [[RACView alloc]initWithFrame:CGRectMake(100, 300, 150, 80)];
    [self.view addSubview:v];
    [[v rac_signalForSelector:@selector(testRACView:par:)] subscribeNext:^(RACTuple * _Nullable x) {
        NSLog(@"我检测到了视图方法的调用");
    }];
```

点击查看方法调用

```objective-c
- (RACSignal *)rac_signalForSelector:(SEL)selector {
	NSCParameterAssert(selector != NULL);

	return NSObjectRACSignalForSelector(self, selector, NULL);
}
```

```objective-c
//返回值是一个RACSignal
static RACSignal *NSObjectRACSignalForSelector(NSObject *self, SEL selector, Protocol *protocol) {
	SEL aliasSelector = RACAliasForSelector(selector);

	@synchronized (self) {
	//创建的是RACSubject
		RACSubject *subject = objc_getAssociatedObject(self, aliasSelector);
		if (subject != nil) return subject;

		Class class = RACSwizzleClass(self);
		NSCAssert(class != nil, @"Could not swizzle class of %@", self);

		subject = [[RACSubject subject] setNameWithFormat:@"%@ -rac_signalForSelector: %s", RACDescription(self), sel_getName(selector)];
		objc_setAssociatedObject(self, aliasSelector, subject, OBJC_ASSOCIATION_RETAIN);

		[self.rac_deallocDisposable addDisposable:[RACDisposable disposableWithBlock:^{
			[subject sendCompleted];
		}]];

		Method targetMethod = class_getInstanceMethod(class, selector);
		if (targetMethod == NULL) {
			const char *typeEncoding;
			if (protocol == NULL) {
				typeEncoding = RACSignatureForUndefinedSelector(selector);
			} else {
				// Look for the selector as an optional instance method.
				struct objc_method_description methodDescription = protocol_getMethodDescription(protocol, selector, NO, YES);

				if (methodDescription.name == NULL) {
					// Then fall back to looking for a required instance
					// method.
					methodDescription = protocol_getMethodDescription(protocol, selector, YES, YES);
					NSCAssert(methodDescription.name != NULL, @"Selector %@ does not exist in <%s>", NSStringFromSelector(selector), protocol_getName(protocol));
				}

				typeEncoding = methodDescription.types;
			}

			RACCheckTypeEncoding(typeEncoding);

			// Define the selector to call -forwardInvocation:.
			if (!class_addMethod(class, selector, _objc_msgForward, typeEncoding)) {
				NSDictionary *userInfo = @{
					NSLocalizedDescriptionKey: [NSString stringWithFormat:NSLocalizedString(@"A race condition occurred implementing %@ on class %@", nil), NSStringFromSelector(selector), class],
					NSLocalizedRecoverySuggestionErrorKey: NSLocalizedString(@"Invoke -rac_signalForSelector: again to override the implementation.", nil)
				};

				return [RACSignal error:[NSError errorWithDomain:RACSelectorSignalErrorDomain code:RACSelectorSignalErrorMethodSwizzlingRace userInfo:userInfo]];
			}
		} else if (method_getImplementation(targetMethod) != _objc_msgForward) {
			// Make a method alias for the existing method implementation.
			const char *typeEncoding = method_getTypeEncoding(targetMethod);

			RACCheckTypeEncoding(typeEncoding);

			BOOL addedAlias __attribute__((unused)) = class_addMethod(class, aliasSelector, method_getImplementation(targetMethod), typeEncoding);
			NSCAssert(addedAlias, @"Original implementation for %@ is already copied to %@ on %@", NSStringFromSelector(selector), NSStringFromSelector(aliasSelector), class);

			// Redefine the selector to call -forwardInvocation:.
			class_replaceMethod(class, selector, _objc_msgForward, method_getTypeEncoding(targetMethod));
		}

		return subject;
	}
}

```

从上面可以看出返回值是信号，既然是信号那就可以订阅

内部创建的是subject，那就可以发送信号，订阅信号
所以我们在调用`rac_signalForSelector`这个方法可以直接订阅，内部又是一个`subject`，所以他会发送信号给到我们

## 监听属性

通常我们要使用KVO需要`addObserver`并且还要在`observeValueForKeyPath...`这个方法中去监听，
 如果一个界面监听多个还需要判断，还必须记得释放掉。
 但是这些东西在RAC中就做了一层包装，现在我们如果想监听对象的某个属性，就可以写如下代码就可以完成，
 并且针对某个属性都会产生不同的信号，我们只需要监听所产生的信号在进行处理就可以了

```objective-c
    //监听属性
    //    方法一
    [v rac_observeKeyPath:@"frame" options:NSKeyValueObservingOptionNew observer:nil block:^(id value, NSDictionary *change, BOOL causedByDealloc, BOOL affectedOnlyLastComponent) {
        NSLog(@"1 - %@",value);
    }];
    //    方法二
    [[v rac_valuesForKeyPath:@"frame" observer:nil] subscribeNext:^(id  _Nullable x) {
        NSLog(@"2 - %@",x);
    }];
    //    方法三
    [RACObserve(v, frame) subscribeNext:^(id  _Nullable x) {
        NSLog(@"3 - %@",x);
    }];
    
    v.frame = CGRectMake(100, 400, 150, 100);
```

注意：写法二、写法三需要在程序运行的时候就会监听到，通过log就可以看出区别。

## 监听事件

```objective-c
[[button rac_signalForControlEvents:UIControlEventTouchUpInside] subscribeNext:^(__kindof UIControl * _Nullable x) {
  NSLog(@"点击按钮了");
}];
```

内部实现

```objective-c
- (RACSignal *)rac_signalForControlEvents:(UIControlEvents)controlEvents {
	@weakify(self);

	return [[RACSignal
		createSignal:^(id<RACSubscriber> subscriber) {
			@strongify(self);

			[self addTarget:subscriber action:@selector(sendNext:) forControlEvents:controlEvents];

			RACDisposable *disposable = [RACDisposable disposableWithBlock:^{
				[subscriber sendCompleted];
			}];
			[self.rac_deallocDisposable addDisposable:disposable];

			return [RACDisposable disposableWithBlock:^{
				@strongify(self);
				[self.rac_deallocDisposable removeDisposable:disposable];
				[self removeTarget:subscriber action:@selector(sendNext:) forControlEvents:controlEvents];
			}];
		}]
		setNameWithFormat:@"%@ -rac_signalForControlEvents: %lx", RACDescription(self), (unsigned long)controlEvents];
}
```

里面最关键的代码就是`[self addTarget:subscriber action:@selector(sendNext:) forControlEvents:controlEvents];`
 `self` 就是`btn`本身，因为是`btn`调用的方法
 `target`是`subscriber`订阅者
`action`是 ：`sendNext:`
 事件是传入的事件，
 所以现在按钮的点击方法会通过`subscriber`去调用`sendNext方法`,我们之前有提到过，`RACSignal`，所以这个时候我们订阅他就可以拿到`sendNext`的值。

## 手势

```objective-c
UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc] init];
[textLab addGestureRecognizer:tap];
[[tap rac_gestureSignal] subscribeNext:^(id x) {
    NSLog(@"点击Lab");
}];
```

## 通知

```objective-c
    [[[NSNotificationCenter defaultCenter] rac_addObserverForName:UIKeyboardDidShowNotification object:nil] subscribeNext:^(NSNotification * _Nullable x) {
            NSLog(@"%@",x);
    }];
```

这样处理事件非常的内聚呢，并且管理起来也很方便。但是内部是怎么样处理的呢？
一起来揭开他的面纱

```objective-c
- (RACSignal *)rac_addObserverForName:(NSString *)notificationName object:(id)object {
	@unsafeify(object);
	return [[RACSignal createSignal:^(id<RACSubscriber> subscriber) {
		@strongify(object);
		id observer = [self addObserverForName:notificationName object:object queue:nil usingBlock:^(NSNotification *note) {
			[subscriber sendNext:note];
		}];

		return [RACDisposable disposableWithBlock:^{
			[self removeObserver:observer];
		}];
	}] setNameWithFormat:@"-rac_addObserverForName: %@ object: <%@: %p>", notificationName, [object class], object];
}
```

没错又是`RACSignal`，这个里面的代码很简单，就是调用系统提供的方法，在`block`中使用订阅者发布信息，在`RACDisposable`中把`observer`移除。

## 监听textfield输入

```objective-c
    UITextField *textField = [[UITextField alloc]init];
    [textField.rac_textSignal subscribeNext:^(NSString * _Nullable x) {
        NSLog(@"%@",x);
      label.text = x;
    }];
```

textField的文字改变，同时修改label的文字。

```objective-c
RAC(label,text) = textField.rac_textSignal;
```

其中RAC是一个宏，宏的用法：

RAC(对象，对象的属性) = (一个信号);
比如：RAC(btn,enable) = (RACSignal) 按钮的enable等于一个信号

## 代替代理

通常需要定义代理，实现代理协议方法，并且还要注意循环引用等问题存在，RAC也可以做到代替代理。

创建一个`view`，内部添加一个`button`。我们要做的就是监听`button`按下事件。

1、在处理完成UI之后，创建一个`GreenView`，并导入头文件`#import "ReactiveObjC.h"`

2、创建一个`RACSubject`并且命名为`btnClickSignal`，这里大家需要注意是命名尽量规范，否则以后维护起来你会很痛苦。然后这里为什么会用`RACSubject`，因为`RACSubject`可以自己控制发送数据时间。

目前为止代码应该类似于这样子：

```objective-c
#import <UIKit/UIKit.h>
#import "ReactiveObjC.h"
@interface GreenView : UIView
@property (nonatomic,strong) RACSubject *btnClickSignal;
@end
```

进入`.m`文件，完成下面代码

```objective-c
#import "GreenView.h"

@implementation GreenView

- (RACSubject *)btnClickSignal{
    if (!_btnClickSignal) {
        _btnClickSignal = [RACSubject subject];
    }
    return _btnClickSignal;
}

- (IBAction)btnClick:(id)sender{
    [_btnClickSignal sendNext:@"我可以代替代理哦"];
}

@end
```

上面代码中完成了两个功能：懒加载`RACSubject`，以及在按钮点击时候发布数据

然后回到`ViewController`中

```objective-c
- (void)replaceDelegate{
    [_greenView.btnClickSignal subscribeNext:^(id  _Nullable x) {
        NSLog(@"%@",x);
    }];
}
```

比传统的代理来的更简单、内聚。



























































