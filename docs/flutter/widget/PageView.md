# PageView

## 底部tabBar中间按钮

```dart
class RootPage extends StatefulWidget {
  const RootPage({Key? key}) : super(key: key);
  @override
  State<RootPage> createState() => _RootPageState();
}

class _RootPageState extends State<RootPage> {
  int _currentIndex = 0;
  final PageController _pageController = PageController(); //保存在widget树中 不被销毁
  
  //定义一个pages数组
  final List<Widget> _pages = [
    const AccountDetails(),
    //中间占位
    const SizedBox(),
    const Mine()
  ];
  
  //底部导航栏items
  final List<BottomNavigationBarItem> _bottomNavigationBarItems = [
    BottomNavigationBarItem(
      icon: Image(
        height: 20,
        width: 20,
        image: AssetImage('images/tabbar_chat.png'),
      ),
      activeIcon: Image(
        height: 20,
        width: 20,
        image: AssetImage('images/tabbar_chat_hl.png'),
      ),
      label: '微信',
    ),
    // 中间占位按钮
    BottomNavigationBarItem(
      icon: SizedBox(
        width: 60,
      ),
      label: "记一笔",
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.person_outline),
      label: '我的',
    ),
  ];
    
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      //这种情况：切换页面的时候，会把之前的那个tab给干掉。不在widget树中的页面都会被销毁。所以使用PageView。
      //onTap方法调用setState，树中就没有了。所以需要把所有的tab都放到**widget树**中，切换的时候是显示不显示的问题。
      // body: _pages[_currentIndex],
      // bottomNavigationBar: BottomNavigationBar(
      //   items: [],//底部导航按钮
      //   onTap: (index) {
      //     setState(() {
      //       _currentIndex = index;
      //     });
      //   },
      // ),
      
      body: PageView(
        //禁止拖拽
        //physics: const NeverScrollableScrollPhysics(),
        //滑动改变
        onPageChanged: (int index) {
          setState(() {
            _currentIndex = index;
          });
        },
        controller: _pageController,
        children: _pages,
      ),
      
      //底部导航条
      bottomNavigationBar: BottomNavigationBar(
        selectedFontSize: 16.0, //文字选中
        //点击改变
        onTap: (index) {
          //点击中间按钮
          if (index == 1) {
            clickCenterButton(context);
          } else {
            setState(() {
              _currentIndex = index;
              _pageController.jumpToPage(index);
            });
          }
        },
        //样式 不然几个显示是白色的，看不到
        type: BottomNavigationBarType.fixed,
        fixedColor: Colors.green, //选中时的颜色
        currentIndex: _currentIndex,
        items: _bottomNavigationBarItems,
      ),
      
      //浮动按钮
      floatingActionButton: FloatingActionButton(
        onPressed: () => clickCenterButton(context),
        child: const Icon(
          Icons.add_circle_rounded,
          size: 50,
        ),
      ),
      // 浮动按钮 停靠在底部中间位置
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked, 
    );
  }
  
  //中间按钮点击方法
  void clickCenterButton(BuildContext context) => hh.navigatorPush(context, const AccTabBar());
}
```

禁止拖拽滑动：

```dart
physics: const NeverScrollableScrollPhysics(),
```

主动设置页面跳转：

```dart
_pageController.jumpToPage(_currentIndex);
```

页面改变的回调：

```dart
onPageChanged: (int index) {
}
```

## 无限滑动

```dart
late PageController _pageController; //创建一个pageController，控制页面的切换

@override
void initState() {
  super.initState();
  _pageController = PageController(
    initialPage: 3,//默认滚动位置
  );
}


PageView.builder(
  controller: _pageController,
  onPageChanged: (index) {},
  itemBuilder: (context, index) {
    return Container();
  },
),
```

