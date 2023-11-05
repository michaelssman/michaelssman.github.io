# 模版template

C++语言模版是一个重要内容，

有两种模版：

1. 类模版
2. 函数模版

函数模版在**编译**的时候，会自动的实例化，创建不同的函数。

```c++
template <class T>
class X {
  ...
};
```

重要的是`template`关键字。

## 类模版

### 数组越界问题

C++数组不检查越界。

自己写一个class，把数组封装起来，检查不允许越界。

```c++
class Array
{
    enum {size = 10};
    int A[size];
public:
    int& operator[](int index)//index 下标，要检查是否越界  内联的函数
    {
        //对下标进行检查，下标大于等于0，小于size
        return A[index];//如果没有越界，就返回数组里的数据。
    }
};
//调试
void test() {
    Array b;
    std::cout << b[8] <<std::endl;//没越界
    std::cout << b[10] <<std::endl;//越界，会检查，然后处理
}
```

这样封装的就比C++的好一些。

但是C++类型非常多，整型，浮点型，等等。要针对每一个类型做一个数组class。比较繁琐，写很多class。代码都是重复的。

可以使用继承，但是继承会比较复杂。简单的问题复杂化了。比较好的解决办法就是模版。

```c++
//这是一个模版，模版不是一个真正的类，使用模版进行实例化，C++会创建一个类出来。
template<class T>//T是模版的替换参数，代表一个类型
class Array
{
    enum {size = 10};//枚举常量
    T A[size];
public:
    T& operator[](int index);//重载下标运算符。index：下标。要检查是否越界
//    {
//        //对下标进行检查，下标大于等于0，小于size
//        return A[index];//如果没有越界，就返回数组里的数据。
//    }
};

//函数写到类外面，比较复杂，还要写`template<class T>` 和`Array<T>::`，写到类里面是内联函数比较简单。
template<class T>
T& Array<T>::operator[](int index)//重载下标运算符。index：下标。要检查是否越界
{
    //对下标进行检查，下标大于等于0，小于size
    return A[index];//如果没有越界，就返回数组里的数据。
}

//调试
void test() {
    Array<int> ia;//当这样写的时候，C++会帮我们从上面的模版，用int把所有的T换掉。
    Array<float> fa;
    //根据需要 C++会帮我们创建不同的类。非常灵活。
    
    for (int i = 0; i < 10; i++) {
        ia[i] = i * i;
        fa[i] = float(i) * 1.414;
    }
    for (int j = 0; j<10; j++) {
        std::cout << j << ":" << ia[j] << ", " << fa[j] <<std::endl;
    }
}
```

类模版和普通的类是不一样的，做模版的时候，代码都得放到头文件中，不能在源文件。C++编译的时候会生成类，所以必须是可见的。否则没有办法编译。

## 函数模版

函数模版**实例化**函数

做一个简单的函数

做一个交换

`void swap(int &a, int &b)//传引用`，就可以交换两个int型的，但是如果要交换两个double型的就不可以，只能再写一个同名函数**重载**。

```c++
//做一个简单的函数
//做一个交换
void Swap(int &a, int &b)//传引用
{
    int temp = a;
    a = b;
    b = temp;
}
void Swap(double &a, double &b)//传引用
{
    double temp = a;
    a = b;
    b = temp;
}
```

##### 调用：

```c++
void test()
{
    int x = 10, y = 20;
    double m = 1.23, n = 9.78;
    
    Swap(x, y);
    std::cout << x << "," << y << std::endl;
    Swap(m, n);
    std::cout << m << "," << n << std::endl;
}
```

C++类型特别多，int，double，还可以定义新的类型Dog，Cat等等。

这样一个函数就要针对每一种类型都要写一个同名的函数重载，工作都是重复的。（重复是万恶之源）。不应该这样做。

可以用C++的模版，做一个函数模版。C++在**编译的时候**根据模版动态的生成需要的函数。用到哪一个C++会自动的创建哪一个。

##### 模版函数：

```c++
//模版
template<class T>
void Swap(T &a, T &b)
{
    T temp;
    temp = a;
    a = b;
    b = temp;
}
```

##### 调用

```c++
void test()
{
    int x = 10, y = 20;
    double m = 1.23, n = 9.78;
    
    Swap(x, y);
    std::cout << x << "," << y << std::endl;
    Swap(m, n);
    std::cout << m << "," << n << std::endl;
}
```

函数模版经常会用到，非常实用。

交换函数的这个模版C++已经做好了，有内置的。做好的是小写的swap。所以自己写的这个交换模版的函数名字首字母要大写。

做一些通用的函数，对各种类型，考虑用函数模版写。

C++容器算法模版。stl标准函数模版。

## 模版中的常量

模版的参数中可以使用C++内置类型（常量）。还可以设置默认值。

模版变成类的时候C++会把`int size = 10`变成常量，所以size是不可以修改的。

```c++
template<class T, int size = 100>//模版常量size
class Array
{
		//enum {size = 10};//枚举常量
    T A[size];
public:
    ...
};
```

```c++
template<class T, int size = 10>
class Array
{
    //enum {size = 10};//枚举常量
    T array[size];
public:
    T& operator[](int index);//重载下标运算符。index：下标。要检查是否越界
    int length() const { return size; }//成员函数，返回长度。
};

template<class T, int size>//这里不用写size = 1
T& Array<T, size>::operator[](int index)//重载下标运算符。index：下标。要检查是否越界
{
    //对下标进行检查，下标大于等于0，小于size
    return array[index];//如果没有越界，就返回数组里的数据。
}

//再做一个Number类 封装float
class Number
{
    float f;
public:
    //类型转换，float转为Number
    Number(float ff = 0.0f) : f(ff) {}//构造函数，做类型转换用的
    Number& operator=(const Number& x)//赋值运算符重载
    {
        f = x.f;
        return *this;
    }
    //Number转float
    operator float() const {return f;}
    //友元函数 用来输出，也是用运算符重载 流输出运算符重载
    friend std::ostream& operator<<(std::ostream& os, const Number& x)
    {
        return os << x.f;
    }
};

//测试
void test() {
    Array<int, 100> ia; //第二个参数，如果不写size就是默认的10，写了就是写的值100，可以重新定义.
    Array<Number, 50> a;
    Number n = 1.23;
    std::cout << n <<std::endl;//输出运算符 使用运算符重载
    
    float f = n;//Number变成float
    std::cout << f <<std::endl;//输出运算符 使用运算符重载

}
```

例二：

再做一个模版

```c++
//创建一个容器Holder类
template<class T, int size = 20>
class Holder
{
    Array<T,size>* np;//数组 指针指向数组
public:
//    Holder()
//    {
//        np = new Array<T, size>;//在构造函数中初始化数组，这是其中的一种方法
//    }
    Holder():np(0){}
    T& operator[](int i)//重载下标运算符。index：下标。
    {
        //第一次使用的时候，初始化数组，使用这种方法比较好
        if (!np)  new Array<T, size>;
        return np->operator[](i); //调用数组ARRAY的运算符重载
    }
    int length() const { return size; }//成员函数，返回长度。
    ~Holder() {delete np;}
};

//测试
void test() {
    Holder<Number> h;//调用构造函数创建对象，这时候数组还没有创建。
    for (int i = 0; i<20; i++) {
        h[i] = i * 10;
    }
    //数组中的元素 显示出来
    for (int j = 0; j < 20; j++) {
        std::cout << h[j] <<std::endl;
    }
}
```

## 模版化的指针Stash

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

//调试：
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

## Stack堆栈模板

Stack先进后出

### 简单的Stack模板

```c++
//做的这个stack是固定大小的数组，比较简单。数组大小用模版常量定义。
template<class T, int size = 100>
class StackTemplate
{
    T stack[size];
public:
    void push(const T& i){...}
    T pop(){...}
    ...
    
};
```

直接在头文件中写。

不是模版的例子：

```c++
//整型堆栈，保存整型
class IntStack
{
    enum {size = 100};
    int stack[size];
    int top;//栈顶
public:
    IntStack() : top(0) {}//构造函数 栈顶初始化为0
    void push(int i) //压入堆栈
    {
        //堆栈是否已经满了
        stack[top++] = i; //top++
    }
    //从堆栈取数据
    int pop()
    {
        //取数据的时候，堆栈不能是空的,堆栈必须有数据
        return stack[--top];
    }
};
```

然后改成模版：

```c++
//堆栈模版，在堆栈里可以保存各种类型的数据。
template<class T, int ssize = 100>
class StackTemplate
{
    T stack[ssize];
    int top;//栈顶
public:
    StackTemplate() : top(0) {}//构造函数 栈顶初始化为0
    void push(const T& i) //压入堆栈
    {
        //堆栈是否已经满了
        stack[top++] = i; //top++
    }
    //从堆栈取数据
    T pop()
    {
        //取数据的时候，堆栈不能是空的,堆栈必须有数据
        return stack[--top];
    }
    //返回堆栈的大小 ,堆栈里有多少数据
    int size() {return top;}
};
```

测试：

```c++
void test() {
    StackTemplate<int,20> is;
    for (int i = 0; i < 20; i++) {
        is.push(i);
    }
    for (int k = 0; k < 20; k++) {
        std::cout << is.pop() <<std::endl;
    }
    
    
    //读取文件
    StackTemplate<string> strings;
    ifstream in("main.cpp");
    string line;
    while(getline(in, line))
        strings.push(line);
    while (strings.size() > 0) {
        std::cout << strings.pop() <<std::endl;
    }
}
```

### 链表的Stack模版

堆栈里面不是数组，而是链表。

链表长度是动态的。

```c++
//堆栈模版，在堆栈里可以保存各种类型的数据。
template<class T>
class Stack
{
    class Link
    {
    public:
        T* data;
        Link* next;
        Link(T* dat, Link* nxt) : data(dat),next(nxt){}
        ~Link(){}
    }* head;
public:
    Stack() : head(0){}
    ~Stack()
    {
        while (head) {
            delete pop();
        }
    }
    void push(T* dat)
    {
        head = new Link(dat,head);
    }
    T* pop()
    {
        if (head == 0) {
            return 0;
        }
        T* result = head->data;
        Link* oldHead = head;
        head = head->next;
        delete oldHead;
        return result;
    }
    T* peek()
    {
        return head ? head->data : 0;
    }
};
```

堆栈模版可以保存各种类型，包括自定义的class类型。

如果想要放入class Q的子类行，那么Q必须有虚的析构函数（防止销毁的时候，没有销毁，有内存泄漏）。

只要有继承，基类必须有虚的析构函数。

```c++
class Q {
public:
    virtual ~Q(){}
};
class R : public Q
{
};
```

测试：

```c++
//测试
void test() {
    ifstream in("main.cpp");
    Stack<string> textlines;
    string line;
    while (getline(in, line)) {
        textlines.push(new string(line));//堆栈里保存的是指针，new得到的是指针
    }
    //pop得到的是指针
    string* s;
    for (int i = 0; i < 10; i++) {
        if ((s = (string*)textlines.pop()) == 0) break;
        std::cout << *s <<std::endl;
        delete s;
    }
    
    
    //存自定义class
		Stack<Q> qq;
    for (int j = 0; j < 10; j++) {
        qq.push(new R);//存子类
    }
}
```
