# Stash

stash是存储，储藏，储存。

CStash是用C语言做的。使用struct结构做出来的。

利用Stash可以储存各种各样的数据，可以存整型，字符串，浮点型。

存储的数据可多可少，指针动态分配内存。

```c++
// C语言的Stash
typedef struct CStashTag
{
    int size;// 每一个是多大。存字符串的话就是最多的存多少字符。
    int quantity;// 数量。一共可以保存多少个。
    int next;// 已经保存了多少个。
    unsigned char* storage;// 指针
}CStash;
// 一些操作
void initialize(CStash* s,int size);
void cleanup(CStash* s);
void inflate(CStash* s,int increase);
void* fetch(CStash* s,int index);
int add(CStash* s,const void* element);
int count(CStash* s);
// 扩大内存
void inflate(CStash* s, int increase);
```

下面是函数的定义

```c++
// 一些操作
// 初始化，每个数据是多大size
void initialize(CStash* s,int sz)
{
    s->size = sz;
    // 开始的时候没有数据 下面的参数都是0
    s->quantity = 0;
    s->next = 0;
    s->storage = 0;
}

const int increment = 100;
// 扩大内存
void inflate(CStash* s, int increase)
{
    //加断言 必须大于0
    assert(increase > 0);
    //分配新的大一点的内存，然后把数据拷贝放到新的内存里。
    int newQuantity = s->quantity + increase; // 这是增大多少个
    int newBytes = newQuantity * s-> size;//这是增大多少子节
    int oldBytes = s->quantity * s->size;//原来的大小
    unsigned char* b = (unsigned char*)malloc(newBytes);//分配新内存
    //把旧数据 复制新分配的内存过来
    for (int i = 0; i < oldBytes; i++) {
        b[i] = s->storage[i];
    }
    //释放就内存
    free(s->storage);
    s->storage = b;
    s->quantity = newQuantity;
}
// 往里面放数据,做成通用的，可能是int 可能是字符串，所以是void*
int add(CStash* s,const void* element)
{
    // 如果有c足够的位置就添加，没有就扩大内存。
    if (s->next >= s->quantity) {
        // 扩大内存
        inflate(s, increment);
    }
    int startBytes = s->next * s->size;
    //element 要保存的数据，可能是各种类型，都转变为字符指针。
    unsigned char *e = (unsigned char*)element;
    for (int i = 0; i < s->size; i++) {
        s->storage[startBytes + i] = e[i];
    }
    s->next++;
    //返回添加的数据所在的位置
    return (s->next - 1);
}

//计算数据有多少个
int count(CStash* s)
{
    return s->next;
}

// 取出某个数 得到是一个指针
void* fetch(CStash* s,int index)
{
    //加断言
    assert(0 <= index);
    if (index >= s->next) {
        return 0;//取完了。没数据了。
    }
    return &(s->storage[index * s->size]);
}

//清除
void cleanup(CStash* s)
{
    //释放内存 内存可以被使用 防止内存泄漏
    if (s->storage != 0) {
        free(s->storage);
    }
}
```

调用：

```c++
void test()
{
    CStash intStash, stringStash;
    const int bufsize = 80;
    // 把地址传进去
    initialize(&intStash, sizeof(int));
    for (int i = 0; i < 150; i++) {
        add(&intStash, &i);//放的都是地址
    }
    for (int i = 0; i < count(&intStash); i++) {
        std::cout << *(int *)fetch(&intStash, i) << std::endl;
    }
    cleanup(&intStash);
    
    initialize(&stringStash, bufsize * sizeof(char));//每个最多保存80个字符
}
```

C语言 CStash 不是对象 只是结构
C++ Stash 是对象

C++ 函数可以放到结构里，C语言函数不能放到结构里

C语言结构define C++不需要define 直接struct

C++不需要传自己  默认会传 隐式的操作
成员函数 成员变量

C语言free  C++ delete

对象可以`.`    通过对象`.`点出来  成员函数 
向对象发送消息  对象调用对象的成员函数

C++的结构和C语言的结构不一样
C++的结构又叫class
C++的类class和结构struct差不多，public 共有私有不同 其他的一样

抽象数据类型 （用户定义类型）和其他类型一样 

## stash创建库

做成库使用起来方便

把上面的Stash的源文件头文件做成一个库。

源文件：.h .cpp 两个文件 

做成库：.h .lib .dll三个文件。

库

1. 动态链接库 动态库
2. 静态链接库 静态库

做一个库需要头文件源文件。如果库比较复杂就需要很多头文件源文件。

创建项目要创建库项目，不是常规的项目。

头文件 需要把函数 导出`__declspec(dllexport)`。不然就是库内部的函数，外界不能使用。

```c++
// C语言的Stash
typedef struct CStashTag
{
    int size;// 每一个是多大。存字符串的话就是最多的存多少字符。
    int quantity;// 数量。一共可以保存多少个。
    int next;// 已经保存了多少个。
    unsigned char* storage;// 指针
}CStash;
// 一些操作
//__declspec(dllexport) void initialize(CStash* s,int size);
__declspec(dllexport) void cleanup(CStash* s);
__declspec(dllexport) void inflate(CStash* s,int increase);
__declspec(dllexport) void* fetch(CStash* s,int index);
__declspec(dllexport) int add(CStash* s,const void* element);
__declspec(dllexport) int count(CStash* s);
// 扩大内存
__declspec(dllexport) void inflate(CStash* s, int increase);
```

源文件不需要修改，和之前一样。

使用的时候，创建常规项目，然后把.h .lib .dll拖进项目中。

然后去使用。使用的时候导入头文件。

```c++
#pragma comment(lib,"lib文件位置") //编译时候要用
```

要把库的dll文件放到Debug文件，和exe放到一个文件中。

