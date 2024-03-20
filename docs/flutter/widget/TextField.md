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
  //字体设置
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

要实现仅在手动滚动时隐藏键盘，而在自动滚动（如动画滚动或其他程序触发的滚动）时不隐藏键盘，你需要检查`ScrollNotification`的类型。在Flutter中，手动滚动通常会触发`UserScrollNotification`，而自动滚动会触发`ScrollStartNotification`和`ScrollUpdateNotification`，但不会触发`UserScrollNotification`。

你可以通过检查`ScrollNotification`的runtimeType来判断是否为`UserScrollNotification`，如果是，则隐藏键盘。

```dart
Widget autoHiddenKeyBoardWidget(BuildContext context, Widget child) {
  return GestureDetector(
    //点击回收
    onTap: () => FocusScope.of(context).unfocus(),
    //滑动回收
    child: NotificationListener<ScrollNotification>(
      onNotification: (ScrollNotification notification) {
        // Check if the notification is specifically a UserScrollNotification
        if (notification is UserScrollNotification) {
          // Check the direction of the scroll to determine if it's a forward scroll
          if (notification.direction == ScrollDirection.forward ||
              notification.direction == ScrollDirection.reverse) {
            // Hide the keyboard
            FocusScope.of(context).unfocus();
          }
        }
        // Return true to stop the notification from propagating further
        return true;
      },
      child: child,
    ),
  );
}
```

在这个修改后的代码中，`NotificationListener`现在监听`ScrollNotification`，并且在`onNotification`回调中检查通知是否为`UserScrollNotification`。如果是，并且滚动方向是向前或向后，它会调用`FocusScope.of(context).unfocus()`来隐藏键盘。

请注意，`ScrollDirection.idle`不会被考虑，因为它表示滚动动作已经停止，而不是用户主动滚动。这样，只有当用户实际滚动屏幕时，键盘才会被隐藏。

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

