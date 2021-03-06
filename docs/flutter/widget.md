# Widget

widget只是界面的描述，并不是界面本身。渲染不是整体渲染。

想要更改大小颜色等等，都会重新渲染。

# 部件

无限嵌套部件

## Scaffold

带有导航栏appBar的小部件，可以不带导航栏（可选）。

切换页面的时候，会把之前的那个tab给干掉。不在widget树中的页面都会被销毁。

```
onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
```

onTap方法调用setState，树中就没有了。所以需要把所有的tab都放到**widget树**中，切换的时候是显示不显示的问题。

- Scaffold页面架构 
  - appBar属性
    - 导航栏可以设置文字，颜色。而且可以自定义widget
    - centerTitle：title居中
    - actions：导航栏按钮
    - elevation: 0.0,//去除导航栏下面的线
  - body属性 导航栏下面的内容
  - bottomNavigationBar 类似iOS的tabBar

## ListView

类似iOS中的tableView

构造方法

```
ListView.builder(
	shrinkWrap: true,//根据ListView的内容大小来展示
  itemBuilder: _itemForRow, //itemBuilder是一个回调，方法返回一个widget 相当于cell，鼠标放上去根据提示快速创建createMethod方法
  itemCount: datas.length,//总共有多少个item
),
```

- itemCount

  总共有多少个item

- itemBuilder

  是一个回调函数：Function(BuildContext context, int index);

  作用

  返回每一个item，类似iOS中tableView的cellForRow

  参数

  context

  index：返回第几个item

listView滚动的时候需要一个controller属性，

#### ListView滚动

item的高度 必须要提前知道位置是多少，根据数据内容计算。

## Container

类似iOS的UIView，一个空的小部件，很常用。**一般写部件都会用Container包一下，方便抽取。**

Container可以给大小，可以给颜色，方便调试。

父部件会随子部件变化，弹性布局。

```
alignment: Alignment(0.0, 0.0),//中心点
```

x和y是从-1.0到1.0。原点在中间位置。

margin属性

- 内边距，让小部件往里面缩
- EdgeInsets.all(10)上下左右都往里面缩10
- 每一个视图的widget都可以看成一个矩形

color属性

- 当前这个widget的颜色
- 技巧：当布局某个widget的时候，先给个颜色，便于调整布局。

## Image 图片小部件

Image.network(图片url地址), 构造函数：从网络上加载一张图片

## SizeBox

用来占位的小部件，在复杂的布局中很常用。

## 自定义widget

**万物皆widget**

widget有两大类

1. 有状态StatefulWidget

   widget内部的部件可以改变状态。

2. 无状态StatelessWidget

   不能更改，不可变。如果想变就换一个。

**自定义widget要能够渲染必须重写build方法**，build方法返回渲染widget。快捷键：`alt+回车`

#### 数据对象widget

属性的值可以变化，定义一个数据类（可变的），与界面没有关系，里面的属性是可变的。模型对象，里面的属性可以变。通过模型对象创建新的界面对象。

## 抽取widget

新建.dart文件

输入stl自动出来代码块。然后输入类的名字就会自动生成一个StatelessWidget类。

```dart
class ListViewDemo extends StatelessWidget {
  const ListViewDemo({Key? key}) : super(key: key);//唯一定位的

  @override
  Widget build(BuildContext context) {
    return Container();
  }
}
```

## GestureDetector

可以响应点击

onTap：没有参数的回调

## FutureBuilder

异步渲染页面

网络请求会用，刷新UI。

future 更新UI使用的数据来源，异步的网络数据。

没有数据的时候，也要渲染，不能卡住UI。有数据的时候渲染真正的UI，更新UI。

数据少的时候可以用FutureBuilder，数据多复杂的时候 使用一个数组保存数据。
