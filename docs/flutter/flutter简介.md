# flutter简介

### RN和flutter

1. RN

   调的系统的UIKit。原生UI的基础上进行的包装。

2. flutter

   不依赖原生Ui，有自己独立的渲染引擎，iOS和安卓都有渲染引擎去解析Dart代码。

   iOS控件==flutter widget

总结：

RN性能不如flutter，原生更新的话，RN也需要更新。

flutter包大，因为有渲染引擎，效率高，界面不依赖原生。iOS和安卓UI高度统一。

# 创建flutter项目

1. Project name 不能用驼峰命名，需要用下划线，全用小写字母。

flutter写的dart代码在lib文件中。

### 强制退出AS

AS强退，会锁死lock，会锁住运行环境，再次打开工程运行会出问题。

为了保存数据，有一个缓存机制。需要删除缓存文件，cd/fluter/bin/cache/，cache里面有一个lockfile，删除lockfile就可以了。

在main.dart文件中写代码。

入口是main函数。

iOS有UIKit，flutter中有`import 'package:flutter/material.dart';`库，素材。

显示app的话就执行runApp函数。

flutter万物皆Widget组件，iOS在window上创建视图，flutter上runApp(里面创建控件)，创建了控件就会在屏幕上显示。

### 渲染机制

不变的就定义常量const。

核心渲染：**增量渲染**。

flutter修改UI，增量渲染，哪个widget变了就渲染谁。所以不变的定义const。

flutter整个页面是一个树，不变的不用管，只会渲染（新建）树中改变的节点widget，并不是全部都渲染。没有图层，只有一层页面。想要改变某一个控件的值，直接新创建一个widget对象控件，把原来的替换掉。

iOS有一层一层的控件。

### 箭头函数

如果代码只有一行的话 可以使用箭头函数。

```dart
void main() {
  runApp(App());
}
//等于下面一行
void main() => runApp(App());
```

### final

不会变化的，最终变量。被定义出来之后，**可以赋值一次**。

用final修饰的属性，const修饰的构造方法（常量对象）。常量对象的创建效率更高。

`?`表示可选参数，可以为空，使用参数的时候需要用到`!`强制解包。

`required`修饰 必传参数

```dart
class DiscoverCell extends StatelessWidget {
  final String title;
  final String imageName;
  final String? subTitle;
  final String? subImageName;

  DiscoverCell({//大括号表示可选参数
    required this.title, //title必须有
    this.subTitle,
    required this.imageName, //imageName必须有
    this.subImageName,
  })  : assert(title != null, 'title不能为空！'),
        assert(imageName != null, 'imageName不能为空！');
  
  //后面在使用subTitle和subImageName的时候需要！强制解包
}
```

Dart 2.12后对空安全检测：

### 不需要对外暴露

使用`_`下划线，私有的。

本文件私有，可以使用，跨文件不能使用。

包括类和变量都可以`_`开头。

### static

类方法 静态方法

# dart2.12.0

#### 可选 空安全

`fiinal` 变量类型后面需要加`？`，使用的时候需要先判断是否为空，然后加上`!`强制解包。

#### 类型问题

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

