# ListView

## 1、数据固定写死的

```dart
ListView(
  children: [
    listViewSection('现金'),
    DiscoverCell(
      imageName: defaultImageName,
      title: '现金',
      onTapCallBack: () {},
    ),
    listViewSection('网络'),
    DiscoverCell(
      title: '微信',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
    lineWidget(),
    DiscoverCell(
      title: '支付宝',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
    listViewSection('银行卡'),
    DiscoverCell(
      title: '民生',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
    lineWidget(),
    DiscoverCell(
      title: '建设',
      imageName: defaultImageName,
      onTapCallBack: () {},
    ),
  ],
),
```

## 2、数据和UI分离

构造方法

```dart
ListView.builder(
  
  //重要‼️：根据ListView的内容大小来展示，有多少内容，ListView就多大。当item很少占不满一屏，滑动会超出ListView而看不到。
	shrinkWrap: true,
  
  //itemBuilder是一个回调函数：Function(BuildContext context, int index); 
  //方法返回一个widget 返回每一个item，类似iOS中tableView的cellForRow，鼠标放上去根据提示快速创建createMethod方法
  itemBuilder: _itemForRow, 
  
  //总共有多少个item
  itemCount: datas.length,
)


  //定义方法，返回一个widget
  //dart中不希望外界访问的话加下划线 下划线的内部指文件内部。整个文件都可以访问，其它文件不能访问。
  Widget _itemForRow(BuildContext context, int index) {
    return Container(
      ///省略代码
    );
  }
```

listView滚动的时候需要一个controller属性，

## ListView滚动

item的高度 必须要提前知道位置是多少，根据数据内容计算。