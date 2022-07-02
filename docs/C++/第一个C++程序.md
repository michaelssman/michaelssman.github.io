# 第一个C++程序

- 头文件 iostream  （o是输出 stream是流）

- 类 ostream，istream

- 对象 cout，cin

  -   C语言的scanf，printf不好，C++又写了功能更好的cout，cin。

- 名称空间 std

  - C语言没有名称空间，C++有名称空间。C语言所有的东西都放在了一起，C++是分开放的。分门别类的放在不同的名称空间里。在大项目中，C语言的函数名称就容易冲突。
  - 每次都要写s t d::比较麻烦，有一种方法可以简化：`using namespace std;`这样就可以不写了。

- 运算符重载 << >>

  - 同一个符号有不同作用，C语言没有运算符重载，C++有运算符重载。

- 字符串

  -  C语言的字符数组 ，只是一个数组。
  - C++的string是一个class，一个类型，把字符数组进行了包装，有各种操作。

  ```c++
      char s[6] = "hello"; //C语言的
      string s1,s2;
      string s3 = "Hello world";
      string s4("I am");//类的构造函数进行初始化
      s2 = "Today";
      s1 = s3 + " " + s4;  //+是string类的方法。C语言
      s1 += " 8 ";
      cout << s1 + s2 + "!" << endl;  
  ```

  上面代码 C++可以调用string的`+`运算，C语言的话实现加法就比较复杂。

导入头文件：

- C++头文件不需要写`.h`

- C 语言需要`.h`

```c++
    int num1,num2,sum;
    cout << "Enter first number:" << endl;
    cin >> num1;
    cout << "Enter second number:" << endl;
    cin >> num2;
    sum = num1 + num2;
    cout << num1 << "+" << num2 << "=" << sum << endl;
```



