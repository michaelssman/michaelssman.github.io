# 抽象类

抽象类（协议，接口）
抽象类：不能被实例化的类，使用abstract修饰

```dart
//测试
abstractDemo() {
  AbstractClass as = SubClass();
  as.sum(10, 20);

  SubClass1 sC = SubClass1();
  sC.sum(10, 20);
  sC.sum1(20, 20);
  sC.sum2(30, 20);
}

abstract class AbstractClass {
  //没有实现的方法就是抽象方法
  //抽象方法只能放在抽象类里面
  int sum(int a, int b);
}

abstract class AbstractClass1 {
  int sum1(int a, int b);
}

abstract class AbstractClass2 {
  int sum2(int a, int b);
}

///抽象类的使用，使用子类
///子类必须实现抽象方法
class SubClass extends AbstractClass {
  @override
  int sum(int a, int b) {
    // TODO: implement sum
    print('a+b=${a + b}');
    return a + b;
  }
}

class a {
  var name;
  run() {}
}

///多继承implements，所有的方法和属性必须都重写
class SubClass1 implements AbstractClass, AbstractClass1, AbstractClass2, a {
  @override
  var name;

  @override
  run() {
    // TODO: implement run
    throw UnimplementedError();
  }

  @override
  int sum(int a, int b) {
    print('subClass1..sum');
    return a + b;
  }

  @override
  int sum1(int a, int b) {
    print('subClass1..sum1');
    return a + b;
  }

  @override
  int sum2(int a, int b) {
    print('subClass1..su2m');
    return a + b;
  }
}
```

