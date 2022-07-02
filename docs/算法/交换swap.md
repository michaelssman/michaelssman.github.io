# 交换swap

交换是算法的基础，把交换做成通用的函数。

首先是一种不行的方法，方法没有错，但是不会发生交换。没有发生变化，因为传参数的方式问题。

这是按值传递，把a和b各自拷贝一个传进去，只是把拷贝的数交换了，原来的a和b没有变。

```c++
void swap(int x, int y)
{
    int tmp;
    tmp = x;
    x = y;
    y = tmp;
}
```

用C语言实现的话就需要传指针

用C++实现，可以继续使用传指针方式也可以使用C++传引用

### 使用宏定义函数

宏函数

```c
#define swap(x,y,t) ((t) = (x),(x) = (y),(y) = (t))
```

```c++
void test()
{
    int a,b,temp;
    a = 1;
    b = 10;
    std::cout << "a = " << a << ", b = " << b << std::endl;
    
    SWAP(a,b,temp);
    
    std::cout << "a = " << a << ", b = " << b << std::endl;
}
```

### 传指针

使用指针进行交换

```c++
void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}
```

```c++
void test()
{
    int a,b;
    a = 1;
    b = 10;
    std::cout << "a = " << a << ", b = " << b << std::endl;
    // 拷贝的是指针（地址） 拿到的是地址，操作的就是原来的数据
    swap(&a, &b);
    
    std::cout << "a = " << a << ", b = " << b << std::endl;
}
```

### 传引用

引用就是别名

C语言大量使用指针比较复杂，容易出错，所以C++使用引用。

别名的写法上就简单多了。

```c++
void swap(int &rx, int &ry)
{
    int tmp;
    tmp = rx;
    rx = ry;
    ry = tmp;
}
```

调用

```c++
void test()
{
    int a,b;
    a = 1;
    b = 10;
    std::cout << "a = " << a << ", b = " << b << std::endl;
    // 引用就是别名，传的时候直接用就行了
    swap(a, b);
    
    std::cout << "a = " << a << ", b = " << b << std::endl;
}
```

这种最简单

### 还有一种C++做好的函数

不需要我们自己做，并且还是模版函数，各种类型都可以使用。

```c++
template<class T> void swap(T& x, T& b);
```

```c++
void test()
{
    int a,b;
    a = 1;
    b = 10;
    std::cout << "a = " << a << ", b = " << b << std::endl;
    
    std::swap(a, b);
    
    std::cout << "a = " << a << ", b = " << b << std::endl;
}
```

### 总结

宏定义和C++做好的模版函数可以使用任何类型，传指针和传引用的只能是一种类型。