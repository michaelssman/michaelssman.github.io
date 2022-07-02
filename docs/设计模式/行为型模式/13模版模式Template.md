# 模版模式

## 概念

Template Method模式也叫模板方法模式，是行为模式之一。

它把具有特定步骤算法中的某些必要的处理委让给抽象方法，通过子类继承对抽象方法的不同实现改变整个算法的行为。

## 应用场景

Template Method模式一般应用在具有以下条件的应用中：

- 具有统一的操作步骤或操作过程
- 具有不同的操作细节
- 存在多个具有同样操作步骤的应用场景，但某些具体的操作细节却各不相同

## 总结

在抽象类中统一操作步骤，并规定好接口；让子类实现接口。这样可以把各个具体的子类和操作步骤解耦合

把方法声明和调用先做好  

方法的实现由子类去完成

声明很多空函数 把函数的调用做成一个方法

抽象类提前把子函数的调用提前规划好。

## 角色和职责

1. AbstractClass

   抽象类的父类

2. ConcreteClass

   具体的实现子类

3. templateMethod()

   模版方法

4. method1()与method2()

   具体步骤方法

#### 例：

```c++
#include <iostream>
using namespace std;

class MakeCar
{
public:
	virtual void makeHead() = 0;
	virtual void makeBody() = 0;
	virtual void makeTail() = 0;

public:   //把一组行为 变成 一个模板
	void make()
	{
		makeHead();
		makeBody();
		makeTail();
	}
	
protected:
private:
};

class MakeBus : public MakeCar
{
public:
	virtual void makeHead()
	{
		cout << "bus 组装 车头" << endl;
	}
	virtual void makeBody()
	{
		cout << "bus 组装 车身" << endl;
	}
	virtual void makeTail()
	{
		cout << "bus 组装 车尾" << endl;
	}
protected:
private:
};

class MakeJeep : public MakeCar
{
public:
	virtual void makeHead()
	{
		cout << "Jeep 组装 车头" << endl;
	}
	virtual void makeBody()
	{
		cout << "Jeep 组装 车身" << endl;
	}
	virtual void makeTail()
	{
		cout << "Jeep 组装 车尾" << endl;
	}
protected:
private:
};

void main()
{
	MakeCar *bus = new MakeBus;
	
	//bus->makeHead();
	//bus->makeBody();
	//bus->makeTail();
	bus->make();

	MakeCar *jeep = new MakeJeep;
	//jeep->makeHead();
	//jeep->makeBody();
	//jeep->makeTail();
	jeep->make();

	delete bus;
	delete jeep;

	cout<<"hello..."<<endl;
	system("pause");
	return ;
}
```

模版函数就是把函数的调用做好。

**模版函数把业务逻辑确定好了。**

例如

造车  造车头 造车身 造车尾。造车调用这三个方法。造车头，车身，车尾的具体实现由子类完成。

无论是造Jeep还是宝马，造车都是这三个部分，顺序一样。只是具体子类的实现不一样。

### 总结

抽象函数里定义子函数，但是不实现。让子类实现，子函数的实现推迟到子类中实现。但是业务逻辑提前做好了。

无论子类怎么实现，函数调用是固定的，业务逻辑已经提前写好了。子类只需要实现子任务就可以了。