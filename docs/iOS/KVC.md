# KVC
NSKeyValueCoding

先找方法，再找成员变量。

属性本质：setter、getter、成员变量三部分。

## set

1. setKey
2. _setKey
3. setIsKey
4. accessInstanceVariablesDirectly是否可以直接给成员变量赋值
5. _key
6. _isKey
7. key
8. isKey
9. Exception程序崩溃

```objective-c
- (void)setValue:(id)value forUndefinedKey:(NSString *)key
{
}
```

## get

valueForKey调用顺序

1. 先调用相关方法 先后顺序是：getKey -> key -> isKey->_key 

  如果实现了`countOfKey`，`objectInKeyAtIndex`这两个方法，key变成了NSKeyValueArray是NSArray子类，返回一个数组。

2. 如果没有相关方法 就看accessInstanceVariablesDirectly 是否可以直接取**实例变量** 方法的返回值
   1. 返回NO 异常crash，报reason:  valueForUndefinedKey:
   2. 返回YES就找成员变量，先后顺序是：_key -> _isKey -> key -> isKey，如果这四个成员变量都没有，则crash，报reason:  valueForUndefinedKey:

```objective-c
- (id)valueForUndefinedKey:(NSString *)key
{
    return nil;
}
```

## KeyPath

```objective-c
//嵌套拿数据     里面是点语法 一直点下去 点分离key
id age = [p valueForKeyPath:@"dog.age"];//dog是p的属性
NSLog(@"狗的年龄是:%@",age);
```

