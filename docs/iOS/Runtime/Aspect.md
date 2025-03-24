# Aspects切面

面向切面编程（AOP）

在不修改原有代码结构的情况下，为程序添加额外的行为，比如日志记录、性能监控、事务处理、异常处理等。业务逻辑隔离，代码耦合度降低。

在 iOS 开发中，这通常是通过运行时(Runtime)方法交换(Method Swizzling)来实现的。

面向对象的扩展

通过预编译的方式或者运行时期动态代理

## 继承 

耦合程度高。

需要对基类修改。

## AOP

分类：具体业务逻辑拆分

runtime。

SDWebImage。 Manager	downloader和cache。下载功能逻辑。

埋点 打log：抽取一个基类：log方法。如果A类不具备log功能，继承基类，对ModuleA造成一定污染，入侵。

## 原理

Hook person的test方法，不是交换imp，而是先交换person中的ForwardInvocation，指向自定义的函数。

Aspects 库简化了面向切面编程的实现。Aspects 库通过 Objective-C 的动态特性，允许开发者在运行时拦截消息，并为其添加前置、后置或替换执行的代码。这里是它的基本原理：

1. **消息发送机制**：Objective-C 是一门动态语言，它的方法调用是通过消息发送（message sending）实现的。当你对一个对象发送消息时（即调用一个方法），Objective-C 的运行时系统会寻找这个消息对应的方法实现，并执行它。

2. **Method Swizzling**：这是 Objective-C 运行时的一个特性，允许开发者在运行时交换两个方法的实现。这意味着你可以将一个方法的实现动态地替换为另一个方法的实现。

3. **Block（闭包）**：Aspects 使用了 Objective-C 的 block 语法来允许开发者定义在原方法执行前、执行后或替换原方法时要执行的代码块。

4. **动态方法解析**：Aspects 可能会使用 Objective-C 的动态方法解析来动态地添加方法实现，或者在某个方法被调用时进行拦截。

5. **关联对象**：Aspects 可能会使用 Objective-C 的关联对象（associated objects）功能来在运行时给现有类添加存储属性，这样可以存储需要在方法拦截中使用的信息。

## 类

### AspectOptions

枚举，用来定义切面的时机

```objective-c
typedef NS_OPTIONS(NSUInteger, AspectOptions) {
    /// 原有方法调用前执行（default）
    AspectPositionAfter   = 0,            /// Called after the original implementation (default)
    /// 替换原有方法
    AspectPositionInstead = 1,            /// Will replace the original implementation.
    /// 原有方法调用后执行
    AspectPositionBefore  = 2,            /// Called before the original implementation.
    /// 执行完之后就恢复切面操作，即撤销hook。只执行一次（调用完就删除切面逻辑）
    AspectOptionAutomaticRemoval = 1 << 3 /// Will remove the hook after the first execution.
};
```

### AspectInfo

NSInvocation sign target 信息

### AspectIdentifier

一个model，用来存储hook方法的原有方法、切面block、block方法签名、切面时机。

```objective-c
@interface AspectIdentifier : NSObject
+ (instancetype)identifierWithSelector:(SEL)selector object:(id)object options:(AspectOptions)options block:(id)block error:(NSError **)error;
- (BOOL)invokeWithInfo:(id<AspectInfo>)info;
@property (nonatomic, assign) SEL selector;//原来方法的SEL
@property (nonatomic, strong) id block;//保存要执行的切面block，即原方法执行前后要调用的方法
@property (nonatomic, strong) NSMethodSignature *blockSignature;//block签名信息
@property (nonatomic, weak) id object;//target，即保存当前对象
@property (nonatomic, assign) AspectOptions options;//是个枚举，切面执行时机
@end
```

### AspectsContainer

以关联对象的形式存储在当前类或对象中，主要用来存储当前类或对象所有的切面信息。

```objective-c
@interface AspectsContainer : NSObject
- (void)addAspect:(AspectIdentifier *)aspect withOptions:(AspectOptions)injectPosition;
- (BOOL)removeAspect:(id)aspect;
- (BOOL)hasAspects;
@property (atomic, copy) NSArray *beforeAspects;//存储原方法 调用前要执行的操作
@property (atomic, copy) NSArray *insteadAspects;//存储替换原方法的操作
@property (atomic, copy) NSArray *afterAspects;//存储原方法调用后要执行的操作
@end
```

### AspectTracker

追踪类 对象所有hook操作。

作用：方便撤销。

## 调用流程

**对外暴露的核心API**

```objective-c
/// 作用域：针对所有对象生效
/// @param selector 需要hook的方法
/// @param options 是个枚举，主要定义了切面的时机（调用前、替换、调用后）
/// @param block 需要在selector前后插入执行的代码块
/// @param error 错误信息
+ (id<AspectToken>)aspect_hookSelector:(SEL)selector
                           withOptions:(AspectOptions)options
                            usingBlock:(id)block
                                 error:(NSError **)error;

/// 作用域：针对当前对象生效
- (id<AspectToken>)aspect_hookSelector:(SEL)selector
                           withOptions:(AspectOptions)options
                            usingBlock:(id)block
                                 error:(NSError **)error;
```

### 存储切面信息

存储切面信息主要用到了AspectIdentifier、AspectsContainer两个类

1. 获取当前类的容器对象 aspectContainer ，如果没有则创建一个
2. 创建一个标识符对象 identifier ，用来存储原方法信息、block、切面时机等信息
3. 把标识符对象 identifier 添加到容器中

类方法 对象方法都调用了aspect_add

- 初始化AspectIdentifier这个类。
  - IMP
  - block
  - 获取block的签名信息，然后进行比对。
- 比较签名信息
  - block sign > sel sign 直接pass
  - Block sign > 1，第一个默认参数遵循了AspectInfo协议
  - 从第二位开始 一一比较，通过for循环遍历。
- 通过options添加到容器对应的数组中。

### aspect_add

```objective-c
static id aspect_add(id self, SEL selector, AspectOptions options, id block, NSError **error) {
    NSCParameterAssert(self);
    NSCParameterAssert(selector);
    NSCParameterAssert(block);

    __block AspectIdentifier *identifier = nil;
    //自旋锁 保证安全性 block内容的执行是互斥的
    aspect_performLocked(^{
        //aspect_isSelectorAllowedAndTrack 过滤。有一些方法不能hook
        if (aspect_isSelectorAllowedAndTrack(self, selector, options, error)) {
            //获取容器对象，主要用来存储当前类或对象所有切面信息。
            //容器的对象以关联对象的方式添加到了当前对象上，key值为：前缀+selector
            AspectsContainer *aspectContainer = aspect_getContainerForObject(self, selector);
            //初始化切片信息。 创建标识符，用来存储SEL、block、切片时机（调用前、调用后）等信息
            identifier = [AspectIdentifier identifierWithSelector:selector object:self options:options block:block error:error];
            if (identifier) {
                //把identifier添加到容器中
                [aspectContainer addAspect:identifier withOptions:options];
								
                // Modify the class to allow message interception.
              	// 修改类以允许消息拦截
                aspect_prepareClassAndHookSelector(self, selector, error);
            }
        }
    });
    return identifier;
}
```

### aspect_isSelectorAllowedAndTrack

过滤拦截

```objective-c
static BOOL aspect_isSelectorAllowedAndTrack(NSObject *self, SEL selector, AspectOptions options, NSError **error) {
    static NSSet *disallowedSelectorList;
    static dispatch_once_t pred;
    dispatch_once(&pred, ^{//初始化黑名单列表，有些方法禁止hook的
        disallowedSelectorList = [NSSet setWithObjects:@"retain", @"release", @"autorelease", @"forwardInvocation:", nil];
    });

    // Check against the blacklist.
    //第一步：检查是否在黑名单内
    NSString *selectorName = NSStringFromSelector(selector);
    if ([disallowedSelectorList containsObject:selectorName]) {
        NSString *errorDescription = [NSString stringWithFormat:@"Selector %@ is blacklisted.", selectorName];
        AspectError(AspectErrorSelectorBlacklisted, errorDescription);
        return NO;
    }

    // Additional checks.
    //第二步：dealloc方法只能在调用前插入
    AspectOptions position = options&AspectPositionFilter;
    if ([selectorName isEqualToString:@"dealloc"] && position != AspectPositionBefore) {
        NSString *errorDesc = @"AspectPositionBefore is the only valid position when hooking dealloc.";
        AspectError(AspectErrorSelectorDeallocPosition, errorDesc);
        return NO;
    }
    //第三步：检查类是否存在这个方法
    if (![self respondsToSelector:selector] && ![self.class instancesRespondToSelector:selector]) {
        NSString *errorDesc = [NSString stringWithFormat:@"Unable to find selector -[%@ %@].", NSStringFromClass(self.class), selectorName];
        AspectError(AspectErrorDoesNotRespondToSelector, errorDesc);
        return NO;
    }

    // Search for the current class and the class hierarchy IF we are modifying a class object
    //第四步：如果是类而非实例（这个是类，不是类方法，是指hook的作用域对所有对象都生效），则在整个类即继承链中，同一个方法只能被hook一次，即对于所有实例对象都生效的操作，整个继承链中只能被hook一次。
    if (class_isMetaClass(object_getClass(self))) {
        Class klass = [self class];
        NSMutableDictionary *swizzledClassesDict = aspect_getSwizzledClassesDict();
        Class currentClass = [self class];

        AspectTracker *tracker = swizzledClassesDict[currentClass];
        if ([tracker subclassHasHookedSelectorName:selectorName]) {
            NSSet *subclassTracker = [tracker subclassTrackersHookingSelectorName:selectorName];
            NSSet *subclassNames = [subclassTracker valueForKey:@"trackedClassName"];
            NSString *errorDescription = [NSString stringWithFormat:@"Error: %@ already hooked subclasses: %@. A method can only be hooked once per class hierarchy.", selectorName, subclassNames];
            AspectError(AspectErrorSelectorAlreadyHookedInClassHierarchy, errorDescription);
            return NO;
        }

        do {
            tracker = swizzledClassesDict[currentClass];
            if ([tracker.selectorNames containsObject:selectorName]) {
                if (klass == currentClass) {
                    // Already modified and topmost!
                    return YES;
                }
                NSString *errorDescription = [NSString stringWithFormat:@"Error: %@ already hooked in %@. A method can only be hooked once per class hierarchy.", selectorName, NSStringFromClass(currentClass)];
                AspectError(AspectErrorSelectorAlreadyHookedInClassHierarchy, errorDescription);
                return NO;
            }
        } while ((currentClass = class_getSuperclass(currentClass)));

        // Add the selector as being modified.
        currentClass = klass;
        AspectTracker *subclassTracker = nil;
        do {
            tracker = swizzledClassesDict[currentClass];
            if (!tracker) {
                tracker = [[AspectTracker alloc] initWithTrackedClass:currentClass];
                swizzledClassesDict[(id<NSCopying>)currentClass] = tracker;
            }
            if (subclassTracker) {
                [tracker addSubclassTracker:subclassTracker hookingSelectorName:selectorName];
            } else {
                [tracker.selectorNames addObject:selectorName];
            }

            // All superclasses get marked as having a subclass that is modified.
            subclassTracker = tracker;
        }while ((currentClass = class_getSuperclass(currentClass)));
	} else {
		return YES;
	}

    return YES;
}
```

1. 不允许hook：retain 、 release 、 autorelease 、 forwardInvocation。
2. 允许hook dealloc ，但是只能在 dealloc 执行前，这都是为了程序的安全性设置的
3. 检查这个方法是否存在，不存在则不能hook
4. Aspects对于hook的生效作用域做了区分：所有实例对象&某个具体实例对象。对于所有实例对象在整个继承链中，同一个方法只能被hook一次，这么做的目的是为了规避循环调用的问题（详情可以了解下 supper 关键字）

### aspect_prepareClassAndHookSelector

Aspects 的核心原理是消息转发，runtime中有个方法 `_objc_msgForward`，直接调用可以触发消息转发机制。

假如要hook的方法叫 m1 ，那么把 m1 的 IMP 指向`_objc_msgForward`，这样当调用方法 m1 时就自动触发消息转发机制。

```objective-c
static void aspect_prepareClassAndHookSelector(NSObject *self, SEL selector, NSError **error) {
    NSCParameterAssert(selector);
    Class klass = aspect_hookClass(self, error);
    Method targetMethod = class_getInstanceMethod(klass, selector);
    IMP targetMethodIMP = method_getImplementation(targetMethod);
    if (!aspect_isMsgForwardIMP(targetMethodIMP)) {
        // Make a method alias for the existing method implementation, it not already copied.
        const char *typeEncoding = method_getTypeEncoding(targetMethod);
        SEL aliasSelector = aspect_aliasForSelector(selector);
        if (![klass instancesRespondToSelector:aliasSelector]) {
            __unused BOOL addedAlias = class_addMethod(klass, aliasSelector, method_getImplementation(targetMethod), typeEncoding);
            NSCAssert(addedAlias, @"Original implementation for %@ is already copied to %@ on %@", NSStringFromSelector(selector), NSStringFromSelector(aliasSelector), klass);
        }

        // We use forwardInvocation to hook in.
      	// 把函数的调用直接触发消息转发函数，转发函数已经被hook，所以在转发函数时进行hook的调用
        class_replaceMethod(klass, selector, aspect_getMsgForwardIMP(self, selector), typeEncoding);
        AspectLog(@"Aspects: Installed hook for -[%@ %@].", klass, NSStringFromSelector(selector));
    }
}
```

### aspect_hookClass

类似kvo的机制，隐式的创建一个中间类。记录一个哪个对象 哪个类 进行hook。

1. 可以做到hook只对单一对象有效
2. 避免了对原有类的侵入

这一步主要做了几个操作：

1. 如果已经存在中间类，则直接返回
2. 如果是类对象，则不用创建中间类，并把这个类存储在 swizzledClasses 集合中，标记这个类已经被hook了
3. 如果存在kvo的情况，那么系统已经帮我们创建好了中间类，那就直接使用
4. 对于不存在kvo且是实例对象的，则单独创建一个继承当前类的中间类 midcls ，并hook它的 forwardInvocation: 方法，并把当前对象的isa指针指向 midcls ，这样就做到了hook操作只针对当前对象有效，因为其他对象的isa指针指向的还是原有类。

```objective-c
/**
 1. 记录类
 2. 交换forwardInvocation
 万物皆NSObject
 */
static Class aspect_hookClass(NSObject *self, NSError **error) {
    NSCParameterAssert(self);
    //获取当前类的对象。对象 获取类对象，类对象 返回自身
    Class statedClass = self.class;
    //获取isa指针
    Class baseClass = object_getClass(self);
    NSString *className = NSStringFromClass(baseClass);
    
    // Already subclassed
    if ([className hasSuffix:AspectsSubclassSuffix]) {
        return baseClass;
        
        // We swizzle a class object, not a single object.
    }else if (class_isMetaClass(baseClass)) {
        return aspect_swizzleClassInPlace((Class)self);
        // Probably a KVO'ed class. Swizzle in place. Also swizzle meta classes in place.
    }else if (statedClass != baseClass) {
        return aspect_swizzleClassInPlace(baseClass);
    }
    
    // Default case. Create dynamic subclass.
    //动态生成一个子类
    const char *subclassName = [className stringByAppendingString:AspectsSubclassSuffix].UTF8String;
    Class subclass = objc_getClass(subclassName);
    
    if (subclass == nil) {
        //生成一个类
        subclass = objc_allocateClassPair(baseClass, subclassName, 0);
        if (subclass == nil) {
            NSString *errrorDesc = [NSString stringWithFormat:@"objc_allocateClassPair failed to allocate class %s.", subclassName];
            AspectError(AspectErrorFailedToAllocateClassPair, errrorDesc);
            return nil;
        }
        
        aspect_swizzleForwardInvocation(subclass);
        //hook class方法，把子类的class方法的IMP指向父类，这样外界并不知道内部创建了子类
        aspect_hookedGetClass(subclass, statedClass);
        aspect_hookedGetClass(object_getClass(subclass), statedClass);
        objc_registerClassPair(subclass);
    }
    //把当前对象的isa指向子类，类似kvo的用法
    object_setClass(self, subclass);
    return subclass;
}
```

### aspect_swizzleForwardInvocation

主要功能就是把当前类的 forwardInvocation: 替换成` __ASPECTS_ARE_BEING_CALLED__` ，这样当触发消息转发的时候，就会调用 ` __ASPECTS_ARE_BEING_CALLED__`  方法

```objective-c
static NSString *const AspectsForwardInvocationSelectorName = @"__aspects_forwardInvocation:";
//hook forwardInvocation方法，用来拦截消息的发送
static void aspect_swizzleForwardInvocation(Class klass) {
    NSCParameterAssert(klass);
    // If there is no method, replace will act like class_addMethod.
    IMP originalImplementation = class_replaceMethod(klass, @selector(forwardInvocation:), (IMP)__ASPECTS_ARE_BEING_CALLED__, "v@:@");
    if (originalImplementation) {
        class_addMethod(klass, NSSelectorFromString(AspectsForwardInvocationSelectorName), originalImplementation, "v@:@");
    }
    AspectLog(@"Aspects: %@ is now aspect aware.", NSStringFromClass(klass));
}
```

### `__ASPECTS_ARE_BEING_CALLED__`

` __ASPECTS_ARE_BEING_CALLED__` 方法是 Aspects 的核心操作，主要就是做消息的调用和分发，控制方法的调用的时机。

```objective-c
// This is the swizzled forwardInvocation: method.
static void __ASPECTS_ARE_BEING_CALLED__(__unsafe_unretained NSObject *self, SEL selector, NSInvocation *invocation) {
    NSCParameterAssert(self);
    NSCParameterAssert(invocation);
    SEL originalSelector = invocation.selector;
		SEL aliasSelector = aspect_aliasForSelector(invocation.selector);
    invocation.selector = aliasSelector;
    AspectsContainer *objectContainer = objc_getAssociatedObject(self, aliasSelector);
    AspectsContainer *classContainer = aspect_getContainerForClass(object_getClass(self), aliasSelector);
    AspectInfo *info = [[AspectInfo alloc] initWithInstance:self invocation:invocation];
    NSArray *aspectsToRemove = nil;

    // Before hooks.
    aspect_invoke(classContainer.beforeAspects, info);
    aspect_invoke(objectContainer.beforeAspects, info);

    // Instead hooks.
    BOOL respondsToAlias = YES;
    if (objectContainer.insteadAspects.count || classContainer.insteadAspects.count) {
        aspect_invoke(classContainer.insteadAspects, info);
        aspect_invoke(objectContainer.insteadAspects, info);
    }else {
        Class klass = object_getClass(invocation.target);
        do {
            if ((respondsToAlias = [klass instancesRespondToSelector:aliasSelector])) {
                [invocation invoke];
                break;
            }
        }while (!respondsToAlias && (klass = class_getSuperclass(klass)));
    }

    // After hooks.
    aspect_invoke(classContainer.afterAspects, info);
    aspect_invoke(objectContainer.afterAspects, info);

    // If no hooks are installed, call original implementation (usually to throw an exception)
    if (!respondsToAlias) {
        invocation.selector = originalSelector;
        SEL originalForwardInvocationSEL = NSSelectorFromString(AspectsForwardInvocationSelectorName);
        if ([self respondsToSelector:originalForwardInvocationSEL]) {
            ((void( *)(id, SEL, NSInvocation *))objc_msgSend)(self, originalForwardInvocationSEL, invocation);
        }else {
            [self doesNotRecognizeSelector:invocation.selector];
        }
    }

    // Remove any hooks that are queued for deregistration.
    [aspectsToRemove makeObjectsPerformSelector:@selector(remove)];
}
```

## 总结：

Aspects 利用消息转发机制，通过hook第三层的转发方法`forwardInvocation: `，然后根据切面的时机来动态调用block。接下来详细分析巧妙的设计

1. 类A的方法m被添加切面方法。
2. 创建类A的子类B，并hook子类B的`forwardInvocation: `方法拦截消息转发，使`forwardInvocation: `的 IMP 指向事先准备好的`ASPECTS_ARE_BEING_CALLED`函数（后面简称 ABC 函数），block方法的执行就在 ABC 函数中。
3. 把类A的对象的isa指针指向B，这样就把消息的处理转发到类B上，类似 KVO 的机制，同时会更改 class 方法的IMP，把它指向类A的 class 方法，当外界调用 class 时获取的还是类A，并不知道中间类B的存在。
4. 对于方法m，**类B会直接把方法m的 IMP 指向`_objc_msgForward`方法**，这样调用方法m时就会自动触发消息转发机制。
5. hook第三层的转发方法`forwardInvocation: `，把它的 IMP 指向` __ASPECTS_ARE_BEING_CALLED__` 方法
6. 调用方法 m1 则会直接触发 `__ASPECTS_ARE_BEING_CALLED__`方法，而 `__ASPECTS_ARE_BEING_CALLED__`方法就是处理切面block用和原有函数的调用时机，详细看下面实现步骤
   1. 根据调用的 selector ，获取容器对象 AspectsContainer ，这里面存储了这个类或对象的所有切面信息
   2. AspectInfo 会存储当前的参数信息，用于传递
   3. 首先触发函数调用前的block，存储在容器的 beforeAspects 数组中
   4. 接下来如果存在替换原有函数的block，即 insteadAspects 不为空，则触发它，如果不存在则调用原来的函数
   5. 最后触发函数调用后的block，存在在容器的 afterAspects 数组中
