# 代理模式

## 概念

代理模式（Proxy模式），是构造型的设计模式之一，它可以为其他对象提供一种代理（Proxy）以控制对这个对象的访问。	
所谓代理，是指具有与代理元（被代理的对象）具有相同的接口的类，客户端必须通过代理与被代理的目标类交互，而代理一般在交互的过程中（交互前后），进行某些特别的处理。

#### 适合于

为其他对象提供一种代理以控制对这个对象的访问。

#### 例子

卖书
定义一个抽象类 定义一个卖书的方法接口
定义一个当当网类 去实现卖书 还可以添加自己的处理 可以打折等。

一共有三个类。

1. subject（抽象主题角色）：
   	真实主题与代理主题的共同接口。
2. RealSubject（真实主题角色）：
   	定义了代理角色所代表的真实对象。 
3. Proxy（代理主题角色）：
   	含有对真实主题角色的引用，代理角色通常在将客户端调用传递给真是主题对象之前或者之后执行某些操作，而不是单纯返回真实的对象。

### 提示

a中包含b类；a、b类实现协议类protocol 
a包含了一个类b，类b实现了某一个协议（一套接口）

示例代码：
```C++
#include "iostream"
using namespace std;

//接口
class AppProtocol
{
public:
	virtual int ApplicationDidFinsh() = 0;
protected:
private:
};

//协议实现类
class AppDelegate : public AppProtocol
{
public:
	AppDelegate() { }
	virtual int ApplicationDidFinsh()  //cocos2dx函数的入口点
	{
		cout<<"ApplicationDidFinsh do...\n";
		return 0;
	}
};

//Application是代理类，在代理类中包含一个真正的实体类
class Application
{
public:
	Application()
	{
		ap = NULL;
	}
public:
	void run()
	{
		ap = new AppDelegate();
		ap->ApplicationDidFinsh();
		delete ap;
	}
protected:
private:
	AppDelegate *ap;
};

//好处：main函数不需要修改了。只需要修改协议实现类
void main()
{
	Application *app = new Application();
	app->run();

	if (app == NULL)
	{
		free(app);
	}

	cout<<"hello..."<<endl;
	system("pause");
}
```

- 一个协议类
- 一个协议实现类
- 一个代理类

实质就是找人替你做事  事情的完成由别人去做。

## iOS中的代理模式

要使协议中的方法是可选的，需要使用`@objc`属性标记协议，并且协议必须继承自`NSObjectProtocol`。因为可选协议要求是Objective-C的特性。这样，如果`ViewController`没有实现`didCompleteTask`方法，程序就不会编译通过，除非你将该方法标记为可选。

下面是如何声明一个可选代理方法的例子：

首先，将协议标记为`@objc`并使方法可选：

```swift
@objc protocol TaskDelegate: AnyObject {
    @objc optional func didCompleteTask(_ sender: TaskManager)
}
```

`TaskManager`类：

```swift
class TaskManager {
    weak var delegate: TaskDelegate?

    func completeTask() {
        print("Task completed.")
        delegate?.didCompleteTask?(self)
    }
}
```

注意，在调用可选方法时，你需要在方法名后面添加`?`来表明这是一个可选的调用。

## 总结

接口：定义一套接口 造火箭

A类delegate：遵循协议，实现接口 造火箭

B类delegate：遵循协议，实现接口 造火箭

C类delegate：遵循协议，实现接口 造火箭

D类：可以调A（delegate）实现造火箭接口的方法，可以调B实现的方法。

