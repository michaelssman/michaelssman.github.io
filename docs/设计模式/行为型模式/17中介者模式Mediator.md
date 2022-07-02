# 中介者模式

## 概念

Mediator模式也叫中介者模式，是由GoF提出的23种软件设计模式的一种。Mediator模式是行为模式之一。

在Mediator模式中，类之间的交互行为被统一放在Mediator的对象中，对象通过Mediator对象同其他对象交互，Mediator对象起着控制器的作用。

### 角色和职责

GOOD：用一个中介对象来封装一系列的对象交互，中介者使各对象不需要显示的相互引用，从而降低耦合；而且可以独立地改变它们之间的交互。
![image.png](https://upload-images.jianshu.io/upload_images/1892989-ea0e98ed8aa11690.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- Mediator抽象中介者
  中介者类的抽象父类。
- concreteMediator
  具体的中介者类。
- Colleague
  关联类的抽象父类。
- concreteColleague
  具体的关联类。

### 适用于：

​	用一个中介对象，封装一系列对象（同事）的交换，中介者使各个对象不需要显示的相互作用，从而实现了耦合松散，而且可以独立的改变他们之间的交换。

#### 模式优点

1. 将系统按功能分割成更小的对象，符合类的最小设计原则

2. 对关联对象的集中控制

3. 减小类的耦合程度，明确类之间的相互关系

   当类之间的关系过于复杂时，其中任何一个类的修改都会影响到其他类，不符合类的设计的开闭原则 ，而Mediator模式将原来相互依存的多对多的类之间的关系简化为Mediator控制类与其他关联类的一对多的关系，当其中一个类修改时，可以对其他关联类不产生影响（即使有修改，也集中在Mediator控制类）。

4. 有利于提高类的重用性


A和B都持有中介者
然后让中介者去干活

#### 例：

相亲：

很多男人和很多女人相亲，如果男人直接找女人的话，一个男人要和很多女人打交道。女人也是。耦合高。

可以通过中介者，每一个人都通过中介者和其他人联系，耦合度降低。

- 普通模式
  定义一个抽象类 人  

  男人和女人都继承 人类
  男人和女人自己去实现找对象的操作

- 中介者模式
  男人和女人每一个人都持有一个中介者的引用  找对象的操作由中介者去完成，中介者是男人类女人类的成员变量。男人和女人通过中介者发生关系。通过中介者找对象。    
  其中中介者类中 持有男人和女人两类对象的引用， 在找对象的操作需要用。

### 扩展

中介者类中 还可以持有一个list 数组，n个对象的集合，女人可以在n个男人里面找对象，找对象可以从一个数组中去找，功能更强大。

打开思路。

#### 例：

```c++
#include <iostream>
using namespace std;
#include "string"

class Person
{
public:
	Person(string name, int sex, int condit)
	{
		m_name = name;
		m_sex = sex;
		m_condition = condit;
	}
	string getName()
	{
		return m_name;
	}
	int getSex()
	{
		return m_sex;
	}
	int getCondit()
	{
		return m_condition;
	}
	virtual void getParter(Person *p) = 0;

protected:
	string	m_name;	//
	int		m_sex; //1男  2女
	int		m_condition; //123456789;
};

class Man : public Person
{
public: 
	Man(string name, int sex, int condit):Person(name, sex, condit)
	{
		;
	}
	virtual void getParter(Person *p)
	{
		if (this->getSex() == p->getSex())
		{
			cout << "No No No 我不是同性恋" << endl;
		}
		if (this->getCondit() == p->getCondit())
		{
			cout << this->getName() << " 和 " << p->getName() << "绝配" << endl;
		}
		else
		{
			cout << this->getName() << " 和 " << p->getName() << "不配" << endl;
		}
	}
protected:

};

class Woman : public Person
{
public: 
	Woman(string name, int sex, int condit):Person(name, sex, condit)
	{
		;
	}
	virtual void getParter(Person *p)
	{
		if (this->getSex() == p->getSex())
		{
			cout << "No No No 我不是同性恋" << endl;
		}
		if (this->getCondit() == p->getCondit())
		{
			cout << this->getName() << " 和 " << p->getName() << "绝配" << endl;
		}
		else
		{
			cout << this->getName() << " 和 " << p->getName() << "不配" << endl;
		}
	}
protected:

};

//以上  Woman  Man类的太紧密 需要解耦合
void main1901()
{
	
	Woman *w1 = new Woman("小芳", 2, 4);
	Man *m1 = new Man("张三", 1, 3);
	Man *m2 = new Man("李四", 1, 4);

	w1->getParter(m1);
	w1->getParter(m2);

	delete w1;
	delete m1;
	delete m2;
	
	return ;
}

class Mediator ;
class Person2
{
public:
	Person2(string name, int sex, int condition, Mediator *m)
	{
		m_name = name;
		m_sex = sex;
		m_condition = condition;
		m_m = m;
	}
	string getName()
	{
		return m_name;
	}
	int getSex()
	{
		return m_sex;
	}
	int getCondit()
	{
		return m_condition;
	}
	
	Mediator *getMediator()
	{
		return m_m;
	}
public:
	virtual void getParter(Person2 *p) = 0;

protected:
	string	m_name;	//
	int		m_sex; //1男  2女
	int		m_condition; //123456789;
	Mediator *m_m;
};


class Mediator 
{
public:
	Mediator()
	{
		pMan = NULL;
		pWoman = NULL;
	}
	void setWoman(Person2 *p)
	{
		pWoman = p;
	}
	void setMan(Person2 *p)
	{
		pMan = p;
	}

	void getPartner()
	{
		if (pMan->getSex() == pWoman->getSex())
		{
			cout << "No No No 我不是同性恋" << endl;
		}
		if (pMan->getCondit() == pWoman->getCondit())
		{
			cout << pMan->getName() << " 和 " << pWoman->getName() << "绝配" << endl;
		}
		else
		{
			cout << pMan->getName() << " 和 " << pWoman->getName() << "不配" << endl;
		}
	}

protected:
private:
	Person2	*pMan;
	Person2	*pWoman;
};

class Woman2 : public Person2
{
public:
	Woman2(string name, int sex, int condition, Mediator *m) : Person2(name, sex, condition, m)
	{
		;
	}
	virtual void getParter(Person2 *p)
	{
		this->getMediator()->setWoman(this);
		this->getMediator()->setMan(p);
		this->getMediator()->getPartner();
	}
private:
};

class Man2 : public Person2
{
public:
	Man2(string name, int sex, int condition, Mediator *m) : Person2(name, sex, condition, m)
	{
		;
	}
	virtual void getParter(Person2 *p)
	{
		this->getMediator()->setMan(this);
		this->getMediator()->setWoman(p);
		this->getMediator()->getPartner();
	}
private:
};

void main1902()
{
	Mediator *mediator = new Mediator;
	Woman2 *w1 = new Woman2("小芳", 2, 4, mediator);
	Man2 *m1 = new Man2("张三", 1, 3, mediator);
	Man2 *m2 = new Man2("李四", 1, 4, mediator);

	w1->getParter(m1);
	w1->getParter(m2);

	delete w1;
	delete m1;
	delete m2;
	delete mediator;
}
void main()
{
	//main1901(); //问题的引出
	main1902(); //用中介者模式 进行优化
	system("pause");
}
```

### 总结

之前找对象操作是在男人和女人类里面都要写一遍，使用中介者模式之后，找对象的操作只需要在中介者中写一份代码就可以。

相当于男人和女人都拥有一个中介者，让中介者做事。

每个人都可以通过中介者找对象，每一个人都持有一个中介者的引用（或指针）。

中介要为每一个人服务，中介里面也应包含人的实例（男人和女人，或者一个集合）

中介者做找对象的操作。





页面跳转的路由router九种中介者模式