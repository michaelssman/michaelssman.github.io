# 模版化的指针

模版要求所有的代码都放在头文件里，不能在源文件里写。

头文件代码：

```c++
namespace ThinkingInCppDemoLib {
template<class T, int incr = 10>//stash存储空间不够的时候，每次增大incr10，定义一个常量，默认10.
class PStash
{
private:
    int quantity;
    int next;
    T** storage;
    void inFlate(int increase = incr);//增大默认的大小
public:
    PStash() : quantity(0),next(0),storage(0){}
    
    int add(T* element);
    
    T* operator[](int index) const;//下标操作
    
    T* remove(int index);
    
    int count()
    {
        return next;
    }
    
    ~PStash();
};
template<class T,int incr>
int PStash<T,incr>::add(T* element)
{
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
        delete storage[i];
        storage[i] = 0;//指针变成空指针
    }
    delete [] storage;
}

template<class T,int incr>
T* PStash<T,incr>::remove(int index)
{
    T* v = operator[](index);
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

template<class T,int incr>
void PStash<T,incr>::inFlate(int increase)
{
    assert(increase >= 0);
    const int psz = sizeof(T*);
    T** st = new T*[quantity + increase];
    memset(st,0,(quantity + increase)*psz);
    memcpy(st,storage,quantity*psz);
    quantity += increase;
    
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

