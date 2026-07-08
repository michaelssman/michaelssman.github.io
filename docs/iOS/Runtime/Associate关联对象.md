# Associate 关联对象

关联对象用于在运行时给对象绑定额外数据，常见场景是在分类中模拟属性。

## 底层存储

关联对象使用全局哈希表存储关联关系。整个进程里只有一张全局关联对象表。

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

## objc_setAssociatedObject

`objc_setAssociatedObject` 会把关联关系写入 `AssociationsHashMap`。

- key：`DisguisedPtr`，表示被关联的实例对象。
- value：`ObjectAssociationMap`，表示该对象上的所有关联键值。

```c++
typedef DenseMap<const void *, ObjcAssociation> ObjectAssociationMap;
```

`ObjectAssociationMap` 内部：

- key：关联对象时传入的 key 指针。
- value：`ObjcAssociation`，保存关联策略和值。

## objc_getAssociatedObject

`objc_getAssociatedObject` 会通过对象在全局哈希表中找到关联策略和值。

关联对象不需要额外手动管理内存，因为底层会根据关联策略处理持有和释放。

## 使用案例

```swift
private var selectIndexKey: Void? // 使用 & 操作符获取变量的指针地址作为关联键

extension UIPickerView {
    var selectIndex: Int? {
        set {
            // 设置关联对象
            // 参数说明：
            // 1. 目标对象
            // 2. 关联键的指针
            // 3. 新关联值
            // 4. 关联策略（是否强引用 + 是否原子性）
            objc_setAssociatedObject(self, &selectIndexKey, newValue, .OBJC_ASSOCIATION_ASSIGN)
        }
        get {
            // 获取关联对象
            // 参数说明：
            // 1. 目标对象
            // 2. 关联键的指针
            objc_getAssociatedObject(self, &selectIndexKey) as? Int
        }
    }
}
```

## 与 Category 的关系

Category 原则上不能直接添加成员变量。通过关联对象，可以在分类中为已有类补充“类似属性”的能力。
