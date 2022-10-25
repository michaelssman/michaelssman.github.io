# 适配器模式 Adapter

## 适用于

**适配器模式是将一个类的接口转换成客户希望的另外一个接口，使得原本由于接口不兼容而不能一起工作的那些类可以一起工作。属于结构型设计模式。**

两个不同的类进行扭和。

### 例：

iOS为适配第三方HUD或者AFN版本升级更新出现问题，可以为第三方的接口建一个适配层，使用时使用自己的接口。以后第三方更新的话 只改适配层即可，不需要整个项目很多地方都修改。

适配层里面其实调的还是原来的接口，只是包了一下。

#### 三个

1. 原本的接口  已经实现的的方法
2. 客户希望的接口  虚函数
3. 适配器 继承希望的接口类

- 适配器类继承客户希望的接口类 
- 实现接口类中的函数方法
- 在该方法中实际使用原本的接口方法 （创建一个方法，把老接口方法的类参数传入，用一个属性去接收，里面组合）。

#### 例：

1：家里用电是220V电压， 用电器电脑使用18V电压，所以需要适配器转一下。使用是18V 但实际内部是用220V。

```c++
#include <iostream>
using namespace std;

// Current18 
// Current220
// Adapter 

class  Current18v
{
public:
	virtual void useCurrent18v() = 0;
};

class  Current220v
{
public:
	void useCurrent220v()
	{
		cout << "我是220v 欢迎使用" << endl;
	}
};

class Adapter : public Current18v
{
public:
	Adapter(Current220v *current)
	{
		m_current = current;
	}
	virtual void useCurrent18v()
	{
		cout << "适配器 适配 220v " ;
		m_current->useCurrent220v();
	}
protected:
private:
	Current220v *m_current;
};


void main()
{
	Current220v		*current220v = NULL;
	Adapter			*adapter = NULL;

	current220v = new Current220v;
	adapter = new Adapter(current220v);
	adapter->useCurrent18v();

	delete current220v ;
	delete adapter;

	cout<<"hello..."<<endl;
	system("pause");
	return ;
}
```



2：发动机  4400cc发动机   4500cc发动机



接口的转换，把一个名字转成另一个名字。