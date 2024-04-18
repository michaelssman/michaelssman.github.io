# async和await

在 Dart 中，`async`和`await`是用于处理异步操作的关键字。这些关键字用于在处理可能需要一段时间的操作（例如网络请求或文件读写操作）时保持应用的响应性。

Future类似H5中的promise。

- `async`：这是一个用于声明异步函数的关键字。必须使用在函数上，他会把一个函数标记为`异步函数`。异步函数是一种可以在等待某些操作完成时不阻塞程序执行的函数。异步函数在执行时返回一个 Future 对象。
- `await`：这是一个只能在`异步函数(async 标记的函数）`中使用的关键字，它可以暂停代码的执行，直到等待的 Future 完成。

使用async/await替代.then()：.then()在某些情况下是有用的，使用async/await可以使代码更易读，更易理解。

async 和await 关键字让我们可以用一种更简洁的方式写出基于 Promise 的异步行为，而无需刻意地链式调用promise。

这是一个简单的示例：

```dart
import 'dart:io';

void main() {
  print('Fetching data...');
  fetchData().then((value) {
    print('Data received: $value');
  });
}

Future<String> fetchData() async {
  await Future.delayed(Duration(seconds: 2));   // 模拟网络延迟
  return 'Hello, World!';
}
```

在这个示例中，`fetchData`函数被标记为`async`，这意味着它会返回一个 `Future<String>`。然后，我们在函数体内部使用了 `await` 关键字来等待一个模拟的网络延迟操作完成。这样，我们的主函数可以在等待数据时继续执行其他操作，而不会被阻塞。

请注意，`async` 和 `await` 关键字通常一起使用，以便在处理可能需要一段时间的操作时，保持应用的响应性。

## Don't use 'BuildContext's across async gaps

在Flutter中，警告"Don't use 'BuildContext's across async gaps"通常是指在一个异步操作中使用了一个旧的`BuildContext`，而这个上下文可能在异步操作完成时不再有效。

这个问题通常出现在使用`Future`、`async`和`await`时，你在一个异步的gap（例如在调用了`await`之后）引用了一个`BuildContext`，这个上下文可能是从一个之前的build方法中获得的。如果在异步操作完成后，与该上下文相关联的widget已经从widget树中移除，那么使用这个上下文可能会导致异常。

例如，以下代码会引发这个警告：

```dart
Future<void> loadData(BuildContext context) async {
  await Future.delayed(Duration(seconds: 2));
  // 使用异步操作后的上下文
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
    content: Text('Data Loaded'),
  ));
}
```

在上面的代码中，如果在`await`调用完成之后，与`context`相关联的widget已经不在widget树中了，那么调用`ScaffoldMessenger.of(context)`就会抛出一个异常。

为了解决这个问题，可以采取以下措施：

1. **使用`mounted`属性**：
   在调用异步操作之后，你可以检查当前的widget是否仍然挂载（即仍然在widget树中）。

```dart
Future<void> loadData(BuildContext context) async {
  await Future.delayed(Duration(seconds: 2));
  if (!mounted) return; // 如果当前widget没有挂载，则直接返回
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
    content: Text('Data Loaded'),
  ));
}
```

2. **使用GlobalKey**：
   使用`GlobalKey`来获取当前的`ScaffoldState`，而不是通过`BuildContext`。

```dart
final GlobalKey<ScaffoldState> scaffoldKey = GlobalKey<ScaffoldState>();

// ...

scaffoldKey.currentState?.showSnackBar(SnackBar(
  content: Text('Data Loaded'),
));
```

3. **将BuildContext传递到异步操作之前**：
   在异步操作开始之前获取所需的数据，例如`ScaffoldMessenger`的实例。

```dart
Future<void> loadData(BuildContext context) async {
  // 获取ScaffoldMessenger实例
  final scaffoldMessenger = ScaffoldMessenger.of(context);
  await Future.delayed(Duration(seconds: 2));
  if (!mounted) return;
  scaffoldMessenger.showSnackBar(SnackBar(
    content: Text('Data Loaded'),
  ));
}
```

4. **使用Stateful Widgets的状态**：
   如果你在Stateful Widget中，确保你的异步操作与widget的状态保持一致，而不是依赖于构建方法中传入的BuildContext。

注意，`mounted`属性是State对象的一部分，所以如果你在一个无状态widget中，你需要找到其他方法来确保你不会在widget被卸载后使用上下文。通常，最好的做法是确保异步操作完成后不依赖于已经可能失效的BuildContext。