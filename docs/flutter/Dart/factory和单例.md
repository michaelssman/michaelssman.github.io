# Factory和单例

```dart
void factoryDemo() {
  FactoryClass fact1 = FactoryClass();
  FactoryClass fact2 = FactoryClass();

  print(fact1 == fact2);
}

class FactoryClass {
  //需要一个单例对象
  //静态
  static FactoryClass? _instance;

  //构造函数不能写return，如果要return的话，加factory。工厂构造方法
  factory FactoryClass() => _instance ??= FactoryClass._init();

  //私有的命名构造函数！
  FactoryClass._init();
}
```

