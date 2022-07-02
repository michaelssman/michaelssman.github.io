# cache分析

作用：方法再次调用的时候，更快的响应。

当类第一次从磁盘加载到内存时的结构：

isa，superclass，cache，bits。

class ro

- flags
- instanceStart
- instanceSize
- reserved
- name
- ivarLayout
- weakIvarLayout
- ivars
- baseMethodList
- baseProtocols
- baseProperties

### 分析原理

```
        LGPerson *p  = [LGPerson alloc];
        Class pClass = [LGPerson class];
        //打断点
```

### LLDB 验证方法存储

在控制台打印

>**(lldb) p/x pClass**
>
>(Class) $0 = 0x0000000100008428
>
>//内存平移16字节 isa+superclass=16
>
>**(lldb) p (cache_t \*)0x0000000100008438**
>
>(cache_t *) $1 = 0x0000000100008438
>
>//看里面的数据
>
>**(lldb) p \*$1**
>
>(cache_t) $2 = {
>
>_bucketsAndMaybeMask = {
>
>std::__1::atomic<unsigned long> = {
>
>Value = 4298548112
>
>}
>
>}
>
>= {
>
>= {
>
>_maybeMask = {
>
>​    std::__1::atomic<unsigned int> = {
>
>​     Value = 0
>
>​    }
>
>}
>
>_flags = 32808
>
>_occupied = 0
>
>}
>
>_originalPreoptCache = {
>
>std::__1::atomic<preopt_cache_t *> = {
>
>​    Value = 0x0000802800000000
>
>}
>
>}
>
>}
>
>}
>
>**(lldb) p $2.buckets()**
>
>(bucket_t *) $3 = 0x0001802800000003
>
>**(lldb) p $3[1]** //内存平移一个单位。
>
>**(lldb) p *$3** 
>
>(bucket_t) $4 = {//没有调用方法，所以没有方法缓存
>  _sel = {
>    std::__1::atomic<objc_selector *> = (null) {
>      Value = nil
>    }
>  }
>  _imp = {
>    std::__1::atomic<unsigned long> = {
>      Value = 0
>    }
>  }
>}

### cache_t数据结构

_maybeMask == bucket_t长度-1

capacity == bucket_t长度

```c++
struct cache_t {//8+8=16字节
private:
    explicit_atomic<uintptr_t> _bucketsAndMaybeMask; // 8字节  指针地址 存的是buckets首地址
    union {//联合体  成员变量之间互斥 8字节
      //互斥结构，有struct没_originalPreoptCache，有_originalPreoptCache没struct
        struct {
            explicit_atomic<mask_t>    _maybeMask; // 4字节 bucket_t长度-1
#if __LP64__  //long point 64位
            uint16_t                   _flags;  // 2字节
#endif
            uint16_t                   _occupied; // 2字节
        };
        explicit_atomic<preopt_cache_t *> _originalPreoptCache; // 指针8字节  隐藏的数据 一般看上面的struct
    };

  /*
  省略代码
  */

    void incrementOccupied();
    void setBucketsAndMask(struct bucket_t *newBuckets, mask_t newMask);

    void reallocate(mask_t oldCapacity, mask_t newCapacity, bool freeOld);
    void collect_free(bucket_t *oldBuckets, mask_t oldCapacity);

    static bucket_t *emptyBuckets();
    static bucket_t *allocateBuckets(mask_t newCapacity);
    static bucket_t *emptyBucketsForCapacity(mask_t capacity, bool allocate = true);
    static struct bucket_t * endMarker(struct bucket_t *b, uint32_t cap);
    void bad_cache(id receiver, SEL sel) __attribute__((noreturn, cold));

public:
    // The following four fields are public for objcdt's use only.
    // objcdt reaches into fields while the process is suspended
    // hence doesn't care for locks and pesky little details like this
    // and can safely use these.
    unsigned capacity() const;
    struct bucket_t *buckets() const;//提供buckets()方法，返回bucket_t
    Class cls() const;

  /*
  省略代码
  */
  	void insert(SEL sel, IMP imp, id receiver);
    void copyCacheNolock(objc_imp_cache_entry *buffer, int len);
    void destroy();
    void eraseNolock(const char *func);

    static void init();
    static void collectNolock(bool collectALot);
    static size_t bytesForCapacity(uint32_t cap);

  /*
  省略代码
  */
}
```

### cache_t::insert

插入的位置 根据sel哈希得到

缓存方法

```c++
void cache_t::insert(SEL sel, IMP imp, id receiver)
{
	/**
	省略代码
	*/
  
    // Use the cache as-is if until we exceed our expected fill ratio.
    mask_t newOccupied = occupied() + 1;//occupied自增1
    unsigned oldCapacity = capacity(), capacity = oldCapacity;
  
  //在arm64架构下开辟一个长度为2的桶子，在X86_64架构下开辟一个长度为4的桶子
    if (slowpath(isConstantEmptyCache())) {//cache是否为空
        // Cache is read-only. Replace it.
        if (!capacity) capacity = INIT_CACHE_SIZE;//初始值capacity：X86_64架构为4，arm64架构为2
        reallocate(oldCapacity, capacity, /* freeOld */false);
    }
  
  //判断是否满了cache_fill_ratio，在arm64架构下如果缓存大小小于等于bucket_t长度的八分之七，在X86_64架构下如果缓存的大小小于等于桶子长度bucket_t长度的四分之三，则什么都不干。
    else if (fastpath(newOccupied + CACHE_END_MARKER <= cache_fill_ratio(capacity))) {
        // Cache is less than 3/4 or 7/8 full. Use it as-is.
    }
  
  //在arm64架构下，当桶子的长度小于等于8的时候，什么都不做。
#if CACHE_ALLOW_FULL_UTILIZATION
    else if (capacity <= FULL_UTILIZATION_CACHE_SIZE && newOccupied + CACHE_END_MARKER <= capacity) {
        // Allow 100% cache utilization for small buckets. Use it as-is.
    }
#endif
    else {//2倍的扩容
        capacity = capacity ? capacity * 2 : INIT_CACHE_SIZE;
        if (capacity > MAX_CACHE_SIZE) {//cache的极限值 1左移16位
            capacity = MAX_CACHE_SIZE;
        }
        reallocate(oldCapacity, capacity, true);//干掉老桶子，老桶子里面的值不存在了。
    }

    bucket_t *b = buckets();
    mask_t m = capacity - 1;
    mask_t begin = cache_hash(sel, m);//通过sel和m的hash函数得到begin
    mask_t i = begin;

    // Scan for the first unused slot and insert there.
    // There is guaranteed to be an empty slot.
  //操作bucket_t 往bucket里面set插入数据
    do {
        if (fastpath(b[i].sel() == 0)) {
            incrementOccupied();
            b[i].set<Atomic, Encoded>(b, sel, imp, cls());
            return;
        }
      //已经缓存过了
        if (b[i].sel() == sel) {
            // The entry was added to the cache by some other thread
            // before we grabbed the cacheUpdateLock.
            return;
        }
    } while (fastpath((i = cache_next(i, m)) != begin));//哈希冲突时，改变i的值，i+1增大i，存到下一个

    bad_cache(receiver, (SEL)sel);
#endif // !DEBUG_TASK_THREADS
}
```

## cache扩容

**arm64架构**

- 也就是真机环境下，刚开始初始化的缓存方法的容器的长度2。
- 当桶子的长度小于8的时侯，是满容量了才扩容。也就是说当容器的长度为8时，容器可以存储8个方法。
- 当容器的长度大于8时，是7/8扩容。当容器的长度为16时，第14个方法进来的时候不会扩容，当第15个方法需要存储进来的时候，容器就要扩容了。
- 2倍扩容

**x86_64架构**

- 刚开始初始化的容器的长度为4。
- 是3/4扩容。这里的3/4扩容指的是：如果容器的长度为4，当第3个数据需要存储的时候，就要扩容了。如果容器的长度为8，当第6个数据需要存储的时候，就要扩容了。也就是说容器只能存储容器长度的3/4减1个方法。

**还有一点就是：当容器扩容之后，前面存储的方法也会随之清空。只有新增的那一个。为了性能效率考虑，舍弃了之前旧的。**

负载因子。0.75。空间利用率比较高。哈希冲突不会过多。

```
void cache_t::insert(SEL sel, IMP imp, id receiver)
{
//在这个方法里打断点，可以看到调用堆栈 log_and_fill_cache
}
```

log_and_fill_cache在方法lookUpImpOrForward里面。

### cache_t::buckets

cache_t获取bucket

```c++
struct bucket_t *cache_t::buckets() const
{
    uintptr_t addr = _bucketsAndMaybeMask.load(memory_order_relaxed);
    return (bucket_t *)(addr & bucketsMask);
}
```

buckets，bucket_t里面不止一个方法，有多个，不是数组，但是内存是连续的。里面是哈希。

_bucketsAndMaybeMask存的是buckets的首地址，可以查找所有的bucket。

occupied 结束。

### bucket_t

bucket_t是桶子，里面存IMP SEL

```c++
struct hh_bucket_t {
    SEL _sel;
    IMP _imp;
};
```

bucket_t::set保存方法

```c++
template<Atomicity atomicity, IMPEncoding impEncoding>
void bucket_t::set(bucket_t *base, SEL newSel, IMP newImp, Class cls)
{
	//编码imp
  uintptr_t newIMP = (impEncoding == Encoded
                        ? encodeImp(base, newImp, newSel, cls)
                        : (uintptr_t)newImp);

  //是否是原子操作
  //store存imp和sel，load是取
    if (atomicity == Atomic) {
        _imp.store(newIMP, memory_order_relaxed);
        
        if (_sel.load(memory_order_relaxed) != newSel) {
#ifdef __arm__
            mega_barrier();
            _sel.store(newSel, memory_order_relaxed);
#elif __x86_64__ || __i386__
            _sel.store(newSel, memory_order_release);
#else
#error Don't know how to do bucket_t::set on this architecture.
#endif
        }
    } else {
        _imp.store(newIMP, memory_order_relaxed);
        _sel.store(newSel, memory_order_relaxed);
    }
}
```

#### objc_cache.mm文件注释

```c++
 /***********************************************************************
 *
 * Cache readers (PC-checked by collecting_in_critical())
 * 从cache里面读取数据流程
 * objc_msgSend*
 * cache_getImp//cache什么时候发起和调用。读取缓存里的imp
 *
 * //cache读和写
 * Cache readers/writers (hold cacheUpdateLock during access; not PC-checked)
 *
 * //锁
 * cache_t::copyCacheNolock    (caller must hold the lock)
 * cache_t::eraseNolock        (caller must hold the lock)
 * cache_t::collectNolock      (caller must hold the lock)
 *
 * cache_t::insert             (acquires lock)
 * cache_t::destroy            (acquires lock)
 *
 * UNPROTECTED cache readers (NOT thread-safe; used for debug info only)
 * cache_print
 * _class_printMethodCaches
 * _class_printDuplicateCacheEntries
 * _class_printMethodCacheStatistics
 *
 ***********************************************************************/
```

谁发起调用cache流程