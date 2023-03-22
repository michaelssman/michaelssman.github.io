# Scaffold

带有导航栏appBar的小部件，可以不带导航栏（可选）。

## Scaffold页面架构 

- appBar属性。导航栏 不写就不显示导航栏。
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

## 自定义Scaffold基类

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

## 