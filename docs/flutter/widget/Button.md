# Button

## ElevatedButton

```dart
ElevatedButton(
  //去除ElevatedButton的背景色
  style: ButtonStyle(
    backgroundColor:
    MaterialStateProperty.all<
    Color>(Colors.transparent),
    shadowColor: MaterialStateProperty
    .all<Color>(Colors.transparent),
  ),
  onPressed: () {
    print("点击按钮");
  },
  child: Text("data"),
),
```

## IconButton

```dart
IconButton(
  icon: const Icon(Icons.close),
  onPressed: () {},
),
```

## 自定义按钮

```dart
GestureDetector(
  onTap: () async {
  },
  child: Container(
    alignment: Alignment.center,
    margin:
    const EdgeInsets.symmetric(horizontal: 15, vertical: 20),
    height: 50,
    decoration: BoxDecoration(
      color: themeColor,
      borderRadius: BorderRadius.circular(25),
    ),
    child: const Text(
      "保存",
      style: TextStyle(
        fontSize: 16.0,
        color: Colors.white,
      ),
    ),
  ),
),
```

## InkWell

`InkWell`是一个专门为水波纹效果设计的小部件。

```dart
InkWell(
  onTap: () {
    print('Tap!');
  },
  splashColor: Colors.blue, // 水波纹颜色
  child: Container(
    // ...
  ),
)
```
