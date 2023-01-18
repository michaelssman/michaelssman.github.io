# Widget

widget只是界面的描述，并不是界面本身。渲染不是整体渲染。

想要更改大小颜色等等，都会重新渲染。

## 部件

无限嵌套部件

## MaterialApp

开发基于MaterialApp（APP素材），相当于UIKit的UIApplication的main。

```dart
MaterialApp(
  title: 'Flutter Demo', //安卓使用，切换应用显示
  debugShowCheckedModeBanner: false, //是否是调试
  theme: ThemeData(
    // This is the theme of your application.
    //
    // Try running your application with "flutter run". You'll see the
    // application has a blue toolbar. Then, without quitting the app, try
    // changing the primarySwatch below to Colors.green and then invoke
    // "hot reload" (press "r" in the console where you ran "flutter run",
    // or simply save your changes to "hot reload" in a Flutter IDE).
    // Notice that the counter didn't reset back to zero; the application
    // is not restarted.
    primaryColor: Colors.yellow,
    primarySwatch: Colors.grey, //主题色 影响整个app
    highlightColor: const Color.fromRGBO(1, 0, 0, 0), //点击
    splashColor: const Color.fromRGBO(1, 0, 0, 0.0), //弹开
  ),
  home: homeWidget, //主页面
);
```

## Scaffold

带有导航栏appBar的小部件，可以不带导航栏（可选）。

### Scaffold页面架构 

- appBar属性
  - 导航栏可以设置文字，颜色。而且可以自定义widget
  - centerTitle：title居中
  - actions：导航栏按钮
  - elevation: 0.0,//去除导航栏下面的线
- body属性 导航栏下面的内容
- bottomNavigationBar 类似iOS的tabBar

```dart
Scaffold(
  //Scaffold也是一个Widget 里面有appBar
  backgroundColor: Colors.white,
  appBar: AppBar(
    //导航栏 不写就不显示导航栏
    backgroundColor: themeColor, //导航栏背景色
    title: const Text('导航栏标题'), //导航栏标题
    centerTitle: true, //安卓 切换应用时显示
    elevation: 0.0, //去除导航栏底部的条
  ),
  body: body, //MyWidget父部件是body。开发界面是放到了body里面。
);
```

### 自定义Scaffold基类

```dart
class HHScaffold extends StatelessWidget {
  final Widget body;
  final String? title;
  const HHScaffold(this.body, {this.title, Key? key}) : super(key: key);
  // const ScaffoldDemo({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //Scaffold也是一个Widget 里面有appBar
      backgroundColor: Colors.white,
      appBar: AppBar(
        //导航栏 不写就不显示导航栏
        backgroundColor: themeColor, //导航栏背景色
        title: Text(title ?? 'Scaffold'), //导航栏标题
        centerTitle: true, //安卓 切换应用时显示
        elevation: 0.0, //去除导航栏底部的条
      ),
      body: body, //MyWidget父部件是body。开发界面是放到了body里面。
    );
  }
}
```

## ListView

### 1、数据固定写死的

```dart
ListView(
  children: [
    listViewSection('现金'),
    DiscoverCell(
      imageName: defaultImageName,
      title: '现金',
      onTapCallBack: () {},
    ),
    listViewSection('网络'),
    DiscoverCell(
      title: '微信',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
    lineWidget(),
    DiscoverCell(
      title: '支付宝',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
    listViewSection('银行卡'),
    DiscoverCell(
      title: '民生',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
    lineWidget(),
    DiscoverCell(
      title: '建设',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
  ],
),
```

### 2、数据和UI分离

构造方法

```dart
ListView.builder(
	shrinkWrap: true,//根据ListView的内容大小来展示
  itemBuilder: _itemForRow, //itemBuilder是一个回调，方法返回一个widget 相当于cell，鼠标放上去根据提示快速创建createMethod方法
  itemCount: datas.length,//总共有多少个item
),
```

例：

```dart
ListView.builder(
  itemBuilder: (BuildContext context, int index) {
    return ListTile(
      title: Text(options[index]),
      onTap: () {
        Navigator.of(context).pop(index);
      });
  },
  itemCount: options.length,
)
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

类似iOS的UIView，一个空的小部件，很常用。**一般写部件都会用Container包一下，方便抽取和调试。**

Container可以设置间隔、大小、背景颜色、圆角、边框、背景图片。

父部件会随子部件变化，弹性布局。

child:Container内容小部件

### alignment

```
alignment: Alignment(0.0, 0.0),//中心点
```

x和y是从-1.0到1.0。原点在中间位置。

### margin属性

- 内边距，让小部件往里面缩
- EdgeInsets.all(10)上下左右都往里面缩10
- 每一个视图的widget都可以看成一个矩形

### color属性

- 当前这个widget的颜色
- 技巧：当布局某个widget的时候，先给个颜色，便于调整布局。

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
    border: Border.all(width: 2.0, color: Colors.amberAccent),
    //背景颜色
    color: Colors.green,
    //圆角
    borderRadius: const BorderRadius.all(Radius.circular(20.0)),
    //背景图片
    image: const DecorationImage(
      image: NetworkImage(
        'https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fwww.gpbctv.com%2Fuploads%2F20210424%2Fzip_1619246266UkP6CL.jpg&refer=http%3A%2F%2Fwww.gpbctv.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1669529410&t=e2a5d5b4f49e3977d1b24560f354029e')),
  ),
  padding: const EdgeInsets.all(20),
  margin: const EdgeInsets.all(50),
  // color: Colors.red, //设置了decoration就不能设置color属性了
  child: const Text(
    'Hello World',
    style: TextStyle(
      fontSize: 20,
    ),
  ),
);
```

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

## FutureBuilder

异步渲染页面

网络请求会用，刷新UI。

future 更新UI使用的数据来源，异步的网络数据。

没有数据的时候，也要渲染，不能卡住UI。有数据的时候渲染真正的UI，更新UI。

数据少的时候可以用FutureBuilder，数据多复杂的时候 使用一个数组保存数据。
