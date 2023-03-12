# Stack堆栈模板

Stack先进后出

## 简单的Stack模板

做的这个stack是固定大小的数组，比较简单。数组大小用模版常量定义。

```c++
template<class T, int size = 100>
class StackTemplate//做的这个stack是固定大小的数组，比较简单。数组大小用模版常量定义。
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

## 链表的Stack模版

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
