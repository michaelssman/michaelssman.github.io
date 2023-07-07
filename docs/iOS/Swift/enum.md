# Enum 

## 枚举的基本用法 

```swift
enum LGEnum {
    case test_one
    case test_two
    case test_three
}
```

在 C 或者 OC 中默认受整数支持，也就意味着下面的例子中： A， B， C分别默认代表 0， 1，2

```objective-c
typedef NS_ENUM(NSUInteger, LGEnum) { 
  A,
  B,
  C, 
};
```

Swift 中的枚举更加灵活，并且**不需给枚举中的每一个成员都提供值**。如果一个值（所谓“原始”值）要被提供给每一个枚举成员，那么这个值可以是字符串、字符、任意的整数值，或者是浮点类型。

```swift
enum Color : String {
    case red = "Red"
    case amber = "Amber"
    case green = "Green"
}

enum LGEnum : Double {
    case a = 10.0
    case b = 20.0
    case c = 30.0
    case d = 40.0
}
```

## 隐士 RawValue 分配

建立在 Swift 的类型推断机制上的 

```swift
enum DayOfWeekIn: Int {
    case mon, tue, wed, thu, fri = 10, sat, sun
}//0,1,2,3,4,10,11,12
enum DayOfWeekStr: String {
    case mon, tue, wed, thu, fri = "Hello world", sat, sun
}
print(DayOfWeekStr.mon.rawValue)//mon
print(DayOfWeekStr.fri.rawValue)//Hello world
print(DayOfWeekStr.sun.rawValue)//sun
//    switch DayOfWeekStr.init(rawValue: "mon"):
```

枚举值在连续内存空间的数组中。

## 关联值 

关联值，没有原始值

```swift
enum Shape{
    case circle(radious: Double)//圆形 半径
    case rectangle(width: Double, height: Double)//矩形
}
let shape = Shape.circle(radious: 10.0)
switch shape {
  case .circle(let radious):
  print("Circle radious:\(radious)")//Circle radious:10.0
  case .rectangle(let width, let height):
  print("rectangle width:\(width),height\(height)")
}
```

## 模式匹配 switch

```swift
enum Weak: String {
  case MONDAY
  case TUEDAY
  case WEDDAY
  case THUDAY
  case FRIDAY
  case SATDAY
  case SUNDAY
}

let currentWeak: Weak

switch currentWeak{
  case .MONDAY: print(Weak.MONDAY.rawValue)
  case .TUEDAY: print(Weak.TUEDAY.rawValue)
  case .WEDDAY: print(Weak.WEDDAY.rawValue)
  case .THUDAY: print(Weak.THUDAY.rawValue)
  case .FRIDAY: print(Weak.FRIDAY.rawValue)
  case .SUNDAY: print(Weak.SUNDAY.rawValue)
  case .SATDAY: print(Weak.SUNDAY.rawValue)
}
```

如果不想匹配所有的 case ，使用 defalut 关键字 

```swift
enum Weak: String {
  case MONDAY
  case TUEDAY
  case WEDDAY
  case THUDAY
  case FRIDAY
  case SATDAY
  case SUNDAY
}

let currentWeak: Weak = Weak.MONDAY

switch currentWeak{
  case .THUDAY, .SUNDAY: print("THUDAY  SUNDAY")
  case .SATDAY: print(Weak.SUNDAY.rawValue)
  default: print("SAD DAY")
}
```

如果我们要匹配关联值的话 

```swift
enum Shape{
  case circle(radious: Double)//圆形 半径
  case rectangle(width: Double, height: Double)//矩形
}
let shape = Shape.circle(radious: 10.0)
switch shape {
  case .circle(let radious):
  print("Circle radious:\(radious)")
  case .rectangle(let width, let height):
  print("rectangle width:\(width),height\(height)")
}
```

枚举值可以修改。

枚举可以定义方法（mutaing 异变方法）。

枚举可以定义属性。

枚举可以扩展extension。

枚举可以遵循协议。

## 枚举的大小 

枚举是值类型，存储在栈上。

枚举占用的内存大小。这里区分几种不同的情况。

###  1、No-payload enums

没有隐式值，只有关联值。

```swift
enum Weak {//没有关联值时，默认是UInt8类型存储，1字节，UInt最多表示256
  case MONDAY
  case TUEDAY
  case WEDDAY
  case THUDAY
  case FRIDAY
  case SATDAY
  case SUNDAY
}
print(MemoryLayout<Weak>.size)//打印结果是1
```

### 2、Single- payload enums

只有有一个负载的 enum

```swift
enum LGEnum{//只有一个成员负载，大小1字节
  case test_one(Bool)
  case test_two
  case test_three
  case test_four
}
print(MemoryLayout<LGEnum>.size)//打印结果是1
print(MemoryLayout<LGEnum>.stride)//1

enum LGEnum1{//只有一个成员负载，大小9字节
  case test_one(Int)
  case test_two
  case test_three
  case test_four
}
print(MemoryLayout<LGEnum1>.size)//打印结果是9
print(MemoryLayout<LGEnum1>.stride)//16
```

Swift 中的 enum 中的 Single-payload enums 会使用负载类型中的额外空间来记录没有负载的 case 值。

首先 Bool 类型是 1字节，也就是 UInt8 ，所以当前能表达 256 个 case的情况，对于布尔类型来说，只需要使用低位的 0, 1 这两种情况，其他剩余的空间就可以用来表示没有负载的 case 值。 

可以看到，不同的 case 值确实是按照我们在开始得出来的那个结论进行布局的。 

对于 Int 类型的负载来说，系统没有办法推算当前的负载所要使用的位数，也就意味着当前 Int 类型的负载是没有额外的剩余空间，这个时候就需要额外开辟内存空间来去存储我们的 case 值，也就是 8 + 1 = 9 字节。 

### 3、Mutil-payload enums 

有多个负载的情况产生时，当前的 enum 是如何进行布局的。

```swift
enum LGEnum2{//有两个成员负载，大小1字节
  case test_one(Bool)
  case test_two(Bool)
  case test_three
  case test_four
}
print(MemoryLayout<LGEnum2>.size)//打印结果是1
print(MemoryLayout<LGEnum2>.stride)
```

上面这个例子中，有两个 Bool 类型的负载，这个时候我们打印当前的 enum 大小，发现其大小仍然为 1，这个时候我们来看一下内存当中的存储情况 

当前一般来说，有多个负载的枚举时，当前枚举类型的大小取决于当前最大关联值的大小。 

来看一个例子 

```swift
enum LGEnum{//有两个成员负载
  case test_one(Bool)
  case test_two(Int)
  case test_three
  case test_four
}
print(MemoryLayout<LGEnum>.size)//打印结果是9
print(MemoryLayout<LGEnum>.stride)//16
```

当前 LGEnum 的大小就等于 sizeof(Int) + sizeof(rawVlaue) = 9，在比如 

```swift
enum LGEnum3{
  case test_one(Bool)
  case test_two(Int, Int, Int)
  case test_three
  case test_four
}
print(MemoryLayout<LGEnum3>.size)//打印结果是25
print(MemoryLayout<LGEnum3>.stride)//32
```

当前大小就是 sizeof(Int) * 3 + sizeof(rawVlaue) = 25。 

最后这里有几个特殊情况我们需要理解一下，我们来看下面的案例 

```swift
enum LGEnumTest {
    case test_one
}
```

对于当前的 LGEnum 只有一个 case ,不需要用任何东西来去区分当前的 case ,所以打印当前的 LGEnum 大小是0。 

**值类型在编译期大小已经确定**。

## indirect关键字

indirect修饰enum 分配到**堆**上

```swift
//二叉树
indirect enum BinaryTree<T>{
  case empty
  case node(left: BinaryTree, value: T, right: BinaryTree)
}
var node = BinaryTree<Int>.node(left: BinaryTree<Int>.empty, value: 10, right: BinaryTree<Int>.empty)
print(MemoryLayout<BinaryTree<Int>>.size)//8
print(MemoryLayout<BinaryTree<Int>>.stride)//8

//链表
indirect enum List<Element>{
  case end
  case node(Element, next: List<Element>)
}
var x = List.node(10, next: List.node(20, next: List.node(30, next: List.end)))//链表 10->20->30
```
