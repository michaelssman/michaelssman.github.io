# iOS应用加载流程

## 一、基础概念

### 1. image 镜像文件

iOS 应用程序并不是从零开始构建全部代码的。`UIKit`、`Foundation`、`libObjc`、`libDispatch`、`libSystem` 等系统库，在被映射到内存之后，统称为**镜像（image）**。每一个 Mach-O 格式的可执行文件或动态库，都是一个 image。

---

### 2. 物理内存与虚拟内存
![image-20210512215147699](iOS应用加载流程.assets/image-20210512215147699.png)

在 lldb 调试中，打印出的地址（如 `0x7fee81409190`）是**虚拟地址**，并非物理地址。

`虚拟地址 - ASLR 偏移 = 文件中的偏移地址`（并非物理地址）

#### 2.1 物理内存时代

早期系统启动应用程序时，会将整个程序直接加载到物理内存。

**优点：**
- 实现简单，代码在内存中的位置与文件中的偏移地址一一对应。

**缺点：**

- **安全问题**：直接使用物理地址进行数据读写，一个应用可以直接读取其他应用的内存数据，存在严重安全隐患。
- **内存不足**：将整个程序加载到物理内存，多个应用同时运行时内存会很快耗尽。

#### 2.2 虚拟内存

引入虚拟内存后，每个应用程序拥有独立的虚拟地址空间，地址从固定值（如 `0x000000`）开始。应用访问的都是虚拟地址，由操作系统和 CPU 中的 **MMU（内存管理单元）** 负责将虚拟地址翻译为真实物理地址。

由于虚拟地址是固定且连续的，攻击者可以轻松预测函数地址，因此进一步引入了 **ASLR（地址空间布局随机化）**。

**优点：**
- 解决了应用间内存隔离的安全问题（不同进程各自拥有独立的虚拟地址空间）。

#### 2.3 虚拟内存的分段与分页管理

**分段（懒加载）：**
应用程序加载到内存时采用**懒加载**策略，只加载启动所需的代码，用到新功能时再按需加载。这解决了内存不够用的问题，但会导致物理内存中数据不连续。

**分页（Page）：**
为解决物理地址不连续带来的访问效率问题，系统引入了**分页机制**，通过 MMU 维护虚拟地址到物理地址的映射表。

- iOS 每页大小为 **16KB**，macOS 每页大小为 **4KB**。
- 程序访问的是连续的虚拟地址，实际物理地址可以是乱序的，中间由 MMU 和操作系统协同完成地址翻译。
- 每次只能访问当前进程映射页内的地址，无法访问其他进程的物理地址，实现了进程隔离。

#### 2.4 共享缓存区（dyld shared cache）

`UIKit`、`Foundation` 等系统库是所有 App 公用的，操作系统将它们预先加载到一块共享内存区域（dyld shared cache）。

- 不同 App 访问共享缓存区时，**物理地址相同**（真正共享），但**虚拟地址不同**（因为各自的 ASLR 偏移不同）。

---

## 二、加载流程总览

```
点击 App 图标
    → exec() 系统调用
        → 内核创建进程，开辟虚拟内存空间
            → 将 Mach-O 可执行文件映射进虚拟内存
                → 启动 dyld 动态链接器
                    → Load dylibs（递归加载依赖动态库）
                    → Rebase（重定向，修复内部指针）
                    → Bind（绑定，修复外部符号指针）
                    → ObjC Runtime 初始化（_objc_init → map_images → load_images）
                    → Initializers（C++ 构造函数、+load 方法）
                        → main()
                            → UIApplicationMain
                                → AppDelegate
```

---

## 三、加载到内存

点击 App 图标后，操作系统会通过 `exec()` 系统调用，为程序创建进程并开辟虚拟内存空间，然后将 **Mach-O** 格式的可执行二进制文件映射进去。

### ASLR（地址空间布局随机化）

Mach-O 文件编译完成后，其内部各段的偏移地址是固定的。为了防止攻击者预测函数地址进行精准攻击，iOS 引入了 **ASLR（Address Space Layout Randomization）** 技术：

- 每次 App 启动时，在 Mach-O 的起始地址前加上一个随机的 **PAGEZERO 偏移量**。
- 这样，即使攻击者知道某函数在文件中的偏移，也无法预测其在内存中的实际地址。
- 真实地址 = ASLR 偏移（基地址）+ 函数在 Mach-O 中的偏移值。

> 使用 lldb 命令 `image list` 可查看当前进程的基地址（即第一个条目对应的地址）。

---

## 四、dyld 动态链接器

> 在 `+load` 方法中打断点，执行 `bt` 打印调用堆栈，最底层即为 `dyld_start`，说明整个流程由 dyld 发起。

点击应用程序图标后，系统调用 `exec()` 函数，随后启动 **dyld（dynamic linker）** 进程。

dyld 将 Mach-O 文件作为 image 加载到虚拟内存后，根据 `Load Commands` 中的指令，将所有依赖的动态库也加载到虚拟内存。

### dyld 的主要工作

1. **递归加载所依赖的动态库**
   - 按依赖顺序加载动态库
   - `libSystem` 最先被初始化，随后调用 `libdispatch`，再由 `libdispatch` 调用 `libObjc` 中的 `_objc_init`
   - `_objc_init` 中调用 `_dyld_objc_notify_register(&map_images, load_images, unmap_image)` 注册三个回调，驱动后续 ObjC 运行时初始化
2. **Rebase 重定向** — 修复内部函数指针
3. **Bind 绑定** — 修复外部符号指针
4. **调用 main 函数**

---

## 五、ObjC 运行时初始化

### 5.1 _objc_init

`_objc_init` 是 ObjC 运行时的入口初始化函数，由 `libSystem` 间接触发调用。

```c++
void _objc_init(void)
{
    static bool initialized = false;
    if (initialized) return;
    initialized = true;
    
    environ_init();      // 读取并处理影响 ObjC 运行时行为的环境变量（如 OBJC_PRINT_LOAD_METHODS）
    tls_init();          // 初始化线程本地存储（Thread Local Storage），创建线程的析构函数
    static_init();       // 运行 C++ 静态构造函数（在 dyld 调用它们之前，ObjC 需要先初始化）
    runtime_init();      // 初始化分类表（unattachedCategories）和类表（allocatedClasses）
    exception_init();    // 初始化异常处理（数组越界、方法找不到等运行时错误的处理）
#if __OBJC2__
    cache_t::init();     // 初始化方法缓存（用于 objc_msgSend 的缓存机制）
#endif
    _imp_implementationWithBlock_init(); // 初始化 Block-IMP 转换支持（主要用于 macOS）
    
    // 向 dyld 注册三个关键回调函数：
    // - map_images：当 dyld 加载镜像时调用，负责类的注册与初始化
    // - load_images：负责调用所有类和分类的 +load 方法
    // - unmap_image：当镜像被卸载时调用，做清理工作
    _dyld_objc_notify_register(&map_images, load_images, unmap_image);

#if __OBJC2__
    didCallDyldNotifyRegister = true; // 标识 _dyld_objc_notify_register 调用已完成
#endif
}
```

#### runtime_init

```c++
void runtime_init(void)
{
    objc::unattachedCategories.init(32); // 初始化"未附加到类"的分类表（容量初始为32）
    objc::allocatedClasses.init();       // 初始化全局类表，存储所有已分配的类
}
```

---

### 5.2 load_images — 调用 +load 方法

`load_images` 由 dyld 在每次映射新镜像时触发，负责找到并执行所有 `+load` 方法。

```c++
void load_images(const char *path __unused, const struct mach_header *mh)
{
    // 第一次调用时，先加载所有分类
    if (!didInitialAttachCategories && didCallDyldNotifyRegister) {
        didInitialAttachCategories = true;
        loadAllCategories();
    }

    // 如果当前镜像没有 +load 方法，直接返回，提升性能
    if (!hasLoadMethods((const headerType *)mh)) return;

    recursive_mutex_locker_t lock(loadMethodLock);

    // 第一步：收集所有需要执行 +load 的类和分类（加运行时锁）
    {
        mutex_locker_t lock2(runtimeLock);
        prepare_load_methods((const headerType *)mh); // 找到所有 +load 方法并排序
    }

    // 第二步：执行所有 +load 方法（不持有 runtimeLock，支持可重入）
    call_load_methods();
}
```

#### prepare_load_methods — 收集 +load 方法

```c++
void prepare_load_methods(const headerType *mhdr)
{
    size_t count, i;

    runtimeLock.assertLocked();
    
    // 获取所有非懒加载类（即实现了 +load 方法的类）列表
    classref_t const *classlist = _getObjc2NonlazyClassList(mhdr, &count);
    for (i = 0; i < count; i++) {
        // schedule_class_load 会递归处理父类，确保父类的 +load 先入队
        schedule_class_load(remapClass(classlist[i]));
    }

    // 再处理非懒加载分类（实现了 +load 的分类），分类的 +load 在类之后执行
    category_t * const *categorylist = _getObjc2NonlazyCategoryList(mhdr, &count);
    for (i = 0; i < count; i++) {
        category_t *cat = categorylist[i];
        Class cls = remapClass(cat->cls);
        if (!cls) continue;  // 跳过被忽略的弱链接类的分类
        if (cls->isSwiftStable()) {
            // Swift 类不允许其 ObjC 分类或扩展中有 +load 方法
            _objc_fatal("Swift class extensions and categories on Swift "
                        "classes are not allowed to have +load methods");
        }
        realizeClassWithoutSwift(cls, nil); // 确保类已初始化（realized）
        ASSERT(cls->ISA()->isRealized());
        add_category_to_loadable_list(cat); // 将分类加入待执行 +load 列表
    }
}
```

##### schedule_class_load — 递归调度类的 +load

```c++
static void schedule_class_load(Class cls)
{
    if (!cls) return;
    ASSERT(cls->isRealized());  // 类必须已经过 realize 处理

    if (cls->data()->flags & RW_LOADED) return; // 已加入队列则跳过，避免重复

    // 递归调用，先处理父类，保证父类 +load 优先于子类执行
    schedule_class_load(cls->getSuperclass());

    add_class_to_loadable_list(cls);  // 将当前类加入待执行 +load 列表
    cls->setInfo(RW_LOADED);          // 标记为已加入，防止重复处理
}
```

#### call_load_methods — 执行 +load 方法

```c++
void call_load_methods(void)
{
    static bool loading = NO;
    bool more_categories;

    loadMethodLock.assertLocked();

    // 防止重入：如果已经在执行 +load，直接返回，最外层调用会处理所有任务
    if (loading) return;
    loading = YES;

    void *pool = objc_autoreleasePoolPush(); // 创建自动释放池，防止 +load 中的对象泄漏

    do {
        // 1. 循环执行类的 +load，直到队列为空（类的 +load 优先于分类）
        while (loadable_classes_used > 0) {
            call_class_loads();
        }

        // 2. 执行分类的 +load（每轮循环只调用一次）
        more_categories = call_category_loads();

        // 3. 如果执行分类 +load 的过程中又触发了新的类 +load，则继续循环
    } while (loadable_classes_used > 0 || more_categories);

    objc_autoreleasePoolPop(pool);

    loading = NO;
}
```

#### +load 方法执行顺序总结

1. **父类早于子类**：`SuperClass +load → SubClass +load`
2. **类早于分类**：所有类的 +load 执行完毕后，再执行分类的 +load
3. **编译顺序**：同级别的类或分类，**先编译的后执行**（Build Phases 中排在前面的文件反而后执行）
4. 完整顺序：`父类 → 子类 → 父类的分类 → 子类的分类`

#### +load 方法使用注意事项

1. `+load` 在 main 函数执行**之前**由系统自动调用，应用启动时会加载所有实现了 `+load` 的类。
2. `+load` 由系统调用，**无需也不应手动调用**，也不需要调用 `[super load]`（父类会被自动处理）。
3. 每个类和分类的 `+load` 在整个进程生命周期内**只执行一次**。
4. `+load` 的实现内部有加锁操作，是**线程安全**的，但在其内部调用其他方法时需注意死锁风险。
5. `+load` 执行时机过早，应尽量减少其中的工作量，避免影响启动性能。

#### +load 与 +initialize 的区别

| 特性 | `+load` | `+initialize` |
|---|---|---|
| 调用时机 | 类被加载到内存时（main 之前） | 类第一次收到消息时（按需，懒加载） |
| 调用次数 | 每个类只调用一次 | 每个类只调用一次，但若子类未实现会继承父类实现 |
| 是否需要 super | 不需要，自动处理 | 通常不需要，但子类未覆盖时会调用父类 |
| 调用方式 | 直接调用函数指针（不走消息发送） | 通过 objc_msgSend 消息机制调用 |
| 适用场景 | Method Swizzle、注册操作等 | 类第一次使用前的初始化工作 |

---

### 5.3 map_images — 镜像映射与类注册

`map_images` 是 ObjC 运行时处理镜像文件的核心入口，最终调用 `_read_images` 完成所有类、协议、分类的注册与初始化。

```c++
void map_images(unsigned count, const char * const paths[],
                const struct mach_header * const mhdrs[])
{
    mutex_locker_t lock(runtimeLock); // 加运行时锁，保证线程安全
    return map_images_nolock(count, paths, mhdrs);
}
```

```c++
void map_images_nolock(unsigned mhCount, const char * const mhPaths[],
                       const struct mach_header * const mhdrs[])
{
    static bool firstTime = YES;
    header_info *hList[mhCount];
    uint32_t hCount;
    size_t selrefCount = 0;

    if (firstTime) {
        preopt_init(); // 初始化与 dyld 共享缓存（shared cache）相关的预优化数据
    }

    // 统计所有镜像中的类数量（包括可执行文件和所有动态库中的类）
    // 可执行文件和动态库都是 Mach-O 格式的文件
    hCount = 0;
    int totalClasses = 0;
    int unoptimizedTotalClasses = 0;
    {
        uint32_t i = mhCount;
        while (i--) {
            const headerType *mhdr = (const headerType *)mhdrs[i];
            // 从 Mach-O 头部读取 ObjC 相关段信息，统计类数量
            auto hi = addHeader(mhdr, mhPaths[i], totalClasses, unoptimizedTotalClasses);
            if (!hi) {
                continue; // 该镜像中没有 ObjC 数据，跳过
            }
            
            if (mhdr->filetype == MH_EXECUTE) {
                // 主可执行文件：统计 selector 引用数量，用于初始化 selector 表的容量
#if __OBJC2__
                if (!hi->hasPreoptimizedSelectors()) {
                    size_t count;
                    _getObjc2SelectorRefs(hi, &count);
                    selrefCount += count;
                    _getObjc2MessageRefs(hi, &count);
                    selrefCount += count;
                }
#else
                _getObjcSelectorRefs(hi, &selrefCount);
#endif
            }
            
            hList[hCount++] = hi;
        }
    }

    if (firstTime) {
        sel_init(selrefCount); // 初始化 selector 表，预分配容量以提升性能
        arr_init();            // 初始化自动释放池、散列表、关联对象等基础设施
    }

    // 所有头部信息收集完毕后，调用 _read_images 完成核心初始化
    if (hCount > 0) {
        _read_images(hList, hCount, totalClasses, unoptimizedTotalClasses);
    }

    firstTime = NO;
    
    // 调用通过 objc_addLoadImageFunc 注册的回调（供第三方框架使用）
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
    AutoreleasePoolPage::init(); // 初始化自动释放池（基于双向链表的 Page 结构）
    SideTablesMap.init();        // 初始化 SideTables 散列表（存储引用计数和弱引用信息）
    _objc_associations_init();   // 初始化关联对象（objc_setAssociatedObject）所需的数据结构
    if (DebugScanWeakTables)
        startWeakTableScan();    // 调试模式：开启弱引用表扫描
}
```

---

### 5.4 _read_images — 核心初始化

`_read_images` 是整个运行时初始化中工作量最重的函数，完成类、协议、分类的注册，以及 ASLR 导致的指针修复。

**主要流程：**

1. 初始化全局类表 `gdb_objc_realized_classes`，预分配容量
2. 修复所有 SEL 引用（Rebase，将 selector 指针修正为正确的内存地址）
3. 发现并注册所有类（`readClass`），加入类表
4. 对所有类引用和父类引用做重映射（remap）
5. 修复旧版 `objc_msgSend_fixup` 调用点
6. 发现并注册所有 Protocol，修复协议引用
7. 发现并加载分类（Category）
8. **初始化所有非懒加载类**（实现了 `+load` 的类），执行 `realizeClassWithoutSwift`
9. 初始化所有已解析的 future classes

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

        // 如果存在 Swift 2.x 以下的旧代码，禁用 non-pointer ISA 优化
        // 默认情况下 non-pointer ISA 是开启的
        
        // 初始化全局类表（gdb_objc_realized_classes）
        // 容量 = 类总数 × 4/3（NXMapTable 的负载因子）
        int namedClassesSize = 
            (isPreoptimized() ? unoptimizedTotalClasses : totalClasses) * 4 / 3;
        gdb_objc_realized_classes =
            NXCreateMapTable(NXStrValueMapPrototype, namedClassesSize);
    }

    // 修复 selector 引用（Rebase 阶段的 SEL 修复）
    // 将所有 SEL 指针统一注册到全局 selector 表，确保同名 SEL 地址唯一
    static size_t UnfixedSelectors;
    {
        mutex_locker_t lock(selLock);
        for (EACH_HEADER) {
            if (hi->hasPreoptimizedSelectors()) continue; // 已被 dyld 预优化，跳过
            bool isBundle = hi->isBundle();
            SEL *sels = _getObjc2SelectorRefs(hi, &count);
            UnfixedSelectors += count;
            for (i = 0; i < count; i++) {
                const char *name = sel_cname(sels[i]);
                SEL sel = sel_registerNameNoLock(name, isBundle);
                if (sels[i] != sel) {
                    sels[i] = sel; // 将本地 SEL 指针修正为全局唯一的 SEL 地址
                }
            }
        }
    }

    // 发现并注册类：将所有类加入全局类表
    for (EACH_HEADER) {
        classref_t const *classlist = _getObjc2ClassList(hi, &count);
        for (i = 0; i < count; i++) {
            Class cls = (Class)classlist[i];
            Class newCls = readClass(cls, headerIsBundle, headerIsPreoptimized);
            // 如果类被移动（如解析了 future class），记录下来以便后续非懒加载初始化
            if (newCls != cls && newCls) {
                resolvedFutureClasses[resolvedFutureClassCount++] = newCls;
            }
        }
    }

    // 修复类引用和父类引用的重映射（处理 future class 替换等情况）
    if (!noClassesRemapped()) {
        for (EACH_HEADER) {
            Class *classrefs = _getObjc2ClassRefs(hi, &count);
            for (i = 0; i < count; i++) remapClassRef(&classrefs[i]);
            classrefs = _getObjc2SuperRefs(hi, &count);
            for (i = 0; i < count; i++) remapClassRef(&classrefs[i]);
        }
    }

    // 发现并注册所有 Protocol
    for (EACH_HEADER) {
        protocol_t * const *protolist = _getObjc2ProtocolList(hi, &count);
        for (i = 0; i < count; i++) {
            readProtocol(protolist[i], cls, protocol_map, isPreoptimized, isBundle);
        }
    }

    // 修复 @protocol 引用（将 protocol 引用指向统一的 canonical 定义）
    for (EACH_HEADER) {
        protocol_t **protolist = _getObjc2ProtocolRefs(hi, &count);
        for (i = 0; i < count; i++) remapProtocolRef(&protolist[i]);
    }

    // 加载分类（在初次 attach 完成后才执行，避免竞争条件）
    if (didInitialAttachCategories) {
        for (EACH_HEADER) load_categories_nolock(hi);
    }

    // 初始化所有非懒加载类（实现了 +load 方法的类）
    // 非懒加载类在 App 启动时立即完成 realize，而不是等到第一次使用
    for (EACH_HEADER) {
        classref_t const *classlist = hi->nlclslist(&count);
        for (i = 0; i < count; i++) {
            Class cls = remapClass(classlist[i]);
            if (!cls) continue;
            addClassTableEntry(cls);
            realizeClassWithoutSwift(cls, nil); // 对类做 realize 初始化
        }
    }

    // 初始化已解析的 future classes
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
}
```

---

## 六、Rebase 与 Bind

### 6.1 Rebase 重定向（针对内部符号）

**适用场景：** 本地函数，如 `viewDidLoad`、自定义的 `testFunc` 等。

由于 ASLR，Mach-O 文件中所有内部函数的地址都需要在运行时修正：

```
函数在内存中的地址 = ASLR（基地址）+ 函数在 Mach-O 文件中的偏移值
```

Rebase 过程就是将 Mach-O 中所有**内部**指针加上这个 ASLR 偏移，修正为正确的虚拟地址。

### 6.2 Bind 绑定（针对外部符号）

**适用场景：** 外部动态库中的函数，如 `NSLog`（位于 Foundation.framework）。

外部函数的地址在编译时未知，Mach-O 中只保留了符号名称。在运行时，dyld 加载对应动态库后，将符号的实际地址写入 Mach-O 的符号表指针处，这一过程称为 **Bind（绑定）**。

- **懒绑定（Lazy Binding）：** 大多数外部符号采用懒绑定，第一次调用时才完成绑定（如 `NSLog`）。
- **非懒绑定（Non-lazy Binding）：** 少数符号在启动时立即绑定，如 `dyld_stub_binder`。

### 6.3 PIC 技术（位置无关代码）

Mach-O 内部通过 **桩（stub）** 和**符号指针表**间接调用外部函数，而不是直接跳转到外部地址。这使得可执行文件本身与外部库的地址无关，支持动态链接和 ASLR。

---

## 七、非懒加载类的初始化 — realizeClassWithoutSwift

`realizeClassWithoutSwift` 是类首次初始化的核心函数，将只读的 `class_ro_t` 数据"升级"为可读写的 `class_rw_t`，并完成继承链的初始化。

```c++
static Class realizeClassWithoutSwift(Class cls, Class previously)
{
    // ... 省略部分代码
    
    if (ro->flags & RO_FUTURE) {
        // Future class：rw 数据已提前分配好
        rw = cls->data();
        ro = cls->data()->ro();
        cls->changeInfo(RW_REALIZED | RW_REALIZING, RW_FUTURE);
    } else {
        // 普通类：为 rw 分配可读写内存，并将 ro 中的数据关联到 rw
        // class_ro_t（只读）存储编译期确定的数据（方法列表、属性、协议等）
        // class_rw_t（可读写）是运行时动态扩展的数据结构
        rw = objc::zalloc<class_rw_t>(); // 分配并清零 class_rw_t 内存
        rw->set_ro(ro);                   // 将只读数据关联到 rw
        rw->flags = RW_REALIZED | RW_REALIZING | isMeta;
        cls->setData(rw);                 // 将 rw 设置为类的 data
    }

    cls->cache.initializeToEmptyOrPreoptimizedInDisguise(); // 初始化方法缓存

    cls->chooseClassArrayIndex(); // 为类分配在类数组中的索引，用于 non-pointer ISA

    // 递归地对父类和元类也执行 realize（如果尚未 realize）
    // 必须在 RW_REALIZED 标志设置之后才调用，防止循环
    supercls = realizeClassWithoutSwift(remapClass(cls->getSuperclass()), nil);
    metacls  = realizeClassWithoutSwift(remapClass(cls->ISA()), nil);

    // 根据父类等条件，决定是否禁用 non-pointer ISA 优化
    // （non-pointer ISA 在 isa 指针的低位中编码了引用计数等额外信息）

    // 设置父类指针和 ISA 指针，完成继承链的连接
    cls->setSuperclass(supercls);
    cls->initClassIsa(metacls);
    
    // ... 省略分类附加、属性继承等后续操作

    return cls;
}
```

---

## 八、Initializers 阶段

在 Rebase、Bind、ObjC 运行时初始化完成后，进入 Initializers 阶段：

1. 执行所有 **C++ 静态对象的构造函数**（`__attribute__((constructor))` 修饰的函数）
2. 执行所有类和分类的 **`+load` 方法**

全部完成后，dyld 调用程序的 **`main()` 函数**，正式进入应用代码。

---

## 九、执行 main 函数

`main()` 函数执行后，通过 `UIApplicationMain` 启动一个 **RunLoop**，保持程序持续运行，随后执行 `AppDelegate` 中的代码（如 `application:didFinishLaunchingWithOptions:`）。

---

## 十、完整加载流程总结

```
Load dylibs → Rebase → Bind → ObjC → Initializers → main()
```

| 阶段 | 主要工作 |
|---|---|
| **Load dylibs** | dyld 递归加载所有依赖的动态库 |
| **Rebase** | 修复 Mach-O 内部指针（加上 ASLR 偏移） |
| **Bind** | 将外部符号绑定到动态库中的实际地址 |
| **ObjC** | 注册类、协议、分类；修复 SEL；realize 非懒加载类 |
| **Initializers** | 执行 C++ 构造函数和 `+load` 方法 |
| **main()** | 启动 RunLoop，执行应用代码 |
