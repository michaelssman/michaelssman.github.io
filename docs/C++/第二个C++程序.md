# 第二个C++程序

要进行文件的读写，使用文件流

还要使用容器

- 头文件 fstream
- 类 ifstream ofstream
- 函数 getline
- 容器 vector
  - vector<string>
  - vector<int>

### 文件的读写

```c++
void test()
{
    //一次读一个单词
    string s;
    ifstream in0("HarryPotter.txt");//文件输入流
    in0 >> s;//流输入操作符，遇到空格就停了。一次只读一个单词。
    
    //一次读一行
    string line;
    ifstream in1("HarryPotter.txt");//文件输入流
    getline(in1, line);
    
    //输出文件流
    ifstream in2("HarryPotter.txt");//文件输入流
    ofstream out("HarryPotter2.txt");//文件输出流
    string s2;
    while (getline(in2,s2)) {
        out << s2 << "\n";
    }
    
    //整个文件读到一个string里
    ifstream in3("HarryPotter.txt");//文件输入流
    string s3,line3;
    while (getline(in3,line3)) {
        s3 += line3 + "\n";
    }
}
```

### 容器

- C语言的数组有很多缺点，尽量不要使用C语言的数组
- C++里有vector（非常灵活的动态数组）。容器 箱子。

```c++
void test()
{
    //C语言的数组
    int arr[10];
    for (int i = 0; i < 10; i++) {
        arr[i] = i;
    }
    
    //C++
    //vector是一个类，并且是一个模版。可以指定保存的类型。
    vector<int> v; //创建对象
    for (int i = 0; i < 10; i++) {
        v.push_back(i);
    }
//    v.size()//是一个函数
    for (int i = 0; i < v.size(); i++) {
        cout << v[i] << endl; //对[]进行的重载 可以向数组一样使用。
    }
    
    //读取文件，把字符串放到一个容器里
    vector<string> h;
    ifstream in("HarryPotter.txt");//文件输入流
    string line;
    while (getline(in,line)) {
        h.push_back(line);
    }
    for (int i = 0; i < h.size(); i++) {
          cout << i << ":" << h[i] << endl; //对[]进行的重载 可以向数组一样使用。
      }

}
```



