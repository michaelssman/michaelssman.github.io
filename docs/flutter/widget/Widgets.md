## Button

### ElevatedButton

```dart
ElevatedButton(
  //去除ElevatedButton的背景色
  style: ButtonStyle(
    backgroundColor:
    MaterialStateProperty.all<
    Color>(Colors.transparent),
    shadowColor: MaterialStateProperty
    .all<Color>(Colors.transparent),
  ),
  onPressed: () {
    print("点击按钮");
  },
  child: Text("data"),
),
```

### IconButton

```dart
IconButton(
  icon: const Icon(Icons.close),
  onPressed: () {},
),
```

### 自定义按钮

```dart
Widget customButton(VoidCallback callback) {
  return GestureDetector(
    onTap: () => callback(),
    child: SafeArea(
      child: Container(
        alignment: Alignment.center,
        margin: const EdgeInsets.symmetric(horizontal: 15, vertical: 20),
        height: 50,
        decoration: BoxDecoration(
          color: Colors.blue,
          borderRadius: BorderRadius.circular(25),
        ),
        child: const Text(
          "保存",
          style: TextStyle(
            fontSize: 16.0,
            color: Colors.white,
          ),
        ),
      ),
    ),
  );
}
```

### InkWell

`InkWell`是一个专门为水波纹效果设计的小部件。

```dart
InkWell(
  onTap: () {
    print('Tap!');
  },
  splashColor: Colors.blue, // 水波纹颜色
  child: Container(
    // ...
  ),
)
```

## Image

图片小部件

`Image.network(imageUrlString)`, 构造函数：从网络上加载一张图片。

```dart
const Image(
  image: AssetImage('images/badge.png'),//本地加载图片
  width: 20,
),
```

### 图片添加圆角

```dart
Container(
  margin: const EdgeInsets.all(10),
  width: 34,
  height: 34,
  //圆角
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(6.0),
    image: DecorationImage(
      image: imageUrl != null
      ? NetworkImage(imageUrl!) as ImageProvider
      : AssetImage(imageAssets!),
    ),
  ),
),
```

### 选择相册Package

```dart
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_demo/widgets/scaffold_demo.dart';
import 'package:image_picker/image_picker.dart';

class ImagePickerDemo extends StatefulWidget {
  const ImagePickerDemo({Key? key}) : super(key: key);
  @override
  State<ImagePickerDemo> createState() => _ImagePickerDemoState();
}

class _ImagePickerDemoState extends State<ImagePickerDemo> {
  File? _avatarFile;

  @override
  Widget build(BuildContext context) {
    return HHScaffold(
      //头像
      GestureDetector(
        onTap: _pickImage,
        child: Container(
          width: 70,
          height: 70,
          //圆角
          decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              image: DecorationImage(
                  image: _avatarFile == null
                      ? const AssetImage('images/Hank.png') as ImageProvider
                      : FileImage(_avatarFile!),
                  //裁剪
                  fit: BoxFit.cover)),
        ),
      ),
    );
  }

  void _pickImage() async {
    try {
      XFile? file = await ImagePicker()
          .pickImage(source: ImageSource.gallery); //返回Future所以方法使用async
      _avatarFile = File(file!.path);
      setState(() {});
    } catch (e) {
      print(e.toString());
      setState(() {
        _avatarFile = null;
      });
    }
  }
  
}
```

## Wrap

`Wrap` 是一个布局widget，它可以在水平或垂直方向上排列其子widget，并且会**在主轴上的空间不足时，将超出空间的子widget换行或换列到下一个运行**。这使得`Wrap`非常适合用于创建流式布局，如标签组或者按钮组。

`Wrap`的基本用法非常简单。你只需要将一个widget列表传递给`Wrap`的`children`属性，并且可以设置一些其他属性来控制间距和对齐方式。

下面是`Wrap`的一个基本示例：

```dart
Wrap(
  spacing: 8.0, // 主轴(水平)方向间距
  runSpacing: 4.0, // 纵轴（垂直）方向间距
  alignment: WrapAlignment.center, // 沿主轴方向居中
  children: <Widget>[
    Chip(
      avatar: CircleAvatar(backgroundColor: Colors.blue, child: Text('A')),
      label: Text('Hamilton'),
    ),
    Chip(
      avatar: CircleAvatar(backgroundColor: Colors.blue, child: Text('M')),
      label: Text('Lafayette'),
    ),
    Chip(
      avatar: CircleAvatar(backgroundColor: Colors.blue, child: Text('H')),
      label: Text('Mulligan'),
    ),
    Chip(
      avatar: CircleAvatar(backgroundColor: Colors.blue, child: Text('J')),
      label: Text('Laurens'),
    ),
  ],
)
```

在这个例子中，`Wrap`包含了几个`Chip`widget，每个`Chip`都有一个头像和一个标签。如果水平空间不足以容纳所有的`Chip`，`Wrap`会将多出的`Chip`移到下一行。

`Wrap`的一些重要属性包括：

- `direction`: 主轴方向，默认是`Axis.horizontal`，也可以设置为`Axis.vertical`。
- `alignment`: 主轴方向上如何对齐子widget，默认是`WrapAlignment.start`。
- `spacing`: 主轴方向上子widget之间的间隔。
- `runAlignment`: 交叉轴方向上如何对齐运行，默认是`WrapAlignment.start`。
- `runSpacing`: 交叉轴方向之间的间隔。
- `crossAxisAlignment`: 交叉轴方向上子widget如何对齐，默认是`WrapCrossAlignment.start`。

使用`Wrap`时，可以通过调整这些属性来精确控制布局的表现。

## Card卡片

```dart
Card(
  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
  margin: const EdgeInsets.only(left: 16, right: 16, top: 8, bottom: 8),
  semanticContainer: true,
  color: color.withOpacity(0.4),
  clipBehavior: Clip.antiAlias,
  child: chartLine,
)
```

