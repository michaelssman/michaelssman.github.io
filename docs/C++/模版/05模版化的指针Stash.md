# 模版化的指针

模版要求所有的代码都放在头文件里，不能在源文件里写。

头文件代码：

```c++
namespace ThinkingInCppDemoLib {
template<class T, int incr = 10>//stash存储空间不够的时候，每次增大incr10，定义一个常量，默认10.
class PStash
{
private:
    int quantity;	// 数量。一共可以保存多少个。
    int next;			// 已经保存了多少个。
    T** storage;	//通过指针 在堆上动态的创建对象，分配内存。可以是整型数据，字符串数据等各种类型。普通的stach有size大小，指针的stach没有size，因为是T* 大小是一个指针的大小。
    void inFlate(int increase = incr);//增大默认的大小
public:
    PStash() : quantity(0),next(0),storage(0){}
    
    int add(T* element);
    
    T* operator[](int index) const;//下标操作
    
    T* remove(int index);//使用remove移除。因为里面有T*，delete的时候 可能不走析构函数
    
    int count()
    {
        return next;
    }
    
    ~PStash();
};
template<class T,int incr>
int PStash<T,incr>::add(T* element)
{
	  //add先判断大小。不够了需要重新分配内存。增大内存。
    if (next >= quantity) {
        inFlate(incr);
    }
    storage[next++] = element;
    return (next - 1);
}

template<class T,int incr>
PStash<T,incr>::~PStash()
{
    for (int i = 0; i < next; i++) {
        delete storage[i];//delete由客户端去delete，谁使用谁delete。因为析构函数中delete T*有问题。
        storage[i] = 0;//指针变成空指针
    }
    delete [] storage;
}

//客户端可以使用remove，通过operator拿到指定下标的指针然后进行delete。
template<class T,int incr>
T* PStash<T,incr>::remove(int index)
{
    T* v = operator[](index);
	  //把指针返回并且清零。客户端拿到指针，进行delete。
    if (v != 0) {
        storage[index] = 0;
    }
    return v;
}

//下标运算符重载
template<class T,int incr>
T* PStash<T,incr>::operator[](int index) const
{
    //先检查下标index>=0，不能小于0
    if (index >= next) {
        return 0;
    }
    //return必须是有效的指针，不能是0
    return storage[index];
}
//追加内存的方法
template<class T,int incr>
void PStash<T,incr>::inFlate(int increase)
{
    assert(increase >= 0);
    const int psz = sizeof(T*);
    T** st = new T*[quantity + increase];
    memset(st,0,(quantity + increase)*psz);
  	//把原来的数据copy到新的内存里。
    memcpy(st,storage,quantity*psz);
    quantity += increase;
    //原来的内存空间删除。
    delete [] storage;
    storage = st;
}
}
```

调试：

```c++
void test() {
    ThinkingInCppDemoLib::PStash<int> intStash;
    for (int i = 0; i < 25; i++) {
        intStash.add(new int(i));
    }
    for (int i = 0; i < intStash.count(); i++) {
        std::cout << *(int*)intStash[i] << std::endl;
    }
    for (int k = 0; k < intStash.count(); k++) {
        delete (int*)intStash.remove(k);
    }
}
```

