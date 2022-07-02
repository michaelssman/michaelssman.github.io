# block

Block也是一个对象，内存结构中也是一个结构体，它封装了一段代码，这段代码可以在任何时候执行。

clang编译 看底层实现

Block可以作为函数参数或者函数的返回值，而其本身又可以带输入参数或返回值。它是对C语言的扩展，用来实现匿名函数的特性。

Block的使用很像函数指针，不过与函数最大的不同是：Block可以访问函数以外、词法作用域以内的外部变量的值。

换句话说，Block不仅 实现函数的功能，还能携带函数的执行环境，更通俗的讲Block就是能够读取其它函数内部变量的函数。

# 内存管理

Block的内存需要开发人员自己管理，错误的内存管理会造成循环引用内存泄露，或者内存因为提前释放造成崩溃。

Block其实包含两部分：

一部分是Block所执行的代码，这一部分在编译的时候已经生产好了。

另一部分是Block执行时所需要的外部变量值的数据结构，注意的是Block会将使用到的变量的值拷贝到栈上。

# block分类

1. 全局

   没有捕获外界变量，或者只用到全局变量、静态(static)变量的block就是全局block

   NSGlobalBlock，类似函数，存储在程序的数据区域（text段），我们只要实现一个没有对周围变量没有引用的Block，就会显示为是它

   对于Global的Block，我们无需多处理，不需retain和copy，即使copy，也不会copy到堆区，内存不会发生变化，操作都无效。

   ```objective-c
       //1. __NSGlobalBlock__ 没有捕获任何的外界变量（除非是全局区的（静态变量））
       void (^globalBlock)(int, int) = ^(int a, int b){
           NSLog(@"%d",a+b);
       };
       NSLog(@"globalBlock:%@",globalBlock);//__NSGlobalBlock__
   ```

   特点：命长，应用程序在它就在。

   对于全局block，用weak，strong，还是copy修饰都是可以的。（但最好不用用weak）

   注意：如果block中没有用到外界变量，不管他是用什么修饰符修饰，他都是全局block！

2. 栈

   位于栈内存，函数返回后Block将无效；对于定义的Block加入了对定义环境变量的引用，也就是说内部使用了外部变量，就是NSStackBlock。

   对于Stack的Block，如果不做任何操作，随栈自生自灭。

   而如果想让它获得比stack更久的生命，那就调用Block_copy()，或者copy修饰，让它搬家到堆内存上，这也是我们为什么一直用copy修饰Block的原因。

   ```objective-c
   		int a = 10;
       void (^block)(void) = ^{//copy
           //保存一份代码块
           NSLog(@"hello %d",a);
       };
       NSLog(@"block:%@--%@",block,[block copy]);
   ```

   MRC下

    `__NSStackBlock__ __NSMallocBlock__`

   结果分析：当Block中使用了外部变量，Block为NSStackBlock类型，存储在栈区，当函数执行结束后 该Block就会被释放，调用copy后，栈区Block被copy到了堆区NSMallocBlock

   ARC下：

   `__NSMallocBlock__ __NSMallocBlock__`

   分析结果：在ARC模式下，没有了__NSStackBlock__类型，不要认为ARC没有了栈区Block这种类型。

   其实在ARC下，生产的Block默认也是NSStackBlock类型，只是在变量赋值的时候，系统默认对其进行了copy。

   从NSStackBlock给copy到堆区的NSMallocBlock类型，而在非arc中，则需要手动copy.。

3. 堆

   捕获了外界变量，或者是OC的属性，或者赋值给强引用

   只需要对NSStackBlock进行copy操作就可以获取，所以，当我们定义的Block要在外部回调使用的时候，在MRC下，我们需要copy的堆区，永远的持有，不让释放。

   在堆区的NSMallocBlock，我们可以对其retain，release，copy（等价于retain，引用计数的加一）。

   在ARC下，系统会给我们copy到堆区，避免了很多不必要的麻烦。

# 循环引用

因为Block在拷贝到堆上的时候，会retain其引用的外部变量，那么如果Block中如果引用了他的宿主对象，（也就是定义Block的类）那很有可能引起循环引用，既在自身类的Block中用了self对象，例如：

```objective-c
//循环引用
self.block = ^{
	[self function];
};
```

分析：因为Block是当前self属性，self拥有了Block，在ARC下为强引用； 当在Block中使用了self的时候，Block便强引用了self，两者相互持有，无法释放。  

解决方法是ARC 下`__weak`修饰self：__`weak Class *weakSelf =self;` MRC下`__weak`改为`__block`.

**补充：**

对于两个对象之间的Block回调，只有双方持有的时候才会造成循环引用，例如：

ClassA 中定义了Block闭包函数，ClassB中的Block指针去回调ClassA的Block，

此时如果Block中使用了ClassA的self自身对象，ClassB便强引用了ClassA，此时不会造成循环引用。

只有ClassB为ClassA的属性的属性，既ClassA也持有ClassB才会造成循环引用问题。

##### 强弱共舞

```objective-c
__weak typeof(self) weakSelf = self;
        self.block = ^{
            __strong typeof(weakSelf) strongSelf = weakSelf;
            dispatch_async(dispatch_get_global_queue(0, 0), ^{
                [NSThread sleepForTimeInterval:1];
                NSLog(@"%@",strongSelf);
            });
        };}
```

使用了`__strong`在`strongSelf`变量作用域结束之前，对`weakSelf`有一个引用，防止对象(self)提前被释放。而作用域一过，`strongSelf`不存在了，对象`(self)`也会被释放。

# Block对外部变量的存取管理

## 1、局部变量

1、基本数据类型

当在Block中使用局部变量时，在Block中只读。

Block会copy该局部变量的值，在Block中作为常量使用，是不允许修改的，只能使用，所以即使变量的值在Block外改变，也不影响他在Block中的值。

```objective-c
    int a = 100;
    void(^block)() = ^{
        NSLog(@"%d",a);//打印100
//        a = 300;//编译会报错
    };
    a = 200;
    block();
```

block内部修改外界变量i的值直接报错，如果想要修改，可以在int a = 0前面加上关键字__block，此时i等效于全局变量或静态变量

```objective-c
    __block int b = 0;   
    void (^block2) () = ^ {
        NSLog(@"b = %d",b); // 输出结果 b = 0;
        b = 2;
    };
    block2();
    NSLog(@"b = %d",b); //输出结果 b = 2;
```

2、指针类型

   block会copy一份指针并强引用指针所指对象，且内部不能修改指针的指向，但是可以修改指针所指向对象的值

```objective-c
　　NSMutableString *str = @"abc".mutableCopy; 
     void (^block4) () = ^ { 
//        str = @"def"; 报错
      [str appendString:@"def"];
      NSLog(@"str = %@",str);
    };
    str = @"123".mutableCopy;
    block4(); //输出结果为 "adbdef"
```

## 2、全局变量

1、static修饰符的全局变量，静态变量，或者全局属性

因为全局变量或静态变量在内存中的地址是固定的，Block在读取该变量值的时候是直接从其所在内存读出，获取到的是最新值，而不是在定义时copy的常量.

```objective-c
    static int a = 100;
    void(^block)() = ^{
        a += 100;
        NSLog(@"%d",a);//打印300
    };
    a = 200;
    block();
```

2、基本数据类型：成员变量（实例变量），全局变量

block直接访问变量地址，在block内部可以修改变量的值，并且外部变量被修改后，block内部也会跟着变

```objective-c
self.num = 1;
self.num ++;  

void (^block3) () = ^ {
		self.num++;
};
block3();
NSLog(@"%d",self.num);
//输出结果为 3
```

3、指针类型： 成员变量（实例变量），静态变量，全局变量

block不会复制指针，但是会强引用该对象，内部可修改指针指向，block会强引用成员属性\变量所属的对象，这也是为什么block内部用到self.xxx或_xxx可能会引起循环引用的原因

```objective-c
static NSString *staticStr = @"abc";  
void (^block5) () = ^ {
  	NSLog(@"staticStr = %@",staticStr);
  	staticStr = @"def";
  	NSLog(@"staticStr = %@",staticStr);
};
staticStr = @"123";
block5();    
//输出结果为 staticStr = 123  staticStr = def
```

## 3、__block修饰的变量

对外界进行修改的时候需要加__block，拷贝到堆区

#### block copy 从栈copy到堆

# block底层原理分析

```objective-c
int main0(){
    
    void(^block)(void) = ^{
        printf("Hello hh");
    };
    
    block();
    return 0;
}
```

进入该文件目录下

` clang -rewrite-objc block.c -o block.cpp`进行编译成C++

在底部找到int main0()函数 三行代码 .cpp的三行代码对应上面的三个代码 定义 调用 和return0.

block就是__main0_block_impl_0这个函数

 __main0_block_impl_0这个函数就是一个struct

对象在底层是结构体

```c++
int main0(){
    //首先去除类型转换的代码
    //__main0_block_impl_0 函数
    //两个参数__main0_block_func_0  __main0_block_desc_0_DATA
    void(*block)(void) = __main0_block_impl_0(__main0_block_func_0, &__main0_block_desc_0_DATA));

    //去除类型强转 下面一行可以简写：block->FuncPtr(block)
    ((void (*)(__block_impl *))((__block_impl *)block)->FuncPtr)((__block_impl *)block);
    return 0;
}

//block结构体
struct __main0_block_impl_0 {
  struct __block_impl impl;
  struct __main0_block_desc_0* Desc;
    //void *fp就是第一个参数
    //结构体的构造函数
  __main0_block_impl_0(void *fp, struct __main0_block_desc_0 *desc, int flags=0) {
    impl.isa = &_NSConcreteStackBlock;//栈区的block
    impl.Flags = flags;
    impl.FuncPtr = fp; //编程思想：函数式。先保存 在合适的地方调用，需要的地方调用。
    Desc = desc;
  }
};
 
 //第一个参数__main0_block_func_0就是下面的方法，里面就是block里面的代码 所以block能够保存代码就是因为在底层这样实现保存代码。
 static void __main0_block_func_0(struct __main0_block_impl_0 *__cself) {
     printf("Hello hh");
 }
```

block fp函数式保存

#### __block_impl结构体 

fp函数保存，block调用的时候执行。

__block_impl 结构体：

```c++
struct __block_impl {
  void *isa;//指针指向（栈block、堆block）
  int Flags;//枚举类型
  int Reserved;
  void *FuncPtr;
};
```

 - Flags 
    - BLOCK_HAS_COPY_DISPOSE 捕获外界变量的时候 这个是有值的。
    - BLOCK_HAS_SIGNATURE 签名
    - 方法有签名v@: 普通签名
        - v返回值
        - @对象
        - ：cmd方法编号

#### 捕获变量  

捕获对象 如何保存和释放 keep-dispose

**block底层会生成相应的成员变量。**

```objective-c
int main1(){
//    int a = 10;
    //如果要修改a的值 要在前面加__block
    __block int a = 10;
    void(^block)(void) = ^{
        a++;//如果int a不加__block修饰，但是在里面修改a的值，但是里面的a和外面的a不是同一个a，所以就会代码歧义，报错。加了__block就是指针拷贝。同一内存空间。编码也能通过。
        printf("Hello hh - %d",a);
    };
    
    block();
    return 0;
}
```

```c++
 int main1(){
     int a = 10;
 //比之前多个一个参数a  3个参数
     void(*block)(void) = (__main1_block_impl_0(__main1_block_func_0, &__main1_block_desc_0_DATA, a));
     ((void (*)(__block_impl *))((__block_impl *)block)->FuncPtr)((__block_impl *)block);
     return 0;
 }
 //a就传到了__main1_block_impl_0里面
 struct __main1_block_impl_0 {
   struct __block_impl impl;
   struct __main1_block_desc_0* Desc;
   int a; //成员变量a
   //fp是一个函数
   __main1_block_impl_0(void *fp, struct __main1_block_desc_0 *desc, int _a, int flags=0) : a(_a) {
     impl.isa = &_NSConcreteStackBlock;//编译期block是一个StackBlock
     impl.Flags = flags;
     impl.FuncPtr = fp;
     Desc = desc;
   }
 };
 
 //block代码块 是一个函数
 static void __main1_block_func_0(struct __main1_block_impl_0 *__cself) {
 int a = __cself->a; // bound by copy  值拷贝 生成了一个新的变量a，值相同，地址不同。
       printf("Hello hh - %d",a);
   }

static void __main1_block_copy_0(struct __main1_block_impl_0*dst, struct __main1_block_impl_0*src) {
  _Block_object_assign((void*)&dst->a, (void*)src->a, 8/*BLOCK_FIELD_IS_BYREF*/);
}

static void __main1_block_dispose_0(struct __main1_block_impl_0*src) {
  _Block_object_dispose((void*)src->a, 8/*BLOCK_FIELD_IS_BYREF*/);
}

static struct __main1_block_desc_0 {
  size_t reserved;
  size_t Block_size;
  void (*copy)(struct __main1_block_impl_0*, struct __main1_block_impl_0*);
  void (*dispose)(struct __main1_block_impl_0*);
} __main1_block_desc_0_DATA = { 0, sizeof(struct __main1_block_impl_0), __main1_block_copy_0, __main1_block_dispose_0};
```

block捕获外界变量，会根据外界变量编译的时候自动生成相应的成员变量。

block把a的值传了进去，里面生成了一个新的变量a。

#### __block原理

如果要修改a的值 要在前面加__block

加__block 生成`__Block_byref_a_0`结构体，传给block的是指针地址，和外面的变量是同一个内存空间，所以可以修改外面的变量。

```c++
 int main1(){
 //__block修饰的变量
 //先声明一个a 的结构体，对a赋值。结构体a有了外部int a的值和地址空间。
 //对结构体赋值 初始化
 //结构体在堆里。int a在栈，结构体a在堆区。
   //结构体初始化
     __Block_byref_a_0 a = { //假象 拷贝到堆
         (void*)0,
         (__Block_byref_a_0 *)&a, //地址空间 取a的地址
         0,
         sizeof(__Block_byref_a_0),
         10//值
    };
     
     
     void(*block)(void) = ((void (*)())&__main1_block_impl_0((void *)__main1_block_func_0, &__main1_block_desc_0_DATA, (__Block_byref_a_0 *)&a, 570425344));//数字570425344是一个flag
     
     ((void (*)(__block_impl *))((__block_impl *)block)->FuncPtr)((__block_impl *)block);
     return 0;
 }
 
 //__Block_byref_a_0是一个结构体
 struct __Block_byref_a_0 {
   void *__isa;
 __Block_byref_a_0 *__forwarding;//指向a的地址
  int __flags;
  int __size;
  int a;
 };

 struct __main1_block_impl_0 {
  struct __block_impl impl;
  struct __main1_block_desc_0* Desc;
  __Block_byref_a_0 *a; // by ref
  __main1_block_impl_0(void *fp, struct __main1_block_desc_0 *desc, __Block_byref_a_0 *_a, int flags=0) : a(_a->__forwarding) {
    impl.isa = &_NSConcreteStackBlock;
    impl.Flags = flags;
    impl.FuncPtr = fp;
    Desc = desc;
  }
};

 static void __main1_block_func_0(struct __main1_block_impl_0 *__cself) {
 __Block_byref_a_0 *a = __cself->a; // bound by ref  指针拷贝 指向同一个内存空间

       printf("Hello hh - %d",(a->__forwarding->a));
   }
```

## block 底层copy处理

通过汇编 查看 走到了objc_retainBlock

```c++
id objc_retainBlock(id x) {
    return (id)_Block_copy(x);
}
```

_Block_copy在lib system_blocks.dylib库

```c++
// 重点提示: 这里是核心重点 block的拷贝操作: 栈Block -> 堆Block
void *_Block_copy(const void *arg) {
    struct Block_layout *aBlock;

    if (!arg) return NULL;
    
    // The following would be better done as a switch statement
    aBlock = (struct Block_layout *)arg;
    if (aBlock->flags & BLOCK_NEEDS_FREE) {
        // latches on high
        latching_incr_int(&aBlock->flags);
        return aBlock;
    }
    else if (aBlock->flags & BLOCK_IS_GLOBAL) {
        return aBlock;
    }
    else {//编译期：栈block
        // Its a stack block.  Make a copy. -> heap
        struct Block_layout *result =
            (struct Block_layout *)malloc(aBlock->descriptor->size);
        if (!result) return NULL;
        memmove(result, aBlock, aBlock->descriptor->size); // bitcopy first
#if __has_feature(ptrauth_calls)
        // Resign the invoke pointer as it uses address authentication.
        result->invoke = aBlock->invoke;
#endif
        // reset refcount -- 对象 isa 联合体位于
        result->flags &= ~(BLOCK_REFCOUNT_MASK|BLOCK_DEALLOCATING);    // XXX not needed
        result->flags |= BLOCK_NEEDS_FREE | 2;  // logical refcount 1
        _Block_call_copy_helper(result, aBlock);
        // Set isa last so memory analysis tools see a fully-initialized object.
        result->isa = _NSConcreteMallocBlock;//isa标记堆block
        return result;
    }
}
```

#### block底层结构 

fp函数保存，block调用的时候执行。

Block 结构体包含：

 - isa指针指向（栈block、堆block）
 - Flags 枚举类型
   - BLOCK_HAS_COPY_DISPOSE 捕获外界变量的时候 这个是有值的。
   - BLOCK_HAS_SIGNATURE 签名
   - 方法有签名v@: 普通签名
     - v返回值
     - @对象
     - ：cmd方法编号
- invoke
- 签名信息
- Desc

block是Block_layout结构体

```c++
//block在底层 结构体
// 注释:Block 结构体
struct Block_layout {
    void *isa; //isa指向 栈block 堆block
    volatile int32_t flags; // contains ref count//标识符 存数据信息，是否正在析构，是否有keep函数，是否有析构函数 等等很多
    int32_t reserved;
    BlockInvokeFunction invoke;//调用函数（指针）
    struct Block_descriptor_1 *descriptor;//其它相关描述（block描述信息 捕获外界信息 有方法签名）
    // imported variables  //还有可选变量
};
```

结构体可选：**Block_descriptor_**

```c++
#define BLOCK_DESCRIPTOR_1 1
struct Block_descriptor_1 {
    uintptr_t reserved;
    uintptr_t size;
};

#define BLOCK_DESCRIPTOR_2 1
struct Block_descriptor_2 {
    // requires BLOCK_HAS_COPY_DISPOSE
    BlockCopyFunction copy;
    BlockDisposeFunction dispose;
};

#define BLOCK_DESCRIPTOR_3 1
struct Block_descriptor_3 {
    // requires BLOCK_HAS_SIGNATURE
    const char *signature;
    const char *layout;     // contents depend on BLOCK_HAS_EXTENDED_LAYOUT
};
```

引用了外部变量 没经过_Block_copy操作 是栈block 经过block_copy是堆block

### isa

### invoke

### 签名

block签名是`@?`

hook：invoke消息 消息机制 转发需要先获取签名 然后invocation处理

### 捕获变量

三层拷贝：

1. _Block_copy拷贝到堆
2. block捕获Block_byref_ 对Block_byref_进行copy
3. Block_byref对object进行copy

### 保存

_Block_object_assign 里面有对捕获变量类型的处理：例 是否有加__block

```c++
// 注释: Block 捕获外界变量的操作
void _Block_object_assign(void *destArg, const void *object, const int flags) {
    const void **dest = (const void **)destArg;
    switch (os_assumes(flags & BLOCK_ALL_COPY_DISPOSE_FLAGS)) {
      case BLOCK_FIELD_IS_OBJECT://普通的类型
        /*******
        id object = ...;
        [^{ object; } copy];
        ********/
            
            //_Block_retain_object_default 默认空的实现 交给ARC系统的操作
        _Block_retain_object(object);
        *dest = object;
        break;

      case BLOCK_FIELD_IS_BLOCK:
        /*******
        void (^object)(void) = ...;
        [^{ object; } copy];
        ********/

            //把变量 搞到堆里
        *dest = _Block_copy(object);
        break;
    
      case BLOCK_FIELD_IS_BYREF | BLOCK_FIELD_IS_WEAK:
      case BLOCK_FIELD_IS_BYREF:
        /*******
         // copy the onstack __block container to the heap
         // Note this __weak is old GC-weak/MRC-unretained.
         // ARC-style __weak is handled by the copy helper directly.
         __block ... x;
         __weak __block ... x;
         [^{ x; } copy];
         ********/

        *dest = _Block_byref_copy(object);
        break;
        
      case BLOCK_BYREF_CALLER | BLOCK_FIELD_IS_OBJECT:
      case BLOCK_BYREF_CALLER | BLOCK_FIELD_IS_BLOCK:
        /*******
         // copy the actual field held in the __block container
         // Note this is MRC unretained __block only. 
         // ARC retained __block is handled by the copy helper directly.
         __block id object;
         __block void (^object)(void);
         [^{ object; } copy];
         ********/

        *dest = object;
        break;

      case BLOCK_BYREF_CALLER | BLOCK_FIELD_IS_OBJECT | BLOCK_FIELD_IS_WEAK:
      case BLOCK_BYREF_CALLER | BLOCK_FIELD_IS_BLOCK  | BLOCK_FIELD_IS_WEAK:
        /*******
         // copy the actual field held in the __block container
         // Note this __weak is old GC-weak/MRC-unretained.
         // ARC-style __weak is handled by the copy helper directly.
         __weak __block id object;
         __weak __block void (^object)(void);
         [^{ object; } copy];
         ********/

        *dest = object;
        break;

      default:
        break;
    }
}
```

```c++
// 重点提示: 这里是核心重点 block的拷贝操作: 栈Block -> 堆Block
void *_Block_copy(const void *arg) {
    struct Block_layout *aBlock;

    if (!arg) return NULL;
    
    // The following would be better done as a switch statement
    aBlock = (struct Block_layout *)arg;
    if (aBlock->flags & BLOCK_NEEDS_FREE) {
        // latches on high
        latching_incr_int(&aBlock->flags);
        return aBlock;
    }
    else if (aBlock->flags & BLOCK_IS_GLOBAL) {
        return aBlock;
    }
    else {
        // Its a stack block.  Make a copy. -> heap
        struct Block_layout *result =
            (struct Block_layout *)malloc(aBlock->descriptor->size);
        if (!result) return NULL;
        memmove(result, aBlock, aBlock->descriptor->size); // bitcopy first
#if __has_feature(ptrauth_calls)
        // Resign the invoke pointer as it uses address authentication.
        result->invoke = aBlock->invoke;
#endif
        // reset refcount -- 对象 isa 联合体位于
        result->flags &= ~(BLOCK_REFCOUNT_MASK|BLOCK_DEALLOCATING);    // XXX not needed
        result->flags |= BLOCK_NEEDS_FREE | 2;  // logical refcount 1
        _Block_call_copy_helper(result, aBlock);
        // Set isa last so memory analysis tools see a fully-initialized object.
        result->isa = _NSConcreteMallocBlock;
        return result;
    }
}
```

__block修饰的会走`_Block_byref_copy`

```c++
// Cooci注释: __Block 捕获外界变量的操作 内存拷贝 以及常规处理

static struct Block_byref *_Block_byref_copy(const void *arg) {
    struct Block_byref *src = (struct Block_byref *)arg;
//__block 内存是一样的 同一个
    if ((src->forwarding->flags & BLOCK_REFCOUNT_MASK) == 0) {
        // src points to stack
        struct Block_byref *copy = (struct Block_byref *)malloc(src->size);
        copy->isa = NULL;
        // byref value 4 is logical refcount of 2: one for caller, one for stack
        copy->flags = src->flags | BLOCK_BYREF_NEEDS_FREE | 4;
        copy->forwarding = copy; // patch heap copy to point to itself
        src->forwarding = copy;  // patch stack to point to heap copy
        copy->size = src->size;

        if (src->flags & BLOCK_BYREF_HAS_COPY_DISPOSE) {
            // Trust copy helper to copy everything of interest
            // If more than one field shows up in a byref block this is wrong XXX
            struct Block_byref_2 *src2 = (struct Block_byref_2 *)(src+1);
            struct Block_byref_2 *copy2 = (struct Block_byref_2 *)(copy+1);
            copy2->byref_keep = src2->byref_keep;
            copy2->byref_destroy = src2->byref_destroy;

            if (src->flags & BLOCK_BYREF_LAYOUT_EXTENDED) {
                struct Block_byref_3 *src3 = (struct Block_byref_3 *)(src2+1);
                struct Block_byref_3 *copy3 = (struct Block_byref_3*)(copy2+1);
                copy3->layout = src3->layout;
            }
//捕获到了外界变量 进行相关内存处理 生命周期的保存
            (*src2->byref_keep)(copy, src);
        }
        else {
            // Bitwise copy.
            // This copy includes Block_byref_3, if any.
            memmove(copy+1, src+1, src->size - sizeof(*src));
        }
    }
    // already copied to heap
    else if ((src->forwarding->flags & BLOCK_BYREF_NEEDS_FREE) == BLOCK_BYREF_NEEDS_FREE) {
        latching_incr_int(&src->forwarding->flags);
    }
    
    return src->forwarding;
}
```

### dispose

相反

---

block其实是一个对象，需要一个初始化过程。

- desc1
- desc2
  - copy 给相应的代码 函数实现
  - dispose













































































