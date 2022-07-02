# 指针的stash

### 以前的Stash

```c++
struct Stash
{
    int size;// 每一个是多大。存字符串的话就是最多的存多少字符。
    int quantity;// 数量。一共可以保存多少个。
    int next;// 已经保存了多少个。
    unsigned char* storage;// 指针
};
```

### 指针的Stash

```c++
PStash
{
    int quantity;
    int next;
    void* storage; //通过指针 在堆上动态的创建对象。
};
```

指针的stash，用void*  

通过指针 在堆上动态的创建对象，分配内存。可以是整型数据，字符串数据等各种类型。

普通的stach有size大小，指针的stach没有size，因为是void*  大小是一个指针的大小。

### .h头文件

![image-20190921121205221](assets/image-20190921121205221.png)

![image-20190921114917795](assets/image-20190921114917795.png)

使用remove移除。因为里面有void*，delete的时候 可能不走析构函数

### .m源文件

### add添加数据

![image-20190921113144947](assets/image-20190921113144947.png)

add先判断大小。不够了需要重新分配内存。增大内存。

#### 追加内存的方法：

![image-20190921114649897](assets/image-20190921114649897.png)

把原来的数据copy到新的内存里。原来的内存空间删除。

### 读取数据：

像操作数组那样根据下标读取数据

重写方法 

下标操作符重载

![image-20190921115512014](assets/image-20190921115512014.png)

### 析构函数

析构函数不能delete动态创建的对象 void*

delete由客户端去delete，谁使用谁delete。因为析构函数中delete void*有问题。

![image-20190921115350017](assets/image-20190921115350017.png)

所以做一个remove。客户端可以使用remove，通过operator拿到指定下标的指针然后进行delete。

![image-20190921115706127](assets/image-20190921115706127.png)

把指针返回并且清零。

客户端拿到指针，进行delete。

### 调用测试：

![image-20190921121503644](assets/image-20190921121503644.png)

读取文件，把文件的内容一行一行的add到stash中，然后读取出来，最后通过remove函数拿到指针，delete释放内存。

![image-20190921122003732](assets/image-20190921122003732.png)





C++还有更好的方法	使用模版代替void *



