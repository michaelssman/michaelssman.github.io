# 策略模式

Map<策略类的名称, 策略的具体实现> m;

减少if else判断。

## 概念

Strategy模式也叫策略模式是行为模式之一。

它对一系列的算法加以封装，为所有算法定义一个抽象的算法接口，并通过继承该抽象算法接口对所有的算法加以封装和实现，具体的算法选择交由客户端决定（策略）。

Strategy模式主要用来平滑地处理算法的切换 。	

## 角色和职责

![image.png](https://upload-images.jianshu.io/upload_images/1892989-70cc73c3b4c8959c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- Strategy
  策略（算法）抽象。
  
- ConcreteStrategy    
  各种策略（算法）的具体实现。
  
- Context    	
  策略的外部封装类，或者说策略的容器类。根据不同策略执行不同的行为。策略由外部环境决定。 

  context持有算法的引用

客户端面向context编程，以后添加新的算法，可以和客户端进行解耦合。

### 适用于

​	准备一组算法，并将每一个算法封装起来，使得它们可以互换。

### 策略模式优缺点

#### 优点：

1. 策略模式提供了管理相关的算法族的办法。

   策略类的等级结构定义了一个算法或行为族。恰当使用继承可以把公共的代码移到父类里面，从而避免重复的代码。

2. 策略模式提供了可以替换继承关系的办法。继承可以处理多种算法或行为。

   如果不是用策略模式，那么使用算法或行为的环境类就可能会有一些子类，每一个子类提供一个不同的算法或行为。但是，这样一来算法或行为的使用者就和算法或行为本身混在一起。决定使用哪一种算法或采取哪一种行为的逻辑就和算法或行为的逻辑混合在一起，从而不可能再独立演化。继承使得动态改变算法或行为变得不可能。

3. 使用策略模式可以避免使用多重条件转移语句。

   多重转移语句不易维护，它把采取哪一种算法或采取哪一种行为的逻辑与算法或行为的逻辑混合在一起，统统列在一个多重转移语句里面，比使用继承的办法还要原始和落后。

#### 缺点：

1. 客户端必须知道所有的策略类，并自行决定使用哪一个策略类。这就意味着客户端必须理解这些算法的区别，以便适时选择恰当的算法类。换言之，策略模式只适用于客户端知道所有的算法或行为的情况。
2. 策略模式造成很多的策略类。有时候可以通过把依赖于环境的状态保存到客户端里面，而将策略类设计成可共享的，这样策略类实例可以被不同客户端使用。换言之，可以使用享元模式来减少对象的数量。



- 一个策略的抽象基类

- 若干个策略的实现类

- 一个context类 持有一个策略的引用  里面有一个策略的属性。和一个操作方法 策略去执行任务。

  上下文持有一个策略的引用

可以自由自在的替换策略



### 例：

有一个策略，加密算法。有DES加密，有AES加密。

再有一个上下文Context，Context持有策略。

使用的时候，new一个策略，new一个上下文，把策略给上下文 ，然后上下文去执行。

上下文里是A则执行A的算法，是B的时候则执行B的算法。

客户端可以透明的替换算法。

```c++

//Symmetric encryption

class Strategy
{
public:
	virtual void SymEncrypt() = 0;
};

class Des : public Strategy
{
public:
  virtual void SymEncrypt()
  {
  cout << "Des加密" << endl; 
  }
};

class AES : public Strategy
{
public:
  virtual void SymEncrypt()
  {
  cout << "AES加密" << endl; 
  }
};

class Context
{
public:
  Context(Strategy *strategy)
  {
  p = strategy;
  }
  void Operator()
  {
  p->SymEncrypt();
  }
private:
	Strategy *p;
};

//算法的实现 和 客户端的使用 解耦合

//使得算法变化，不会影响客户端

void main()

{

  /*不符合开闭原则

  Strategy *strategy = NULL;

  strategy = new AES;

  strategy->SymEncrypt();

  delete strategy;

  strategy = new Des;

  strategy->SymEncrypt();

  delete strategy;

  */

  Strategy *strategy = NULL;

  Context *ctx = NULL;

  strategy = new AES;

  ctx = new Context(strategy);

  ctx->Operator();

  delete strategy;

  delete ctx;

  cout<<"hello..."<

  system("pause");

  return ;

}

```

### 总结

context持有一个当前策略的引用，客户端就可以自由自在的替换策略。