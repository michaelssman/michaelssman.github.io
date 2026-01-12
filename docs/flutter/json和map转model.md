# 字典模型转换

```dart
import 'dart:convert';

class ChatModel {
  final String? name;//final修饰，赋值之后不会再修改。?空安全
  final String? message;
  final String? imageUrl;

  const ChatModel({this.name, this.message, this.imageUrl});//构造函数 大括号表示可选，下面的属性要么有默认值= 要么是?空安全的
  
  //工厂构造 可以有返回值。Map转Model。
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
```

