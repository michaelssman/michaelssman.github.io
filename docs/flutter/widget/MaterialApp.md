# MaterialApp

开发基于MaterialApp（APP素材），相当于UIKit的UIApplication的main。

配置深色模式，导航栏、底部tabBar、背景色等等

```dart
MaterialApp(
  title: 'Flutter Demo', //安卓使用，切换应用显示
  debugShowCheckedModeBanner: false, //是否是调试
  //浅色模式
  theme: ThemeData(
    // This is the theme of your application.
    //
    // TRY THIS: Try running your application with "flutter run". You'll see
    // the application has a blue toolbar. Then, without quitting the app,
    // try changing the seedColor in the colorScheme below to Colors.green
    // and then invoke "hot reload" (save your changes or press the "hot
    // reload" button in a Flutter-supported IDE, or press "r" if you used
    // the command line to start the app).
    //
    // Notice that the counter didn't reset back to zero; the application
    // state is not lost during the reload. To reset the state, use hot
    // restart instead.
    //
    // This works for code too, not just values: Most code changes can be
    // tested with just a hot reload.
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
    useMaterial3: true,
    //主题色
    primaryColor: const Color(0xFF0cb2f1),
    primarySwatch: Colors.grey, //主题色 影响整个app
    highlightColor: const Color.fromRGBO(1, 0, 0, 0), //点击
    splashColor: const Color.fromRGBO(1, 0, 0, 0.0), //弹开
    //背景色
    scaffoldBackgroundColor: const Color.fromRGBO(220, 220, 220, 1.0),
    brightness: Brightness.light, // 明确指定为亮色主题
  ),
  //深色模式
  darkTheme: ThemeData(
    brightness: Brightness.dark, // 明确指定为深色主题
    //主题色
    primaryColor: const Color(0xFF0cb2f1),
    //背景色
    scaffoldBackgroundColor: const Color(0xFF1A1A1C),
    //底部导航tab
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF1B1B21), // 底部导航栏背景色
      selectedItemColor: Colors.white, // 选中项的颜色
      unselectedItemColor: Colors.grey, // 未选中项的颜色
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF1B1B21), // AppBar背景色
    ),
  ),
  themeMode: ThemeMode.system,
  home: const Account(),
);
```
