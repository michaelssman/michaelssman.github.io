# TextField

```dart
TextField(
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
  enabled: false,
  //TextInputType.none不弹出键盘
  keyboardType: TextInputType.none,
  decoration: const InputDecoration(
    //内容约束
    contentPadding: EdgeInsets.only(left: 5),
    border: InputBorder.none,		//输入框边框
    hintText: '金额',						//站位文字
    hintStyle: TextStyle(
      color: Color(0xeaeaeaea),
      fontSize: 18,
      letterSpacing: 2.0,
    ),
  ),
)
```

