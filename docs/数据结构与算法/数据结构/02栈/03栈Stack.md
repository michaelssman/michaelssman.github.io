# 栈Stack

- 堆栈-先进后出，后进先出
- 头文件（加保护，多重包含，有多个文件）
- 嵌套结构（struct中有struct）

堆栈基本原理：

堆栈是一种容器，开始的时候堆栈是空的，堆栈有一个头（header），头head是一个指针，开始的时候头head=0是一个空指针

然后再堆栈中放入数据push，头head就指向第一个数据。然后放第二个数据，head就指向第二个数据。一直这样保存，head始终指向最上面的那个。

一个一个数据是用链表做的。有指针指向下一个数据。链式栈。

代码

```c++
struct Stack
{
    //结构中嵌套结构
    struct Link //堆栈中的每一个数据都是Link。
    {
        void* data;//Link中的数据
        Link* next;//指针 指向下一个数据
        void initialize(void* dat, Link* nxt);//Link节点初始化
    }* head;//头
    
    void initialize();//堆栈初始化
    void push(void* dat);//把数据压入堆栈
    void* pop();//从堆栈中拿数据，只能从一头拿 不能从中间拿。把head指向的数据拿出来，head指向下一个。
    void* peak();//只看一下数据，不拿出来。
    void cleanup();
};
//初始化Link
void Stack::Link::initialize(void* dat, Link* nxt)
{
    data = dat;
    next = nxt;
}
//初始化堆栈
void Stack::initialize()
{
    head = 0;
}
// 把数据放入堆栈
void Stack::push(void* dat)
{
    //数据是保存在Link里面的
    Link* newLink = new Link;
    newLink -> initialize(dat, head);
    head = newLink;
}
//查看最上面的数 head
void* Stack::peak()
{
    //加一个检查，头指针不能是0，是0的话栈就是空的。
    return head->data;
}
//从堆栈中取数据
void* Stack::pop()
{
    if (head == 0) {
        return 0;
    }
    void* result = head->data;
    //head指向下一个指针，原来的head指向的就删除了
    Link* oldHead = head;
    head = head->next;
    delete oldHead;
    return result;
}
//清理堆栈
void Stack::cleanup()
{
    //加一个检查，如果head==0,则堆栈是空的。
    //这里并没有做真正的清理，让外部使用pop做清理，这里就只有一个是否为空的检查。
}
```

调用：

```c++
void test()
{
    ifstream in("Test.cpp");
    
    Stack textlines;
    textlines.initialize();//初始化
    
    string line;
    while (getline(in, line)) {
        textlines.push(new string(line));
    }
    
    string *s;
    while ((s = (string *)textlines.pop()) != 0) {
        cout << *s << endl;
        delete s;
    }
    
    textlines.cleanup();

//    cout << *(string *)textlines.peak() << endl;
    
}
```



