# stash创建库

做成库使用起来方便

把上面的Stash的源文件头文件做成一个库。

源文件：.h .cpp 两个文件 做成库：.h .lib .dll三个文件。

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

源文件不需要修改。和之前一样。

使用的时候，创建常规项目，然后把.h .lib .dll拖进项目中。

然后去使用。使用的时候导入头文件。

```c++
#pragma comment(lib,"lib文件位置") //编译时候要用
```

要把库的dll文件放到Debug文件，和exe放到一个文件中。





