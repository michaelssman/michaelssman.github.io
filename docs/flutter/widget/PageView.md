# PageView

```dart
class RootPage extends StatefulWidget {
  const RootPage({Key? key}) : super(key: key);
  @override
  _RootPageState createState() => _RootPageState();
}

class _RootPageState extends State<RootPage> {
  int _currentIndex = 0;
  //定义一个pages数组
  final List<Widget> _pages = [
    const Account(),
    const Account(),
    const Account(),
    const Account()
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
    BottomNavigationBarItem(
      icon: Icon(Icons.bookmark),
      label: '通讯录',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.apartment),
      label: 'apps',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.person_outline),
      label: 'Demos',
    ),
  ];
  
  final PageController _pageController = PageController(); //保存在widget树中 不被销毁
    
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
          _currentIndex = index;
          setState(() {});
        },
        controller: _pageController,
        children: _pages,
      ),
      
      //底部导航条
      bottomNavigationBar: BottomNavigationBar(
        selectedFontSize: 16.0, //文字选中
        //点击改变
        onTap: (index) {
          setState(() {
            _currentIndex = index;
            _pageController.jumpToPage(_currentIndex);
          });
        },
        //样式 不然4个显示是白色的，看不到
        type: BottomNavigationBarType.fixed,
        fixedColor: Colors.green, //选中时的颜色
        currentIndex: _currentIndex,
        items: _bottomNavigationBarItems,
      ),
    );
  }
}
```
