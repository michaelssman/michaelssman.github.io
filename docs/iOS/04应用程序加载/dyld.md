# dyld

点击应用程序的时候，系统调用exec函数，

dyld具体的工作

dyld链接之后

1. 递归加载所依赖的动态库
   1. 加载动态库和可执行文件的初始化
   2. libsystem第一个被初始化，libsystem调libdispatch，libdispatch调libObjc初始化`_objc_init`
   3. `_objc_init`里面调`_dyld_objc_notify_register(&map_images, load_images, unmap_image);`。关于类的加载。
2. rebase和binding
3. 调起main函数

重写load方法，可以查看main之前打调用。

## _objc_init

```c++
void _objc_init(void)
{
    static bool initialized = false;
    if (initialized) return;
    initialized = true;
    
    // fixme defer initialization until an objc-using image is found?
    environ_init();		//环境变量初始化
    tls_init();				//创建线程的析构函数
    static_init();		//运⾏C++静态构造函数
    runtime_init();		//分类表初始化，类表初始化
    exception_init();	//异常处理的初始化(数组越界，方法找不到的报错)
#if __OBJC2__
    cache_t::init();	//缓存的初始化
#endif
    _imp_implementationWithBlock_init();//Mac OS的
		//&map_images引用传递，load_images值传递，加载load方法
    _dyld_objc_notify_register(&map_images, load_images, unmap_image);//3个函数

#if __OBJC2__
    didCallDyldNotifyRegister = true;//标识对_dyld_objc_notify_register的调⽤已完成
#endif
}
```

### runtime_init

```c++
void runtime_init(void)
{
  //初始化两张表
    objc::unattachedCategories.init(32);//分类表的初始化
    objc::allocatedClasses.init();//类表的初始化，类表里面存的所有的类
}
```

### _dyld_objc_notify_register(&map_images, load_images, unmap_image);

3个函数

### load_images

```c++
void
load_images(const char *path __unused, const struct mach_header *mh)
{
    if (!didInitialAttachCategories && didCallDyldNotifyRegister) {
        didInitialAttachCategories = true;
        loadAllCategories();
    }

    // Return without taking locks if there are no +load methods here.
    if (!hasLoadMethods((const headerType *)mh)) return;

    recursive_mutex_locker_t lock(loadMethodLock);

    // Discover load methods
    {
        mutex_locker_t lock2(runtimeLock);
        //找load方法
        prepare_load_methods((const headerType *)mh);
    }

    // Call +load methods (without runtimeLock - re-entrant)
    call_load_methods();//执行load方法
}
```

#### prepare_load_methods

```c++
void prepare_load_methods(const headerType *mhdr)
{
    size_t count, i;

    runtimeLock.assertLocked();
		//找所有的非懒加载类（重写了load就是非懒加载类）
    classref_t const *classlist = 
        _getObjc2NonlazyClassList(mhdr, &count);
    for (i = 0; i < count; i++) {
        schedule_class_load(remapClass(classlist[i]));
    }

  	//找完类的load，然后找分类的load
    category_t * const *categorylist = _getObjc2NonlazyCategoryList(mhdr, &count);
    for (i = 0; i < count; i++) {
        category_t *cat = categorylist[i];
        Class cls = remapClass(cat->cls);
        if (!cls) continue;  // category for ignored weak-linked class
        if (cls->isSwiftStable()) {
            _objc_fatal("Swift class extensions and categories on Swift "
                        "classes are not allowed to have +load methods");
        }
        realizeClassWithoutSwift(cls, nil);
        ASSERT(cls->ISA()->isRealized());
        add_category_to_loadable_list(cat);
    }
}
```

##### schedule_class_load

```c++
static void schedule_class_load(Class cls)
{
  //不需要super load，父类的load优先子类的load
    if (!cls) return;
    ASSERT(cls->isRealized());  // _read_images should realize

    if (cls->data()->flags & RW_LOADED) return;

    // Ensure superclass-first ordering
  //递归，会先找父类的load
    schedule_class_load(cls->getSuperclass());

    add_class_to_loadable_list(cls);
    cls->setInfo(RW_LOADED); 
}
```

#### call_load_methods

```c++
void call_load_methods(void)
{
    static bool loading = NO;
    bool more_categories;

    loadMethodLock.assertLocked();

    // Re-entrant calls do nothing; the outermost call will finish the job.
    if (loading) return;
    loading = YES;

    void *pool = objc_autoreleasePoolPush();

    do {
        // 1. Repeatedly call class +loads until there aren't any more
        while (loadable_classes_used > 0) {
            call_class_loads();//类的load
        }

        // 2. Call category +loads ONCE
        more_categories = call_category_loads();//分类的load

        // 3. Run more +loads if there are classes OR more untried categories
    } while (loadable_classes_used > 0  ||  more_categories);

    objc_autoreleasePoolPop(pool);

    loading = NO;
}
```

#### +load方法执行顺序

1. +load方法调用顺序是：`SuperClass -->SubClass --> SuperClassCategaryClass --> SubClassCategaryClass`。
2. 不同的类按照编译先后顺序调用+load方法（后编译，先执行）；
3. 分类顺序按照编译先后顺序调用+load（后编译，先执行）；

#### 总结

1. load方法是在main函数执行前执行的。iOS应用启动的时候，就会加载所有的类，就会调用这个方法。
2. +load方法是在加载类和分类时系统调用，一般不手动调用，如果想要在类或分类加载时做一些事情，可以重写类或分类的+load方法。
3. 不需要[super load]，因为会自动的找superClass的load。
4. 类、分类的加载和+load方法有关，在程序运行过程只调用一次。
5. load是线程安全的，上面都有加锁操作。

想在类加载进内存的时候调用，就用load方法

如果想在第一次加载类的时候调用，就用initialized方法，也是只会调用一次。

### map_images

```c++
void
map_images(unsigned count, const char * const paths[],
           const struct mach_header * const mhdrs[])
{
    mutex_locker_t lock(runtimeLock);
    return map_images_nolock(count, paths, mhdrs);
}
```

```c++
void 
map_images_nolock(unsigned mhCount, const char * const mhPaths[],
                  const struct mach_header * const mhdrs[])
{
    static bool firstTime = YES;
    header_info *hList[mhCount];
    uint32_t hCount;
    size_t selrefCount = 0;

    // Perform first-time initialization if necessary.
    // This function is called before ordinary library initializers. 
    // fixme defer initialization until an objc-using image is found?
    if (firstTime) {
        preopt_init();//共享缓存有关
    }

    if (PrintImages) {
        _objc_inform("IMAGES: processing %u newly-mapped images...\n", mhCount);
    }


    // Find all images with Objective-C metadata.
    hCount = 0;

  	//统计所有类（可执行文件中类，动态库中的类）。可执行文件、动态库都是Mach O格式的文件
    // Count classes. Size various table based on the total.
    int totalClasses = 0;
    int unoptimizedTotalClasses = 0;
    {
        uint32_t i = mhCount;
        while (i--) {//找到所有的类
            const headerType *mhdr = (const headerType *)mhdrs[i];
						//从头部文件读
            auto hi = addHeader(mhdr, mhPaths[i], totalClasses, unoptimizedTotalClasses);
            if (!hi) {
                // no objc data in this entry
                continue;
            }
            
            if (mhdr->filetype == MH_EXECUTE) {
                // Size some data structures based on main executable's size
#if __OBJC2__
                // If dyld3 optimized the main executable, then there shouldn't
                // be any selrefs needed in the dynamic map so we can just init
                // to a 0 sized map
                if ( !hi->hasPreoptimizedSelectors() ) {
                  size_t count;
                  _getObjc2SelectorRefs(hi, &count);
                  selrefCount += count;
                  _getObjc2MessageRefs(hi, &count);
                  selrefCount += count;
                }
#else
                _getObjcSelectorRefs(hi, &selrefCount);
#endif
                
#if SUPPORT_GC_COMPAT
                // Halt if this is a GC app.
                if (shouldRejectGCApp(hi)) {
                    _objc_fatal_with_reason
                        (OBJC_EXIT_REASON_GC_NOT_SUPPORTED, 
                         OS_REASON_FLAG_CONSISTENT_FAILURE, 
                         "Objective-C garbage collection " 
                         "is no longer supported.");
                }
#endif
            }
            
            hList[hCount++] = hi;
            
            if (PrintImages) {
                _objc_inform("IMAGES: loading image for %s%s%s%s%s\n", 
                             hi->fname(),
                             mhdr->filetype == MH_BUNDLE ? " (bundle)" : "",
                             hi->info()->isReplacement() ? " (replacement)" : "",
                             hi->info()->hasCategoryClassProperties() ? " (has class properties)" : "",
                             hi->info()->optimizedByDyld()?" (preoptimized)":"");
            }
        }
    }

    // Perform one-time runtime initialization that must be deferred until 
    // the executable itself is found. This needs to be done before 
    // further initialization.
    // (The executable may not be present in this infoList if the 
    // executable does not contain Objective-C code but Objective-C 
    // is dynamically loaded later.
    if (firstTime) {
        sel_init(selrefCount);//C++的构造函数和析构方法。
        arr_init();

#if SUPPORT_GC_COMPAT
        /**
        关于Mac OS的，不用管。
        */
#endif

#if TARGET_OS_OSX
        /**
        关于Mac OS的，不用管。
        */
#endif
      
    }

  //所有类初始化完成之后
    if (hCount > 0) {
        _read_images(hList, hCount, totalClasses, unoptimizedTotalClasses);
    }

    firstTime = NO;
    
    // Call image load funcs after everything is set up.
    for (auto func : loadImageFuncs) {
        for (uint32_t i = 0; i < mhCount; i++) {
            func(mhdrs[i]);
        }
    }
}
```

#### arr_init

```c++
void arr_init(void) 
{
    AutoreleasePoolPage::init();//自动释放池
    SideTablesMap.init();//散列表
    _objc_associations_init();//关联对象的初始化操作
    if (DebugScanWeakTables)
        startWeakTableScan();
}
```

#### _read_images

_read_images镜像文件，llvm编译阶段SEL和IMP绑定修复。

_read_images里面有很多的fix up，因为虚拟内存（ASLR）。地址空间随机布局。app每次启动内存地址都不固定。需要dyld的rebase和binding，修改镜像指针地址。

作用：进行类的初始化。

流程：

1. 加载所有类到类的gdb_objc_realized_classes表中。 
2. 对所有类做重映射。
3. 将所有SEL都注册到namedSelectors表中。
4. 修复函数指针遗留。
5. 将所有Protocol都添加到protocol_map表中。
6. 对所有Protocol做重映射。
7. 初始化所有非懒加载的类，进行rw、ro等操作。 
8. 遍历已标记的懒加载的类，并做初始化操作。
9. 处理所有Category，包括Class和Meta Class。 
10. 初始化所有未初始化的类。

```c++
void _read_images(header_info **hList, uint32_t hCount, int totalClasses, int unoptimizedTotalClasses)
{
    header_info *hi;
    uint32_t hIndex;
    size_t count;
    size_t i;
    Class *resolvedFutureClasses = nil;
    size_t resolvedFutureClassCount = 0;
    static bool doneOnce;
    bool launchTime = NO;
    TimeLogger ts(PrintImageTimes);

    runtimeLock.assertLocked();

#define EACH_HEADER \
    hIndex = 0;         \
    hIndex < hCount && (hi = hList[hIndex]); \
    hIndex++

    if (!doneOnce) {
        doneOnce = YES;
        launchTime = YES;

#if SUPPORT_NONPOINTER_ISA
        // Disable non-pointer isa under some conditions.

# if SUPPORT_INDEXED_ISA
        // Disable nonpointer isa if any image contains old Swift code
        //默认开启isa指针优化
        for (EACH_HEADER) {
            if (hi->info()->containsSwift()  &&
                hi->info()->swiftUnstableVersion() < objc_image_info::SwiftVersion3)
            {
                DisableNonpointerIsa = true;
                if (PrintRawIsa) {
                    _objc_inform("RAW ISA: disabling non-pointer isa because "
                                 "the app or a framework contains Swift code "
                                 "older than Swift 3.0");
                }
                break;
            }
        }
# endif

# if TARGET_OS_OSX
        // Disable non-pointer isa if the app is too old
        // (linked before OS X 10.11)
        // Note: we must check for macOS, because Catalyst and Almond apps
        // return false for a Mac SDK check! rdar://78225780
//        if (dyld_get_active_platform() == PLATFORM_MACOS && !dyld_program_sdk_at_least(dyld_platform_version_macOS_10_11)) {
//            DisableNonpointerIsa = true;
//            if (PrintRawIsa) {
//                _objc_inform("RAW ISA: disabling non-pointer isa because "
//                             "the app is too old.");
//            }
//        }

        // Disable non-pointer isa if the app has a __DATA,__objc_rawisa section
        // New apps that load old extensions may need this.
        for (EACH_HEADER) {
            if (hi->mhdr()->filetype != MH_EXECUTE) continue;
            unsigned long size;
            if (getsectiondata(hi->mhdr(), "__DATA", "__objc_rawisa", &size)) {
                DisableNonpointerIsa = true;
                if (PrintRawIsa) {
                    _objc_inform("RAW ISA: disabling non-pointer isa because "
                                 "the app has a __DATA,__objc_rawisa section");
                }
            }
            break;  // assume only one MH_EXECUTE image
        }
# endif

#endif

        if (DisableTaggedPointers) {
            disableTaggedPointers();
        }
        
        initializeTaggedPointerObfuscator();

        if (PrintConnecting) {
            _objc_inform("CLASS: found %d classes during launch", totalClasses);
        }

        // namedClasses
        // Preoptimized classes don't go in this table.
        // 4/3 is NXMapTable's load factor
        int namedClassesSize = 
            (isPreoptimized() ? unoptimizedTotalClasses : totalClasses) * 4 / 3;
        gdb_objc_realized_classes =
            NXCreateMapTable(NXStrValueMapPrototype, namedClassesSize);

        ts.log("IMAGE TIMES: first time tasks");
    }

    // Fix up @selector references
    // Note this has to be before anyone uses a method list, as relative method
    // lists point to selRefs, and assume they are already fixed up (uniqued).
    //修复selector。rebase过程，sel修改为正确的内存地址。
    static size_t UnfixedSelectors;
    {
        mutex_locker_t lock(selLock);
        for (EACH_HEADER) {
            if (hi->hasPreoptimizedSelectors()) continue;

            bool isBundle = hi->isBundle();
            SEL *sels = _getObjc2SelectorRefs(hi, &count);
            UnfixedSelectors += count;
            for (i = 0; i < count; i++) {
                const char *name = sel_cname(sels[i]);
                SEL sel = sel_registerNameNoLock(name, isBundle);
                if (sels[i] != sel) {
                    sels[i] = sel;
                }
            }
        }
    }

    ts.log("IMAGE TIMES: fix up selector references");

    // Discover classes. Fix up unresolved future classes. Mark bundle classes.
    bool hasDyldRoots = dyld_shared_cache_some_image_overridden();

    for (EACH_HEADER) {
        if (! mustReadClasses(hi, hasDyldRoots)) {
            // Image is sufficiently optimized that we need not call readClass()
            continue;
        }

        classref_t const *classlist = _getObjc2ClassList(hi, &count);

        bool headerIsBundle = hi->isBundle();
        bool headerIsPreoptimized = hi->hasPreoptimizedClasses();

        for (i = 0; i < count; i++) {
            Class cls = (Class)classlist[i];
            Class newCls = readClass(cls, headerIsBundle, headerIsPreoptimized);

            if (newCls != cls  &&  newCls) {
                // Class was moved but not deleted. Currently this occurs 
                // only when the new class resolved a future class.
                // Non-lazily realize the class below.
                resolvedFutureClasses = (Class *)
                    realloc(resolvedFutureClasses, 
                            (resolvedFutureClassCount+1) * sizeof(Class));
                resolvedFutureClasses[resolvedFutureClassCount++] = newCls;
            }
        }
    }

    ts.log("IMAGE TIMES: discover classes");

    // Fix up remapped classes
    // Class list and nonlazy class list remain unremapped.
    // Class refs and super refs are remapped for message dispatching.
    
    if (!noClassesRemapped()) {
        for (EACH_HEADER) {
            Class *classrefs = _getObjc2ClassRefs(hi, &count);
            for (i = 0; i < count; i++) {
                remapClassRef(&classrefs[i]);
            }
            // fixme why doesn't test future1 catch the absence of this?
            classrefs = _getObjc2SuperRefs(hi, &count);
            for (i = 0; i < count; i++) {
                remapClassRef(&classrefs[i]);
            }
        }
    }

    ts.log("IMAGE TIMES: remap classes");

#if SUPPORT_FIXUP
    // Fix up old objc_msgSend_fixup call sites
    for (EACH_HEADER) {
        message_ref_t *refs = _getObjc2MessageRefs(hi, &count);
        if (count == 0) continue;

        if (PrintVtables) {
            _objc_inform("VTABLES: repairing %zu unsupported vtable dispatch "
                         "call sites in %s", count, hi->fname());
        }
        for (i = 0; i < count; i++) {
            fixupMessageRef(refs+i);
        }
    }

    ts.log("IMAGE TIMES: fix up objc_msgSend_fixup");
#endif


    // Discover protocols. Fix up protocol refs.
    for (EACH_HEADER) {
        extern objc_class OBJC_CLASS_$_Protocol;
        Class cls = (Class)&OBJC_CLASS_$_Protocol;
        ASSERT(cls);
        NXMapTable *protocol_map = protocols();
        bool isPreoptimized = hi->hasPreoptimizedProtocols();

        // Skip reading protocols if this is an image from the shared cache
        // and we support roots
        // Note, after launch we do need to walk the protocol as the protocol
        // in the shared cache is marked with isCanonical() and that may not
        // be true if some non-shared cache binary was chosen as the canonical
        // definition
        if (launchTime && isPreoptimized) {
            if (PrintProtocols) {
                _objc_inform("PROTOCOLS: Skipping reading protocols in image: %s",
                             hi->fname());
            }
            continue;
        }

        bool isBundle = hi->isBundle();

        protocol_t * const *protolist = _getObjc2ProtocolList(hi, &count);
        for (i = 0; i < count; i++) {
            readProtocol(protolist[i], cls, protocol_map, 
                         isPreoptimized, isBundle);
        }
    }

    ts.log("IMAGE TIMES: discover protocols");

    // Fix up @protocol references
    // Preoptimized images may have the right 
    // answer already but we don't know for sure.
    for (EACH_HEADER) {
        // At launch time, we know preoptimized image refs are pointing at the
        // shared cache definition of a protocol.  We can skip the check on
        // launch, but have to visit @protocol refs for shared cache images
        // loaded later.
        if (launchTime && hi->isPreoptimized())
            continue;
        protocol_t **protolist = _getObjc2ProtocolRefs(hi, &count);
        for (i = 0; i < count; i++) {
            remapProtocolRef(&protolist[i]);
        }
    }

    ts.log("IMAGE TIMES: fix up @protocol references");

    // Discover categories. Only do this after the initial category
    // attachment has been done. For categories present at startup,
    // discovery is deferred until the first load_images call after
    // the call to _dyld_objc_notify_register completes. rdar://problem/53119145
    if (didInitialAttachCategories) {
        for (EACH_HEADER) {
            load_categories_nolock(hi);
        }
    }

    ts.log("IMAGE TIMES: discover categories");

    // Category discovery MUST BE Late to avoid potential races
    // when other threads call the new category code before
    // this thread finishes its fixups.

    // +load handled by prepare_load_methods()

    // Realize non-lazy classes (for +load methods and static instances)
  //处理非懒加载类的加载
    for (EACH_HEADER) {
        classref_t const *classlist = hi->nlclslist(&count);
        for (i = 0; i < count; i++) {
            Class cls = remapClass(classlist[i]);
            if (!cls) continue;

            addClassTableEntry(cls);

            if (cls->isSwiftStable()) {
                if (cls->swiftMetadataInitializer()) {
                    _objc_fatal("Swift class %s with a metadata initializer "
                                "is not allowed to be non-lazy",
                                cls->nameForLogging());
                }
                // fixme also disallow relocatable classes
                // We can't disallow all Swift classes because of
                // classes like Swift.__EmptyArrayStorage
            }
            realizeClassWithoutSwift(cls, nil);
        }
    }

    ts.log("IMAGE TIMES: realize non-lazy classes");

    // Realize newly-resolved future classes, in case CF manipulates them
    if (resolvedFutureClasses) {
        for (i = 0; i < resolvedFutureClassCount; i++) {
            Class cls = resolvedFutureClasses[i];
            if (cls->isSwiftStable()) {
                _objc_fatal("Swift class is not allowed to be future");
            }
            realizeClassWithoutSwift(cls, nil);
            cls->setInstancesRequireRawIsaRecursively(false/*inherited*/);
        }
        free(resolvedFutureClasses);
    }

    ts.log("IMAGE TIMES: realize future classes");

    if (DebugNonFragileIvars) {
        realizeAllClasses();
    }


    // Print preoptimization statistics
    if (PrintPreopt) {
        static unsigned int PreoptTotalMethodLists;
        static unsigned int PreoptOptimizedMethodLists;
        static unsigned int PreoptTotalClasses;
        static unsigned int PreoptOptimizedClasses;

        for (EACH_HEADER) {
            if (hi->hasPreoptimizedSelectors()) {
                _objc_inform("PREOPTIMIZATION: honoring preoptimized selectors "
                             "in %s", hi->fname());
            }
            else if (hi->info()->optimizedByDyld()) {
                _objc_inform("PREOPTIMIZATION: IGNORING preoptimized selectors "
                             "in %s", hi->fname());
            }

            classref_t const *classlist = _getObjc2ClassList(hi, &count);
            for (i = 0; i < count; i++) {
                Class cls = remapClass(classlist[i]);
                if (!cls) continue;

                PreoptTotalClasses++;
                if (hi->hasPreoptimizedClasses()) {
                    PreoptOptimizedClasses++;
                }
                
                const method_list_t *mlist;
                if ((mlist = cls->bits.safe_ro()->baseMethods)) {
                    PreoptTotalMethodLists++;
                    if (mlist->isFixedUp()) {
                        PreoptOptimizedMethodLists++;
                    }
                }
                if ((mlist = cls->ISA()->bits.safe_ro()->baseMethods)) {
                    PreoptTotalMethodLists++;
                    if (mlist->isFixedUp()) {
                        PreoptOptimizedMethodLists++;
                    }
                }
            }
        }

        _objc_inform("PREOPTIMIZATION: %zu selector references not "
                     "pre-optimized", UnfixedSelectors);
        _objc_inform("PREOPTIMIZATION: %u/%u (%.3g%%) method lists pre-sorted",
                     PreoptOptimizedMethodLists, PreoptTotalMethodLists, 
                     PreoptTotalMethodLists
                     ? 100.0*PreoptOptimizedMethodLists/PreoptTotalMethodLists 
                     : 0.0);
        _objc_inform("PREOPTIMIZATION: %u/%u (%.3g%%) classes pre-registered",
                     PreoptOptimizedClasses, PreoptTotalClasses, 
                     PreoptTotalClasses 
                     ? 100.0*PreoptOptimizedClasses/PreoptTotalClasses
                     : 0.0);
        _objc_inform("PREOPTIMIZATION: %zu protocol references not "
                     "pre-optimized", UnfixedProtocolReferences);
    }

#undef EACH_HEADER
}
```

## ⾮懒加载类的初始化

关键函数： realizeClassWithoutSwift

```c++
/***********************************************************************
* realizeClassWithoutSwift
* Performs first-time initialization on class cls, 
* including allocating its read-write data.
* Does not perform any Swift-side initialization.
* Returns the real class structure for the class. 
* Locking: runtimeLock must be write-locked by the caller
**********************************************************************/
static Class realizeClassWithoutSwift(Class cls, Class previously)
{
    /**
 		 省略代码
 		 */
    if (ro->flags & RO_FUTURE) {
        // This was a future class. rw data is already allocated.
        rw = cls->data();
        ro = cls->data()->ro();
        ASSERT(!isMeta);
        cls->changeInfo(RW_REALIZED|RW_REALIZING, RW_FUTURE);
    } else {
        // Normal class. Allocate writeable class data.
      	//给rw开辟内存空间，然后将ro的数据“拷⻉”到rw⾥⾯。
        rw = objc::zalloc<class_rw_t>();
        rw->set_ro(ro);
        rw->flags = RW_REALIZED|RW_REALIZING|isMeta;
        cls->setData(rw);
    }

    cls->cache.initializeToEmptyOrPreoptimizedInDisguise();

#if FAST_CACHE_META
    if (isMeta) cls->cache.setBit(FAST_CACHE_META);
#endif

    // Choose an index for this class.
    // Sets cls->instancesRequireRawIsa if indexes no more indexes are available
    cls->chooseClassArrayIndex();

    if (PrintConnecting) {
        _objc_inform("CLASS: realizing class '%s'%s %p %p #%u %s%s",
                     cls->nameForLogging(), isMeta ? " (meta)" : "", 
                     (void*)cls, ro, cls->classArrayIndex(),
                     cls->isSwiftStable() ? "(swift)" : "",
                     cls->isSwiftLegacy() ? "(pre-stable swift)" : "");
    }

    // Realize superclass and metaclass, if they aren't already.
    // This needs to be done after RW_REALIZED is set above, for root classes.
    // This needs to be done after class index is chosen, for root metaclasses.
    // This assumes that none of those classes have Swift contents,
    //   or that Swift's initializers have already been called.
    //   fixme that assumption will be wrong if we add support
    //   for ObjC subclasses of Swift classes.
  //递归调⽤realizeClassWithoutSwift，对⽗类和元类进⾏初始化
    supercls = realizeClassWithoutSwift(remapClass(cls->getSuperclass()), nil);
    metacls = realizeClassWithoutSwift(remapClass(cls->ISA()), nil);

#if SUPPORT_NONPOINTER_ISA
    if (isMeta) {
        // Metaclasses do not need any features from non pointer ISA
        // This allows for a faspath for classes in objc_retain/objc_release.
        cls->setInstancesRequireRawIsa();
    } else {
        // Disable non-pointer isa for some classes and/or platforms.
        // Set instancesRequireRawIsa.
        bool instancesRequireRawIsa = cls->instancesRequireRawIsa();
        bool rawIsaIsInherited = false;
        static bool hackedDispatch = false;

        if (DisableNonpointerIsa) {
            // Non-pointer isa disabled by environment or app SDK version
            instancesRequireRawIsa = true;
        }
        else if (!hackedDispatch  &&  0 == strcmp(ro->getName(), "OS_object"))
        {
            // hack for libdispatch et al - isa also acts as vtable pointer
            hackedDispatch = true;
            instancesRequireRawIsa = true;
        }
        else if (supercls  &&  supercls->getSuperclass()  &&
                 supercls->instancesRequireRawIsa())
        {
            // This is also propagated by addSubclass()
            // but nonpointer isa setup needs it earlier.
            // Special case: instancesRequireRawIsa does not propagate
            // from root class to root metaclass
            instancesRequireRawIsa = true;
            rawIsaIsInherited = true;
        }

        if (instancesRequireRawIsa) {
            cls->setInstancesRequireRawIsaRecursively(rawIsaIsInherited);
        }
    }
// SUPPORT_NONPOINTER_ISA
#endif

    // Update superclass and metaclass in case of remapping
  //设置⽗类，isa指针的初始化
    cls->setSuperclass(supercls);
    cls->initClassIsa(metacls);
  
    /**
 		 省略代码
 		 */
    return cls;
}
```

