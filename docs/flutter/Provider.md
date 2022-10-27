# Provider

需要在`pubspec.yaml`引入状态管理的框架`provider`。

管理页面数据，也可以使用数据共享，数据共享是单向传递。

Provider更加方便，各个页面共享数据。

传递数据，通讯。

### 根页面

数据要放在根页面（父页面）

#### ChangeNotifierProvider

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

//定义一个数据模型 通过混入ChangeNotifier管理监听者（通知模式）
class CountModel with ChangeNotifier {
  int _count = 0;
  //读数据
  int get counter => _count;
  //写数据
  void increment() {
    _count++;
    notifyListeners(); //告诉监听者 刷新build
  }
}

class ProviderDemo extends StatelessWidget {
  const ProviderDemo({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    //通过Provider组建封装数据资源
    return ChangeNotifierProvider.value(
      value: CountModel(), //需要共享的数据
      child: const MaterialApp(
        title: 'ProviderDemo',
        home: ProviderOne(),
      ),
    );
  }
}
```

### 第一个页面

#### 取数据`Provider.of<CountModel>(context)`

```dart
class ProviderOne extends StatelessWidget {
  const ProviderOne({Key? key}) : super(key: key);
  @override
  Widget build(BuildContext context) {
    //取数据
    final _counter = Provider.of<CountModel>(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('ProviderOne'),
      ),
      body: Center(
        child: Text('第一个页面count:${_counter.counter}'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.of(context).push(MaterialPageRoute(
            builder: (BuildContext context) => const ProviderTwo())),
        child: const Icon(Icons.next_plan),
      ),
    );
  }
}
```

### 第二个页面

性能优化：最小颗粒度的渲染刷新UI。使用`Consumer`。

Consumer包括：

- key
- builder 
- child

```dart
//第二个页面
class ProviderTwo extends StatelessWidget {
  const ProviderTwo({Key? key}) : super(key: key);
  @override
  Widget build(BuildContext context) {
    // //取数据 -- 不再统一的取数据
    // final _counter = Provider.of<CountModel>(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('ProviderTwo'),
      ),
      body: Center(
        //哪里用数据，就在哪里取数据
        child: Consumer<CountModel>(
          builder: (context, CountModel counter, _) =>
              Text('第二个页面count:${counter.counter}'),
        ),
      ),
      floatingActionButton: Consumer(
        child: const MyIcon(), //通过child隔离开，数据变的时候，child不需要重新渲染
        builder: (context, CountModel counter, child) => FloatingActionButton(
          onPressed: counter.increment,
          child: child,
        ),
      ),
    );
  }
}

//自定义icon
class MyIcon extends StatelessWidget {
  const MyIcon({Key? key}) : super(key: key);
  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    print('MyIcon build');
    return const Icon(Icons.add);
  }
}
```



