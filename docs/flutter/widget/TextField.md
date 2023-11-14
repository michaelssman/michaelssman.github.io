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
      FocusScope.of(context).unfocus();
    },
    //滑动回收
    child: NotificationListener<ScrollNotification>(
      onNotification: (ScrollNotification _event) {
        FocusScope.of(context).unfocus();
        return true;
      },
      child: CustomScrollView(),
    ),
  );
}
```

## 自动弹出键盘

```dart
@override
void initState() {
  // TODO: implement initState
  super.initState();
  
  _focusNode.addListener(() {
    if (_focusNode.hasFocus) {
      _keyboardKey.currentState?.showKeyboard();
    } else {
      _keyboardKey.currentState?.hiddenKeyboard();
    }
  });
  
  WidgetsBinding.instance.addPostFrameCallback((timeStamp) {
    //请求焦点
    FocusScope.of(context).requestFocus(_focusNode);
  });
}
```

## 从光标选中位置插入和删除

在 TextField 控制器 TextEditingController 中有一个 selection 属性，记录了选定内容的文本范围。主要用到其中两个属性: baseOffset 和 extentOffset，baseOffset 是文本选择的起始偏移位置，extentOffset 是文本选择的结束偏移位置。baseOffset 和 extentOffset 相等时 baseOffset 就是光标的位置

### 任意位置的插入

```ini
String text = "新插入的内容";
int oldOffset = controller.selection.baseOffset; // 获取起始位置
int oldExtentOffset = controller.selection.extentOffset; // 获取结束位置
String oldValue = controller.text; // 获取输入框原有内容
String newValue = oldValue.replaceRange(oldOffset, oldExtentOffset, text); // 根据起始位置和束位置替换内容，生成新内容
int newOffset = oldOffset + text.length; // 从新计算起始位置
controller.value = TextEditingValue(
  // 修改输入框内容和光标位置
  text: newValue,
  selection: TextSelection(baseOffset: newOffset, extentOffset: newOffset),
); // 起始位置和结束位置相同就是光标位置
```

### 任意位置的删除

```ini
int oldOffset = controller.selection.baseOffset; // 获取起始位置
int oldExtentOffset = controller.selection.extentOffset; // 获取结束位置
String oldValue = controller.text; // 获取输入框原有内容
// 光标在最左边
if (oldOffset == 0 && oldExtentOffset == 0) {
  // 光标在输入框最左侧没有可删除内容，直接返回
  return;
}
// 当没有选中文本
if (oldOffset == oldExtentOffset) {
  // 起始位置和束位置相同，即没有选中内容
  oldOffset--; // 起始位置自减，自减之后可以看成选中了左边一个内容
}
int newOffset = oldOffset; // 生成新的起始位置
String newValue = oldValue.replaceRange(oldOffset, oldExtentOffset, ''); // 根据起始位置和束位置替换成空支付，生成新内容
controller.value = TextEditingValue(
  // 修改输入框内容和光标位置
  text: newValue,
  selection:
  TextSelection(baseOffset: newOffset, extentOffset: newOffset),
); // 起始位置和结束位置相同就是光标位置
```

## 设置光标位置

```dart
// 在设置TextField的text属性后，将焦点移动到文本的末尾
_textEditingController.text = "你的文本内容";
_textEditingController.selection = TextSelection.fromPosition(
  TextPosition(offset: _textEditingController.text.length),
);
```

