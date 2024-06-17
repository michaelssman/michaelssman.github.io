# Text

## Text

```dart
class TextDemo1 extends StatelessWidget {
  
  final TextStyle _textStyle = const TextStyle(
    fontSize: 16.0,
    fontWeight: FontWeight.bold, //FontWeight是个类
    fontStyle: FontStyle.italic, //斜体
    color: Colors.red, //Colors是个类
    //decoration: TextDecoration.none,//文字的下方出现了两条黄色下划线的处理
  );

  final String _teacher = 'Michael';
  final String _title = 'Flutter进阶';

  const TextDemo1({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Text(
      //Text的构造方法，下面都是Text的成员属性，只能赋值一次，在别的地方不能修改。
      //title
      '<$_title> -- $_teacher。圣诞快乐附近的路口；法兰克福家里快放假了；房价多少了；房价的快乐分会更加好盖好科技股和奋斗科技护肤隔开；发赶快发货感觉快疯了和姑父健康联合国将宽带发了个',
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
      //文字方向 从左到右 必须得有一个方向
      style: _textStyle,
      maxLines: 3,
      overflow: TextOverflow.ellipsis, //显示省略号
    );
  }
}
```

### textScaleFactor

 `textScaleFactor` 属性用于控制文本的缩放比例。

可以通过在应用的根部使用 `MediaQuery` 小部件来实现全局设置 `textScaleFactor`。

```dart
import 'package:flutter/material.dart';

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: MediaQuery(
        data: MediaQueryData(
          textScaleFactor: 1.5, // 设置全局 textScaleFactor
        ),
        child: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Text('This is normal text.'),
                Text('This is larger text.'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

通过在 `MaterialApp` 的根部包裹一个 `MediaQuery` 小部件，并设置 `MediaQueryData` 的 `textScaleFactor` 属性来实现全局的文本缩放比例。

1. **`MediaQuery` 小部件**：提供有关设备和应用程序窗口的各种信息，包括屏幕尺寸、文本缩放比例等。
2. **`MediaQueryData`**：包含了各种设备相关的信息。通过设置 `textScaleFactor` 属性，可以控制全局的文本缩放比例。

这样做可以确保应用中的所有文本都遵循统一的缩放比例，而不需要在每个 `Text` 小部件中单独设置 `textScaleFactor`。

## RichText

显示不同的样式。

```dart
RichText(
  // 设置字体比例
  textScaler: MediaQuery.textScalerOf(context),
  text: TextSpan(
    text: '《Flutter高级进阶班》',
    style: TextStyle(fontSize: 30, color: Colors.black,),
    children: [
      TextSpan(
        text: list[index]['fromAcName'],
        style: _textStyle1,
      ),
      TextSpan(
        text: list[index]['acDetailDate'],  
        style: _textStyle2,
      ),
    ],
  ),
),
```

