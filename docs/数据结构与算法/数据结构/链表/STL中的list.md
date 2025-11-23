# STL的list类

C++已经做好的标准模版库STL，STL中的list类是双向链表，功能强并且健壮。

链表可以保存数据，链表里面有一个指针指向下一个数据元素

双向链表有两个指针，一个指向下一个节点，一个指向前一个节点。

链表就是很多个节点，一个节点一个节点通过指针连成一条链。

## 链表比数组好的优点

链表比较方便，可以在任何地方插入数据（开头，结尾，中间），都是非常快的。插入所需要的时间是固定的，不会随数据增多而增加。数组只在末尾插数据比较快。

## 迭代器

C++的链表做的还有一个迭代器，通过迭代器可以把链表中的数据一个一个的进行处理。

所以自己设计的链表也应该有迭代器功能。增加一个迭代器。

做一些复杂的数据结构的时候，需要自己写。

```c++
#include <list>//C++ STL中的链表
using namespace std;//list也是用的std命名空间
```

```c++
//标准C++ STL中的链表和迭代器
//可以往链表的前面增加数据，也可以往链表的后面增加数据
list<int> listIntegers;//list
listIntegers.push_front(5);//在链表前面插入数据
listIntegers.push_front(15);
listIntegers.push_front(25);
listIntegers.push_front(35);

//查看链表中的数据 使用迭代器
list<int>::iterator i = listIntegers.begin();//迭代器 返回第一个数据
//迭代器是一个指针
cout << *i << "->";
while (i != listIntegers.end()) {
    cout << *i << "->";
    ++i;//下一个元素
}
cout << endl;
```

操作**类私有的数据成员**。需要做成友元类。

### 插入数据

#### 1、从list开头插入

```c++
a.push_front(9999);//每次都是从头插入，新插入的都在最前面
```

#### 2、从list末尾插入

```c++
a.push_back(8989);//往链表后端插入
```

#### 3、在list中间插入

有三种方法

第一种方法：

```c++
//中间插入数据
//用迭代器指定位置
a.insert(a.begin(), 10);//在begin头插
```

insert方法 第一个参数是一个迭代器 指定插入的位置，`a.begin()`就是头部插入。第二个参数是插入的数据。

第二种情况：

```c++
a.insert(a.end(), 4, 20);//在末端插入4个20
```

第三种情况：

**通过迭代器指定位置**，可以在任意位置插入数据

```c++
void test()
{

    list<int> a;//a就是双向链表
    
    //显示链表中的数据不能使用下标，因为不是数组，数组才可以用下标
    //链表只能使用迭代器
    std::list<int>::iterator iter;//迭代器类型

    a.push_front(4);
    a.push_front(3);
    a.push_front(2);
    a.push_front(1);//每次都是从头插入，新插入的都在最前面
    
    a.push_back(5);//往链表后端插入
    
    iter = a.begin();//迭代器指向位置
    ++iter;//变成第二个位置
    a.insert(iter, 10);//在第二个位置插入10
    ++iter;		//改变位置
    a.insert(iter, 4, 20);//插入4个20

    //中间插入数据
    //用迭代器指定位置
    a.insert(a.begin(), 10);//在begin头插
    
    a.insert(a.end(), 4, 20);//在后端插入4个20
    
    //通过a.begin()得到迭代器
    for (iter = a.begin(); iter != a.end(); ++iter) {
        cout << *iter << endl;//迭代器是指针
    }
    
}
```

改变迭代器的位置。

通过控制**迭代器**，利用`insert`在链表的中间插入数据。

迭代器指定插入的位置。

取元素，查看元素，链表不能使用下标，只能使用迭代器。数组才可以用下标。

```c++
std::list<int>::iterator iter;//迭代器类型 创建一个迭代器
//通过a.begin()得到迭代器
for (iter = a.begin(); iter != a.end(); ++iter) {
    cout << *iter << endl;//迭代器是指针
}
```

##### 打印list中的数据：

```c++
void PrintListContents(const list<int>& listInput)
{
    std::list<int>::const_iterator iter;//常迭代器
    //通过a.begin()得到迭代器
    for (iter = listInput.begin(); iter != listInput.end(); ++iter) {
        cout << *iter << endl;//迭代器是指针
    }
}
```

#### 把一个list中的数据插入到另一个list中：

两个list。

把b插入到a里面：

b插入到a的前面：

```c++
a.insert(a.begin(), b.begin(), b.end());
```

b插入到a的后面：

```c++
a.insert(a.end(), b.begin(), b.end());
```

也可以插入到中间

```c++
iter = a.begin();
++iter;//变成第二个位置
a.insert(iter, b.begin(), b.end());
```

也可以这样：

```c++
a.insert(iter, ++b.begin(), --b.end());
```

b.begin()是一个迭代器，b.end()也是一个迭代器。

指的是位置。第一个位置，最后一个位置。

++b.begin()从b的第二个开始

--b.end()，b的倒数第二个 结束。b最后一个不插入。

insert第一个参数是迭代器 从哪儿插入

第二个 第三个参数也是迭代器，是一个区间。插入的数据。

上面三个insert函数是函数重载，完成不一样的功能。

### 删除list中的元素

往list中insert的时候，就会返回一个迭代器，并且这个迭代器就指向insert的这个数据的位置。

```c++
std::list<int> a;
a.push_front(4);
a.push_front(3);

list<int>::iterator iElementValueTwo;

iElementValueTwo = a.insert(a.begin(), 2);//insert返回一个迭代器 迭代器指向这个数据2
```

通过迭代器删除：

```c++
a.erase(iElementValueTwo);
```

这样就把迭代器指向的2给删了。

删除的时候也可以给两个迭代器，从第一个迭代器到第二个迭代器区间的所有数据都删除。

```c++
a.erase(a.begin(), iElementValueTwo);
```

左闭右开，包括a.begin()这个 但是不包括iElementValueTwo迭代器指向的2。

两次删除：

```c++
a.erase(a.begin(), iElementValueTwo);
a.erase(iElementValueTwo, a.end());
```

从开始到2，从2到最后，a.end()指向的是最后一个的后一个，这样就删完了。

可以通过迭代器删除迭代器指向的数据。

### 反转数据 

```c++
a.reverse();
```

### 排序数据

```c++
a.sort();
```

list标准模版库，里面有各种方法，可以直接使用，还有迭代器。
