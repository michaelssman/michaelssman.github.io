# category

## 特点

- category只能给某个已有的类扩充方法，不能扩充成员变量。
- category中也可以添加属性，只不过@property只声明里实例变量，没有setter和getter方法。需要关联对象。
- 如果category中的**方法**和类中原有方法同名，运行时会优先调用category中的方法。所以开发中尽量保证不要让分类中的方法和原有类中的方法名相同。避免出现这种情况的解决方案是给分类的方法名统一添加前缀。比如category_。
- 如果多个category中存在同名的方法，运行时到底调用哪个方法由编译器决定，最后一个参与编译的方法插入到方法列表前面会被调用。

## 关联对象

HashMap存储，存储关联策略 关联值。两个哈希表：多个类，多个属性。

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

- hashmap：AssociationsHashMap

  - key：DisguisedPtr（关联的实例对象）
  - value：ObjectAssociationMap
    - key
    - value：ObjcAssociation（关联策略和值）

AssociationsHashMap：DisguisedPtr和ObjectAssociationMap

```c++
typedef DenseMap<const void *, ObjcAssociation> ObjectAssociationMap;
```

### get

通过对象在hashmap找到关联策略和值

关联对象不需要考虑内存管理，因为底层代码会自动的放到自动释放池中。

## 分类的意义

1. 分类在架构设计上面：解耦，开发过程中比较繁重啰嗦的业务代码对项目的可读性造成了压力，为追求架构清晰，维护成本低，通过分类梳理。（AppDelegate分类 第三方分享 推送等等拆分）
2. 可以为系统类添加分类进行拓展
3. 模拟多继承
4. 把静态库的私有方法公开

注意事项：

1. 如果分类中有和原有类同名的方法，会优先调用分类中的方法，就是说会忽略原有类的方法
2. 如果多个分类中都有和 原有类中同名的方法，那么调用该方法的时候执行谁由编译器决定，编译器会执行最后一个参与编译的分类中的方法
3. 过度使用分类也会导致APP项目支离破碎感和性能降低

objc-runtime-new.h

## category_t

category_t没有ivars，所以没有成员变量的存储。

```c++
struct category_t {
    const char *name;//类的名称
    classref_t cls;//cls要扩展的类对象
    struct method_list_t *instanceMethods;//实例方法
    struct method_list_t *classMethods;//类方法 说明分类没有元类
    struct protocol_list_t *protocols;//协议
    struct property_list_t *instanceProperties;//实例属性
    // Fields below this point are not always present on disk.
    struct property_list_t *_classProperties;//类属性

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

#### 需要注意的有两点：

1. category的方法没有“完全替换掉”原来类已经有的方法，也就是说如果category和原来类都有methodA，那么category附加完成之后，类的方法列表里会有两个methodA。
2. category的方法被放到了新方法列表的前面，而原来类的方法被放到了新方法列表的后面，这也就是我们平常所说的category的方法会“覆盖”掉原来类的同名方法，这是因为运行时在查找方法的时候是顺着方法列表的顺序查找的，它只要一找到对应名字的方法，就会罢休，殊不知后面可能还有一样名字的方法。

### 为什么不能添加成员变量

因为成员变量在编译时期 内存布局已经确定好了，所以不能添加。

## 类扩展

匿名分类

可以添加方法、属性、成员变量

## 分类的加载

类有懒加载和非懒加载，分类也有懒加载和非懒加载。

类和分类加载：

attachCategories

1. 类和分类都是非懒加载，两个都有load方法：

   ro里面没有加载分类的数据

   1. read_images
   2. loadAllCategories()
   3. load_categories_nolock
   4. attachCategories

2. 类没有load（懒加载类）分类有load（非懒加载类）

   ro里面有分类的数据，没有rwe。

3. 类有load（非懒加载类）分类没有load（懒加载类）

   ro里面有分类的数据，没有rwe。

   没有走attachCategories

   1. read_images

4. 分类主类都没有load，都是懒加载类

   ro里面有分类的数据，没有rwe。