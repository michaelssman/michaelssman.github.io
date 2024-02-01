# Widget

widget只是界面的描述，并不是界面本身。渲染不是整体渲染。

想要更改大小颜色等等，都会重新渲染。

## 部件

无限嵌套部件

## Container

类似iOS的UIView，一个空的小部件，很常用。**一般写部件都会用Container包一下，方便抽取和调试。**

Container可以设置间隔、大小、背景颜色、圆角、边框、背景图片。

父部件会随子部件变化，弹性布局。

child:Container内容小部件

### alignment

```
alignment: Alignment(0.0, 0.0),//中心点
```

x和y是从-1.0到1.0。原点在中间位置。

### margin

外边距

```dart
margin: const EdgeInsets.only(top: 20, bottom: 20, left: 20, right: 10),
margin: const EdgeInsets.all(10),//上下左右都往里面缩10
```

每一个视图的widget都可以看成一个矩形

### padding

内边距

```dart
padding: const EdgeInsets.all(20),
```

### decoration圆角和color

技巧：当布局某个widget的时候，先给个颜色，便于调整布局。

```dart
Container(
  alignment: Alignment.center, //控制child对齐方式
  // child的额外约束条件
  constraints: const BoxConstraints.expand(
    height: 200,
  ),
  //Container变换矩阵
  transform: Matrix4.rotationZ(0.3),
  //child的装饰
  decoration: BoxDecoration(
    //设置边框
    border: Border.all(color: Colors.amberAccent, width: 2.0),
    //背景颜色
    color: Colors.green,
    //圆角
    borderRadius: const BorderRadius.all(Radius.circular(20.0)),
		/**
    //单独设置圆角
    borderRadius: BorderRadius.only(
      topLeft: Radius.circular(20.0),
      topRight: Radius.circular(20.0),
    ),
		*/
    //背景图片
    image: const DecorationImage(
      image: NetworkImage('https://www.hh.imageurl.png')),
    //渐变背景色
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [Colors.blue, Colors.purple],
    ),
  ),
  // color: Colors.red, //设置了decoration就不能设置color属性了
  child: const Text(),
);
```

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

## FutureBuilder

异步渲染页面

网络请求会用，刷新UI。

future 更新UI使用的数据来源，异步的网络数据。

没有数据的时候，也要渲染，不能卡住UI。有数据的时候渲染真正的UI，更新UI。

数据少的时候可以用FutureBuilder，数据多复杂的时候 使用一个数组保存数据。
