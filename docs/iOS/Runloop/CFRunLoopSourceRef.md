# CFRunLoopSourceRef

事件源也就是输入源。

APP运行的过程其实就是处理各种事件的过程，如果把事件分类，会有下面这种：

系统层事件、应用层事件、特殊事件。（这只是为了理解source1和source0举得一个不严谨的例子）

## source1

**基于mach_Port的，来自系统内核或者其他进程或线程的事件，通过内核和其它的线程互相发送消息，source1可以主动唤醒休眠中的RunLoop（iOS里进程间通信开发过程中我们一般不主动使用）。**

mach_port大家就理解成进程间相互发送消息的一种机制就好, 比如屏幕点击, 网络数据的传输都会触发sourse1。

字典存储：key是machport，value是sources1

## source0

非基于Port的处理事件，什么叫非基于Port的呢？就是说你这个消息不是其他进程或者内核直接发送给你的。一般是APP内部的事件, 比如`hitTest:withEvent`的处理, `PerformSelector`的事件。

非基于port的事件，手动weakup来唤醒runloop。就是应用层事件。是一个数组。

## 简单举个例子

一个APP在前台静止着，此时，用户用手指点击了一下APP界面，那么过程就是下面这样的：

首先触摸到硬件(屏幕)，屏幕表面的事件会被IOKit先包装成UIEvent，通过`mach_Port`传给正在活跃的APP，mach_port和source1是一一对应的（key和value），source1唤醒RunLoop，然后将事件Event分发给source0，然后由source0来处理。

如果没有source，也没有timer，则runloop就会睡眠，如果有，则runloop就会被唤醒，然后跑一圈。

## Machport 跨线程通讯

进程通讯是基于线程通讯的。

接收权限，发送权限。

- 点击屏幕
- app之间的分享

监听端口