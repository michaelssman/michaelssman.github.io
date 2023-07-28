# isa

isa指针是一个联合体，联合体里面有一个结构体ISA_BITFIELD。

```c++
union isa_t {
    //两个构造方法
    isa_t() { }
    isa_t(uintptr_t value) : bits(value) { }

    uintptr_t bits;

private:
    // Accessing the class requires custom ptrauth operations, so
    // force clients to go through setClass/getClass by making this
    // private.
    Class cls;

public:
#if defined(ISA_BITFIELD)
    struct {
        ISA_BITFIELD;  // defined in isa.h
    };

  	//标志对象是否正在释放内存。
    bool isDeallocating() {
        return extra_rc == 0 && has_sidetable_rc == 0;
    }
    void setDeallocating() {
        extra_rc = 0;
        has_sidetable_rc = 0;
    }
#endif

    void setClass(Class cls, objc_object *obj);
    Class getClass(bool authenticated);
    Class getDecodedClass(bool authenticated);
};
```

## ISA_BITFIELD

里面使用了位域，优化内存

```c++
#   define ISA_BITFIELD                                                        \

			//nonPointer表示是否对isa指针开启指针优化。
			//0:纯isa指针
			//1:不止是类对象地址，isa包含类信息，对象引用计数等。
			//目的：节省内存空间
			//isa是8字节，1字节8位，所以是64位，64位里面存很多东西。以前只存类对象的内存地址，但是类对象内存地址不需要这么大内存，所以就把关于对象相关的信息包括内存地址、引用计数存在isa里面。
      uintptr_t nonpointer        : 1;                                         \
        
      //关联对象标志位，0没有，1存在
      uintptr_t has_assoc         : 1;                                         \
        
      //该对象是否有C++或者Objc等析构器，如果有析构函数，则需要做析构逻辑，如果没有，则可以更快的释放对象。
      uintptr_t has_cxx_dtor      : 1;                                         \
        
      //就是类对象的内存地址，存储类指针的值。
      uintptr_t shiftcls          : 44; /*MACH_VM_MAX_ADDRESS 0x7fffffe00000*/ \
      uintptr_t magic             : 6;                                         \
        
      //标志对象是否被指向或者曾经指向一个ARC的弱变量，没有弱引用的对象可以更快释放。（是否被`__weak`修饰）
      uintptr_t weakly_referenced : 1;                                         \
      uintptr_t unused            : 1;                                         \
        
      //散列表。当引用计数大于extra_rc所能存储的最大范围时，则需要借用该变量存储进位。
      uintptr_t has_sidetable_rc  : 1;                                         \
        
      //引用计数 最多2^8-1个，超过了就要存在散列表里面
      uintptr_t extra_rc          : 8

//64位地址空间 8字节
```

通过对象的isa，

每一个类都有一个isa：存储类+其它值。

对象isa和类不一样，类的isa和元类一样。

每个类：是否正在释放 引用计数 weak 关联对象 析构函数

看位域：nonPointer

## 如何通过isa的位运算得到类对象

通过isa右移左移右移（把其它位的清零），位移的方式就可以得到类。

也可以通过isa MASK掩码得到类。

isa的class