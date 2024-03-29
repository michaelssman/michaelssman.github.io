# 交换swap

交换是算法的基础，把交换做成通用的函数。

按值传递，把a和b各自拷贝一个传进去，**只是把拷贝的数交换了，原来的a和b不会发生交换**。

```c++
void swap(int x, int y)
{
    int tmp;
    tmp = x;
    x = y;
    y = tmp;
}
```

C语言需要传指针

C++可以传指针也可以传引用

## 宏定义函数

```c++
#define swap(x,y,t) ((t) = (x),(x) = (y),(y) = (t))

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

## 传指针

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

## 传引用

C语言大量使用指针比较复杂，容易出错，所以C++使用引用。

引用就是别名，这种最简单。

```c++
void swap(int &rx, int &ry)
{
    int tmp;
    tmp = rx;
    rx = ry;
    ry = tmp;
}
```

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

## C++做好的函数

并且还是模版函数，各种类型都可以使用。

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

## 总结

宏定义和C++做好的模版函数可以使用任何类型，传指针和传引用的只能是一种类型。