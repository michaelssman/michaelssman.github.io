# alloc

内存的创建来自alloc。

**callAlloc走两次**

### alloc

llvm底层拦截 先标记。汇编代码把SEL是alloc的 IMP指向objc_alloc

### objc_alloc

```c++
// Calls [cls alloc].
id
objc_alloc(Class cls)
{
    return callAlloc(cls, true/*checkNil*/, false/*allocWithZone*/);
}
```

### callAlloc

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

### alloc

```c++
+ (id)alloc {
    return _objc_rootAlloc(self);
}
```

### _objc_rootAlloc

```c++
id
_objc_rootAlloc(Class cls)
{
    return callAlloc(cls, false/*checkNil*/, true/*allocWithZone*/);
}
```

### callAlloc

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

### _objc_rootAllocWithZone

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

### _class_createInstanceFromZone

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

### objc_object::initIsa

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

## alloc init new区别

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

影响因素：**成员变量**。和其它的（协议，方法）没有关系。

2个成员变量 8(isa)+8+8=24，然后16字节对齐，结果为32。



