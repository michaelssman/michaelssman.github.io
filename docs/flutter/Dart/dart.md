# dart

dart安装位置查看`which dart`。

dart是单线程的。但是单线程也可以异步。

## 继承

所有的类默认继承Object。

默认构造方法，子类会默认调用。如果是有名称或有参数的构造方法，必须显式的主动实现。

## 不需要对外暴露

使用`_`下划线，私有的。

加下划线，外部文件不能访问。同文件，不管是不是私有的都可以访问。

包括类和变量都可以`_`开头。

## static

类方法 静态方法

## 可选 空安全

Dart 2.12后对空安全检测

`fiinal` 变量类型后面需要加`？`，使用的时候需要先判断是否为空，然后加上`!`强制解包。

## 类型问题

加圆角的时候，网络图片，使用`as`强转。

```dart
Container(
  margin: EdgeInsets.all(10),
  width: 34,
  height: 34,
  //圆角
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(6.0),
    image: DecorationImage(
      image: imageUrl != null
      ? NetworkImage(imageUrl!) as ImageProvider
      : AssetImage(imageAssets!),
    ),
  ),
),
```

