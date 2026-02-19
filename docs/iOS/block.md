# block

Block是一个对象，内存结构中是一个结构体。

Block可以作为函数参数或者函数的返回值，而其本身又可以带输入参数或返回值。它是对C语言的扩展，用来实现匿名函数的特性。

## Block与函数指针的区别

- 函数指针只是一个指向函数的地址。
- Block不仅实现函数的功能，还能捕获外部变量（形成闭包）。

## block分类

### 1、NSGlobalBlock

**没有捕获外界变量，或者只用到全局变量、静态(static)变量的block就是全局block。**

存储在程序的数据区域（text段）。

不需retain和copy，即使copy，也不会copy到堆区，内存不会发生变化，操作都无效。

```objective-c
void (^globalBlock)(int, int) = ^(int a, int b){
    NSLog(@"%d",a+b);
};
NSLog(@"globalBlock:%@",globalBlock);//__NSGlobalBlock__
```

特点：命长，应用程序在它就在。

对于全局block，用strong或copy修饰都可以。

### 2、NSStackBlock

捕获了外界变量，或者OC的属性，并且**赋值给弱引用**。

如果想让它获得比stack更久的生命，那就调用`Block_copy()`，或者copy修饰，拷贝到堆上。

```objective-c
int a = 10;
void (^block)(void) = ^{//copy
    //保存一份代码块
    NSLog(@"hello %d",a);
};
NSLog(@"block:%@--%@",block,[block copy]);
```

MRC下：

 `__NSStackBlock__ __NSMallocBlock__`

结果分析：当Block中使用了外部变量，Block为NSStackBlock类型。**存储在栈区内存，随栈自生自灭。当函数执行结束后，该Block就会被释放。**调用copy后，栈区Block被copy到堆区NSMallocBlock。

ARC下：

`__NSMallocBlock__ __NSMallocBlock__`

在ARC下，生成的Block默认也是NSStackBlock类型，只是在变量赋值的时候，系统默认对其进行了copy，从NSStackBlock给copy到堆区的NSMallocBlock类型。而在mrc中，则需要手动copy。

### 3、NSMallocBlock

捕获了外界变量，或者OC的属性，并且**赋值给强引用**

定义的Block要在外部回调使用时，在MRC下，我们需要copy的堆区，永远的持有，不让释放。

在堆区的NSMallocBlock，我们可以对其retain，release，copy（等价于retain，引用计数的加1）。

在ARC下，系统会给我们copy到堆区，避免了很多不必要的麻烦。

引用了外部变量，没经过_Block_copy操作 是栈block，经过block_copy是堆block。

## block使用copy

- **没有引用临时变量的block是放在global区**, 是不会被释放的。
- block引用了栈里的临时变量, 才会被创建在stack区。
- **stack区的block只要赋值给strong类型的变量, 就会自动copy到堆里**。

**block在创建的时候，默认是分配在栈上的。因为栈区中的变量管理是由它自己管理的，随时可能被销毁，一旦被销毁后续再次调用空对象就可能会造成程序崩溃问题。**

MRC使用copy的目的是将创建默认放在栈区的block拷贝一份到堆区。block放在了堆中，block有个指针指向了栈中的block代码块。

1. 如果访问了外部处于栈区的变量（比如局部变量），或处于堆区的变量。都会存放在堆区，如果访问的是内部创建的变量还是存储在全局区。
2. 在ARC模式下，系统自动的做了copy操作，所以为`__NSMallocBlock__`在MRC中是`__NSStackBlock__`。

## 内存管理

Block的内存需要开发人员自己管理，错误的内存管理会造成循环引用内存泄露，或者内存因为提前释放造成崩溃。

Block包含两部分：

1. Block所执行的代码，这一部分在编译的时候已经生产好了。
2. Block执行时所需要的外部变量值的数据结构，注意的是Block会将使用到的变量的值拷贝到栈上。

## 循环引用

因为Block在拷贝到堆上的时候，会retain其引用的外部变量，那么如果Block中如果引用了他的宿主对象，（也就是定义Block的类）那很有可能引起循环引用，既在自身类的Block中用了self对象，例如：

```objective-c
//循环引用
self.block = ^{
	[self function];
};
```

分析：Block是当前self属性，self强引用Block。当在Block内部捕获了self，Block便强引用了self，两者相互持有，无法释放。  

解决方法是ARC 下`__weak`修饰self：`__weak Class *weakSelf = self;` MRC下`__weak`改为`__block`。

**只有双方持有的时候才会造成循环引用。**

### 1. `__weak`和`__strong`

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

实例2：

报警告：`Capturing 'vc' strongly in this block is likely to lead to a retain cycle`。

```objective-c
vc.refreshFuZhu = ^{
[weakSelf refreshFuzhu:vc];
};
```

警告是因为在 block 中强引用了 `vc`，可能导致 retain cycle（循环引用）。在 Objective-C 和 Swift 中，**block 会捕获并持有其引用的对象**。如果 block 中强引用了 `vc`，而 `vc` 又持有这个 block，就会导致 retain cycle。

要解决这个问题，可以在 block 中使用弱引用（weak reference）来避免 retain cycle。可以使用 `__weak` 或 `__block` 关键字来声明一个弱引用的 `vc`。

```objc
__weak typeof(vc) weakVC = vc;
vc.refreshFuZhu = ^{
    __strong typeof(weakVC) strongVC = weakVC;
    if (strongVC) {
        [weakSelf refreshFuzhu:strongVC];
    }
};
```

在这个修改后的代码中：

1. 使用 `__weak` 关键字创建一个弱引用 `weakVC`，这样可以避免 retain cycle。
2. 在 block 内部，使用 `__strong` 关键字重新创建一个强引用 `strongVC`，以确保在 **block 执行期间 `vc` 不会被释放**。

### 2. 局部变量

手动释放

```objective-c
    //第二种解决方式：引用一个临时第三者中间变量objc。objc->nil手动释放
    __block HHBlockViewController *vc = self;//临时变量vc持有
    self.block = ^{
        //里面代码复杂的情况。里面有异步 耗时操作
        //延长生命周期
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
            NSLog(@"%@",vc.name);
            //因为捕获了vc，所以用完之后需要将vc置空
            vc = nil;//self->block->vc->self
        });
    };
```

### 3. 传参

```objective-c
    //循环引用的原因：因为block里面要用self  作用域之间的通讯 self.name在外部，作用空间在block里面的空间。 作用域和作用域之间的传递可以用参数来传递。
    self.block1 = ^(HHBlockViewController *vc){
        //里面代码复杂的情况。里面有异步 耗时操作
        //延长生命周期
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
            NSLog(@"%@",vc.name);
        });
    };
    //可以通过静态分析或者Product的Profile也可以分析
    self.block1(self);
```

## Block对外部变量的存取管理

### 1、局部变量

#### 1、基本数据类型

Block会copy该局部变量的值，不允许修改。所以即使变量的值在Block外改变，也不影响他在Block中的值。

```objective-c
int a = 100;
void(^block)() = ^{
    NSLog(@"%d",a);//打印100
	//a = 300;//编译会报错
};
a = 200;
block();
```

block内部修改外界变量的值直接报错，如果想要修改，可以在int a = 0前面加上关键字__block，此时i等效于全局变量或静态变量

```objective-c
__block int b = 0;   
void (^block2) () = ^ {
    NSLog(@"b = %d",b); // 输出结果 b = 0;
    b = 2;
};
block2();
NSLog(@"b = %d",b); //输出结果 b = 2;
```

#### 2、指针类型

block会copy一份指针并强引用指针所指对象，不能修改指针的指向，但是可以修改指针所指向对象的值。

```objective-c
NSMutableString *str = @"abc".mutableCopy; 
 void (^block4) () = ^ { 
//    str = @"def"; 报错
  [str appendString:@"def"];
  NSLog(@"str = %@",str);
};
str = @"123".mutableCopy;
block4(); //输出结果为 "adbdef"
```

### 2、全局变量

1、static修饰符的全局变量，静态变量，或者全局属性

全局变量或静态变量在内存中的地址是固定的，Block在读取该变量值的时候是直接从其所在内存读出，获取到的是最新值，而不是在定义时copy的常量。

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
NSLog(@"%d",self.num);	//输出结果为 3
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

### 修改外部变量

- 默认 Block 捕获的外部变量是值拷贝（不能修改）。
- 使用 `__block` 修饰的变量会被包装成对象`__Block_byref_xxx`，拷贝到堆区，从而可以在 Block 内部修改。

## block底层原理分析

进入该文件目录下：` clang -rewrite-objc 文件名.c -o 文件名.cpp`，编译成C++。

### 捕获变量

捕获对象 如何保存和释放 keep-dispose

#### 1、不加__block

```objective-c
int main1(){
    //如果要修改a的值 要在前面加__block
    __block int a = 10;
    void(^block)(void) = ^{
        a++;//如果int a不加__block修饰，但是在里面修改a的值，但是里面的a和外面的a不是同一个a，所以就会代码歧义，报错。加了__block就是指针拷贝。同一内存空间。
        printf("Hello hh - %d",a);
    };
    
    block();
    return 0;
}
```

```c++
int main1(){
     int a = 10;
     //首先去除类型转换的代码
     //__main1_block_impl_0 函数
     //参数1：block的实现函数__main1_block_func_0
     //参数2：__main1_block_desc_0_DATA
     //参数3：a
     void(*block)(void) = (__main1_block_impl_0(__main1_block_func_0, &__main1_block_desc_0_DATA, a));
     //去除类型强转 下面一行可以简写：block->FuncPtr(block)
     ((void (*)(__block_impl *))((__block_impl *)block)->FuncPtr)((__block_impl *)block);
     return 0;
 }
 
 //第一个参数__main1_block_func_0就是下面的方法，里面就是block里面的代码 所以block能够保存代码。
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

block捕获外界变量，把变量的值传了进去，编译的时候**block底层会生成了一个新的同名成员变量。**。

#### 2、__block

**`__block`不能修饰静态变量和全局变量，因为存在全局区。**

⽤`__block`修饰的变量在编译过后会变成` __Block_byref__XXX`类型的结构体，在结构体内部有⼀个`__forwarding` 的结构体指针，指向结构体本身。

block创建的时候是在栈上的，在将栈block拷⻉到堆上的时候，同时也会将block中捕获的对象拷⻉到堆上，然后就会将栈上的`__block`修饰对象的`__forwarding`指针指向堆上的拷⻉之后的对象。

这样在block内部修改的时候虽然是修改堆上的对象的值，但是因为栈上的对象的`__forwarding`指针将堆和栈的对象链接起来。因此就可以达到修改的⽬的。

```c++
 int main1() {
     //__block修饰的变量
     //先声明一个a 的结构体，对a赋值。结构体a有了外部int a的值和地址空间。
     //对结构体赋值 初始化
     //int a在栈，结构体a在堆区。
     //结构体初始化
     __Block_byref_a_0 a = { //假象 拷贝到堆
         (void*)0,
         (__Block_byref_a_0 *)&a, //地址空间 取a的地址
         0,
         sizeof(__Block_byref_a_0),
         10//a的值
    };
     
     void(*block)(void) = ((void (*)())&__main1_block_impl_0((void *)__main1_block_func_0, &__main1_block_desc_0_DATA, (__Block_byref_a_0 *)&a, 570425344));//数字570425344是一个flag
     
     ((void (*)(__block_impl *))((__block_impl *)block)->FuncPtr)((__block_impl *)block);
     return 0;
 }
 
 //__Block_byref_a_0是一个结构体
 struct __Block_byref_a_0 {
   void *__isa;
   __Block_byref_a_0 *__forwarding;//__forwarding指针指向结构体本身（栈或堆上的副本）
   int __flags;
   int __size;
   int a; // 原始变量
 };

static void __main1_block_func_0(struct __main1_block_impl_0 *__cself) {
	__Block_byref_a_0 *a = __cself->a; // bound by ref  指针拷贝 指向同一个内存空间
    printf("Hello hh - %d",(a->__forwarding->a));
}
```

- 通过 `__forwarding` 指针保证无论变量在栈还是堆上，都能正确访问。

### block是struct

```c++
//__block_impl结构体
struct __block_impl {
  void *isa;	//指向 Block 的类型（全局/栈/堆）
  int Flags;	//枚举类型
  int Reserved;
  void *FuncPtr;// Block 的函数指针
}; 

//没有用__block修饰a
//a的值传到了__main1_block_impl_0里面
struct __main1_block_impl_0 {
  struct __block_impl impl;
  struct __main1_block_desc_0* Desc;
  int a; //捕获的外部变量a，栈block可以捕获外部变量。
  //结构体的构造函数
  //void *fp就是第一个参数，fp是一个函数
  __main1_block_impl_0(void *fp, struct __main1_block_desc_0 *desc, int _a, int flags=0) : a(_a) {
    impl.isa = &_NSConcreteStackBlock;//block在创建的时候是一个StackBlock
    impl.Flags = flags;
    impl.FuncPtr = fp; //编程思想：函数式。先保存，在block调用的时候执行。
    Desc = desc;
  }
};

//用__block修饰a
struct __main1_block_impl_0 {
  struct __block_impl impl;
  struct __main1_block_desc_0* Desc;
  __Block_byref_a_0 *a; // byref 用__block修饰
   //结构体的构造函数
  __main1_block_impl_0(void *fp, struct __main1_block_desc_0 *desc, __Block_byref_a_0 *_a, int flags=0) : a(_a->__forwarding) {
    impl.isa = &_NSConcreteStackBlock;
    impl.Flags = flags;
    impl.FuncPtr = fp;//保存block函数实现
    Desc = desc;
  }
};
```

在 Block 的底层实现中，`__Block_byref_xxx` 是一个自动生成的结构体名称，`byref` 是 **by reference** 的缩写，表示这个结构体用于实现**通过引用去捕获变量**的机制。

## block底层copy处理

block copy 从栈copy到堆

通过汇编 查看 block走到了objc_retainBlock。

注：使用`__weak`修饰的时候，不会调用`objc_retainBlock`。

### objc_retainBlock

```c++
id objc_retainBlock(id x) {
    return (id)_Block_copy(x);
}
```

### _Block_copy

_Block_copy在lib system_blocks.dylib库libclosure-master

```c++
// 重点提示: 这里是核心重点 block的拷贝操作: stack栈Block -> malloc堆Block
// 如果原来就在堆上，将引用计数加 1，返回 block 本身;
// 如果 block 在全局区，不加引用计数，也不拷贝，返回 block 本身
// 如果原来在栈上：
  // 1.malloc在堆上开辟内存
  // 2.memmove会拷贝到堆上
  // 3.引用计数初始化为 1
  // 4.调用 copy helper 方法（如果存在的话）；
  // 5.isa标记堆block
// 参数 arg 就是 Block_layout 对象，
// 返回值是拷贝后的 block 的地址
void *_Block_copy(const void *arg) {
    struct Block_layout *aBlock;

    // 如果 arg 为 NULL，直接返回 NULL
    if (!arg) return NULL;
    
    // 强转为 Block_layout 类型
    aBlock = (struct Block_layout *)arg;
    const char *signature = _Block_descriptor_3(aBlock)->signature;
    
    // 如果现在已经在堆上
    if (aBlock->flags & BLOCK_NEEDS_FREE) {
        // latches on high
        // 就只将引用计数加 1
        latching_incr_int(&aBlock->flags);
        return aBlock;
    }
    // 如果 block 在全局区，直接返回 block 本身
    else if (aBlock->flags & BLOCK_IS_GLOBAL) {
        return aBlock;
    }
    else {//编译期：栈block，现在需要将其拷贝到堆上
        // 在堆上重新开辟一块和 aBlock 相同大小的内存
        struct Block_layout *result =
            (struct Block_layout *)malloc(aBlock->descriptor->size);
        // 开辟失败，返回 NULL
        if (!result) return NULL;
        // 将 aBlock 内存上的数据全部复制新开辟的 result 上
        memmove(result, aBlock, aBlock->descriptor->size); // bitcopy first
#if __has_feature(ptrauth_calls)
        // Resign the invoke pointer as it uses address authentication.
        result->invoke = aBlock->invoke;
#endif
        // reset refcount
        // 将 flags 中的 BLOCK_REFCOUNT_MASK 和 BLOCK_DEALLOCATING 部分的位全部清为 0
        result->flags &= ~(BLOCK_REFCOUNT_MASK|BLOCK_DEALLOCATING);    // XXX not needed
        // 将 result 标记位在堆上，需要手动释放；并且引用计数初始化为 1
        result->flags |= BLOCK_NEEDS_FREE | 2;  // logical refcount 1
      
      	//操作成员变量
        // copy 方法中会调用做拷贝成员变量的工作
        _Block_call_copy_helper(result, aBlock);
      
        // 最后设置 isa 指向 _NSConcreteMallocBlock
        result->isa = _NSConcreteMallocBlock;//isa标记堆block
        return result;
    }
}
```

### _Block_call_copy_helper

对成员变量拷贝，浅拷贝。

```c++
// 调用 block 的 copy helper 方法，即 Block_descriptor_2 中的 copy 方法
static void _Block_call_copy_helper(void *result, struct Block_layout *aBlock)
{
    // 取得 block 中的 Block_descriptor_2
    struct Block_descriptor_2 *desc = _Block_descriptor_2(aBlock);
    // 如果没有 Block_descriptor_2，就直接返回
    if (!desc) return;

    // 调用 desc 中的 copy 方法，copy 方法中会调用 _Block_object_assign 函数
    (*desc->copy)(result, aBlock); // do fixup
}
```

### _Block_object_assign

`_Block_object_assign` 在 Block 被复制到堆时调用，用于处理 Block 捕获的各种类型变量的内存管理。例 是否有加__block

```c++
// 注释: Block 捕获外界变量的操作
// 当 block 和 byref 要持有对象时，它们的 copy helper 函数会调用这个函数来完成 assignment，
// destArg: 二级指针，指向要赋值的真正的目标指针位置
// object: 要处理的被捕获对象
// flags: 标志位，表示对象的类型和内存管理方式
void _Block_object_assign(void *destArg, const void *object, const int flags) {
    const void **dest = (const void **)destArg;
    switch (os_assumes(flags & BLOCK_ALL_COPY_DISPOSE_FLAGS)) {
      case BLOCK_FIELD_IS_OBJECT:	// 捕获的对象
        /*******
        id object = ...;
        [^{ object; } copy];
        ********/
        // 默认什么都不干，但在 _Block_use_RR() 中会被 Objc runtime 或者 CoreFoundation 设置 retain 函数，
        // 其中，可能会与 runtime 建立联系，操作对象的引用计数什么的
        // 增加引用计数（在启用ARC时可能为空操作）
        _Block_retain_object(object);
        // 使 dest 指向的目标指针指向 object，浅拷贝
        *dest = object;
        break;

      case BLOCK_FIELD_IS_BLOCK:	// 捕获的Block
        /*******
        void (^object)(void) = ...;
        [^{ object; } copy];
        ********/

        // 使 dest 指向的拷贝到堆上object
        *dest = _Block_copy(object);
        break;
    
      case BLOCK_FIELD_IS_BYREF | BLOCK_FIELD_IS_WEAK:// 弱引用 __block 变量
      case BLOCK_FIELD_IS_BYREF:
        /*******
         // copy the onstack __block container to the heap
         // Note this __weak is old GC-weak/MRC-unretained.
         // ARC-style __weak is handled by the copy helper directly.
         __block ... x;
         __weak __block ... x;
         [^{ x; } copy];
         ********/
         // 使 dest 指向的拷贝到堆上的byref
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

        // 使 dest 指向的目标指针指向 object
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

        // 使 dest 指向的目标指针指向 object
        *dest = object;
        break;

      default:
        break;
    }
}
```

### _Block_byref_copy

__block修饰的（除了对象和block）会走`_Block_byref_copy`

```c++
// 注释: __Block 捕获外界变量的操作 内存拷贝 以及常规处理
// 1. 如果 byref 原来在栈上，就将其拷贝到堆上，拷贝的包括 Block_byref、Block_byref_2、Block_byref_3，
//    被 __weak 修饰的 byref 会被修改 isa 为 _NSConcreteWeakBlockVariable，
//    原来 byref 的 forwarding 也会指向堆上的 byref;
// 2. 如果 byref 已经在堆上，就只增加一个引用计数。
// 参数 dest是一个二级指针，指向了目标指针，最终，目标指针会指向堆上的 byref
static struct Block_byref *_Block_byref_copy(const void *arg) {
    // arg 强转为 Block_byref * 类型
    struct Block_byref *src = (struct Block_byref *)arg;

    // 判断条件：引用计数为 0，说明变量在栈上。栈上变量 -> 堆上拷贝
    if ((src->forwarding->flags & BLOCK_REFCOUNT_MASK) == 0) {
        // 为新的 byref 在堆中分配内存
        struct Block_byref *copy = (struct Block_byref *)malloc(src->size);
        copy->isa = NULL;
      
      	// 新的 byref 设置标志flags：
      	 // BLOCK_BYREF_NEEDS_FREE: 标记需要释放（即标识堆上）
      	 // 4: 设置引用计数为 2（实际是 2，因为低2位是标志位）
        // byref value 4 is logical refcount of 2: one for caller, one for stack
        // 为什么是 2 呢？注释说的是 non-GC one for caller, one for stack
        // one for caller 很好理解，那 one for stack 是为什么呢？
        // 看下面的代码中有一行 src->forwarding = copy。src 的 forwarding 也指向了 copy，相当于引用了 copy
        copy->flags = src->flags | BLOCK_BYREF_NEEDS_FREE | 4;
      
      	//更新 forwarding 指针：
        // 堆上 byref 的 forwarding 指向自己
        copy->forwarding = copy; // patch heap copy to point to itself
        // 原来栈上的 byref 的 forwarding 现在也指向堆上的 byref
        src->forwarding = copy;  // patch stack to point to heap copy
        // 拷贝 size
        copy->size = src->size;

      	// 处理辅助函数
      	// 如果 src 变量有自定义的 copy/dispose helper 函数（如对象类型），调用 byref_keep 来执行特定的内存管理
      	// 展布局信息（用于 ARC 弱引用等）
        if (src->flags & BLOCK_BYREF_HAS_COPY_DISPOSE) {
            // Trust copy helper to copy everything of interest
            // If more than one field shows up in a byref block this is wrong XXX
            // 取得 src 和 copy 的 Block_byref_2
            struct Block_byref_2 *src2 = (struct Block_byref_2 *)(src+1);
            struct Block_byref_2 *copy2 = (struct Block_byref_2 *)(copy+1);
            // copy 的 copy/dispose helper 也与 src 保持一致
            // 因为是函数指针，估计也不是在栈上，所以不用担心被销毁
            copy2->byref_keep = src2->byref_keep;
            copy2->byref_destroy = src2->byref_destroy;

            // 如果 src 有扩展布局，也拷贝扩展布局
            if (src->flags & BLOCK_BYREF_LAYOUT_EXTENDED) {
                struct Block_byref_3 *src3 = (struct Block_byref_3 *)(src2+1);
                struct Block_byref_3 *copy3 = (struct Block_byref_3*)(copy2+1);
                // 没有将 layout 字符串拷贝到堆上，是因为它是 const 常量，不在栈上
                copy3->layout = src3->layout;
            }
          	
            // 调用 copy helper，因为 src 和 copy 的 copy helper 是一样的，所以用谁的都行，调用的都是同一个函数
          	//捕获到了外界变量 进行相关内存处理 生命周期的保存
            (*src2->byref_keep)(copy, src);
        }
        else {
            // Bitwise copy.
            // This copy includes Block_byref_3, if any.
            // 如果 src 没有 copy/dispose helper
            // 将 Block_byref 后面的数据都拷贝到 copy 中，一定包括 Block_byref_3
            memmove(copy+1, src+1, src->size - sizeof(*src));
        }
    }
  
    // src 已经在堆上，就只将引用计数加 1
    else if ((src->forwarding->flags & BLOCK_BYREF_NEEDS_FREE) == BLOCK_BYREF_NEEDS_FREE) {
        latching_incr_int(&src->forwarding->flags);
    }
    
    return src->forwarding;
}
```

block不能修改外部变量指针地址。

#### 内存布局示例

```tex
栈上的 Block_byref:
[ flags | forwarding | size | data... ]
          ↓
堆上的 Block_byref copy:
[ flags | forwarding | size | data... ]
          ↑
```

#### 实际使用场景

```objc
// 示例代码
__block int counter = 0;
__block NSObject *obj = [[NSObject alloc] init];

void (^myBlock)(void) = ^{
    counter++;  // 修改 __block 变量
    NSLog(@"%@", obj);
};

// 当 Block 被复制到堆时，_Block_byref_copy 会被调用
// 确保 counter 和 obj 在栈帧销毁后仍然有效
```

#### __block修饰变量的关键点

1. **forwarding 指针**：保证无论访问栈还是堆上的变量，最终都访问堆上的结构体。
2. **延迟复制**：block创建的时候在栈上，只在 Block 被拷贝到堆时才触发将变量一起拷贝到堆。
3. **引用计数管理**：堆上的 byref 有独立引用计数
4. **类型支持**：通过 copy/dispose 函数支持 Objective-C 对象等复杂类型

这是 Block 实现的重要部分，实现了 `__block` 变量的自动内存管理。

## block结构

block本质是Block_layout结构体

block其实是一个对象，需要一个初始化过程。

```c++
//block在底层 结构体
struct Block_layout {
  
    void *isa; //isa指向（栈block、堆block、全局block），有isa说明block也是一个对象
  
    /**
    Flags 枚举类型
      BLOCK_HAS_COPY_DISPOSE：捕获外界变量的时候 这个是有值的。
      BLOCK_HAS_SIGNATURE：签名
      方法有签名v@: 普通签名
        v 返回值
        @ 对象
        : cmd方法编号  
      block也有签名信息
    */
  	//存储block附加信息
    volatile int32_t flags; // contains ref count//标识符 存数据信息，是否正在析构、是否有keep函数、是否有析构函数、等等
  
    int32_t reserved;//保留的变量（暂时不用）
  
    BlockInvokeFunction invoke;//block实现的函数指针
  
    // block其它描述信息：存储copy、dispose函数、block大小、block描述信息、捕获外界信息、block方法签名
    struct Block_descriptor_1 *descriptor;
    //连续的内存空间
    // imported variables  //还有可选变量
};
```

### Block_descriptor_1

```c++
#define BLOCK_DESCRIPTOR_1 1
struct Block_descriptor_1 {
    uintptr_t reserved;         // 保留字段，通常为0
    uintptr_t size;             // Block 的总大小（包括所有部分），用于内存分配和释放
};
```

### Block_descriptor_2 

```c++
//捕获int变量时，没有copy和dispose。捕获对象才有。
//copy和dispose函数是⽤来对block内部的对象进⾏内存管理的，block拷⻉到堆上会调⽤copy函数，在block从堆上释放的时候会调⽤dispose函数。
//内存平移Block_descriptor_1大小就得到Block_descriptor_2
#define BLOCK_DESCRIPTOR_2 1
struct Block_descriptor_2 {
    // requires BLOCK_HAS_COPY_DISPOSE
    BlockCopyFunction copy;		    //当 Block 被复制到堆时调用，处理捕获变量的内存管理
    BlockDisposeFunction dispose;	//当 Block 从堆中释放时调用，清理捕获的资源
};
```

**何时存在？**
当 Block 捕获了需要特殊内存管理的对象时：

- Objective-C 对象（MRC 下）
- 其他 Block
- `__block` 变量
- C++ 对象等

**示例代码**

```c++
// 捕获 NSString 对象
NSString *str = @"Hello";
void (^block)(void) = ^{
    NSLog(@"%@", str);  // 需要管理 str 的内存
};

// 编译器生成的描述符
static void __main_block_copy_0(struct __main_block_impl_0 *dst, 
                               struct __main_block_impl_0 *src) {
    // 处理 str 的 retain
    _Block_object_assign(&dst->str, src->str, BLOCK_FIELD_IS_OBJECT);
}

static void __main_block_dispose_0(struct __main_block_impl_0 *src) {
    // 处理 str 的 release
    _Block_object_dispose(src->str, BLOCK_FIELD_IS_OBJECT);
}

// Descriptor2
static struct __main_block_desc_0 {
    size_t reserved;
    size_t Block_size;
    void (*copy)(struct __main_block_impl_0*, struct __main_block_impl_0*);
    void (*dispose)(struct __main_block_impl_0*);
} __main_block_desc_0_DATA = {
    0,
    sizeof(struct __main_block_impl_0),
    __main_block_copy_0,
    __main_block_dispose_0
};
```

### Block_descriptor_3

```c++
#define BLOCK_DESCRIPTOR_3 1
struct Block_descriptor_3 {
    // requires BLOCK_HAS_SIGNATURE
    const char *signature;  // Block 的方法签名（类型编码），包含参数和返回值类型
    const char *layout;     // contents depend on BLOCK_HAS_EXTENDED_LAYOUT
};
// hook：invoke消息 消息机制 转发需要先获取签名 然后invocation处理
```

**何时存在？**
当需要额外的运行时信息时：

- 有方法签名需求（如用 Block 实现 delegate）
- 捕获了弱引用对象
- 复杂的捕获变量布局

#### 示例：Block 类型编码

```c
// Block: int (^)(int, NSString *)
signature = "i32@?0i8@\"NSString\"16"

// 解析：
// i32     - 返回值 int (32位)
// @?      - 这是一个 Block 类型，block签名是 @?
// 0       - 从偏移 0 开始
// i8      - 第一个参数 int
// @"NSString"16 - 第二个参数 NSString*，从偏移16开始
```

### 实际使用场景：

### 场景1：无捕获

```objective-c
void (^block)(void) = ^{ NSLog(@"Hello"); };
// 只需要 Descriptor1（size）
```

### 场景2：捕获对象

```objective-c
NSObject *obj = [[NSObject alloc] init];
void (^block)(void) = ^{ NSLog(@"%@", obj); };
// 需要 Descriptor1 + Descriptor2（copy/dispose）
```

### 场景3：捕获弱引用

```objective-c
__weak NSObject *weakObj = obj;
void (^block)(void) = ^{ NSLog(@"%@", weakObj); };
// 需要 Descriptor1 + Descriptor2 + Descriptor3（layout）
```

### 场景4：有类型签名的 Block

```objective-c
int (^block)(int, int) = ^int(int a, int b) { return a + b; };
// 需要 Descriptor1 + Descriptor3（signature）
```

### 捕获变量

三层拷贝：

1. _Block_copy栈block拷贝到堆block
2. block捕获Block_byref_ 对Block_byref_进行copy
3. Block_byref对object进行copy
