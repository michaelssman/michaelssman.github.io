# 模版template

C++语言模版是一个重要内容，

有两种模版：

1. 类模版
2. 函数模版

C++中有函数模版
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

可以用C++的模版，做一个函数模版。C++在编译的时候根据模版动态的生成需要的函数。用到哪一个C++会自动的创建哪一个。

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

交换函数的这个模版C++已经做好了，由内置的。做好的是小写的swap。所以自己写的这个交换模版的函数名字首字母要大写。

做一些通用的函数，对各种类型，考虑用函数模版写。

C++容器算法模版。stl标准函数模版。

## 模版中的常量

模版的参数中可以使用C++内置类型（常量）。还可以设置默认值。

size是不可以修改的。

模版变成类的时候C++会把`int size = 10`变成常量，所以是不能修改的。

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

template<class T, int size>//这里不用谢size = 1
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
```

```c++
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

