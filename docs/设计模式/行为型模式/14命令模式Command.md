# 命令模式

## 概念

Command模式也叫命令模式 ，是行为设计模式的一种。

Command模式通过被称为Command的类封装了对目标对象的调用行为以及调用参数。

在面向对象的程序设计中，一个对象调用另一个对象，一般情况下的调用过程是：创建目标对象实例；设置调用参数；调用目标对象的方法。

**但在有些情况下有必要使用一个专门的类对这种调用过程加以封装，我们把这种专门的类称作command类。**

一个对象调用另一个对象一般情况下是直接new该对象然后调用对象的方法，命令模式就是设计一个command类去调用这个对象 。

整个调用过程比较繁杂，或者存在多处这种调用。这时，使用Command类对该调用加以封装，便于功能的再利用。

调用前后需要对调用参数进行某些处理。调用前后需要进行某些额外处理，比如日志，缓存，记录历史操作等。 

## 角色和职责

![image.png](https://upload-images.jianshu.io/upload_images/1892989-79447a1dd7f4c40d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- Command
  Command命令的抽象类。
- ConcreteCommand
   Command的具体实现类。
- Receiver
  需要被调用的目标对象。
- Invorker
  通过Invorker执行Command对象。

医生功能比较多的时候 看各种病 通过命令就把医生分解了，通过每一种命令看每一种病。

医生越来越牛 功能越来越多，病人也越来越多的时候，就需要排队。也就是把一个一个客户端请求队列化集合化。

Receiver就是医生。

Invorker就相当于一个小护士，把所有的请求都收集起来，然后让医生一个一个的看病，一个一个的处理。

Invorker-持有Command 

Invorker的好处就是，客户端可以面向命令进行编程，Invorker调用不同的命令，对命令进行解耦合。

## 适用于

​	**是将一个请求封装为一个对象，从而可用不同的请求对客户端进行参数化；对请求排队或记录请求日志，以及支持可撤销的操作。** 

命令模式是一种对象行为型模式，其别名为动作（Action）模式或事务（Transaction）模式。

对象的调用，使用一个command类去调用。

## 例

医生看病：医生可以看各种各样的病：可以看眼科 可以看鼻科 等等。

1. 一般情况下  医生直接看病 直接使用医生去看病

   直接new一个医生然后调用看眼科 看耳科。这种情况下客户端和医生的耦合度太高了，如果医生生病了就没法看病了。

2. 通过命令。

   做不同的命令 把医生注入到命令类里面  调用的时候 通过不同的命令来看不同的病。

   看眼病命令类持有一个医生对象，调用医生的看眼病函数去看眼病。

   看耳病命令类持有一个医生对象，调用医生的看耳病函数去看耳病。

病人多了 不同命令类  调用医生去看病

护士下命令 让医生去看病

### 高级用法

批量下单 

护士长  可以收集多个命令，有一个命令list集合  一组命令 然后去调用 

添加看眼科命令，添加看耳科命令。批量处理。

可以添加命令到list中  提交病历，批量下达命令，让医生执行。效率更高。

例：
```c++
#include <iostream>
using namespace std;
#include "list"

class Doctor
{
public:
	void treat_eye()
	{
		cout << "医生 治疗 眼科病" << endl;
	}

	void treat_nose()
	{
		cout << "医生 治疗 鼻科病" << endl;
	}
};

class Command
{
public:
	virtual void treat() = 0;
};
class CommandTreatEye : public Command
{
public:
	CommandTreatEye(Doctor *doctor)
	{
		m_doctor = doctor;
	}
	void treat()
	{
		m_doctor->treat_eye();
	}
private:
	Doctor *m_doctor;
};


class CommandTreatNose : public Command
{
public:
	CommandTreatNose(Doctor *doctor)
	{
		m_doctor = doctor;
	}
	void treat()
	{
		m_doctor->treat_nose();
	}
private:
	Doctor *m_doctor;
};


class BeautyNurse
{
public:
	BeautyNurse(Command *command)
	{
		this->command = command;
	}
public:
	void SubmittedCase() //提交病例 下单命令
	{
		command->treat();
	}
protected:
private:
	Command *command;
};

//护士长
class HeadNurse 
{
public:
	HeadNurse()
	{
		m_list.clear();
	}
	
public:
	void setCommand(Command *command)
	{
		m_list.push_back(command);
	}
	void SubmittedCase() //提交病例 下单命令
	{
		for (list<Command *>::iterator it=m_list.begin(); it!=m_list.end(); it++)
		{
			(*it)->treat();
		}
	}
private:
	list<Command *> m_list;
};



void main21_1()
{
	//1 医生直接看病
	/*
	Doctor *doctor = new Doctor ;
	doctor->treat_eye();
	delete doctor;
	*/

	//2 通过一个命令 医生通过 命令 治疗 治病
	Doctor *doctor = new Doctor ;
	Command * command = new CommandTreatEye(doctor); //shift +u //转小写 shift+ctl + u转大写
	command->treat();
	delete command;
	delete doctor;
	return ;
}


void main21_2()
{
	//3 护士提交简历 给以上看病
	BeautyNurse		*beautynurse = NULL;
	Doctor			*doctor = NULL;
	Command			*command  = NULL;

	doctor = new Doctor ;

	//command = new CommandTreatEye(doctor); //shift +u //转小写 shift+ctl + u转大写
	command = new CommandTreatNose(doctor); //shift +u //转小写 shift+ctl + u转大写
	beautynurse = new BeautyNurse(command);
	beautynurse->SubmittedCase();
	
	delete doctor;
	delete command;
	delete beautynurse;
	return ;
}


//4 通过护士长 批量的下单命令
void main21_3()
{
	//护士提交简历 给以上看病
	HeadNurse		*headnurse = NULL;
	Doctor			*doctor = NULL;
	Command			*command1  = NULL;
	Command			*command2  = NULL;

	doctor = new Doctor ;

	command1 = new CommandTreatEye(doctor); //shift +u //转小写 shift+ctl + u转大写
	command2 = new CommandTreatNose(doctor); //shift +u //转小写 shift+ctl + u转大写

	headnurse = new HeadNurse(); //new 护士长
	headnurse->setCommand(command1);
	headnurse->setCommand(command2);

	headnurse->SubmittedCase(); // 护士长 批量下单命令

	delete doctor;
	delete command1;
	delete command2;
	delete headnurse;
	return ;
}


void main()
{
	//main21_1();
	//main21_2();
	main21_3();
	cout<<"hello..."<<endl;
	system("pause");
	return ;
}
```

### 总结

命令模式就是 把一个功能很多很强大的类 分成很多小命令来使用。

医生多才多艺，会看各种病，把看每一种病通过做对应的一个命令来调用。主要是解耦合。

命令模式把动作进行分解，分解成一个发起者，真正执行动作的人。

医生可以看很多病，还可以有各种医生。

#### 命令模式的优点

- 降低系统的耦合度。
- 新的命令可以很容易地加入到系统中。
- 可以比较容易地设计一个命令队列和宏命令（组合命令）。
- 可以方便地实现对请求的Undo和Redo。