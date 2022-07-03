# alloc

内存的创建来自alloc。

**callAlloc走两次**

alloc会先走objc_alloc，llvm底层拦截 先标记

汇编代码把SEL是alloc的 IMP指向objc_alloc

```c++
// Calls [cls alloc].
id
objc_alloc(Class cls)
{
    return callAlloc(cls, true/*checkNil*/, false/*allocWithZone*/);
}
```

```c++
static ALWAYS_INLINE id
callAlloc(Class cls, bool checkNil, bool allocWithZone=false)
{
#if __OBJC2__
    if (slowpath(checkNil && !cls)) return nil;
    if (fastpath(!cls->ISA()->hasCustomAWZ())) {
      //第二次会走_objc_rootAllocWithZone
        return _objc_rootAllocWithZone(cls, nil);
    }
#endif

    // No shortcuts available.
    if (allocWithZone) {
        return ((id(*)(id, SEL, struct _NSZone *))objc_msgSend)(cls, @selector(allocWithZone:), nil);
    }
  //第一次先走下面的objc_msgSend调用alloc
    return ((id(*)(id, SEL))objc_msgSend)(cls, @selector(alloc));
}
```

然后再`((id(*)(id, SEL))objc_msgSend)(cls, @selector(alloc))`走alloc

```c++
+ (id)alloc {
    return _objc_rootAlloc(self);
}
```

```c++
id
_objc_rootAlloc(Class cls)
{
    return callAlloc(cls, false/*checkNil*/, true/*allocWithZone*/);
}
```

```c++
static ALWAYS_INLINE id
callAlloc(Class cls, bool checkNil, bool allocWithZone=false)
{
#if __OBJC2__
    if (slowpath(checkNil && !cls)) return nil;
    if (fastpath(!cls->ISA()->hasCustomAWZ())) {
      //第二次会走_objc_rootAllocWithZone
        return _objc_rootAllocWithZone(cls, nil);
    }
#endif

    // No shortcuts available.
    if (allocWithZone) {
        return ((id(*)(id, SEL, struct _NSZone *))objc_msgSend)(cls, @selector(allocWithZone:), nil);
    }
  //第一次先走下面的objc_msgSend调用alloc
    return ((id(*)(id, SEL))objc_msgSend)(cls, @selector(alloc));
}
```

```c++
NEVER_INLINE
id
_objc_rootAllocWithZone(Class cls, malloc_zone_t *zone __unused)
{
    // allocWithZone under __OBJC2__ ignores the zone parameter
    return _class_createInstanceFromZone(cls, 0, nil,
                                         OBJECT_CONSTRUCT_CALL_BADALLOC);
}
```

上面的每一个都下一个符号断点。然后就可以知道走到哪一个步。

注：有其它的，需要先来到Person的alloc，然后再进入符号断点。

_class_createInstancesFromZone方法里面：

1. 计算需要分配内存大小，不同的class成员变量多少不同，需要的内存大小不同。
2. 开辟内存空间。
3. 创建初始化isa指针，把类和当前的指针地址关联，申请的内存和class绑定在一起。

```c++
static ALWAYS_INLINE id
_class_createInstanceFromZone(Class cls, size_t extraBytes, void *zone,
                              int construct_flags = OBJECT_CONSTRUCT_NONE,
                              bool cxxConstruct = true,
                              size_t *outAllocatedSize = nil)
{
    ASSERT(cls->isRealized());

    // Read class's info bits all at once for performance
    bool hasCxxCtor = cxxConstruct && cls->hasCxxCtor();
    bool hasCxxDtor = cls->hasCxxDtor();
    bool fast = cls->canAllocNonpointer();
    size_t size;
    //1. 要开辟多少内存，计算实例对象分配多大内存空间
    size = cls->instanceSize(extraBytes);
    if (outAllocatedSize) *outAllocatedSize = size;

    id obj;
    if (zone) {
        obj = (id)malloc_zone_calloc((malloc_zone_t *)zone, 1, size);
    } else {
        //2. 怎么申请内存 对obj赋新值。最终开辟内存大小，16字节对齐
        obj = (id)calloc(1, size);
    }
    if (slowpath(!obj)) {
        if (construct_flags & OBJECT_CONSTRUCT_CALL_BADALLOC) {
            return _objc_callBadAllocHandler(cls);
        }
        return nil;
    }
    //3. 把类和当前的指针地址关联 申请的内存和class绑定在一起
    if (!zone && fast) {
        obj->initInstanceIsa(cls, hasCxxDtor);
    } else {
        // Use raw pointer isa on the assumption that they might be
        // doing something weird with the zone or RR.
        obj->initIsa(cls);
    }

    if (fastpath(!hasCxxCtor)) {
        return obj;
    }

    construct_flags |= OBJECT_CONSTRUCT_FREE_ONFAILURE;
    return object_cxxConstructFromClass(obj, cls, construct_flags);
}
```

```c++
inline void 
objc_object::initIsa(Class cls, bool nonpointer, UNUSED_WITHOUT_INDEXED_ISA_AND_DTOR_BIT bool hasCxxDtor)
{ 
    ASSERT(!isTaggedPointer()); 
    
    isa_t newisa(0);

    if (!nonpointer) {
        newisa.setClass(cls, this);
    } else {
        ASSERT(!DisableNonpointerIsa);
        ASSERT(!cls->instancesRequireRawIsa());


#if SUPPORT_INDEXED_ISA
        ASSERT(cls->classArrayIndex() > 0);
        newisa.bits = ISA_INDEX_MAGIC_VALUE;
        // isa.magic is part of ISA_MAGIC_VALUE
        // isa.nonpointer is part of ISA_MAGIC_VALUE
        newisa.has_cxx_dtor = hasCxxDtor;
        newisa.indexcls = (uintptr_t)cls->classArrayIndex();
#else
        newisa.bits = ISA_MAGIC_VALUE;
        // isa.magic is part of ISA_MAGIC_VALUE
        // isa.nonpointer is part of ISA_MAGIC_VALUE
#   if ISA_HAS_CXX_DTOR_BIT
        newisa.has_cxx_dtor = hasCxxDtor;
#   endif
        newisa.setClass(cls, this);
#endif
        newisa.extra_rc = 1;//通过alloc 引用计数为1
    }

    // This write must be performed in a single store in some cases
    // (for example when realizing a class because other threads
    // may simultaneously try to use the class).
    // fixme use atomics here to guarantee single-store and to
    // guarantee memory order w.r.t. the class index table
    // ...but not too atomic because we don't want to hurt instantiation
    isa = newisa;
}
```

calloc只是申请一个内存，是一个指针，和person对象没有关系

`initInstanceIsa`把类和当前的指针地址关联

## alloc⽅法的底层调⽤流程

1. alloc
2. objc_alloc
3. callAlloc
4. objc_msgSend 
5. alloc 
6. _objc_rootAlloc
7. callAlloc 
8. _objc_rootAllocWithZone 
9. _class_createInstanceFromZone
   1. cls->instanceSize()	//计算对象需要的内存的⼤⼩。
   2. calloc()    //系统实际为对象分配内存的⼤⼩。

# 内存对齐

栈内存 连续的

创建的对象最小内存大小是16字节。

一个对象8字节，isa也是8字节，NSObject是8个字节，指针8字节。

为什么8为倍数， 而不是16或32：没有任何成员变量只有一个isa，则是8。

计算机读---存

person中不同类型的成员变量占内存大小是不一样的，不断变化，CPU读取计算压力大。所以所有的成员变量都设置8字节。已8字节去读取，速度会变快（空间换时间）。

整个内存中8字节的最多，所以是8倍数。

8字节对齐

```c++
int func (int x) {
//    return (x + 7) / 8 * 8;
    return (x + 7) >> 3 << 3;//左移3 右移3
}
```

堆 对象的内存 以16字节对齐

成员变量 8字节对齐 结构体内部

对象和对象之间是16字节对齐

对象16字节对齐 内存访问 野指针错误减少

**对象内部是8字节对齐，对象是16字节对齐。**空间换时间，因为对象isa是8字节。

### 为什么要字节对⻬

字节是内存的容量单位。但是，CPU在读取内存的时候，却不是以字节为单位来读取的，⽽是以“块”为单位读取的，所以⼤家也经常听到⼀块内存，“块”的⼤⼩也就是内存存取的⼒度。如果不对⻬的话，在我们频繁的存取内存的时候，CPU就需要花费⼤量的精⼒去分辨你要读取多少字节，这就会造成CPU的效率低下，如果想要CPU能够⾼效读取数据，那就需要找⼀个规范，这个规范就是字节对⻬。

为什么对象内部的成员变量是以8字节对⻬，系统实际分配的内存以16字节对⻬？

以空间换时间。苹果采取16字节对⻬，是因为OC的对象中，第⼀位叫isa指针，它是必然存在的，⽽且它就占了8位字节，就算对象中没有其他的属性了，也⼀定有⼀个isa，那对象就⾄少要占⽤8位字节。如果以8位字节对⻬的话，如果连续的两块内存都是没有属性的对象，那么它们的内存空间就会完全的挨在⼀起，是容易混乱的。以16字节为⼀块，这就保证了CPU在读取的时候，按照块读取就可以，效率更⾼，同时还不容易混乱。

# alloc init new区别

```c++
+ (id)init {
    return (id)self;
}

- (id)init {
    return _objc_rootInit(self);
}
```

alloc：开辟内存 有了指针地址

init：返回self 构造方法（工厂设计模式） 构造方法入口 便于扩展

```c++
+ (id)new {
    return [callAlloc(self, false/*checkNil*/) init];
}
```

new：等同于 alloc+init

## 对象开辟内存的影响因素

NSObject中有一个isa成员变量

字节对齐：alloc产生的对象16字节对齐， 不容易出错， 速度快

影响因素：成员变量。和其它的（协议，方法）没有关系。

2个成员变量 8(isa)+8+8=24 字节对齐32



