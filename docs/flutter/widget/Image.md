# Image

Image 图片小部件

`Image.network(imageUrlString)`, 构造函数：从网络上加载一张图片。

```dart
const Image(
  image: AssetImage('images/badge.png'),
  width: 20,
),
```

## 选择相册Package

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

