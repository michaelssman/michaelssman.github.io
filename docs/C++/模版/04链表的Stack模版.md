# 链表的Stack模版

堆栈里面不是数组，而是链表。

链表长度是动态的。

堆栈模版：

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























