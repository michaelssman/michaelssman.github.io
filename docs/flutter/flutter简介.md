# flutter简介

## RN和flutter

1. RN

   调的系统的UIKit。原生UI的基础上进行的包装。

2. flutter

   不依赖原生Ui，有自己独立的渲染引擎，iOS和安卓都有渲染引擎去解析Dart代码。

   iOS控件==flutter widget

总结：

RN性能不如flutter，原生更新的话，RN也需要更新。

flutter包大，因为有渲染引擎，效率高，界面不依赖原生。iOS和安卓UI高度统一。

## 创建flutter项目

1. Project name 不能用驼峰命名，需要用下划线，全用小写字母。

flutter写的dart代码在lib文件中。

## 强制退出AS

AS强退，会锁死lock，会锁住运行环境，再次打开工程运行会出问题。

为了保存数据，有一个缓存机制。需要删除缓存文件，cd/fluter/bin/cache/，cache里面有一个lockfile，删除lockfile就可以了。

在main.dart文件中写代码。

入口是main函数。

iOS有UIKit，flutter中有`import 'package:flutter/material.dart';`库，素材。

显示app的话就执行runApp函数。

flutter万物皆Widget组件，iOS在window上创建视图，flutter上runApp(里面创建控件)，创建了控件就会在屏幕上显示。

## 渲染机制

不变的就定义常量const。

核心渲染：**增量渲染**。

flutter修改UI，增量渲染，哪个widget变了就渲染谁。所以不变的定义const。

flutter整个页面是一个树，不变的不用管，只会渲染（新建）树中改变的节点widget，并不是全部都渲染。没有图层，只有一层页面。想要改变某一个控件的值，直接新创建一个widget对象控件，把原来的替换掉。

iOS有一层一层的控件。
