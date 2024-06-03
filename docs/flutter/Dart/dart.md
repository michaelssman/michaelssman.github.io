# dart

dart安装位置查看`which dart`。

dart是单线程的。但是单线程也可以异步。

声明式 UI 的编程语言。

`..`会回传本身。

## 继承

所有的类默认继承Object。

默认构造方法，子类会默认调用。如果是有名称或有参数的构造方法，必须显式的主动实现。

## 不需要对外暴露

dart中不希望外界访问的话加下划线 下划线的内部指文件内部。整个文件都可以访问，其它文件不能访问。

使用`_`下划线，私有的。

加下划线，外部文件不能访问。同文件，不管是不是私有的都可以访问。

包括类和变量都可以`_`开头。

## static

类方法 静态方法

## 可选 空安全

`fiinal` 变量类型后面加`？`，使用的时候需要先判断是否为空，然后加上`!`强制解包。

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

## late

方法里面创建一个变量，如果没有初始化，方法返回该变量，就会提示需要初始化。使用late修饰之后，就可以只声明一个变量，延迟初始化。

## 命令行

```
dart fix --dry-run
```
