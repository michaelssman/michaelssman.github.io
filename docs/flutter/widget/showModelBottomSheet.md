# showModelBottomSheet

showModelBottomSheet 方法用于弹出底部弹窗。

```dart
Future<T?> showModalBottomSheet<T>({
  required BuildContext context,	//必传上下文
  required WidgetBuilder builder,	//必传
  Color? backgroundColor,
  double? elevation,
  ShapeBorder? shape,							//加圆角
  Clip? clipBehavior,
  BoxConstraints? constraints,
  Color? barrierColor,
  bool isScrollControlled = false,//当true时，则是全屏弹窗，默认是false
  bool useRootNavigator = false,
  bool isDismissible = true,
  bool enableDrag = true,
  RouteSettings? routeSettings,
  AnimationController? transitionAnimationController,
})
```

## 代码结构

点击按钮弹出底部弹窗，注意的方式是按钮的 `onPressed` 响应方法，需要使用 `async` 修饰，因为 `ModalBottomSheet` 的返回结果是一个 `Future` 对象，需要通过 `await` 来获取返回结果。

```dart
onPressed: () async {
  int selectedIndex = await _showCustomModalBottomSheet(context, _options);
  print("自定义底部弹层：选中了第$selectedIndex个选项");
},
```

## 基本使用

```dart
Future<int> _showBasicModalBottomSheet(context, List<String> options) async {
    return showModalBottomSheet<int>(
      isScrollControlled: false,
      context: context,
      builder: (BuildContext context) {
        return ListView.builder(
          itemBuilder: (BuildContext context, int index) {
            return ListTile(
                title: Text(options[index]),
                onTap: () {
                  Navigator.of(context).pop(index);
                });
          },
          itemCount: options.length,
        );
      },
    );
  }
```

需要注意的有四点：

- 弹窗需要上下文的 `context`，这是因为实际页面展示是通过 `Navigator` 的 `push` 方法导航的新的页面完成的。
- 弹窗的组件构建的 `builder` 方法，这里可以返回自己自定义的组件。
- 在列表的元素的选中点击事件 `onTap` 方法中，需要使用 `Navigator`的 `pop` 方法返回上一个页面，这里可以携带选中的下标（或其他值）返回，上一个页面可以使用 `await` 的方式接收对应返回的结果。
- 点击蒙层也可以消失，这时候实际调用的方法是 `Navigator.of(context).pop()`。因为没有携带参数，所以接收的结果是 `null`，需要特殊处理一下。

## 自定义底部弹窗

在自定义底部弹窗中，我们做了如下自定义项：

- 弹窗的高度指定为屏幕高度的一半，这可以通过自定义组件的 `Container` 高度实现。
- 增加了标题栏，且标题栏有关闭按钮：标题在整个标题栏是居中的，而关闭按钮是在标题栏右侧顶部。这可以通过 `Stack`堆栈布局组件实现不同的组件层叠及位置。
- 左上角和右上角做了圆角处理，这个可以通过 `Container` 的装饰完成，但需要注意的是，由于底部弹窗默认是有颜色的，因此要显示出圆角需要将底部弹窗的颜色设置为透明。

自定义弹窗的代码如下所示：

```dart
Future<int?> showCustomModalBottomSheet(context, List<String> options) async {
  return showModalBottomSheet<int>(
    backgroundColor: Colors.transparent,
    isScrollControlled: true,
    context: context,
    builder: (BuildContext context) {
      return Container(
        clipBehavior: Clip.antiAlias,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20.0),
            topRight: Radius.circular(20.0),
          ),
        ),
        height: MediaQuery.of(context).size.height / 2.0,
        child: Column(children: [
          SizedBox(
            height: 50,
            child: Stack(
              textDirection: TextDirection.rtl,
              children: [
                const Center(
                  child: Text(
                    '选择账户',
                    style:
                        TextStyle(fontWeight: FontWeight.bold, fontSize: 16.0),
                  ),
                ),
                IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () {
                      Navigator.of(context).pop();//弹窗消失
                    }),
              ],
            ),
          ),
          const Divider(height: 1.0),
          Expanded(
            child: ListView.builder(
              itemBuilder: (BuildContext context, int index) {
                return ListTile(
                    title: Text(options[index]),
                    onTap: () {
                      Navigator.of(context).pop(index);
                    });
              },
              itemCount: options.length,
            ),
          ),
        ]),
      );
    },
  );
}
```

这里有几个额外需要注意的点：

- 获取屏幕的尺寸可以使用`MediaQuery.of(context).size`属性完成。
- `Stack` 组件根据子元素的次序依次堆叠，最后面的在最顶层。`textDirection` 用于排布起始位置。
- 由于 `Column` 下面嵌套了一个 `ListView`，因此需要使用 `Expanded` 将 `ListView` 包裹起来，以便有足够的空间供 `ListView` 的内容区滚动，否则会报布局溢出警告。

## 总结

实际开发过程中，还可以根据需要，利用 ModalBottomSheet的 builder 方法返回不同的组件进而定制自己的底部弹层组件，能够满足绝大多数场景。同时，借 ModalBottomSheet 的启发，我们自己也可以使用 Navigator方法来实现其他形式的弹层，例如从底部弹出登录页，登录后再返回原页面。