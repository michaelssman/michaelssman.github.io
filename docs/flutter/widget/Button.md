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

