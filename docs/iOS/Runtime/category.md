# category

分类在运行时期才加载。为原有类扩展方法。

## 分类的意义

- 解耦（AppDelegate分类、分享、推送等拆分）
- 为系统类进行拓展
- 模拟多继承
- 把静态库的私有方法公开

## category_t

objc-runtime-new.h

```c++
struct category_t {
    const char *name;//类的名称
    classref_t cls;//cls要扩展的类对象
    struct method_list_t *instanceMethods;//实例方法列表
    struct method_list_t *classMethods;//类方法列表 说明分类没有元类
    struct protocol_list_t *protocols;//协议列表
    struct property_list_t *instanceProperties;//实例属性列表
    // Fields below this point are not always present on disk.
    struct property_list_t *_classProperties;//类属性列表

    method_list_t *methodsForMeta(bool isMeta) {
        if (isMeta) return classMethods;
        else return instanceMethods;
    }

    property_list_t *propertiesForMeta(bool isMeta, struct header_info *hi);
    
    protocol_list_t *protocolsForMeta(bool isMeta) {
        if (isMeta) return nullptr;
        else return protocols;
    }
};
```

### 注意事项：

- category只能扩充方法，不能扩充成员变量。
- category中也可以添加属性，只不过@property只声明里实例变量，没有setter和getter方法。需要关联对象。
- 如果分类中有和原有类同名的方法，调用分类中的方法。
- 如果多个分类中都有和原有类中同名的方法，最后一个参与编译的方法插入到方法列表前面会被调用。因为运行时在查找方法的时候是顺着方法列表的顺序查找的，它只要一找到对应名字的方法，就会罢休，殊不知后面还有一样名字的方法。

## 如何调用原类方法

- `CSPerson`类和`CSPerson (Extension)`类

```objective-c
@interface CSPerson : NSObject {
- (void)run;
@end

@implementation CSPerson
- (void)run {
    NSLog(@"%s",__FUNCTION__);
}
@end

#pragma mark - CSPerson (Extension)

@interface CSPerson (Extension)
- (void)run;
@end

@implementation CSPerson (Extension)
- (void)run {
    NSLog(@"%s",__FUNCTION__);
}
@end
```

- 使用 `runtime`调用

```objective-c
- (void)callClassMethod {
    u_int count;
    Method *methods = class_copyMethodList([Student class], &count);
    NSInteger index = 0;
    
    for (int i = 0; i < count; i++) {
        SEL name = method_getName(methods[i]);
        NSString *strName = [NSString stringWithCString:sel_getName(name) encoding:NSUTF8StringEncoding];

        if ([strName isEqualToString:@"run"]) {
            index = i;  // 先获取原类方法在方法列表中的索引
        }
    }
    
    // 调用方法
    Student *stu = [[Student alloc] init];
    SEL sel = method_getName(methods[index]);
    IMP imp = method_getImplementation(methods[index]);
    ((void (*)(id, SEL))imp)(stu,sel);
}
```

运行结果

```
2019-06-26 09:39:20.744704+0800 CallClassMethodNoCategory[51029:14270433] -[Student run]
```

### 总结

通过遍历类`Student`的方法列表，获取`run`方法在方法列表`methods`的索引，然后调用即可。

## 为什么不能添加成员变量

1. 成员变量在编译时期 内存布局已经确定好了，所以不能添加。
2. 分类的数据结构category_t⾥⾯没有成员列表ivars的存储。

## 分类和类扩展的区别

- 分类原则上只能增加⽅法（可以通过rutime关联对象实现添加属性）。
- 类扩展不仅可以增加⽅法，还可以增加实例变量（或者属性）。
- 类扩展在编译阶段被添加到类中，分类在运⾏时添加到类中。
- 类扩展不能像分类那样拥有独⽴的实现部分（@implementation部分），也就是说，类扩展所声明的⽅法必须依托对应类的实现部分来实现。
- 定义在 .m ⽂件中的类扩展⽅法为私有的，定义在 .h ⽂件（头⽂件）中的类扩展⽅法为公有的。类扩展是在 .m ⽂件中声明私有⽅法的⾮常好的⽅式。

## 分类的加载

类有懒加载和非懒加载，分类也有懒加载和非懒加载。

### 1、类和分类都是非懒加载，两个都有load方法：

**编译时**ro⾥⾯只有类的数据没有分类的数据，分类的数据在**运⾏时**被加载到rwe⾥⾯。

1. read_images
2. loadAllCategories()
3. load_categories_nolock
4. attachCategories

### 2、类没有load（懒加载类）分类有load（非懒加载类）

**编译时**类和分类的数据都被加载ro⾥⾯了。没有rwe。

### 3、类有load（非懒加载类）分类没有load（懒加载类）

**编译时**类和分类的数据都被加载ro⾥⾯了。没有rwe。

### 4、分类主类都没有load，都是懒加载类

**在类第⼀次接收到消息时加载数据**，类和分类的数据都被加载在ro⾥⾯。没有rwe。
