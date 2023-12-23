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
GestureDetector(
  onTap: () async {
  },
  child: Container(
    alignment: Alignment.center,
    margin:
    const EdgeInsets.symmetric(horizontal: 15, vertical: 20),
    height: 50,
    decoration: BoxDecoration(
      color: themeColor,
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
  image: AssetImage('images/badge.png'),
  width: 20,
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

```dart
Wrap(
  spacing: 8.0,
  runSpacing: 4.0,
  alignment: WrapAlignment.center,
  children: const [
    Chip(
      avatar: CircleAvatar(
        backgroundColor: Colors.blue,
        child: Text('A'),
      ),
      label: Text('张三三')),
    Chip(
      avatar: CircleAvatar(
        backgroundColor: Colors.blue,
        child: Text('B'),
      ),
      label: Text('李思思')),
    Chip(
      avatar: CircleAvatar(
        backgroundColor: Colors.blue,
        child: Text('C'),
      ),
      label: Text('王呜呜')),
    Chip(
      avatar: CircleAvatar(
        backgroundColor: Colors.blue,
        child: Text('D'),
      ),
      label: Text('赵溜溜')),
  ],
)
```

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

