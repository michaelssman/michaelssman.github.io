# 属性关键字

## MRC和ARC

retain 、assign 是 MRC 时的关键字，到 ARC 时，换成了 strong 和 weak 。

属性默认：

MRC：assign ;

ARC：对象是 strong，基本数据类型还是 assign 。

## strong

strong 是每对这个属性引用一次，retainCount 就会+1，只能修饰 NSObject 对象，不能修饰基本数据类型。是 id 和 对象 的默认修饰符。

## weak

weak 对属性引用时，retainCount 不变。

表示一种“非拥有关系”。为这种属性设置新值时，设置方法既不释放旧值，也不保留新值，不会使引用计数加1。

当所指对象被销毁时，指针会自动被置为`nil`，防止野指针。只能修饰 NSObject 对象，不能修饰基本数据类型。 主要用于避免循环引用。

weak的原理：runtime维护了一个weak表，用于存储指向某个对象的所有weak指针。

weak表其实是一个hash（哈希）表，key是所指对象的地址，value是weak指针的地址（这个地址的值是所指对象指针的地址）数组。

### 代理delegate使用weak

一个类的 Delegate 对象通常还引用着类本身`self.tableView.delegate = self`，这样很容易造成引用循环的问题，所以类的 Delegate 属性要设置为弱引用。

**assign：**

assign 指针赋值，不对引用计数操作，使用之后如果没有置为nil，可能会产生野指针。
delegate指向的对象销毁之后，delegate中依然会保存之前对象的地址，delegate就成了野指针。

**weak：**

weak 指明该对象并不负责保持delegate这个对象，delegate这个对象的销毁是由外部控制的，当delegate指向的对象销毁之后，delegate = nil。

## assign

assign是默认关键字，用来修饰基本数据类型。
对这个关键字声明的属性操作时，retainCount 是一直不变的。

### 为什么不用assign声明对象

因为 assign 修饰的对象，在释放之后，指针的地址还是存在的，也就是说指针并没有被置为nil，造成野指针。访问野指针，会导致程序 crash。

### 为什么可以用assign修饰基本数据类型

因为基本数据类型是分配在栈上，栈的内存会由系统自己自动处理回收，不会造成野指针。

## copy

当某对象的类具有可修改的子类时，应该将属性设为`copy`。例如：`NSString`，`NSArray`，`NSDictionary`

copy分深copy和浅copy

浅copy，对象指针的复制，目标对象指针和原对象指针指向同一块内存空间，引用计数增加

深copy，对象内容的复制，开辟一块新的内存空间

可变的对象的copy和mutableCopy都是深拷贝

不可变对象的copy是浅拷贝，mutable是深拷贝

copy方法返回的都是不可变对象

>```objectivec
>@property (nonatomic，copy) NSMutableArray *array;
>```
>
>添加,删除,修改数组内的元素的时候,程序会因为找不到对应的方法(`unrecognised selector`)而崩溃.因为 `copy` 就是复制一个不可变 `NSArray`的对象。

### NSString使用copy修饰不用strong修饰，

用strong修饰一个name属性，如果赋值的是一个可变对象，当可变对象的值发生改变的时候，name的值也会改变，这不是我们期望的，是因为name使用strong修饰后，指向跟可变对象相同的一块内存地址。

如果使用copy的话，则是深拷贝，会开辟一块新的内存空间，因此可变对象值变化时，也不会影响name的值。

```objective-c
NSMutableString *tS = [NSMutableString stringWithString:@"asd"];
self.name = tS;
[tS appendString:@"fg"];
NSLog(@"%@",self.name);
/**
 name属性用copy修饰 打印asd
 name属性用strong修饰 打印asdfg
 */
```

## retain

alloc new copy 引用计数都会加1。

strong就是retain  通过this（当前对象）获取sideTable 里面引用计数表。rdfCont引用计数加1。
