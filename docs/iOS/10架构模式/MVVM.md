# MVVM

谈到MVVM不得不先说一下MVC，MVC(Model-View-Controller)。

Model模型：用来呈现数据。

View视图：用来呈现用户界面。

Controller控制器：用来调节模型与视图之间的交互。

在 iOS 应用中日益增长的重量级视图控制器的问题。在典型的 MVC 应用里， 许多逻辑被放在 View Controller 里。

它们中的一些确实属于 View Controller，但更多的是所谓的“表示逻辑（presentation logic），为了不让控制器日益增大,便于测试管理,便出现了MVVM。

MVVM：它其实是一个 MVC 的增强版，并将表示逻辑从 Controller 移出放到一个新的对象里，即 View Model。

在 iOS 上使用 MVVM 的动机,就是让它能减少 View Controller 的复杂性并使得表示逻辑更易于测试。

MVVM模式是Model-View-ViewMode模式的简称。由视图(View)、视图模型(ViewModel)、模型(Model)三部分组成。通过这三部分实现UI逻辑、呈现逻辑和状态控制、数据与业务逻辑的分离。

**使用MVVM模式有几大好处：**

1. 低耦合。View可以独立于Model变化和修改，一个ViewModel可以绑定到不同的View上，当View变化的时候Model可以不变，当Model变化的时候View也可以不变。
2. 可重用性。可以把一些视图的逻辑放在ViewModel里面，让很多View重用这段视图逻辑。
3. 独立开发。开发人员可以专注与业务逻辑和数据的开发(ViewModel)。设计人员可以专注于界面(View)的设计。
4. 可测试性。可以针对ViewModel来对界面(View)进行测试

**1. 视图(View)**

视图负责界面和显示。它通过DataContext(数据上下文)和ViewModel进行数据绑定，不直接与Model交互。 

可以绑定Behavior/Comand来调用ViewModel的方法，Command是View到ViewModel的单向通行，通过实现Silverlight提供的IComand接口来实现绑定，让View触发事件，ViewModel来处理事件，以解决事件绑定功能。

**2. 视图模型(ViewModel)**

ViewModel: 它位于 View/Controller 与 Model 之间。

视图模型主要包括界面逻辑和模型数据封装，Behavior/Command事件响应处理，绑定属性定义和集合等。

它是View和Model的桥梁，是对Model的抽象，比如：Model中数据格式是“年月日”，可以在ViewModel中转换Model的数据为“日月年”供View显示。

实现视图模型需要实现Silverlight提供的接口INotifyPropertyChanged， INotifyPropertyChanged接口用于实现属性和集合的变更通知(Change Notifications)。

使得在用户在视图上所做的操作都可以实时通知到视图模型，从而让视图模型对象有的模型进行正确的业务操作。

View的代码隐藏(Code-Behind)部分可能包含界面逻辑或者应用逻辑的代码，这些代码会很难进行单元测试，应根据具体情况尽量避免。

**ViewModel中放信号。**

---

**代码示例：**

1、首先是model层的代码，基于JSONModel封装了BaseModel类（基类：以后的Model都可继承此类），继承自BaseModel，实现HomeModel类。

2、然后是View层的代码，View层控件全部用懒加载方式，尽可能减少内存消耗。

3、接下来看ViewModel层，对封装好的NetWork进行处理，request网络数据存储在HomeModel里，最后将数据用Block带出去，方便在VC中使用数据，reloadData。

4、最终，HomeViewController 将会变得非常轻量级：

MVVM没有破坏 MVC 的现有结构，只不过是移动了一些代码。

只要将 MVC 中的 controller 中的展示逻辑抽取出来，放置到 viewModel 中，然后通过一定的技术手段，来同步 view 和 viewModel ，就完成了 MVC 到 MVVM 的转变。

---

使用block。

加载数据

loadData加载本地数据或者网络请求数据，都在ViewModel中加载。

加载完成之后，通过succeedBlock回调到Controller

**双向绑定**	

使用block通讯 逆向传值

正向：UI给model。不能持有。

所以需要响应式。UI信号的发送，打击按钮cell，实时观察跟新数据，更新UI使用block。

block写一次，可以多处调用。



### view和viewModel绑定