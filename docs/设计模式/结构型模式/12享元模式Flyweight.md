# 享元模式

## 前言

在面向对象系统的设计和实现中，创建对象是最为常见的操作。

这里面就有一个问题：

如果一个应用程序使用了太多的对象，就会造成很大的存储开销，特别是对于大量轻量级（细粒度）的对象，比如在文档编辑器的设计过程中，我们如果为每一个字母创建一个对象的话，系统可能会因为大量的对象而造成存储开销的浪费。例如一个字母"a" 在文档中出现了100000次，而实际上我们可以让这一万个字母"a"共享一个对象，当然因为在不同的位置可能字母"a"有不同的显示效果（例如字体和大小等设置不同），在这种情况我们可以为将对象的状态分为"外部状态"和"内部状态"，将可以被共享（不会变化）的状态作为内部状态存储在对象中，而外部状态（例如上面提到的字体、大小等）我们可以在适当的时候将外部对象作为参数传递给对象（例如在显示的时候，将字体、大小等信息传递给对象）。

## 享元模式

Flyweight模式也叫享元模式，是构造型模式之一。它通过与其他类似对象共享数据来减小内存占用。

共享一些公共的减少内存开发。

> 在面向对象系统的设计和实现中，创建对象是最为常见的操作。这里面就有一个问题：如果一个应用程序使用了太多的对象，就会造成很大的存储开销。特别是对于大量轻量级（细粒度）的对象，比如在文档编辑器的设计过程中，我们如果为每一个字母创建一个对象的话，系统可能会因为大量的对象而造成存储开销的浪费。例如一个字母"a"在文档中出现了100000次，而实际上我们可以让这一万个字母"a"共享一个对象，当然因为在不同位置可能字母"a"有不同的显示效果（例如字体和大小等设置不同），在这种情况我们可以为将对象的状态分为“外部状态”和“内部状态”，将可以被共享（不会变化）的状态作为内部状态存储在对象中，而外部对象（例如上面提到的字体、大小等）我们可以适当的时候将外部对象作为参数传递给对象（例如在显示的时候，将字体、大小等信息传递给对象）

### 角色和职责

![image.png](https://upload-images.jianshu.io/upload_images/1892989-ccb53540aaa4029f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- 抽象享元角色：
  所有具体享元类的父类，规定一些需要实现的公共接口。
- 具体享元角色：
   抽象享元角色的具体实现类，并实现了抽象享元角色规定的方法。
- 享元工厂角色 FlyweightFactory
   负责创建和管理享元角色。

客户端使用一个享元工厂，生产n多个对象。客户端使用这些颗粒度对象操作。

### 使用场景：

是以共享的方式，高效的支持大量的细粒度的对象。


使用一个map 键值（也可以使用一个数组，遍历数组）  

创建对象，从工厂获取。
获取一个对象的时候：
如果map中没有就加一个（新new一个），如果有就直接获取，不用重复创建对象。

map里有很多对象。

##### 注：

map中每一个值 指针指向的对象都是创建的（老师结点是创建出来的），需要释放内存。使用迭代器 移除节点（erase）把new的老师结点delete。
方法：一个while循环 遍历
删除内容  指针指向null

### 例：

人有年龄性别名字

老师还有一个id。生产老师保证每个id只有一个老师对象，不会生产多个相同id的老师对象。

```c++

#include <iostream>
using namespace std;
#include "string"
#include "map"

class Person
{
public:
	Person(string name, int age)
	{
		this->m_name = name;
		this->age = age;
	}
	virtual void printT() = 0;

protected:
	string	m_name;
	int		age;
};

class Teacher : public Person
{
public:
	Teacher(string name, int age, string id) : Person(name, age)
	{
		this->m_id = id;
	}
	void printT()
	{
		cout << "name:" << m_name << " age:" << age << " m_id:" << m_id << endl;
 	}
protected:
private:
	string	m_id;
};


//完成 老师结点 存储

class FlyWeightTeacherFactory 
{
public:
	FlyWeightTeacherFactory()
	{
		map1.clear();
	}

	~FlyWeightTeacherFactory()
	{
		while ( !map1.empty())
		{
			Person *tmp = NULL;
			map<string, Person *>::iterator it = map1.begin();
			tmp = it->second;
			map1.erase(it); //把第一个结点 从容器中删除
			delete tmp;
		}
	}

	Person * GetTeacher(string id)
	{
		Person *tmp = NULL;
		map<string, Person *>::iterator it ;
		it = map1.find(id);
		if (it == map1.end()) //没有找到
		{
			string	tmpname;
			int		tmpage;
			cout << "\n请输入老师name:";
			cin >> tmpname;

			cout << "\n请输入老师age:";
			cin >> tmpage;

			tmp = new Teacher(tmpname, tmpage, id);
			map1.insert(pair<string, Person*>(id, tmp) );
		}
		else
		{
			tmp = it->second;
		}
		return tmp;
	}
private:
	map<string, Person *> map1;

};

void main()
{
	Person *p1 = NULL;
	Person *p2 = NULL;
	FlyWeightTeacherFactory *fwtf = new FlyWeightTeacherFactory;
	p1 = fwtf->GetTeacher("001");
	p1->printT();

	p2 = fwtf->GetTeacher("001");
	p2->printT();

	delete fwtf;
	
	cout<<"hello..."<<endl;
	system("pause");
	return ;
}
```

#### 总结

主要是使用一个容器来存储所有的对象。