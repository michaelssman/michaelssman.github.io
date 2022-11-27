# 字典模型转换

```dart
import 'dart:convert';

class ChatModel {
  final String? name;
  final String? message;
  final String? imageUrl;
  ChatModel({this.name, this.message, this.imageUrl});
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
  //json转模型
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

