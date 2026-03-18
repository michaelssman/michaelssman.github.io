# weak原理

## weak 对象存储原理和销毁为什么会置 nil

weak 在底层维护了一张全局的**weak_table_t弱引用表（哈希表）**，保存了所有的弱引用对象。

- **key**：对象的内存地址（对象在内存中的地址是固定不变的，适合作为 key）。
- **value**：weak 指针的地址数组，存储所有指向该对象的弱引用指针。weak 指针的地址指向当前对象的地址。

弱引用表和引用计数表是两张独立的表。**weak 所引用对象的引用计数不会加 1**。

---

## 原理探索

源码文件：`NSObject.mm`

`__weak` 修饰的变量在 LLVM 编译阶段会进行符号绑定。

打开汇编可以看到底层实际调用的方法为：

```c++
// objc_initWeak：weak 变量初始化入口函数
// 参数：
//   location  —— __weak 变量自身的指针地址（即 weak 指针存放的内存地址）
//   newObj    —— 要被 weak 引用的对象
id
objc_initWeak(id *location, id newObj)
{
    // 如果被引用对象为 nil，直接将 weak 指针置为 nil 并返回
    if (!newObj) {
        *location = nil;
        return nil;
    }

    // 调用 C++ 模板函数 storeWeak 执行实际的存储逻辑
    // DontHaveOld：第一次初始化，不存在旧值
    // DoHaveNew：存在新值需要注册
    // DoCrashIfDeallocating：若对象正在析构则 crash
    return storeWeak<DontHaveOld, DoHaveNew, DoCrashIfDeallocating>
        (location, (objc_object*)newObj);
}

// storeWeak：weak 引用的核心存储函数（C++ 模板函数）
// 模板参数：
//   haveOld              —— 是否存在旧的 weak 引用（需要先注销）
//   haveNew              —— 是否存在新的 weak 引用（需要注册）
//   crashIfDeallocating  —— 若对象正在析构是否触发 crash
template <HaveOld haveOld, HaveNew haveNew,
          enum CrashIfDeallocating crashIfDeallocating>
static id 
storeWeak(id *location, objc_object *newObj)
{
    ASSERT(haveOld  ||  haveNew);
    if (!haveNew) ASSERT(newObj == nil);

    Class previouslyInitializedClass = nil;
    id oldObj;

    // SideTable 用来同时管理引用计数表和弱引用表
    SideTable *oldTable;  // 旧对象对应的 SideTable
    SideTable *newTable;  // 新对象对应的 SideTable

    // 为防止锁的顺序问题导致死锁，按锁地址顺序加锁
    // 若 location 指向的旧值在加锁期间发生变化，则重试（goto retry）
 retry:
    if (haveOld) {
        // 读取 weak 指针当前指向的旧对象
        oldObj = *location;
        // 根据旧对象地址，从全局 SideTables 哈希表中取出对应的 SideTable
        oldTable = &SideTables()[oldObj];
    } else {
        oldTable = nil;
    }
    if (haveNew) {
        // 根据新对象地址，从全局 SideTables 哈希表中取出对应的 SideTable
        newTable = &SideTables()[newObj];
    } else {
        newTable = nil;
    }

    // 同时锁住旧表和新表，保证线程安全
    SideTable::lockTwo<haveOld, haveNew>(oldTable, newTable);

    // 如果加锁期间 location 指向的值已经变化，说明有并发修改，解锁后重试
    if (haveOld  &&  *location != oldObj) {
        SideTable::unlockTwo<haveOld, haveNew>(oldTable, newTable);
        goto retry;
    }

    // 防止 weak 引用机制与 +initialize 机制之间产生死锁：
    // 确保被弱引用的对象的类已经完成了 +initialize 初始化（isa 不能是未初始化状态）
    if (haveNew && newObj) {
        // 通过对象的 isa 指针找到当前类
        Class cls = newObj->getIsa();
        if (cls != previouslyInitializedClass  &&  
            !((objc_class *)cls)->isInitialized()) 
        {
            // 类尚未初始化，先解锁
            SideTable::unlockTwo<haveOld, haveNew>(oldTable, newTable);
            // 触发类的初始化（会递归初始化父类 → 子类）
            class_initialize(cls, (id)newObj);

            // 如果该类的 +initialize 已经完成，则可以继续
            // 如果 +initialize 仍在当前线程上运行（即 +initialize 中对自身实例调用了 storeWeak）
            // 则标记 previouslyInitializedClass，在下次 retry 中跳过重复初始化
            previouslyInitializedClass = cls;

            goto retry;
        }
    }

    // ---- 处理旧值 ----
    // 如果存在旧的弱引用，将其从 SideTable 的 weak_table 中注销
    if (haveOld) {
        weak_unregister_no_lock(&oldTable->weak_table, oldObj, location);
    }

    // ---- 处理新值 ----
    // 如果存在新的弱引用，将其注册到 SideTable 的 weak_table（弱引用表）中
    if (haveNew) {
        newObj = (objc_object *)
            // weak_register_no_lock：将弱引用指针注册到 weak_table
            weak_register_no_lock(&newTable->weak_table, (id)newObj, location, 
                                  crashIfDeallocating);
        // weak_register_no_lock 若注册失败（对象不可被弱引用）则返回 nil

        // 在引用计数表中设置"已被弱引用"标志位
        // TaggedPointer 对象不使用 SideTable，无需处理
        if (newObj && !newObj->isTaggedPointer()) {
            newObj->setWeaklyReferenced_nolock();
        }

        // 将 weak 指针指向新对象（只在这里赋值，避免竞态条件）
        *location = (id)newObj;
    }
    else {
        // 没有新值，存储内容不变
    }
    
    // 解锁旧表和新表
    SideTable::unlockTwo<haveOld, haveNew>(oldTable, newTable);

    return (id)newObj;
}
```

通过哈希运算找到弱引用表的地址，然后把弱引用指针插入到弱引用表。

---

## 调用流程

### 1. objc_initWeak

`objc_initWeak` 调用 `storeWeak`（存储 weak 引用）。

### 2. storeWeak

1. **根据当前对象的指针通过哈希运算取出最外层的 SideTable 散列表。**SideTable 用来管理引用计数和弱引用表。
2. 确保类已完成 `class_initialize` 初始化。
3. 若 `haveOld` 为 true，说明 weak 指针之前已指向某个对象，先将其从旧 SideTable 的 `weak_table` 中移除（调用 `weak_unregister_no_lock`）。
4. 若 `haveNew` 为 true，调用 `weak_register_no_lock` 将弱引用注册到新对象对应的弱引用表。

### 3. weak_register_no_lock —— 注册到 weak 引用表

因为 `weak_table` 里维护着 Person、Dog、Student、Car 等多种类的弱引用，为了避免数据混乱，引入了 `weak_entry_t`（哈希结构）。`weak_entry_t` 内部有 `referrers` 数组，用于存储指向同一个对象的所有 weak 指针地址。

`weak_register_no_lock` 的参数：当前对象的**弱引用表（weak_table）**、**当前被弱引用的对象**、**weak 指针地址**。

该方法内部调用 `weak_entry_for_referent`，将当前要弱引用的对象添加到弱引用表。

### 4. weak_entry_for_referent —— 查找实体引用

`weak_entry_for_referent` 通过哈希运算在弱引用表中找到当前对象对应的 `weak_entry_t` 地址，然后将 weak 指针插入其中。

```c++
// weak_register_no_lock：将弱引用指针注册到弱引用表
// 参数：
//   weak_table    —— 当前对象所在 SideTable 的弱引用表
//   referent_id   —— 被弱引用的对象
//   referrer_id   —— weak 指针自身的地址（即 __weak 变量的地址）
//   crashIfDeallocating —— 若对象正在析构是否 crash
id 
weak_register_no_lock(weak_table_t *weak_table, id referent_id, 
                      id *referrer_id, bool crashIfDeallocating)
{
    /*
    省略：检查对象是否正在析构、是否支持弱引用等前置校验代码
    */

    // 尝试在 weak_table 中查找被弱引用对象对应的 weak_entry_t
    // 层次结构：散列表(SideTable) → weak_table → weak_entry_t → 引用数组
    weak_entry_t *entry;
    if ((entry = weak_entry_for_referent(weak_table, referent))) {
        // 已存在对应的 entry，直接将新 weak 指针追加进去
        append_referrer(entry, referrer);
    } 
    else {
        // 不存在对应的 entry，创建新的 weak_entry_t
        weak_entry_t new_entry(referent, referrer);
        // 检查 weak_table 容量，必要时扩容
        weak_grow_maybe(weak_table);
        // 将新 entry 插入到 weak_table
        weak_entry_insert(weak_table, &new_entry);
    }

    // 注意：不能在此处修改 *referrer，objc_storeWeak() 要求值不变
    return referent_id;
}
```

### 5. 已存在 entry 时 —— append_referrer

调用 `append_referrer` 方法，将新的 weak 引用指针加入已有的 `weak_entry_t`。

```c++
// append_referrer：向 weak_entry_t 中追加一个新的 weak 引用指针
// 参数：
//   entry        —— 目标 weak_entry_t
//   new_referrer —— 新的 weak 指针地址（即 __weak 变量的地址）
static void append_referrer(weak_entry_t *entry, objc_object **new_referrer)
{
    if (!entry->out_of_line()) {
        // 当前 entry 处于内联存储模式（最多存 WEAK_INLINE_COUNT 个，通常为 4）
        // 尝试插入到内联数组 inline_referrers 中的空槽
        for (size_t i = 0; i < WEAK_INLINE_COUNT; i++) {
            if (entry->inline_referrers[i] == nil) {
                entry->inline_referrers[i] = new_referrer;
                return;
            }
        }

        // 内联数组已满，需要迁移到堆上的动态数组（out-of-line 模式）
        weak_referrer_t *new_referrers = (weak_referrer_t *)
            calloc(WEAK_INLINE_COUNT, sizeof(weak_referrer_t));
        // 将内联数组中的已有数据复制到新的堆上数组
        // （此时 table 结构尚不合法，grow_refs_and_insert 会修复并重新哈希）
        for (size_t i = 0; i < WEAK_INLINE_COUNT; i++) {
            new_referrers[i] = entry->inline_referrers[i];
        }
        // 更新 entry 为 out-of-line 模式
        entry->referrers = new_referrers;
        entry->num_refs = WEAK_INLINE_COUNT;
        entry->out_of_line_ness = REFERRERS_OUT_OF_LINE;
        entry->mask = WEAK_INLINE_COUNT - 1;
        entry->max_hash_displacement = 0;
    }
   
    // 断言：此时 entry 一定处于 out-of-line 模式
    ASSERT(entry->out_of_line());

    // 若当前引用数量超过容量的 3/4，先扩容再插入（grow_refs_and_insert 会同时完成扩容和插入）
    if (entry->num_refs >= TABLE_SIZE(entry) * 3/4) {
        return grow_refs_and_insert(entry, new_referrer);
    }

    /*
    省略：通过哈希运算计算 index，处理哈希冲突（线性探测）的代码
    */

    // 将新的 weak 指针写入哈希数组对应位置
    // entry->referrers 是一个哈希数组，index 由哈希运算得出
    weak_referrer_t &ref = entry->referrers[index];
    ref = new_referrer;
    entry->num_refs++;  // 引用计数加 1
}
```

### 6. setWeaklyReferenced_nolock

`storeWeak` 中执行完 `weak_register_no_lock` 之后，还会调用 `setWeaklyReferenced_nolock`，将当前对象 isa 中的标志位`weakly_referenced`置为 `true`，表明该对象存在弱引用，在`dealloc`时需要处理弱引用表。

---

## 添加弱引用流程总结

1. 若被弱引用的对象为 **nil** 或是 **TaggedPointer**，直接返回，不做任何操作。
2. 若被弱引用对象**正在析构**，则抛出异常（或直接返回 nil，取决于 `crashIfDeallocating` 参数）。
3. 若被弱引用对象**不支持 weak 引用**，直接返回 nil。
4. 若对象正常且可被 weak 引用，调用 `weak_entry_for_referent` 根据**被弱引用对象的地址**从弱引用表中查找对应的 `weak_entry_t`：
   - **找到**：调用 `append_referrer` 将 weak 指针地址追加进去。
   - **未找到**：创建新的 `weak_entry_t`，放入 `weak_table`：
     
     ```c++
     weak_entry_t new_entry(referent, referrer);   // 创建新 entry
     weak_grow_maybe(weak_table);                  // 必要时对 weak_table 扩容
     weak_entry_insert(weak_table, &new_entry);    // 将 new_entry 插入 weak_table
     ```

**数据层次结构：**

```
SideTables（全局多张散列表）
  └── SideTable（每张表管理一组对象）
        ├── refcnts（引用计数表）
        └── weak_table（弱引用表）
              └── weak_entry_t（每个对象对应一个 entry）
                    └── referrers / inline_referrers（该对象的所有 weak 指针地址数组）
                          └── entry->referrers[index]（具体的 weak 指针地址）
```

> ⚠️ **性能提示**：声明 weak 变量需要不断通过哈希运算定位地址、查找表结构，开销较大。应仅在解决**循环引用**时使用 weak，避免滥用。

---

## 弱引用表释放

当对象的引用计数为 0 时，其所有 weak 指针将被自动置为 nil。整个过程从对象的 dealloc 方法开始。

### 1. dealloc

入口在 `NSObject.mm`：

```c++
// NSObject 的 dealloc 方法，对象引用计数为 0 时由 ARC 自动调用
- (void)dealloc {
    _objc_rootDealloc(self);
}
```

### 2. _objc_rootDealloc

```c++
// _objc_rootDealloc：dealloc 的 C 层实现入口
void
_objc_rootDealloc(id obj)
{
    ASSERT(obj);
    obj->rootDealloc();  // 调用对象的 rootDealloc 方法
}
```

### 3. rootDealloc()

```c++
// rootDealloc：尝试快速释放对象，不满足条件则走完整销毁流程
inline void
objc_object::rootDealloc()
{
    // 1. 判断是否是 TaggedPointer
    //    Tagged Pointer 不使用堆内存，无需维护引用计数，直接返回
    if (isTaggedPointer()) return;

    // 2. 判断是否满足快速释放的 5 个条件（全部满足才能 free(this) 快速释放）：
    if (fastpath(isa.nonpointer              &&   // 条件1：使用了优化的非指针 isa
                 !isa.weakly_referenced      &&   // 条件2：没有 weak 指针指向该对象
                 !isa.has_assoc             &&   // 条件3：没有设置过关联对象
#if ISA_HAS_CXX_DTOR_BIT
                 !isa.has_cxx_dtor          &&   // 条件4：没有 C++ 析构函数（.cxx_destruct）
#else
                 !isa.getClass(false)->hasCxxDtor() &&
#endif
                 !isa.has_sidetable_rc))          // 条件5：引用计数未溢出到 SideTable（未使用额外散列表存储计数）
    {
        // 满足全部条件，直接 free 内存（快速路径）
        assert(!sidetable_present());
        free(this);
    } 
    else {
        // 不满足快速释放条件，走完整销毁流程
        object_dispose((id)this);
    }
}
```

### 4. object_dispose

如果不能快速释放，则调用 `object_dispose()` 做进一步处理：

```c++
// object_dispose：完整的对象销毁流程
id 
object_dispose(id obj)
{
    if (!obj) return nil;

    objc_destructInstance(obj);  // 执行实例销毁（清理成员变量、关联对象、弱引用等）
    free(obj);                   // 释放堆内存

    return nil;
}
// objc_destructInstance：负责销毁对象内部资源（不释放内存本身）
void *objc_destructInstance(id obj) 
{
    if (obj) {
        // 一次性读取所有标志位，提升性能
        bool cxx = obj->hasCxxDtor();              // 是否存在 C++ 析构函数（负责清理 C++ 成员变量）
        bool assoc = obj->hasAssociatedObjects();  // 是否有关联对象

        // 以下顺序非常重要，不能随意调换

        // Step 1：若有 C++ 析构函数，调用 object_cxxDestruct 销毁 C++ 成员变量
        //         object_cxxDestruct 最终会调用 objc_storeStrong 逐个释放成员变量（实例变量）
        if (cxx) object_cxxDestruct(obj);

        // Step 2：若有关联对象，调用 _object_remove_assocations 移除所有关联对象
        //         常用于 category 中通过 objc_setAssociatedObject 添加的属性
        if (assoc) _object_remove_assocations(obj, /*deallocating*/true);

        // Step 3：清理弱引用表和引用计数表
        obj->clearDeallocating();
    }

    return obj;
}
```

### 5. clearDeallocating

```c++
// clearDeallocating：清理弱引用表和引用计数表
inline void 
objc_object::clearDeallocating()
{
    if (slowpath(!isa.nonpointer)) {
        // 慢速路径：isa 是原始指针（非优化 isa），直接清理 SideTable
        sidetable_clearDeallocating();
    }
    else if (slowpath(isa.weakly_referenced  ||  isa.has_sidetable_rc)) {
        // 慢速路径：优化 isa，但存在 weak 引用 或 引用计数溢出到了 SideTable
        clearDeallocating_slow();
    }
    // 其他情况（nonpointer isa 且无 weak 引用、无 sidetable 引用计数）：
    // 无需清理，直接返回（已由 rootDealloc 的快速路径处理）

    assert(!sidetable_present());
}
```

`sidetable_clearDeallocating` 和 `clearDeallocating_slow` 最终都会调用 `weak_clear_no_lock`，将所有指向该对象的弱指针清空。

```c++
// sidetable_clearDeallocating：通过 SideTable 清理弱引用表和引用计数表
void 
objc_object::sidetable_clearDeallocating()
{
    // 通过对象地址从全局 SideTables 中取出对应的 SideTable
    SideTable& table = SideTables()[this];

    table.lock();
    // 在引用计数表（refcnts）中查找当前对象
    RefcountMap::iterator it = table.refcnts.find(this);
    if (it != table.refcnts.end()) {
        // 检查是否存在弱引用标志位
        if (it->second & SIDE_TABLE_WEAKLY_REFERENCED) {
            // 有弱引用，调用 weak_clear_no_lock 将所有 weak 指针置为 nil
            weak_clear_no_lock(&table.weak_table, (id)this);
        }
        // 从引用计数表中移除该对象的引用计数记录
        table.refcnts.erase(it);
    }
    table.unlock();
}
```

**`clearDeallocating` 共完成两件事：**

1. **清空弱引用表**：将所有弱引用该对象的 weak 指针置为 nil（这就是为什么 weak 不会造成悬空指针的原因）。
2. **清空引用计数表**：当对象引用计数超过 isa 可存储的上限（255）时，引用计数会溢出存储到 SideTable 的 `refcnts` 中（此时 `isa.has_sidetable_rc == 1`），销毁时需要一并清理。

### 6. weak_clear_no_lock

通过 for 循环遍历 `referrers` 数组，将所有 weak 指针（即 `referrers[i]`）的内存空间直接置为 nil；最后将该 `entry` 从 `weak_table` 中移除（与该对象相关的所有弱引用记录全部销毁）。

```c++
// weak_clear_no_lock：将指向指定对象的所有 weak 指针置为 nil，并从弱引用表中移除对应 entry
// 参数：
//   weak_table   —— 对象所在 SideTable 的弱引用表
//   referent_id  —— 即将销毁的对象
void 
weak_clear_no_lock(weak_table_t *weak_table, id referent_id) 
{
    objc_object *referent = (objc_object *)referent_id;

    // 通过哈希运算在 weak_table 中找到该对象对应的 weak_entry_t
    weak_entry_t *entry = weak_entry_for_referent(weak_table, referent);
    if (entry == nil) {
        // 正常情况下不应为空；可能是 CF/ObjC 混用导致的不匹配（已知 bug）
        return;
    }

    // 根据 entry 的存储模式，获取 weak 指针数组及其数量
    weak_referrer_t *referrers;
    size_t count;
    
    if (entry->out_of_line()) {
        // out-of-line 模式：使用堆上的动态哈希数组
        referrers = entry->referrers;
        count = TABLE_SIZE(entry);  // 数组总容量（含空槽）
    } 
    else {
        // inline 模式：使用栈上的固定大小内联数组
        referrers = entry->inline_referrers;
        count = WEAK_INLINE_COUNT;
    }
    
    // 遍历所有 weak 指针地址，将它们指向的内容（即对象地址）置为 nil
    for (size_t i = 0; i < count; ++i) {
        objc_object **referrer = referrers[i];  // referrer 是 weak 变量的地址
        if (referrer) {
            if (*referrer == referent) {
                // weak 指针确实指向当前对象，置为 nil
                *referrer = nil;
            }
            else if (*referrer) {
                // weak 指针指向的是其他对象，说明存在不正确的使用（如直接操作 objc_storeWeak）
                _objc_inform("__weak variable at %p holds %p instead of %p. "
                             "This is probably incorrect use of "
                             "objc_storeWeak() and objc_loadWeak(). "
                             "Break on objc_weak_error to debug.\n", 
                             referrer, (void*)*referrer, (void*)referent);
                objc_weak_error();
            }
        }
    }
    
    // 从 weak_table 中移除该对象对应的 weak_entry_t，完成清理
    weak_entry_remove(weak_table, entry);
}
```

---

## dealloc 完整调用链

```
dealloc
  └── _objc_rootDealloc
        └── objc_object::rootDealloc()
              ├── [快速路径] isTaggedPointer → return（TaggedPointer 无需处理）
              ├── [快速路径] 满足5个条件 → free(this)
              └── [慢速路径] object_dispose(this)
                    └── objc_destructInstance(obj)
                          ├── object_cxxDestruct(obj)          // 释放 C++ 成员变量
                          ├── _object_remove_assocations(obj)  // 移除关联对象
                          └── obj->clearDeallocating()
                                ├── sidetable_clearDeallocating()  // 原始 isa
                                │     └── weak_clear_no_lock()     // 将 weak 指针置 nil
                                └── clearDeallocating_slow()       // 优化 isa（有 weak 或 sidetable rc）
                                      └── weak_clear_no_lock()     // 将 weak 指针置 nil
```

**rootDealloc 快速释放的 5 个判断条件：**

| 条件 | 字段 | 含义 |
|---|---|---|
| 1 | `isa.nonpointer` | 使用了优化的非指针 isa |
| 2 | `!isa.weakly_referenced` | 无 weak 指针指向该对象 |
| 3 | `!isa.has_assoc` | 未设置过关联对象 |
| 4 | `!isa.has_cxx_dtor` | 无 C++ 析构函数 |
| 5 | `!isa.has_sidetable_rc` | 引用计数未溢出至 SideTable |

---

## 移除弱引用流程总结

1. 在 `weak_table` 中找到被弱引用对象对应的 `weak_entry_t`。
2. 在 `weak_entry_t` 中移除 weak 指针地址（置为 nil）。
3. 移除元素后，判断 `weak_entry_t` 是否已空：若为空，则将该 `weak_entry_t` 从 `weak_table` 中完全移除，释放相关内存。
