# app密码保护

## 1、设置密码页面

这个页面允许用户输入一个新密码，并将其保存起来。

```dart
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SetPasswordPage extends StatefulWidget {
  const SetPasswordPage({super.key});

  @override
  State<SetPasswordPage> createState() => _SetPasswordPageState();
}

class _SetPasswordPageState extends State<SetPasswordPage> {
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();
  final _storage = const FlutterSecureStorage();

  void _setPassword() async {
    if (_passwordController.text == _confirmPasswordController.text) {
      final password = _passwordController.text;
      // 保存密码前可以进行加密
      //使用flutter_secure_storage来安全地保存密码
      await _storage.write(key: 'password', value: password);
      // 返回上一页或显示成功消息
      if (mounted) {
        // 确保当前的State对象还挂载在widget树中
        Navigator.pop(context);
      }
    } else {
      //TODO: 密码不匹配，显示错误消息
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Set Password')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            TextField(
              controller: _passwordController,
              decoration:
                  const InputDecoration(labelText: 'Enter your password'),
              obscureText: true,
            ),
            TextField(
              controller: _confirmPasswordController,
              decoration:
                  const InputDecoration(labelText: 'Confirm your password'),
              obscureText: true,
            ),
            ElevatedButton(
              onPressed: _setPassword,
              child: const Text('Set Password'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 2、解锁页面

这个页面在应用程序启动时出现，并让用户输入密码。

```dart
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class UnlockPage extends StatefulWidget {
  const UnlockPage({super.key});

  @override
  State<UnlockPage> createState() => _UnlockPageState();
}

class _UnlockPageState extends State<UnlockPage> {
  final TextEditingController _passwordController = TextEditingController();
  final _storage = const FlutterSecureStorage();

  void _unlockApp() async {
    String? storedPassword = await _storage.read(key: 'password');
    if (_passwordController.text == storedPassword) {
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } else {
      //TODO: 密码不正确，显示错误消息
      _passwordController.text = "";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: '请输入解锁密码'),
              obscureText: true,
            ),
            ElevatedButton(
              onPressed: _unlockApp,
              child: const Text('确定'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 3、在应用程序启动时显示密码输入页面

在`main.dart`中，你可以通过条件检查来决定显示密码输入页面还是直接进入应用程序的首页。

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const storage = FlutterSecureStorage();
  String? storedPassword = await storage.read(key: 'password');
  bool isLocked = storedPassword != null;

  runApp(MyApp(isLocked: isLocked));
}

class MyApp extends StatelessWidget {
  final bool isLocked;

  MyApp({this.isLocked});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: isLocked ? UnlockPage() : HomePage(),
      routes: {
        '/home': (context) => HomePage(),
        '/setPassword': (context) => SetPasswordPage(),
      },
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Home')),
      body: Center(child: Text('Welcome to the app!')),
    );
  }
}
```

确保在`pubspec.yaml`文件中添加了`flutter_secure_storage`依赖项：

```yaml
dependencies:
  flutter_secure_storage: ^5.0.0
```

这是一个为Flutter提供安全存储的插件。它会在iOS上使用Keychain，在Android上使用Keystore来存储数据。

注意，实际应用中可能需要考虑更多的安全性问题，例如使用更安全的密码存储机制，添加密码尝试次数限制，以及使用哈希函数来存储密码等。