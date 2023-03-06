# KVO

KVO（Key Value Observing）
1. 添加观察
2. 回调观察
3. 移除观察
    可能有野指针

## 自定义kvo

kvo基于runtime
A监听B 系统会创建子类NSKVONotifying_B

### 1、objc_allocateClassPair

### 2、objc_registerClassPair

### 3、object_setClass

B的isa 指向NSKVONotifying_B

### 4、class_addMethod

#### 4.1、添加class方法

#### 4.2、添加setter方法

##### 调用父类方法objc_msgSendSuper

objc_msgSend(observer, @selector(observeValueForKeyPath:ofObject:change:context:),key,self,@{key:newName},nil);

#### 4.3、添加dealloc方法

`object_setClass`isa指针指向原本的类。

## 打印person对象的类
```objective-c
NSLog(@"%@", object_getClass(self.person));
[self.person addObserver:self forKeyPath:@"name" options:NSKeyValueObservingOptionNew | NSKeyValueObservingOptionOld context:nil];
NSLog(@"%@", object_getClass(self.person));
```
动态生成类NSKVONotifying_xxx

## NSKVONotifying_xxx重写了哪些方法
使用runtime打印方法列表
```objective-c
unsigned int count;
Method *methods = class_copyMethodList(object_getClass(self.person), &count);
    
for (NSInteger index = 0; index < count; index++) {
   Method method = methods[index];
   
   NSString *methodStr = NSStringFromSelector(method_getName(method));
   
   NSLog(@"%@\n", methodStr);
}
```
打印结果：
>setName:
    class
    dealloc
    _isKVOA

简单分析下重写这些方法的作用：
class：重写这个方法，是为了伪装苹果自动为我们生成的中间类。
dealloc：应该是处理对象销毁之前的一些收尾工作
_isKVOA：告诉系统使用了kvo

注：
remove的时候 把isa指针再指回来
object_setClass(self, class);

## swift - KVO

- 只有 NSObject 才能支持 KVO。
- 要观察的属性必须使用 @objc dynamic 修饰。

iOS 11和Swift 4为KVO带来了重大变化.

- 这些类应该采用`@objcMembers`注释,以使KVO或KVO无声地失败.
- 必须声明要观察的变量`dynamic`.

这是更新的实现,

```swift
@objcMembers
class Approval: NSObject {

    dynamic var approved: Bool = false

    let ApprovalObservingContext = UnsafeMutableRawPointer(bitPattern: 1)

    override init() {
        super.init()

        addObserver(self,
                    forKeyPath: #keyPath(approved),
                    options: [.new, .old],
                    context: ApprovalObservingContext)
    }

    override func observeValue(forKeyPath keyPath: String?,
                               of object: Any?,
                               change: [NSKeyValueChangeKey : Any]?,
                               context: UnsafeMutableRawPointer?) {
        guard let observingContext = context,
            observingContext == ApprovalObservingContext else {
                super.observeValue(forKeyPath: keyPath,
                                   of: object,
                                   change: change,
                                   context: context)
                return
        }

        guard let change = change else {
            return
        }

        if let oldValue = change[.oldKey] {
            print("Old value \(oldValue)")
        }

        if let newValue = change[.newKey]  {
            print("New value \(newValue)")
        }

    }

    deinit {
        removeObserver(self, forKeyPath: #keyPath(approved))
    }
}
```

KVO还有一个新的基于bock的api,就像这样工作,

```swift
@objcMembers
class Approval: NSObject {

    dynamic var approved: Bool = false

    var approvalObserver: NSKeyValueObservation!

    override init() {
        super.init()
        approvalObserver = observe(\.approved, options: [.new, .old]) { _, change in
            if let newValue = change.newValue {
                print("New value is \(newValue)")
            }

            if let oldValue = change.oldValue {
                print("Old value is \(oldValue)")
            }
        }

    }
}
```

基于块的api看起来超级好用且易于使用.此外,KeyValueObservation在deinited时无效,因此不需要删除观察者.
