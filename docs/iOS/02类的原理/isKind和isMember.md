## isKindOfClass

类方法：

isa

元类  元类的父类

```c++
+ (BOOL)isKindOfClass:(Class)cls {
    for (Class tcls = self->ISA(); tcls; tcls = tcls->getSuperclass()) {
        if (tcls == cls) return YES;
    }
    return NO;
}
```

对象方法：

```c++
- (BOOL)isKindOfClass:(Class)cls {
    for (Class tcls = [self class]; tcls; tcls = tcls->getSuperclass()) {
        if (tcls == cls) return YES;
    }
    return NO;
}
```

## isMemberOfClass

类方法：元类和类比较 是否一样

```c++
+ (BOOL)isMemberOfClass:(Class)cls {
    return self->ISA() == cls;
}	
```

对象方法：

```c++
- (BOOL)isMemberOfClass:(Class)cls {
    return [self class] == cls;
}
```



注：

打开汇编看走向。并不是上面的方法。