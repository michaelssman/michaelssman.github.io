# Enum 

## 枚举的基本用法 

swift 中通过 `enum` 关键字来声明一个枚举

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

Swift 中的枚举则更加灵活，并且**不需给枚举中的每一个成员都提供值**。如果一个值（所谓“原始”值）要被提供给每一个枚举成员，那么这个值可以是字符串、字符、任意的整数值，或者是浮点类型。

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

隐士 RawValue 分配 是建立在 Swift 的类型推断机制上的 

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
```

枚举值在连续内存空间的数组中。

## 关联值 

```swift
// MARK: 关联值，没有原始值
enum Shape{
    case circle(radious: Double)//圆形 半径
    case rectangle(width: Double, height: Double)//矩形
}
var circle = Shape.circle(radious: 10.0)
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

枚举值可以修改，

枚举可以定义方法（mutaing 异变方法）。

枚举可以定义属性。

枚举可以扩展extension。

枚举可以遵循协议。

## 枚举的大小 

枚举是指类型，存储在栈上。

###  No-payload enums

接下来我们来讨论一下枚举占用的内存大小，这里我们区分几种不同的情况，首先第一种就是 No-payload enums 。 没有隐式值，只有关联值。

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

### Single- payload enums

No-payload enums 的布局比较简单，我们也比较好理解，接下来我们来理解一下 Single- payload enums 的内存布局， 字面意思就是有一个负载的 enum 比如下面这个例子 

```swift
    enum LGEnum{//只有一个成员负载，大小1字节
        case test_one(Bool)
        case test_two
        case test_three
        case test_four
    }
    print(MemoryLayout<LGEnum>.size)//打印结果是1

    enum LGEnum1{//只有一个成员负载，大小9字节
        case test_one(Int)
        case test_two
        case test_three
        case test_four
    }
    print(MemoryLayout<LGEnum1>.size)//打印结果是9
```

注意， Swift 中的 enum 中的 Single-payload enums 会使用负载类型中的额外空间来记录没有负载的 case 值。这句话该怎么理解？首先 Bool 类型是 1字节，也就是 UInt8 ，所以当前能表达 256 个 case的情况，对于布尔类型来说，只需要使用低位的 0, 1 这两种情况，其他剩余的空间就可以用来表示没有负载的 case 值。 

可以看到，不同的 case 值确实是按照我们在开始得出来的那个结论进行布局的。 

对于 Int 类型的负载来说，其实系统是没有办法推算当前的负载所要使用的位数，也就意味着当前 Int 类型的负载是没有额外的剩余空间的，这个时候我们就需要额外开辟内存空间来去存储我们的 case 值，也就是 8 + 1 = 9 字节。 

### Mutil-payload enums 

上面说完了 Single-payload enums , 接下来我们说第三种情况 Mutil-payload enums , 有多个负载的情况产生时，当前的 enum 是如何进行布局的那？ 

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

上面这个例子中，我们有两个 Bool 类型的负载，这个时候我们打印当前的 enum 大小，发现其大小仍然为 1，这个时候我们来看一下内存当中的存储情况 

当前一般来说，我们有多个负载的枚举时，当前枚举类型的大小取决于当前最大关联值的大小。 

我们来看一个例子 

```swift
    enum LGEnum{
        case test_one(Bool)
        case test_two(Int)
        case test_three
        case test_four
    }
```

当前 LGEnum 的大小就等于 sizeof(Int) + sizeof(rawVlaue) = 9，在比如 

```swift
    enum LGEnum3{
        case test_one(Bool)
        case test_two(Int, Int, Int)
        case test_three
        case test_four
    }
```

当前大小就是 sizeof(Int) * 3 + sizeof(rawVlaue) = 25。 

最后这里有几个特殊情况我们需要理解一下，我们来看下面的案例 

```swift
enum LGEnumTest {
    case test_one
}
```

对于当前的 LGEnum 只有一个 case ,我们不需要用任何东西来去区分当前的 case ,所以当我们打印当前的 LGEnum 大小你会发现时 0。 



**值类型在编译器大小已经确定**。

## indirect关键字

```swift
// MARK: indirect 分配到堆上
func test_indirect() {
    indirect enum BinaryTree<T>{//二叉树
        case empty
        case node(left: BinaryTree, value: T, right: BinaryTree)
    }
    var node = BinaryTree<Int>.node(left: BinaryTree<Int>.empty, value: 10, right: BinaryTree<Int>.empty)
    print(MemoryLayout<BinaryTree<Int>>.size)//测试大小
    print(MemoryLayout<BinaryTree<Int>>.stride)//测试大小
    
    //链表
    indirect enum List<Element>{
        case end
        case node(Element, next: List<Element>)
    }
    var x = List.node(10, next: List.node(20, next: List.node(30, next: List.end)))//链表 10 20 30
}
```

## Optional 

认识可选值 

之前我们在写代码的过程中早就接触过可选值，比如我们在代码这样定义： 

```swift
class LGTeacher{
  var age: Int? 
}
```

当前的 age 我们就称之为可选值，当然可选值的写法这两者是等同的。optional语法糖

```swift
var age: Int? = var age: Optional<Int>
```

那对于 Optional 的本质是什么？我们直接跳转到源码，打开 Optional.swift 文件 

```swift
@frozen
public enum Optional<Wrapped>: ExpressibleByNilLiteral {
  case none 
  case some(Wrapped)
}
```

既然 Optional 的本质是枚举，那么我们也可以仿照系统的实现制作一个自己的 Optional 

```swift
enum MyOptional<Value> { 
  case some(Value)
  case none
}
```

比如给定任意一个自然数，如果当前自然数是偶数返回，否则为 nil，我们应该怎么表达这个案 例 

```swift
    enum MyOptional<Value> {
        case some(Value)
        case none
    }
    
    func getOddValue(_ value: Int) -> MyOptional<Int> {
        if value % 2 == 0 {
            return .some(value)
        }
        else{
            return .none
        }
    }
```

这个时候给定一个数组，我们想删除数组中所有的偶数 

```swift
    var array = [1, 2, 3, 4, 5, 6]
    for element in array{
        let value = getOddValue(element)
        switch value {
        case .some(let value):
            array.remove(at: array.firstIndex(of: value)!)
        default:
            print("not exit")
        }
    }
```

如果每一个可选值都用模式匹配的方式来获取值在代码书写上就比较繁琐，我们还可以使用 if let 的方式来进行可选值绑定 

```swift
        if let value = value{
            array.remove(at: array.firstIndex(of: value)!)
        }
```

除了使用 if let 来处理可选值之外，我们还可以使用 gurad let 来简化我们的代码，我们来看一个具体的案例 

guard let 和 if let 刚好相反， 

guard let 守护一定有值。如果没有，直接返回。 

通常判断是否有值之后，会做具体的逻辑实现，通常代码多 

如果用 if let 凭空多了一层分支， guard let 是降低分支层次的办法 

## 可选链 

我们都知道在OC 中我们给一个 nil 对象发送消息什么也不会发生， Swift 中我们是没有办法向一个 nil 对象直接发送消息，但是借助可选链可以达到类似的效果。我们看下面两段代码

```swift
let str: String? = "abc"
let upperStr = str?.uppercased()// Optional<"ABC">
var strTwo: String?
let upperStrTwo = strTwo?.uppercased() // nil
```

同样的可选链对于下标和函数调用也适用 

```swift
    //闭包
    var closure: ((Int) -> ())?
    closure?(1) // closure 为 nil 不执行
    
    //字典
    let dict = ["one": 1, "two": 2]
    dict?["one"] // Optional(1)
    dict?["three"] // nil
```

## ?? 运算符 （空合并运算符） 

( `a ?? b` ) 将对可选类型 a 进行空判断，如果 a 包含一个值就进行解包，否则就返回 一个默认值 b . 

- 表达式 a 必须是 Optional 类型 
- 默认值 b 的类型必须要和 a 存储值的类型保持一致 

## 运算符重载 

在源码中我们可以看到除了重载了 ?? 运算符， Optional 类型还重载了 == , ?= 等等运算符，实际开发中我们可以通过重载运算符简化我们的表达式。 

比如在开发中我们定义了一个二维向量，这个时候我们想对两个向量进行基本的操作，那么我们就可以通过重载运算符来达到我们的目的 

```swift
// MARK: 运算符重载 必须是static
struct Vector {
    let x: Int
    let y: Int
}
extension Vector {
    static func + (fistVector: Vector, secondVector: Vector) -> Vector {
        return Vector(x: fistVector.x + secondVector.x, y: fistVector.y + secondVector.y)
    }
    static prefix func - (vector: Vector) -> Vector {//前缀 - 
        return Vector(x: -vector.x, y: -vector.y)
    }
    static func - (fistVector: Vector, secondVector: Vector) -> Vector {
        return fistVector + -secondVector
        
    }
}

func yunsuanfuchongzai_test() {
    let x = Vector(x: 10, y: 20)
    let y = Vector(x: 20, y: 30)
    let z = x + y
    print(z)
}
```

## 自定义运算符 

- infix中缀运算符
- perfix前缀运算符
- postfix后缀运算符

```swift
// MARK: 运算符重载 必须是static
struct Vector {
    let x: Int
    let y: Int
}
// MARK: 自定义运算符 ---为乘法
infix operator --- : AdditionPrecedence
precedencegroup HHPrecedence {
    //指定优先级
//    higherThan: lower group names
    lowerThan: AdditionPrecedence
    associativity: left
//    assignment: assignment
}
extension Vector {
    //已有的运算符
    static func + (fistVector: Vector, secondVector: Vector) -> Vector {
        return Vector(x: fistVector.x + secondVector.x, y: fistVector.y + secondVector.y)
    }
    static prefix func - (vector: Vector) -> Vector {//前缀 -
        return Vector(x: -vector.x, y: -vector.y)
    }
    static func - (fistVector: Vector, secondVector: Vector) -> Vector {
        return fistVector + -secondVector
    }
    //没有的运算符
    static func --- (fistVector: Vector, secondVector: Vector) -> Vector {
        return Vector(x: fistVector.x * secondVector.x, y: fistVector.y * secondVector.y)
    }
}
func yunsuanfuchongzai_test() {
    let x = Vector(x: 10, y: 20)
    let y = Vector(x: 20, y: 30)
    let z = x + y
    let s = x --- y
    print(z)
    print(s)
}
```

## 隐士解析可选类型

隐式解析可选类型是可选类型的一种，使用的过程中和非可选类型无异。它们之间唯一的区别是，隐式解析可选类型是你告诉对 Swift 编译器，我在运行时访问时，值不会为 nil。 

```swift
    var age0: Int//不可选
    var age1: Int!//可选值 隐式解包，使用的时候不需要再进行解包的操作了，如果age1为nil了 则崩溃。
    var age2: Int?//可选值
```

## 与可选值有关的高阶函数 

- map ： 这个方法接受一个闭包，如果可选值有内容则调用这个闭包进行转换 

```swift
var dict = ["one": "1", "two": "2"]
let result = dict["one"].map{ Int($0) }
// Optional(Optional(1))
```

上面的代码中我们从字典中取出字符串”1”，并将其转换为Int类型，但因为String转换成Int不一定能成功，所以返回的是Int?类型，而且字典通过键不一定能取得到值，所以map返回的也是一个Optional，所以最后上述代result的类型为Int??类型。 

那么如何把我们的双重可选展平开来，这个时候我们就需要使用到 

- flatMap: 可以把结果展平成为单个可选值 

```swift
var dict = ["one": "1", "two": "2"]
let result = dict["one"].flatMap{ Int($0) }
// Optional(1)
```

- 注意，这个方法是作用在Optioanl的方法，而不是作用在Sequence上的 

- 作用在Sequence上的flatMap方法在Swift4.1中被更名为compactMap，该方法可以将序列中的nil过滤出去

```swift
let array1 = ["1", "2", "3", nil]
let result1 = array1.compactMap{ $0 } // ["1", "2", "3"]
let array2 = ["1", "2", "3", "four"]
let result2 = array2.compactMap{ Int($0) } // [1, 2, 3]
```

