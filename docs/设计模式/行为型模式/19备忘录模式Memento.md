# 备忘录模式

## 概念

Memento模式也叫备忘录模式，是行为模式之一，它的作用是保存对象的内部状态，并在需要的时候（undo/rollback）恢复以前的状态。

## 应用场景

如果一个对象需要保存状态并可通过undo或rollback等操作恢复到以前的状态时，可以使用Memento模式。

1. 一个类需要保存它的对象的状态（相当于Originator角色）
2. 设计一个类，该类知识用来保存上述对象的状态（相当于Memento角色）
3. 需要的时候，Caretaker角色要求Originator返回一个Memento并加以保存
4. undo或rollback操作时，通过Caretaker保存的Memento恢复Originator对象的状态

## 角色和职责

1. Originator（原生者）
   需要被保存状态以便恢复的那个对象。

2. Memento（备忘录）
   该对象由Originator创建，主要用来保存Originator的内部状态。

3. Caretaker（管理者）

   负责在适当的时间保存/恢复Originator对象的状态。

原生者Originator创建一个备忘录，原生者Originator持有一个备忘录。原生者创建的备忘录被管理者管理，管理者也持有备忘录。

管理者持有备忘录的引用。里面一个set 一个 get。

## 适用于

在不破坏封装性的前提下，捕获一个对象的内部状态，并在该对象之外保存这个状态，这样就可以将以后的对象状态恢复到先前保存的状态。

适用于功能比较复杂的，但需要记录或维护属性历史的类；或者需要保存的属性只是众多属性中的一小部分时Originator可以根据保存的Memo还原到前一状态。

### 例

人person类
person持有一个备忘录mememto的引用或包含一个createMememto方法，去创建备忘录。类似备份功能。
person再实现一个实现恢复备忘录的功能，setMememto。还原person 把各个属性恢复保存的那个。

备忘录的管理者：
管理者持有一个备忘录的引用 创建管理者的时候，设置备忘录。
实现getMememto方法 和setMememto方法 设置备忘录和get备忘录

person人就不用直接设置和获取备忘录  而是通过管理者去设置和获取。

#### 例：

```c++

#include <iostream>
using namespace std;
#include "string"

class MememTo
{
public:
	MememTo(string name, int age)
	{
		this->m_name = name;
		this->m_age = age;
	}
	void setName(string name)
	{
		this->m_name = name;
	}
	string getName()
	{
		return m_name;
	}
	void setAge(int  age)
	{
		this->m_age = age;
	}
	int getAge()
	{
		return m_age;
	}
protected:
private:
	string	m_name;
	int		m_age;
};

class Person
{
public:
	Person(string name, int age)
	{
		this->m_name = name;
		this->m_age = age;
	}
	void setName(string name)
	{
		this->m_name = name;
	}
	string getName()
	{
		return m_name;
	}
	void setAge(int  age)
	{
		this->m_age = age;
	}
	int getAge()
	{
		return m_age;
	}
	void printT()
	{
		cout << "name: " << m_name << "age: " << m_age << endl;
	}

public:

	//创建备份
	MememTo *createMememTo()
	{
		return new MememTo(m_name, m_age);
	}

	//恢复备份
	void SetMememTo(MememTo *memto)
	{
		m_name = memto->getName();
		m_age = memto->getAge();
	}

protected:
private:
	string	m_name;
	int		m_age;
};

//管理者
class Caretaker
{
public:
	Caretaker(MememTo *mem)
	{
		this->m_memto = mem;
	}
	MememTo *getMememTo()
	{
		return m_memto;
	}
	void setMememTo(MememTo *mem)
	{
		this->m_memto = mem;
	}
protected:
private:
	MememTo *m_memto;
};

void main23_01()
{
	Person *p = new Person("张三", 18);
	p->printT();

	//创建备份
	Caretaker *ct = new Caretaker(p->createMememTo());
	
	p->setAge(28);
	p->printT();

	//恢复信息
	p->SetMememTo(ct->getMememTo());
	p->printT();

	delete p;
	delete ct->getMememTo();

	return ;
}

void main23_02()
{
	Person *p = new Person("张三", 18);
	p->printT();

	//创建备份
	MememTo * membak = p->createMememTo();
	p->setAge(28);
	p->printT();

	//恢复信息
	p->SetMememTo(membak);
	p->printT();

	delete p;
	delete membak;
}

void main()
{
	//main23_01();
	main23_02();
	system("pause");
}
```

### 个人总结：

创建一个类 备忘录类包含要保存的对象的所有属性，创建备忘录类的对象还保存要保存的对象的属性的值。

相当于把信息存到一个地方， 需要还原的时候再取出来设置。

涉及到深拷贝浅拷贝。

备忘录模式就是保存类的属性。