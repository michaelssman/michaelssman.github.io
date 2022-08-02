# 架构

高内聚，低耦合。（谁的事情谁做）。

类可以多次使用，依赖小。

## 问题一：view和model高耦合

cell的代理中为cell赋值，cell对model强依赖，耦合性高。

view中setModel方法view和model的依赖。UI不应该改变模型，难以维护，数据不安全。

模型改变UI，UI改变模型。解决UI和model不同步问题使用通讯：

1. 代理
2. 通知
3. block
4. 指针 方法
5. 等等

## 问题二：VC加重

1. 繁重的UI
2. 啰嗦的业务逻辑
3. 很长的网络层
4. 难受的代理
5. 内部方法
6. 等等

### 轻量级VC

**VC的任务就只要建立依赖关系。**

定义一个view，在`loadView`方法中设置self.view = view;

VC负责把model赋值UI

建立依赖关系，把UI和model进行绑定

vc过重： 封装 抽取 基类

把数据（请求）放到present类中

网络层。 代理层

函数式封装：cell和model回调绑定。cell代理方法不用每次都写

## MVP

**面向协议编程**。接口

网络层，业务逻辑，代理（tableView代理）使用中间类：使用block保存代码块，在cell中调用。

1. 数据提供层
2. 数据业务处理层
3. 建立关系

cell.model 需要解藕

cell复用问题：

UI（cell）变了 model没有变

使用代理进行通讯

### Present

VC中抽离的放到了present里。VC只需要做建立依赖关系。

- 数据的加载，网络请求的数据，UI的响应方法都放在这里。
- 定义协议，声明delegate属性，加载完数据之后刷新UI，调用代理去刷新UI。

### View

View和Model解耦，cell中不包含model，解耦。

- 点击button，点击cell上控件的响应事件，定义协议方法，调用代理去执行，代理就是Present。

  cell的代理设置为Present是在Controller中设置的。

- 数据的刷新加载更多。 定义协议，Present遵循协议，实现加载数据代理方法。

#### 多个列表UI相似 数据不同

可以使用同一个控制器。

数据源在Present中初始化。

### 双向绑定

点击cell上的button（UI）改变model。

改变model到某个值的时候 刷新UI。

使用代理Delegate

整个模块接口暴露层。根据业务需要增加接口。需求驱动接口，接口驱动代码。

MVP --- 需求 -- 写接口（暴露的接口） -- 代理三部曲

多人开发。可读性强。

### 适配器模式设计

多种cell的时候，iPhone8 iPhone12等带刘海不带刘海等机型。

大部分一样，只有局部不同。

去中心化，设置一个BaseAdaper，模块Home继承BaseAdaper单独自己的HomeAdaper。

#### context+adapter设计

present只适合简单的逻辑，复杂的需要一个adapter设置

context通过字符串一个命名规范，生成XXPresenter，避免中间层的耦合。

View和model需要有关系的时候，可以由一个中间者管理context。降低model和view之间的依赖。

self（ViewController）持有context，context持有present和UI。

context只具备调用的权利，不需要做业务细节。

controller，view等等几乎所有对象都有context，context在NSObject分类中。

页面可能有很多子view，父类有context，子view可以找到父视图（响应链），子view的context和superView使用共享同一个。

### 臃肿的胶水代码（代理）

绑定的

定义宏：什么响应什么代理的什么方法。

流程：

1. 适配器设计
2. UI
3. 请求数据
4. 数据和UI（请求数据 刷新UI）

### MVP优缺点

- 模型与视图完全分离，我们可以修改视图而不影响模型。
- 可以更高效地使用模型，因为所有的交互都发生在一个地方--Present内部
- 我们可以将一个present用于多个视图，而不需要改变present的逻辑。这个特性非常有用，因为视图的变化总是比模型的变化频繁
- 如果我们把逻辑放在present中，那么我们就可以脱离用户接口来测试这些逻辑（单元测试）。

MVP 耦合度低方便单元测试， 但是增加很多代码。

### MVP和MVVM

MVP

使用代理，写接口。

嵌套层次比较少，敏捷开发，迭代方便。

MVVM

使用block。

一层一层嵌套，嵌套比较多，维护麻烦。
