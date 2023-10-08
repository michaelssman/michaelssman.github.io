# TextField

```dart
TextField(
  textAlign: TextAlign.right,//文字对齐方式
  controller: _controller,//TextEditingController
  // onChanged: _onChange,
  //自动聚焦
  autofocus: true,
  //光标颜色
  cursorColor: Colors.green,
  style: const TextStyle(
    fontSize: 18.0,
    color: Colors.black,
    fontWeight: FontWeight.w300,
  ),
  //enabled是false时，点击输入框没反应。
  enabled: false,
  //点击输入框
  onTap: () {
    //显示自定义键盘等处理
  },
  //TextInputType.none不弹出键盘
  keyboardType: TextInputType.none,
  decoration: const InputDecoration(
    //内容约束
    contentPadding: EdgeInsets.only(left: 5),
    border: InputBorder.none,		//输入框边框
    hintText: '金额',						//占位文字
    hintStyle: TextStyle(
      color: Color(0xeaeaeaea),
      fontSize: 18,
      letterSpacing: 2.0,
    ),
  ),
)
```

## 回收键盘

```dart
@override
Widget build(BuildContext context) {
  return GestureDetector(
    //点击回收
    onTap: () {
      if (_isCustomKeyboardVisible) {
        _isCustomKeyboardVisible = false;
        setState(() {});
      }
    },
    //滑动回收
    child: NotificationListener<ScrollNotification>(
      onNotification: (ScrollNotification _event) {
        if (_isCustomKeyboardVisible) {
          setState(() {
            _isCustomKeyboardVisible = false;
          });
        }
        return true;
      },
      child: ,
    ),
  );
}
```

