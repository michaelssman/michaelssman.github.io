# Stash

之前是用C语言做的CStash，用C语言做的有缺点。

用C++语言做一遍CStash，这样就可以克服C语言的缺点。

C++做的Stash是面向对象，C语言做的CStash是面向过程。

C++的结构对C语言的结构进行了改进和增强。也有简化：C语言的结构有typedef，C++不需要。

C++函数可以放到结构里，函数可以简化，第一个参赛可以不写，C++ 回自动的传递给每一个函数。

C语言函数不能放到结构里。

C++结构体中的函数，也叫结构体的成员。变量叫结构体的数据成员。函数叫结构体的函数成员，也叫成员函数。用四个点::表示范围。

C++ 的类和C++的结构一样

```c++
// C++的Stash
struct Stash
{
    int size;// 每一个是多大。存字符串的话就是最多的存多少字符。
    int quantity;// 数量。一共可以保存多少个。
    int next;// 已经保存了多少个。
    unsigned char* storage;// 指针
    
    
    // 一些操作  C++可以放到里面
    // 函数是在结构里面的，所以函数定义的时候要写 结构名加::
    // 这些函数也叫 这个结构的成员
    void initialize(int size);
    void cleanup();
    void* fetch(int index);
    int add(const void* element);
    int count();
    // 扩大内存
    void inflate(int increase);
};
// 一些操作
// 初始化，每个数据是多大size
void Stash::initialize(int sz)
{
    size = sz;
    // 也可以写成
//    this->size = sz; //this 代表当前对象
    // 开始的时候没有数据 下面的参数都是0
    quantity = 0;
    next = 0;
    storage = 0;
}

const int increment = 100;
// 扩大内存
void Stash::inflate(int increase)
{
    //加断言 必须大于0
    assert(increase > 0);
    //分配新的大一点的内存，然后把数据拷贝放到新的内存里。
    int newQuantity = quantity + increase; // 这是增大多少个
    int newBytes = newQuantity * size;//这是增大多少子节
    int oldBytes = quantity * size;//原来的大小
//    unsigned char* b = (unsigned char*)malloc(newBytes);//分配新内存 C语言的 C++使用new
    unsigned char* b = new unsigned char(newBytes);
    //把旧数据 复制新分配的内存过来
    for (int i = 0; i < oldBytes; i++) {
        b[i] = storage[i];
    }
    //释放就内存
//    free(storage);//C语言
    delete[] storage;//C++
    storage = b;
    quantity = newQuantity;
}
// 往里面放数据,做成通用的，可能是int 可能是字符串，所以是void*
int Stash::add(const void* element)
{
    // 如果有c足够的位置就添加，没有就扩大内存。
    if (next >= quantity) {
        // 扩大内存
        inflate(increment);
    }
    int startBytes = next * size;
    //element 要保存的数据，可能是各种类型，都转变为字符指针。
    unsigned char *e = (unsigned char*)element;
    for (int i = 0; i < size; i++) {
        storage[startBytes + i] = e[i];
    }
    next++;
    //返回添加的数据所在的位置
    return (next - 1);
}

//计算数据有多少个
int Stash::count()
{
    return next;
}

// 取出某个数 得到是一个指针
void* Stash::fetch(int index)
{
    //加断言
    assert(0 <= index);
    if (index >= next) {
        return 0;//取完了。没数据了。
    }
    return &(storage[index * size]);
}

//清除
void Stash::cleanup()
{
    //释放内存 内存可以被使用 防止内存泄漏
    if (storage != 0) {
        delete[] storage;
    }
}
```

调用：

```c++
void test()
{
    Stash intStash, stringStash;
    const int bufsize = 80;
    intStash.initialize(sizeof(int));
    for (int i = 0; i < 150; i++) {
        intStash.add(&i);//放的都是地址
    }
    for (int i = 0; i < intStash.count(); i++) {
        std::cout << *(int *)intStash.fetch(i) << std::endl;
    }
    intStash.cleanup();
    
    stringStash.initialize(bufsize * sizeof(char));//每个最多保存80个字符
}
```

C语言的结构里面不能放函数。

C++的结构里可以放函数（成员函数）。这种结构也叫抽象类型，用户定义类型。

通过对象，**向对象发送消息**，调用成员函数。这就是C++面向对象。

C++的struct中的成员默认是共有的，class中的成员默认是私有的