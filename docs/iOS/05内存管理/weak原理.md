# weak原理

## weak对象存储原理和销毁为什么会置nil

弱引用指针添加到**弱引用表**。对引用计数没有处理。因为不是同一个表，一个是引用计数表，一个是弱引用表。

`NSObject.mm`

__weak修饰的LLVM会符号绑定

通过打开汇编可以看到走的方法：

```c++
id
objc_initWeak(id *location, id newObj)//location是当前对象的地址	newObj是要weak的对象
{
    if (!newObj) {
        *location = nil;
        return nil;
    }
    //C++模版函数  第一次进来DontHaveOld是false  DoHaveNew是true
  //location weakself的指针地址	newObj绑定的对象
    return storeWeak<DontHaveOld, DoHaveNew, DoCrashIfDeallocating>
        (location, (objc_object*)newObj);
}
```

```c++
//模版参数
template <HaveOld haveOld, HaveNew haveNew,
          enum CrashIfDeallocating crashIfDeallocating>
static id 
storeWeak(id *location, objc_object *newObj)
{
    ASSERT(haveOld  ||  haveNew);
    if (!haveNew) ASSERT(newObj == nil);

    Class previouslyInitializedClass = nil;
    id oldObj;
    //SideTable用来管理引用计数和弱引用表
    SideTable *oldTable;
    SideTable *newTable;

    // Acquire locks for old and new values.
    // Order by lock address to prevent lock ordering problems. 
    // Retry if the old value changes underneath us.
 retry:
    if (haveOld) {
        oldObj = *location;
        oldTable = &SideTables()[oldObj];
    } else {
        oldTable = nil;
    }
    if (haveNew) {
        newTable = &SideTables()[newObj];
    } else {
        newTable = nil;
    }

    SideTable::lockTwo<haveOld, haveNew>(oldTable, newTable);

    if (haveOld  &&  *location != oldObj) {
        SideTable::unlockTwo<haveOld, haveNew>(oldTable, newTable);
        goto retry;
    }

    // Prevent a deadlock between the weak reference machinery
    // and the +initialize machinery by ensuring that no 
    // weakly-referenced object has an un-+initialized isa.
      //保证对象非空 并且已经初始化的
    if (haveNew  &&  newObj) {
      //通过obj的isa找到当前的类
        Class cls = newObj->getIsa();
        if (cls != previouslyInitializedClass  &&  
            !((objc_class *)cls)->isInitialized()) 
        {
            SideTable::unlockTwo<haveOld, haveNew>(oldTable, newTable);
          //散列表初始化--累的初始化 --父类+子类
            class_initialize(cls, (id)newObj);

            // If this class is finished with +initialize then we're good.
            // If this class is still running +initialize on this thread 
            // (i.e. +initialize called storeWeak on an instance of itself)
            // then we may proceed but it will appear initializing and 
            // not yet initialized to the check above.
            // Instead set previouslyInitializedClass to recognize it on retry.
            previouslyInitializedClass = cls;

            goto retry;
        }
    }

    // Clean up old value, if any.
  //弱引用对象有可能已经在散列表的weakTable里了，移除。
    if (haveOld) {
        weak_unregister_no_lock(&oldTable->weak_table, oldObj, location);
    }
//weakTable弱引用表
    // Assign new value, if any.
    if (haveNew) {
        newObj = (objc_object *)
          //注册 把弱引用对象注册到弱引用表里。
            weak_register_no_lock(&newTable->weak_table, (id)newObj, location, 
                                  crashIfDeallocating);
        // weak_register_no_lock returns nil if weak store should be rejected

        // Set is-weakly-referenced bit in refcount table.
        if (newObj  &&  !newObj->isTaggedPointer()) {
            newObj->setWeaklyReferenced_nolock();
        }

        // Do not set *location anywhere else. That would introduce a race.
        *location = (id)newObj;
    }
    else {
        // No new value. The storage is not changed.
    }
    
    SideTable::unlockTwo<haveOld, haveNew>(oldTable, newTable);

    return (id)newObj;
}
```

```c++
struct SideTable {
      //自旋锁。保证线程的读写安全
    spinlock_t slock;
    //哈希表 保存引用计数
    RefcountMap refcnts;
    //全局的弱引用表。哈希表
    weak_table_t weak_table;

    SideTable() {
        memset(&weak_table, 0, sizeof(weak_table));
    }

    ~SideTable() {
        _objc_fatal("Do not delete SideTable.");
    }

    void lock() { slock.lock(); }
    void unlock() { slock.unlock(); }
    void forceReset() { slock.forceReset(); }

    // Address-ordered lock discipline for a pair of side tables.

    template<HaveOld, HaveNew>
    static void lockTwo(SideTable *lock1, SideTable *lock2);
    template<HaveOld, HaveNew>
    static void unlockTwo(SideTable *lock1, SideTable *lock2);
};
```

弱引用的指针存储到弱引用表

通过哈希运算找到弱引用表的地址，然后把弱引用指针插入到弱引用表。

### 总结：

当前runtime维护了一张全局的弱引用表weak_table，也是哈希表，全局的弱引用表保存了所有的弱引用对象。

key：当前对象地址（因为一个对象在内存中的地址是不变的）

value：weak指针的地址，是一个数组 存储所有和相关对象的弱引用指针。weak指针的地址指向当前对象的地址。

```objective-c
    NSObject *objc = [NSObject alloc];
    //原来的散列表有 weak
    //unregist old
    //regist new
    id __weak obj = objc;
```

### 调用流程：

- objc_initWeak

  objc_initWeak调用storeWeak存储weak

- store_weak

  先在最外层找到SideTable散列表，SideTable用来管理引用计数和弱引用表，根据当前对象的指针通过哈希运算把当前对象的SideTable取出来。

  如果haveOld弱引用对象有可能已经在散列表的weakTable里了，移除。

  如果haveNew，调用weak_register_no_lock注册，把弱引用对象注册到弱引用表里。

  store_weak会找_class_initialize

  _class_initialize中调用weak_register_no_lock，weak_unregister_no_lock

  - weak_register_no_lock注册引用weak表

    注册之前判断，因为weakTable里面维护Person，Dog，Student，car很多类。为了数据不混乱就引入了entry（类似数组其实是哈希），entry里面有refreces，

    弱引用指针存储到弱引用表。通过哈希运算，放入weak_table

    weak_register_no_lock参数是：当前对象的**弱引用表**，**当前对象**，**地址指针**。

    weak_register_no_lock方法里面调用weak_entry_for_referent，把当前要弱引用的对象添加到弱引用表。

    1. weak_entry_for_referent实体引用

       weak_entry_for_referent方法里面通过哈希运算找到当前弱引用表的地址，然后插入。

       ```c++
        id 
       weak_register_no_lock(weak_table_t *weak_table, id referent_id, 
                             id *referrer_id, bool crashIfDeallocating)
       {
       
         /*
         省略代码
         */
       
           // now remember it and where it is being stored
           weak_entry_t *entry;
         //entry 加 weak 引用对象
         //散列表.weak表.entry.数组
           if ((entry = weak_entry_for_referent(weak_table, referent))) {
             //有就添加
               append_referrer(entry, referrer);
           } 
           else {
             //没有就创建
               weak_entry_t new_entry(referent, referrer);
               weak_grow_maybe(weak_table);
               weak_entry_insert(weak_table, &new_entry);
           }
       
           // Do not set *referrer. objc_storeWeak() requires that the 
           // value not change.
       
           return referent_id;
       }
       ```

       1. 有这个entry就添加

          调用append_referrer方法，将新weak弱引用的对象加入entry。
       
          ```c++
           static void append_referrer(weak_entry_t *entry, objc_object **new_referrer)
          {
             if (! entry->out_of_line()) {
                  // Try to insert inline.
                  for (size_t i = 0; i < WEAK_INLINE_COUNT; i++) {
                      if (entry->inline_referrers[i] == nil) {
                          entry->inline_referrers[i] = new_referrer;
                          return;
                      }
                  }
          
                  // Couldn't insert inline. Allocate out of line.
                  weak_referrer_t *new_referrers = (weak_referrer_t *)
                      calloc(WEAK_INLINE_COUNT, sizeof(weak_referrer_t));
                  // This constructed table is invalid, but grow_refs_and_insert
                  // will fix it and rehash it.
                  for (size_t i = 0; i < WEAK_INLINE_COUNT; i++) {
                      new_referrers[i] = entry->inline_referrers[i];
                  }
                  entry->referrers = new_referrers;
                  entry->num_refs = WEAK_INLINE_COUNT;
                  entry->out_of_line_ness = REFERRERS_OUT_OF_LINE;
                  entry->mask = WEAK_INLINE_COUNT-1;
                  entry->max_hash_displacement = 0;
              }
             
              ASSERT(entry->out_of_line());
          		//扩容
              if (entry->num_refs >= TABLE_SIZE(entry) * 3/4) {
                  return grow_refs_and_insert(entry, new_referrer);
              }
            /*
            省略代码
            */
             
            //哈希-->数组[index]
              weak_referrer_t &ref = entry->referrers[index];
              ref = new_referrer;
              entry->num_refs++;
          }
          ```
       
          
       
       2. 如果没有entry
        1. weak_entry_t如果没有就创建这个entry
          2. weak_grow_maybe改变大小，扩容
          3. weak_entry_insert 把referent引用对象添加进去

  - setWeaklyReferenced_nolock没有注册 

    store_weak中执行完weak_register_no_lock之后，又调用了setWeaklyReferenced_nolock，把当前对象的weakly_referenced置为true，表明当前对象是一个弱引用对象。

- objc_destroyWeak 释放

声明weak要不断的通过hash计算来找到地址然后取出表，来进行查找。

声明太多的weak比较耗费性能。只在解决循环引用的时候使用。

散列表--> entry--> 引用对象

#### 总结：

- SideTables：散列表，多张。sideTable里面有weak_table弱引用表。首先得到sideTable的weakTable。

- weak_table里有student，person，dog等等的弱引用，不止一种的弱引用。

- Student里面又有很多属性，subModel，一层层嵌套。

- 创建一个weak_entry_t

  访问Person从weak_table中拿，给一个实体entry。没有就创建entry，放到weak_table。

  找到散列表SideTable，从散列表中找到weak表，通过Person找到entry，

- 把referent加入到weak_table的数组inline_referrers

- 把weak_table扩容一下

- 把new_entry加入到weak_table中

- entry->referrers[index]

  把传过来的弱引用对象new_referrer添加到entry中的referrers（referrers是一个数组）。entry添加到weak_table。

weak_entry_t是一个数组。

1. 通过SideTable找到weak_table弱引用表
2. weak_table根据referent找到或者创建**weak_entry_t**
3. 然后append_referrer(entry, referrer)将新弱引用的对象加进去entry
4. 最后weak_entry_insert把entry加入到weak_table（weak_table中没有这种entry的情况，需要创建，添加到weak_table）

---

## 弱引用表释放

当类对象引用计数变为0的时候，weak修饰的引用对象会置为nil。走对象的dealloc方法。

#### dealloc

从NSObject.h的dealloc一直向下找：

NSObject.mm

```c++
- (void)dealloc {
    _objc_rootDealloc(self);
}
```

```c++
void
_objc_rootDealloc(id obj)
{
    ASSERT(obj);
    obj->rootDealloc();
}
```

#### rootDealloc()

1. 首先判断 isTaggedPointer   是否是标记指针 是直接 return ;
    注：Tagged Pointer技术，用于优化NSNumber、NSDate、NSString等小对象的存储
2. 其次判断该对象是否可以被快速释放。一共有5个判断依据：
   1. nonpointer              是否优化过isa指针（类似Tagger Pointer）
   2. weakly_reference   是否存在弱引用指向
   3. has_assoc                是否设置过关联对象
   4. has_cxx_dtor          是否有c++的析构函数（.cxx_destruct）
   5. has_sidetable_rc    引用计数器是否过大无法存储在isa中(使用 sidetable 来存储引用计数）

```c++
inline void
objc_object::rootDealloc()
{
    if (isTaggedPointer()) return;  // fixme necessary?

    if (fastpath(isa.nonpointer                     &&//优化过isa指针
                 !isa.weakly_referenced             &&//不存在弱引用指向
                 !isa.has_assoc                     &&//没设置过关联对象
#if ISA_HAS_CXX_DTOR_BIT
                 !isa.has_cxx_dtor                  &&// 没有c++的析构函数（.cxx_destruct）
#else
                 !isa.getClass(false)->hasCxxDtor() &&// 不存在引用计数器是否过大无法存储在isa中(使用 sidetable 来存储引用计数）
#endif
                 !isa.has_sidetable_rc))
    {
        assert(!sidetable_present());
        free(this);
    } 
    else {
        object_dispose((id)this);
    }
}
```

如果不能快速释放，则调用 object_dispose()方法，做下一步的处理(调用objc_destructInstance)

```c++
id 
object_dispose(id obj)
{
    if (!obj) return nil;

    objc_destructInstance(obj);    
    free(obj);

    return nil;
}
```

```c++
void *objc_destructInstance(id obj) 
{
    if (obj) {
        // Read all of the flags at once for performance.
        bool cxx = obj->hasCxxDtor();//是否存在析构函数（“清理善后” 的工作的函数）
        bool assoc = obj->hasAssociatedObjects();//是否有关联对象

        // This order is important.
        if (cxx) object_cxxDestruct(obj);//(Calls C++ destructors.)c++的销毁器来销毁成员变量
        if (assoc) _object_remove_assocations(obj, /*deallocating*/true);//(Calls ARC ivar cleanup.)用来释放动态绑定的对象
        obj->clearDeallocating();
    }

    return obj;
}
```

1. 判断是否存在c++的析构函数，有则调用object_cxxDestruct（）

   object_cxxDestruct这个方法最终会调用objc_storeStrong来释放成员变量（实例变量）

2. 移除关联对象_object_remove_assocations（常用于category中添加带变量的属性）

3. 调用clearDeallocating()方法

```c++
inline void 
objc_object::clearDeallocating()
{
    if (slowpath(!isa.nonpointer)) {
        // Slow path for raw pointer isa.
        sidetable_clearDeallocating();
    }
    else if (slowpath(isa.weakly_referenced  ||  isa.has_sidetable_rc)) {
        // Slow path for non-pointer isa with weak refs and/or side table data.
        clearDeallocating_slow();
    }

    assert(!sidetable_present());
}
```

sidetable_clearDeallocating和clearDeallocating_slow，并最终都调用：weak_clear_no_lock，该方法将所有指向所提供对象的所有弱指针置清空。

```c++
void 
objc_object::sidetable_clearDeallocating()
{
    SideTable& table = SideTables()[this];

    // clear any weak table items
    // clear extra retain count and deallocating bit
    // (fixme warn or abort if extra retain count == 0 ?)
    table.lock();
    RefcountMap::iterator it = table.refcnts.find(this);
    if (it != table.refcnts.end()) {
        if (it->second & SIDE_TABLE_WEAKLY_REFERENCED) {
            weak_clear_no_lock(&table.weak_table, (id)this);
        }
        table.refcnts.erase(it);
    }
    table.unlock();
}
```

总结：clearDeallocating一共做了两件事

1. 将对象弱引用表清空，即将弱引用该对象的指针置为nil 
2. 清空引用计数表（当一个对象的引用计数值过大（超过255）时，引用计数会存储在一个叫 SideTable 的属性中，此时isa的 has_sidetable_rc 值为1），这就是为什么弱引用不会导致循环引用的原因

#### weak_clear_no_lock

for循环拿到referrers[i]地址指针的内存空间直接置为nil，同时把entry从weak_table中移除（关于这个对象的所有弱引用的对象都会销毁）。

```c++
void 
weak_clear_no_lock(weak_table_t *weak_table, id referent_id) 
{
    objc_object *referent = (objc_object *)referent_id;

    weak_entry_t *entry = weak_entry_for_referent(weak_table, referent);
    if (entry == nil) {
        /// XXX shouldn't happen, but does with mismatched CF/objc
        //printf("XXX no entry for clear deallocating %p\n", referent);
        return;
    }

    // zero out references
    weak_referrer_t *referrers;
    size_t count;
    
    if (entry->out_of_line()) {
        referrers = entry->referrers;
        count = TABLE_SIZE(entry);
    } 
    else {
        referrers = entry->inline_referrers;
        count = WEAK_INLINE_COUNT;
    }
    
    for (size_t i = 0; i < count; ++i) {
        objc_object **referrer = referrers[i];
        if (referrer) {
            if (*referrer == referent) {
                *referrer = nil;
            }
            else if (*referrer) {
                _objc_inform("__weak variable at %p holds %p instead of %p. "
                             "This is probably incorrect use of "
                             "objc_storeWeak() and objc_loadWeak(). "
                             "Break on objc_weak_error to debug.\n", 
                             referrer, (void*)*referrer, (void*)referent);
                objc_weak_error();
            }
        }
    }
    
    weak_entry_remove(weak_table, entry);
}
```

#### 调用流程：

1. dealloc

2. _objc_rootDealloc

3. objc_object::rootDealloc()

   1. 首先判断 isTaggedPointer   是否是标记指针 是直接 return ;
       注：Tagged Pointer技术，用于优化NSNumber、NSDate、NSString等小对象的存储
   2. 其次判断该对象是否可以被快速释放。一共有5个判断依据：
      1. nonpointer              是否优化过isa指针（类似Tagger Pointer）
      2. weakly_reference   是否存在弱引用指向
      3. has_assoc                是否设置过关联对象
      4. has_cxx_dtor          是否有c++的析构函数（.cxx_destruct）
      5. has_sidetable_rc    引用计数器是否过大无法存储在isa中(使用 sidetable 来存储引用计数）
   3. 不是的话不能快速释放 则调用object_dispose()

4. object_dispose()

5. objc_destructInstance

   1. 判断是否存在c++的析构函数，有则调用object_cxxDestruct（）

      object_cxxDestruct这个方法最终会调用objc_storeStrong来释放成员变量（实例变量）

   2. 移除关联对象_object_remove_assocations（常用于category中添加带变量的属性）

   3. 调用clearDeallocating()方法

6. clearDeallocating

   1. sidetable_clearDeallocating和clearDeallocating_slow，并最终都调用：weak_clear_no_lock，该方法将所有指向所提供对象的所有弱指针置清空。

7. sidetable_clearDeallocating

8. weak_clear_no_lock

























































