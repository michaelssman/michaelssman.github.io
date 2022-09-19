只要写头文件  头要写头文件的保护

C++头文件`.h`中写代码  不能使用命名空间，不能写 `using namespace std;`只能：`std::cout << std::end;`

也可以导入头文件

只能在源文件使用命名空间。

---



typedef int Object;

---



如果类使用它下面的其它类  需要前置声明一下



C++函数 参数前面表示输入、后面表示输出。

泛型
template <typename T>
例：
SeqList<Teacher> list(10);

![image.png](https://upload-images.jianshu.io/upload_images/1892989-0f62726786a0d63a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



下图是对上图的优化



![上面的优化](https://upload-images.jianshu.io/upload_images/1892989-251f971c2cbe8300.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![image.png](https://upload-images.jianshu.io/upload_images/1892989-d2fc671fd10d7b5b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

C语言中的句柄在C++中就不需要了，在C++中相当于this指针。
链表没有容量 线性表顺序存储有容量


![image.png](https://upload-images.jianshu.io/upload_images/1892989-d0dbf6649f4beea8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)





C++ 解决方案是一个项目组。



**父类 是带参数的构造函数，子类就需要初始化列表。**