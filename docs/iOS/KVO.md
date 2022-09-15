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

## 打印person对象的类
```objective-c
NSLog(@"%@", object_getClass(self.person));
[self.person addObserver:self forKeyPath:@"name" options:NSKeyValueObservingOptionNew | NSKeyValueObservingOptionOld context:nil];
NSLog(@"%@", object_getClass(self.person));
```
动态生成类NSKVONotifying_xxx

## NSKVONotifying_xxx重写了哪些方法
使用runtime打印方法列表
```
unsigned int count;
Method *methods = class_copyMethodList(object_getClass(self.person), &count);
    
for (NSInteger index = 0; index < count; index++) {
   Method method = methods[index];
   
   NSString *methodStr = NSStringFromSelector(method_getName(method));
   
   NSLog(@"%@\n", methodStr);
}
```
打印结果：
>
    setName:
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
