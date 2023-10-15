# Key的原理

只要继承Widget的都有一个key。Key是用来标识小部件的。Key是一个抽象类。

StatefulWidget的Widget和State是分开的。

Widget

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

Key本身是一个抽象类，有一个工厂构造方法。创建ValueKey，值是任意类型。

直接子类LocalKey，GlobalKey。

- GlobalKey

  对应某一个Widget State Element(Context)。

  帮助我们访问某个Widget的信息，类似tag标记的功能。

- LocalKey

  用来区别哪个Element保留，哪个Element删除。diff算法的核心所在。

  - ValueKey以值作为参数（数字，字符串）
  - ObjectKey以对象作为参数
  - UniqueKey创建唯一标识，整个项目只有一个，不会被复用。
