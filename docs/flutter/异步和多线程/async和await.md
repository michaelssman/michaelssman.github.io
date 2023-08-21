在 Dart 中，`async`和`await`是用于处理异步操作的关键字。这些关键字用于在处理可能需要一段时间的操作（例如网络请求或文件读写操作）时保持应用的响应性。

- `async`：这是一个用于声明异步函数的关键字。异步函数是一种可以在等待某些操作完成时不阻塞程序执行的函数。异步函数在执行时返回一个 Future 对象。

- `await`：这是一个只能在 `async` 函数中使用的关键字，它可以暂停代码的执行，直到等待的 Future 完成。

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