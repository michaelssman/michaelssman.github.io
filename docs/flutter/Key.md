# Key

只要继承Widget的都有一个key，Key是用来标识小部件。区分widget。

StatefulWidget的Widget和State是分开的。

## Widget

```dart
@immutable
abstract class Widget extends DiagnosticableTree {
  /// Initializes [key] for subclasses.
  const Widget({ this.key });

  final Key? key;

  @protected
  @factory
  Element createElement();

  /// A short, textual description of this widget.
  @override
  String toStringShort() {
    final String type = objectRuntimeType(this, 'Widget');
    return key == null ? type : '$type-$key';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties.defaultDiagnosticsTreeStyle = DiagnosticsTreeStyle.dense;
  }

  @override
  @nonVirtual
  bool operator ==(Object other) => super == other;

  @override
  @nonVirtual
  int get hashCode => super.hashCode;

  /// 增量渲染，改变的内容渲染，大量的内容复用，哪里改变了哪里没变通过下面方法。
  /// oldWidget和newWidget类型一样 并且key也一样
  static bool canUpdate(Widget oldWidget, Widget newWidget) {
    return oldWidget.runtimeType == newWidget.runtimeType
        && oldWidget.key == newWidget.key;
  }

  static int _debugConcreteSubtype(Widget widget) {
    return widget is StatefulWidget ? 1 :
           widget is StatelessWidget ? 2 :
           0;
  }
}
```

Key是一个抽象类，有一个工厂构造方法。创建ValueKey，值是任意类型。

直接子类LocalKey，GlobalKey。

## GlobalKey

GlobalKey对应某一个Widget State Element(Context)。

帮助我们访问某个Widget的信息，类似tag标记的功能。

根据`key.currentState`找到state，就可以使用state里面的data和调用`setState(() {});`方法。

```dart
import 'package:flutter/material.dart';

class GlobalKeyDemo extends StatelessWidget {
  final GlobalKey<_ChildPageState> _globalKey = GlobalKey(); //创建GlobalKey对象

  GlobalKeyDemo({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('GlobalKeyDemo'),
      ),
      body: ChildPage(
        key: _globalKey,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _globalKey.currentState!.setState(() {
            _globalKey.currentState!.data =
                'old' + _globalKey.currentState!.count.toString();
            _globalKey.currentState!.count++;
          });
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}


class ChildPage extends StatefulWidget {
  const ChildPage({Key? key}) : super(key: key);

  @override
  State<ChildPage> createState() => _ChildPageState();
}

class _ChildPageState extends State<ChildPage> {
  int count = 0;
  String data = 'hello';
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: [Text(count.toString()), Text(data)],
      ),
    );
  }
}
```

### 自定义键盘的显示

自定义键盘使用StatefulWidget包装，通过key找到自定义键盘的state，和里面的TextEditingController、isVisible。

## LocalKey

用来区别哪个Element保留，哪个Element删除。diff算法的核心所在。

- ValueKey以值作为参数（数字，字符串）
- ObjectKey以对象作为参数
- UniqueKey()创建唯一标识，整个项目只有一个，不会被复用。

增量渲染对比的是Widget树和Element树。

Widget树：

- Widget111
- Widget222
- Widget333

Element树：

- Element111
- Element222
- Element333

当删除Widget111的时候，会调Element111的canUpdate，canUpdate里面会判断，最后Element333会被删除。

```dart
import 'dart:math';

import 'package:flutter/material.dart';

class KeyDemo extends StatefulWidget {
  const KeyDemo({Key? key}) : super(key: key);

  @override
  State<KeyDemo> createState() => _KeyDemoState();
}

class _KeyDemoState extends State<KeyDemo> {
  List<Widget> items = [
    const StfulItem(
      '1111',
      key: ValueKey(111),
    ),
    const StfulItem(
      '2222',
      key: ValueKey(222),
    ),
    const StfulItem(
      '3333',
      key: ValueKey(333),
    )
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('keyDemo'),
      ),
      body: Row(
        mainAxisAlignment: MainAxisAlignment.center, //主轴
        children: items,
      ),
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.delete),
        onPressed: () {
          setState(() {
            items.removeAt(0); //删除第一个
          });
        },
      ),
    );
  }
}

class StfulItem extends StatefulWidget {
  final String title;

  const StfulItem(this.title, {Key? key}) : super(key: key);

  @override
  State<StfulItem> createState() => _StfulItemState();
}

class _StfulItemState extends State<StfulItem> {
  final color = Color.fromRGBO(Random().nextInt(256), Random().nextInt(256),
      Random().nextInt(256), 1.0); //随机色
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 100,
      height: 100,
      child: Text(widget.title),
      color: color,
    );
  }
}
```

