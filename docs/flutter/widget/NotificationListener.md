# NotificationListener

在Flutter中，`NotificationListener` 是一个包装其它widget的widget，它的作用是用来监听树中冒泡传递的通知（`Notification`）。

- 这些通知可以是用户滚动一个 `Scrollable` widget时的滚动事件
- 也可以是其他类型的事件：
  - 如大小改变（`SizeChangedLayoutNotification`）
  - 或者自定义的通知。

当你想要在widget树的某个节点处处理来自其子树的通知时，可以使用 `NotificationListener`。例如，你可以使用它来监听滚动事件，以便在用户滚动到列表的底部时加载更多数据。

这里有一个简单的例子，展示了如何使用 `NotificationListener` 来监听 `ListView` 的滚动事件：

```dart
import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NotificationListener Demo',
      home: Scaffold(
        appBar: AppBar(
          title: Text('NotificationListener Demo'),
        ),
        body: NotificationListener<ScrollNotification>(
          onNotification: (scrollNotification) {
            if (scrollNotification is ScrollEndNotification) {
              // 检查滚动位置是否到达底部
              if (scrollNotification.metrics.pixels ==
                  scrollNotification.metrics.maxScrollExtent) {
                // 加载更多数据
                print('Reached the bottom!');
              }
            }
            // 返回true表示通知已被处理，不再继续向上冒泡；返回false则继续向上冒泡通知。
            return true;
          },
          child: ListView.builder(
            itemCount: 30,
            itemBuilder: (context, index) {
              return ListTile(title: Text('Item $index'));
            },
          ),
        ),
      ),
    );
  }
}
```

在这个例子中，我们在 `ListView` 外层包裹了一个 `NotificationListener<ScrollNotification>`。我们的 `onNotification` 回调会在每次滚动事件发生时被调用。

我们特别检查了 `ScrollEndNotification`，这意味着滚动动作已经停止。

如果用户已经滚动到了列表的底部，我们打印了一条消息 `"Reached the bottom!"`。在这个回调中，你可以执行加载更多数据的逻辑。

**`NotificationListener` 可以监听各种类型的通知，这取决于你指定的泛型参数。**

在上面的例子中，我们使用的是 `ScrollNotification`，这是一个关于滚动事件的通知。你也可以创建自己的通知类型，并使用 `NotificationListener` 来监听它们。