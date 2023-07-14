# category

分类在运行时期才加载的。为原有类扩展方法。

## 关联对象

HashMap存储，存储关联策略 关联值。

整个内存里只有这一个哈希表。

```c++
void
_object_set_associative_reference(id object, const void *key, id value, uintptr_t policy)
{
    // This code used to work when nil was passed for object and key. Some code
    // probably relies on that to not crash. Check and handle it explicitly.
    // rdar://problem/44094390
    if (!object && !value) return;

    //类的实例不允许关联对象
    if (object->getIsa()->forbidsAssociatedObjects())
        _objc_fatal("objc_setAssociatedObject called on instance (%p) of class %s which does not allow associated objects", object, object_getClassName(object));

    //把object封装成DisguisedPtr这个类
    DisguisedPtr<objc_object> disguised{(objc_object *)object};
    ObjcAssociation association{policy, value};

    // retain the new value (if any) outside the lock.
    //关联策略的处理
    association.acquireValue();

    bool isFirstAssociation = false;
    {
        AssociationsManager manager;//加锁
        AssociationsHashMap &associations(manager.get());//获取，是全局唯一的一张表

        if (value) {
            auto refs_result = associations.try_emplace(disguised, ObjectAssociationMap{});
            if (refs_result.second) {
                /* it's the first association we make */
                isFirstAssociation = true;
            }

            /* establish or replace the association */
            auto &refs = refs_result.first->second;
            auto result = refs.try_emplace(key, std::move(association));
            if (!result.second) {
                association.swap(result.first->second);
            }
        } else {
            auto refs_it = associations.find(disguised);
            if (refs_it != associations.end()) {
                auto &refs = refs_it->second;
                auto it = refs.find(key);
                if (it != refs.end()) {
                    association.swap(it->second);
                    refs.erase(it);
                    if (refs.size() == 0) {
                        associations.erase(refs_it);

                    }
                }
            }
        }
    }

    // Call setHasAssociatedObjects outside the lock, since this
    // will call the object's _noteAssociatedObjects method if it
    // has one, and this may trigger +initialize which might do
    // arbitrary stuff, including setting more associated objects.
    if (isFirstAssociation)
        object->setHasAssociatedObjects();

    // release the old value (outside of the lock).
    association.releaseHeldValue();
}
```

```c++
class AssociationsManager {
    using Storage = ExplicitInitDenseMap<DisguisedPtr<objc_object>, ObjectAssociationMap>;
    static Storage _mapStorage;//静态变量 整个程序运行只有一份

public:
    AssociationsManager()   { AssociationsManagerLock.lock(); }
    ~AssociationsManager()  { AssociationsManagerLock.unlock(); }

    AssociationsHashMap &get() {
        return _mapStorage.get();
    }

    static void init() {
        _mapStorage.init();
    }
};
```

```c++
typedef DenseMap<DisguisedPtr<objc_object>, ObjectAssociationMap> AssociationsHashMap;
```

### set

hashmap：AssociationsHashMap

- key：DisguisedPtr（关联的实例对象）
- value：ObjectAssociationMap
  
  ```c++
  typedef DenseMap<const void *, ObjcAssociation> ObjectAssociationMap;
  ```
  
  - key
  - value：ObjcAssociation（关联策略和值）

### get

通过对象在hashmap找到关联策略和值

关联对象不需要考虑内存管理，因为底层代码会自动的放到自动释放池中。

### 案例

```swift
private var selectIndexKey: Void?
extension UIPickerView {
    var selectIndex: Int {
        set {
            objc_setAssociatedObject(self, &selectIndexKey, newValue, .OBJC_ASSOCIATION_ASSIGN)
        }
        get {
            objc_getAssociatedObject(self, &selectIndexKey) as? Int ?? 0
        }
    }
}
```

### 注

关联对象，里面存的都是对象类型，如果是基本数据类型的话，需要转成对象类型。

## 分类的意义

1. 分类在架构设计上面：解耦，开发过程中比较繁重啰嗦的业务代码对项目的可读性造成了压力，为追求架构清晰，维护成本低，通过分类梳理。（AppDelegate分类 第三方分享 推送等等拆分）
2. 可以为系统类添加分类进行拓展
3. 模拟多继承
4. 把静态库的私有方法公开

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

1. category只能给类扩充方法，不能扩充成员变量。
2. category中也可以添加属性，只不过@property只声明里实例变量，没有setter和getter方法。需要关联对象。
3. 如果分类中有和原有类同名的方法，会优先调用分类中的方法。
4. 如果多个分类中都有和原有类中同名的方法，最后一个参与编译的方法插入到方法列表前面会被调用。因为运行时在查找方法的时候是顺着方法列表的顺序查找的，它只要一找到对应名字的方法，就会罢休，殊不知后面还有一样名字的方法。

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