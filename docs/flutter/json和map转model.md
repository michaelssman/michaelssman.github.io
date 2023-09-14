# 字典模型转换

```dart
import 'dart:convert';

class ChatModel {
  final String? name;//final修饰，一般赋值之后不会再修改。?空安全
  final String? message;
  final String? imageUrl;
  const ChatModel({this.name, this.message, this.imageUrl});//构造函数 大括号表示可选，下面的属性要么有默认值= 要么是?空安全的
  
  //工厂构造 可以有返回值
  factory ChatModel.formMap(Map map) {
    return ChatModel(
      name: map['name'],
      message: map['message'],
      imageUrl: map['imageUrl'],
    );
  }
}

void json_map() {
  //定义map
  final chat = {'name': 'haha', 'message': '吃了吗'};
  //map转json
  final chatJson = json.encode(chat);
  print(chatJson);
  //json转map
  final newChat = json.decode(chatJson);
  print(newChat);
  print(newChat['name']);
  print(newChat is Map);//true

  final chatModel = ChatModel.formMap(newChat);
  print('name:${chatModel.name} message:${chatModel.message}');
}



//全局的数据源
final List<ChatModel> datas = [
  const ChatModel(
    name: '保时捷918 Spyder',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-7d8be6ebc4c7c95b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '兰博基尼Aventador',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-e3bfd824f30afaac?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '法拉利Enzo',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-a1d64cf5da2d9d99?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: 'Zenvo ST1',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-bf883b46690f93ce?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '迈凯伦F1',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-5a7b5550a19b8342?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '萨林S7',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-2e128d18144ad5b8?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '科尼赛克CCR',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-01ced8f6f95219ec?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '布加迪Chiron',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-7fc8359eb61adac0?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '轩尼诗Venom GT',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-d332bf510d61bbc2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
  const ChatModel(
    name: '西贝尔Tuatara',
    message: "肌肤的抗衰老；发动机快乐",
    imageUrl:
        'https://upload-images.jianshu.io/upload_images/2990730-3dd9a70b25ae6bc9?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240',
  ),
];
```

