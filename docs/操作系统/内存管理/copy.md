# copy

- copy的结果都是不可变，mutableCopy的结果都是可变
- 只有不可变的copy是浅拷贝（指针拷贝，对象内存地址相同），其它的都是深拷贝（内容拷贝，对象内存地址不一样）。

两个数组  一个数组里面的元素是另外一个数组里面的元素。改变其中一个数组中的元素另一个数组也会改变。

需要对元素 实现copy协议。

array1 = [[NSMutableArray alloc]initWithArray:array0 copyItems:**YES**];

数组里面是模型的，模型是不拷贝的！

元素遵循<NSCopying>协议

实现`- (id)copyWithZone:(NSZone *)zone`方法。

## 深浅拷贝

### 浅拷贝

使用一个已知实例对新创建实例的成员变量逐个赋值，浅拷贝的对象跟原对象存在公共的引用指向对象。实例对象的属性指向的同一块儿内存地址。

### 深拷贝

当一个类的拷贝构造方法，不仅要复制对象的所有非引用成员变量值，还要**为引用类型的成员变量创建新的实例**，并且初始化为形式参数实例值。值拷贝 新的地址空间，指向的内存地址不是同一个。

通过对象的**序列化跟反序列化**，实现一个对象的**深拷贝**。

## 对于Model

model.copy浅拷贝

model.mutableCopy需要实现copy协议，model里面的子model也会拷贝。属于深拷贝。

## swift

A页面进入B页面，B页面的属性值由A页面传进来，要想B页面的属性修改，不影响A页面。需要拷贝。

```swift
prodPrices = prodPrices.map({$0.mutableCopy() as! SCMPriceModel})
```

要遵循`<NSCopying,NSMutableCopying>`协议，实现方法：
```objective-c
- (id)copyWithZone:(NSZone *)zone {}
- (id)mutableCopyWithZone:(NSZone *)zone {}
```
