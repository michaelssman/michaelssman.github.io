# 异步Future

逻辑iOS技术号公众号 2020-05-19

Future只是异步代码，在一个队列中，还在主线程中。

方法后面加`async`（不加也可以），把耗时的操作（任务）包装到`Future`里面。

使用`await`会等异步操作完成，这时方法后面需要加`async`，把方法包成异步的。

## Future

Future对象来完成异步操作。

Future工厂构造方法，参数是一个回调函数。函数的执行代码将放入事件队列异步执行。

Future对象可以一直点下去`.then .onError .catchError .whenComplete`等等

```dart
 //完整流程 catchError写在最后
  Future(() {
    //任务 丢进异步里面
    //耗时操作
    for (int i = 0; i < 10000000; i++) {
      throw Exception('网络异常');
    }
  })
      .then((value) => print('value = $value'))
      .whenComplete(() => print('完成了'))
      .catchError((e) => print('捕获到了：' + e.toString()));
```

Future结果处理

- `.then`用来注册一个Future完成时要调用的回调
- `.catchError`注册一个回调，来捕捉Future的error
  - `.catchError`回调只处理原始Future抛出的错误，不能处理回调函数抛出的错误
  - `onError`只能处理当前Future的错误
- `.whenComplete`在Future完成之后总是会调用，不管是错误导致的完成还是正常执行完毕

## await和async配合

如果Future内部代码希望同步执行，则使用await修饰。被async修饰的函数为异步执行。

1. await后面的操作必须是异步方法（Future）才能使用await修饰
2. 当前这个函数也必须是异步函数 async修饰的函数

Future后面是任务，要想等任务执行完毕之后再操作，需要加await。

**等待用await**会卡住下面所有的

如果不想卡住所有的，不使用await，在future.then中加入要等待的任务。

## 多个Future

```dart
void main() {
  testFuture();
  print('A');
}

void testFuture() async {
  Future(() {
    sleep(Duration(seconds: 1));
    print('C');
  }).then((value) => print('D'));
  print('B');
}
//打印结果：B A C D
//虽然用了async 但不是异步
```



```dart
void main() {
  testFuture();
  print('A');
}

void testFuture() async {
  await Future(() {
    sleep(Duration(seconds: 1));
    print('C');
  }).then((value) => print('D'));
  print('B');
}

//打印结果：A C D B
//await和async使方法变成了异步的，所以A会先执行
//异步方法里 B会await上面的
```

加不加async取决于有没有await。

#### 多任务

根据异步代码的添加顺序，任务是有序的，是一个队列，dart单线程。加耗时也是有序的。

```dart
void main() {
  testFuture();
  print('A');
}

void testFuture() async {
  Future(() {
    return '任务1';
  }).then((value) => print('$value结束'));

  Future(() {
    sleep(Duration(seconds: 1));
    return '任务2';
  }).then((value) => print('$value结束'));

  Future(() {
    return '任务3';
  }).then((value) => print('$value结束'));

  Future(() {
    return '任务4';
  }).then((value) => print('$value结束'));

  print('任务添加完毕');
}
/**
打印结果：因为没有await 所以不会阻塞下面
flutter: 任务添加完毕
flutter: A
flutter: 任务1结束
flutter: 任务2结束
flutter: 任务3结束
flutter: 任务4结束
任务1 2 3 4必定是有序的。
*/
```

#### Future关联关系 

##### 依赖关系 链式

依赖的链式关系，任务1之后任务2之后任务3。

```dart
void testFuture1() {
  Future(() {
    sleep(Duration(seconds: 1));
    return '任务1';
  }).then((value) {
    print('$value结束');
    return '$value任务2';
  }).then((value) {
    print('$value结束');
    return '$value任务3';
  }).then((value) {
    print('$value结束');
    return '$value任务4';
  });
}
```

##### 同时处理多个任务 之后所有结果结果回来之后统一处理

多个future全部结束 最后结果统一处理

使用wait 任务执行顺序同样是添加顺序

任务A任务B任务C同时处理，ABC任务顺序执行，同步处理。

```dart
//多个future结束之后 处理
void testFuture2() {
  Future.wait([
    Future(() {
      print('任务A 执行');
      return '任务A';
    }),
    Future(() {
      print('任务B 执行');
      return '任务B';
    }),
    Future(() {
      print('任务C 执行');
      return '任务C';
    }),
  ]).then((value) => print(value[1] + value[0] + value[2]));
}
//打印结果:
/**
flutter: 任务A 执行
flutter: 任务B 执行
flutter: 任务C 执行
flutter: 任务B任务A任务C
*/
```

##### 某个任务 紧急处理

flutter两种队列

1. 事件队列 

   Future放在事件队列 

2. 微任务队列

   scheduleMicrotask

主线程（外部代码）优先级最高，微任务优先级比Future高

```dart
void testFuture3() {
  print('外部代码1'); //主线程

  //异步
  Future(() => print('A')).then((value) => print('A结束'));
  Future(() => print('B')).then((value) => print('B结束'));

  //异步 微任务
  scheduleMicrotask(() {
    print('微任务A');
  });
  sleep(Duration(seconds: 2)); //外部代码 睡2秒
  print('外部代码2'); //主线程
}

/**
结果：
flutter: 外部代码1
//两秒后
flutter: 外部代码2
flutter: 微任务A
flutter: A
flutter: A结束
flutter: B
flutter: B结束
*/
```



只要是队列就是有序的，无论是事件队列还是微任务队列，都是按照添加的顺序。

事件队列和微任务队列是在同一个线程。串行的。微任务只是比事件队列优先级高。



### 队列

```dart
//队列顺序 5 3 6 1 4 2
void testFuture4() {
  Future x1 = Future(() => null);
  Future x = Future(() => print('1'));
  Future(() => print('2'));
  scheduleMicrotask(() => print('3'));
  x.then((value) => print('4'));
  print('5'); //主线程最先 其它的按照添加的顺序
  x1.then((value) => print('6'));
}
```

嵌套

`.then()`里面的任务相当于放到了微任务队列，所以会先执行then里面的任务，再执行后面的事件队列的任务。

例1

```dart
//队列顺序 5 3 6 8 7 1 4 2
void testFuture4() {
  Future x1 = Future(() => null);
  x1.then((value) {
    print('6');
    scheduleMicrotask(() => print('7'));
  }).then((value) => print('8'));//then后面的就相当于一个微任务 所以8在7前面

  Future x = Future(() => print('1'));
  x.then((value) => print('4'));

  Future(() => print('2'));
  scheduleMicrotask(() => print('3'));

  print('5'); //主线程最先 其它的按照添加的顺序
}
```

例2

```dart
//队列顺序 5 3 6 8 7 1 4 2
void testFuture4() {
  Future x1 = Future(() => null);
  Future x2 = x1.then((value) {
    print('6');
    scheduleMicrotask(() => print('7'));
  });
  x2.then((value) => print('8'));

  Future x = Future(() => print('1'));
  x.then((value) => print('4'));

  Future(() => print('2'));
  scheduleMicrotask(() => print('3'));

  print('5'); //主线程最先 其它的按照添加的顺序
}
```

例3

2在9之前添加。

```dart
//队列顺序 5 3 6 8 7 1 4 10 2 9
void testFuture4() {
  Future x1 = Future(() => null);
  Future x2 = x1.then((value) {
    print('6');
    scheduleMicrotask(() => print('7'));
  });
  x2.then((value) => print('8'));

  Future x = Future(() => print('1'));
  x.then((value) {
    print('4');
    Future(() => print('9')); //9是最后添加的，在2后面。
  }).then((value) => print('10')); //then是微任务

  Future(() => print('2'));
  scheduleMicrotask(() => print('3'));

  print('5'); //主线程最先 其它的按照添加的顺序
}
```

微任务放优先级比较高的，不耗时的任务。
