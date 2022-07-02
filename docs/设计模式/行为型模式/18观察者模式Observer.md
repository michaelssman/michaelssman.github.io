# 观察者模式

## 概念

Observer模式是行为模式之一，它的作用是当一个对象的状态发生变化时，能够自动通知其他关联对象，自动刷新对象状态。

Observer模式提供给关联对象一种同步通信的手段，使某个对象与依赖它的其他对象之间保持状态同步。

## 典型应用

- 侦听事件驱动程序设计中的外部事件
- 侦听/监视某个对象的状态变化
- 发布者/订阅者（publisher/subscriber）模型中，当一个外部事件（新的产品，消息的出现等等）被触发时，通知邮件列表中的订阅者

## 适用于

定义对象间的一种一对多的依赖关系，使得当一个对象改变状态，则所有依赖于他们的对象都会得到通知。

## 使用场景

定一个了一种一对多的关系，让多个观察对象（公司员工）同时监听一个主题对象（秘书），主题对象状态发生变化时，会通知所有的观察者，使它们能够更新自己。

### 例

秘书与员工
秘书在门口坐着  老板来了就通知所有员工老板来了，员工就好好干活。秘书看见老板走了就通知所有员工老板走了，员工就可以玩游戏了。
好好干活和打游戏都是员工（观察者）实现的 

## 被观察者

里面有一个观察者列表，给所有的观察者发送通知。

秘书是被观察者对象

秘书里面有一个所有观察者员工对象的集合 可以有很多的观察者。

秘书添加观察者员工对象

秘书有一个通知事件，秘书实现去通知 通知的时候 遍历 通知所有的对象 把通知的内容传给所有订阅的观察者。给所有的观察者发送情报。

秘书实现去通知函数， 监听事件去通知的时候 遍历 通知所有的对象 把通知的内容传给观察者，调用观察者的update函数。

## 观察者

**观察者员工持有一个秘书被观察者的引用**

观察者做收到消息之后的动作实现update方法。

#### 例：

```c++

#include <iostream>
using namespace std;
#include "string"
#include "list"


class Secretary;


//π€≤Ï’ﬂ 
class PlayserObserver
{
public:
	PlayserObserver(Secretary *secretary)
	{
		this->m_secretary = secretary;
	}
	void update(string action)
	{
		cout << "action:" << action << endl;
		cout << "¿œ∞Â¿¥¡À Œ“∫‹∫¶≈¬∞°..." << endl;
	}
private:
	Secretary *m_secretary;
};
//
class Secretary
{
public:
	Secretary()
	{
		m_list.clear();
	}
	void Notify(string info)
	{
		//∏¯À˘”–µƒ π€≤Ï’ﬂ ∑¢ÀÕ «È±®
		for ( list<PlayserObserver *>::iterator it=m_list.begin(); it!=m_list.end(); it++)
		{
			(*it)->update(info); //
		}
	}

	void setPlayserObserver(PlayserObserver *o)
	{
		m_list.push_back(o);
	}

private:
	list<PlayserObserver *> m_list;
};
void main()
{
	Secretary			*secretary = NULL;
	PlayserObserver		*po1 = NULL;
	PlayserObserver		*po2 = NULL;

	secretary = new Secretary;
	po1 = new PlayserObserver(secretary);
	po2 = new PlayserObserver(secretary);

	secretary->setPlayserObserver(po1);
	secretary->setPlayserObserver(po2);

	secretary->Notify("¿œ∞Â¿¥¡À") ;
	secretary->Notify("¿œ∞Â◊ﬂ¡À");
	delete secretary ;
	delete po1 ;
	delete po2 ;

	system("pause");
	return ;
}

```

观察者是做相应处理的。被观察者是发信号的。