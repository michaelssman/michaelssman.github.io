# MaterialApp

开发基于MaterialApp（APP素材），相当于UIKit的UIApplication。

配置深色模式，导航栏、底部tabBar、背景色、字体等等

```dart
MaterialApp(
  title: 'Flutter Demo',
  //安卓使用，切换应用显示
  debugShowCheckedModeBanner: false,
  //是否是调试
  //浅色模式
  theme: ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: _themeColor),
    useMaterial3: true,
    // 明确指定为亮色主题
    brightness: Brightness.light,
    //主题色
    primaryColor: const Color(0xFF0cb2f1),
    //主题色 影响整个app
    primarySwatch: Colors.grey,
    //点击
    highlightColor: const Color.fromRGBO(1, 0, 0, 0),
    //弹开
    splashColor: const Color.fromRGBO(1, 0, 0, 0.0),
    //背景色
    scaffoldBackgroundColor: const Color(0xFFF7F7F8),
    // 导航栏
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFFFFFFFF), // AppBar背景色
      elevation: 0.5, // AppBar阴影高度
      titleTextStyle: TextStyle(
        color: Color(0xFF333333), // 标题文字颜色
        fontSize: 16.0, // 标题文字大小
        fontWeight: FontWeight.w600, // 标题文字粗细
      ),
      toolbarHeight: kToolbarHeight,
    ),
    //分割线
    dividerColor: Colors.black12,
    textTheme: const TextTheme(
      titleLarge: TextStyle(color: Colors.black, fontSize: 20.0),
      titleMedium: TextStyle(fontSize: 16.0, color: Color(0xFF333333)),
      titleSmall: TextStyle(fontSize: 12.0, color: Colors.black26),
    ),
    //统一定义TabBar的样式，包括指示器的大小、标签的颜色、标签之间的间距等。
    tabBarTheme: const TabBarTheme(
      labelColor: Color(0xFF0cb2f1), // 选中的标签颜色
      // unselectedLabelColor: Colors.grey, // 未选中的标签颜色
      // 选中标签的样式
      labelStyle: TextStyle(
        fontSize: 16.0,
      ),
      // 未选中标签的样式
      unselectedLabelStyle: TextStyle(
        fontSize: 14.0,
      ),
      indicator: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Color(0xFF0cb2f1), // 指示器颜色
            width: 2.0, // 指示器厚度
          ),
        ),
      ),
    ),
    //光标颜色
    textSelectionTheme: TextSelectionThemeData(
      cursorColor: _themeColor,
    ),
    hintColor: const Color.fromRGBO(155, 155, 155, 1.0),
  ),
  //深色模式
  darkTheme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: _themeColor),
    // 明确指定为深色主题
    brightness: Brightness.dark,
    //主题色
    primaryColor: const Color(0xFF0cb2f1),
    //背景色
    scaffoldBackgroundColor: const Color(0xFF1A1A1C),
    // 导航栏
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF1B1B21), // AppBar背景色
      elevation: 0.5, // AppBar阴影高度
      titleTextStyle: TextStyle(
        color: Color(0xFFDBDBDB), // 标题文字颜色
        fontSize: 16.0, // 标题文字大小
        fontWeight: FontWeight.w600, // 标题文字粗细
      ),
    //底部导航tab
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF1B1B21), // 底部导航栏背景色
      selectedItemColor: Colors.white, // 选中项的颜色
      unselectedItemColor: Colors.grey, // 未选中项的颜色
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF1B1B21), // AppBar背景色
    ),
    //分割线
    dividerColor: Colors.black,
    //字体
    textTheme: const TextTheme(
      titleLarge: TextStyle(color: Colors.white, fontSize: 20.0),
      titleMedium: TextStyle(fontSize: 16.0, color: Color(0xFF333333)),
      titleSmall: TextStyle(fontSize: 12.0, color: Color(0xFFB0B4BB)),
    ),
    //统一定义TabBar的样式，包括指示器的大小、标签的颜色、标签之间的间距等。
    tabBarTheme: const TabBarTheme(
      labelColor: Color(0xFF0cb2f1), // 选中的标签颜色
      // unselectedLabelColor: Colors.grey, // 未选中的标签颜色
      // 选中标签的样式
      labelStyle: TextStyle(
        fontSize: 16.0,
      ),
      // 未选中标签的样式
      unselectedLabelStyle: TextStyle(
        fontSize: 14.0,
      ),
      indicator: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Color(0xFF0cb2f1), // 指示器颜色
            width: 2.0, // 指示器厚度
          ),
        ),
      ),
    ),
    //光标颜色
    textSelectionTheme: TextSelectionThemeData(
      cursorColor: _themeColor,
    ),
    hintColor: const Color(0xFF5E5E66), //占位文字颜色
  ),
  themeMode: ThemeMode.system,
  home: const RootPage(), //主页面
);
```

## 自定义颜色

在Flutter中，`ColorScheme`是一个持有一组颜色的类，这些颜色旨在用于构建Material组件库的颜色主题。`ColorScheme`生成了一组可以在应用程序的许多不同部分中使用的颜色，以保持视觉的一致性。这些颜色被设计为在浅色和深色主题中都有良好的对比度，使得它们可以在不同的主题模式下使用。

`ColorScheme`包含以下颜色：

- `primary`：应用程序主要部分的颜色（例如，应用栏、按钮、文本选择手柄）。
- `primaryVariant`：`primary`的一个较深或较浅的版本，用于需要对比度的地方。
- `secondary`：用于强调和区分UI元素（如浮动操作按钮、链接文本）的颜色。
- `secondaryVariant`：`secondary`的一个较深或较浅的版本，同样用于需要对比度的地方。
- `surface`：UI元素的背景色，如卡片和抽屉。
- `background`：页面的背景色。
- `error`：用于指示错误的颜色。
- `onPrimary`、`onSecondary`、`onSurface`、`onBackground`和`onError`：分别对应于`primary`、`secondary`、`surface`、`background`和`error`颜色上的文本和图标的颜色。
- `brightness`：整体主题的亮度，可以是`Brightness.light`或`Brightness.dark`。

你可以通过在`MaterialApp`的`theme`和`darkTheme`属性中设置`ColorScheme`来为你的应用定义一组颜色。例如：

```dart
MaterialApp(
  theme: ThemeData.from(
    colorScheme: ColorScheme.light(
      primary: Colors.blue, // 用于浅色主题的主要颜色
      secondary: Colors.blueAccent, // 用于浅色主题的次要颜色
    ),
  ),
  darkTheme: ThemeData.from(
    colorScheme: ColorScheme.dark(
      primary: Colors.blue.shade200, // 用于深色主题的主要颜色
      secondary: Colors.blueAccent.shade700, // 用于深色主题的次要颜色
    ),
  ),
  // ...
);
```

在这个例子中，我们使用`ColorScheme.light()`和`ColorScheme.dark()`来创建适用于浅色和深色主题的颜色方案，并将这些颜色方案应用到`ThemeData`中。这样，当用户的设备在浅色模式和深色模式之间切换时，Flutter应用也会自动切换到相应的颜色主题。
