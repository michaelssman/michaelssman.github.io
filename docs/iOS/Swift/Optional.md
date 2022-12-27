# Optional 

通过在变量类型后面加`?`表示

可选项没法直接使用，需要使用`!`展开后才能使用（表示这个可选项里面有值）

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

## Optional本质

直接跳转到源码，打开 Optional.swift 文件 

```swift
@frozen
//泛型<Wrapped>
public enum Optional<Wrapped>: ExpressibleByNilLiteral {
  case none 
  case some(Wrapped)
  
  //泛型属性 public方法，值是Wrapped泛型类型
  @inlinable public var unsafelyUnwrapped: Wrapped { get }
}

//例
var str: Optional<String> = "dfd"
if let actualStr = str {
  let count = actualStr.count
  print(count)
}

//Optional<String>等同于String?
var str: String? = "dfd"

//Optional的展开，通过unsafelyUnwrapped获取实际的值
if str != nil {
  let count = str.unsafelyUnwrapped.count
}
print(count)
```

既然 Optional 的本质是枚举，那么我们也可以仿照系统的实现制作一个自己的 Optional 

```swift
enum MyOptional<Value> {//自定义可选值
  case some(Value)
  case none
}
```

例：给定任意一个自然数，如果当前自然数是偶数返回，否则为 nil

```swift
enum MyOptional<Value> {//自定义可选值
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

//删除数组中所有的偶数
var array = [1, 2, 3, 4, 5, 6]
for element in array{
  let value = getOddValue(element)
  
  //第一种
  switch value {
    case .some(let value):
    array.remove(at: array.firstIndex(of: value)!)
    default:
    print("not exit")
  }
  
  //第二种
  //如果每一个可选值都用模式匹配的方式来获取值在代码书写上就比较繁琐，我们还可以使用 if let 的方式来进行可选值绑定 
   if let value = value{
     array.remove(at: array.firstIndex(of: value)!)
   }
}
```

## Optional绑定

- 可以使用可选项绑定来判断可选项是否包含值，如果包含就把值赋给一个临时的常量或者变量
- 可选绑定可以与 if 和 while 的语句使用来检查可选项内部的值，并赋值给一个变量或常量
- 同一个 if 语句中包含多可选项绑定，用逗号分隔即可。如果任一可选绑定结果是 nil 或者布尔值为 false ，那么整个 if 判断会被看作 false

```swift
var str: String? = "adb"
if let actualStr = str {
  let count = actualStr.count
  print(count)
}
```

除了使用 if let 来处理可选值之外，我们还可以使用 gurad let 来简化我们的代码。

guard let 和 if let 刚好相反， guard let 守护一定有值。如果没有，直接返回。 

通常判断是否有值之后，会做具体的逻辑实现，通常代码多 

如果用 if let 凭空多了一层分支， guard let 是降低分支层次的办法 

## 隐士解析可选类型

- 有些可选项一旦被设定值之后，就会一直拥有值，在这种情况下，就可以去掉检查的需求，也不必每次访问的时候都进行展开
- 通过在声明的类型后边添加一个叹号（ String! ）而非问号（ String? ） 来书写隐式展开可选项
- 隐式展开可选项主要被用在 Swift 类的初始化过程中

```swift
var str: String! = "adb"
let count = str.count
print(count)
```

隐式解析可选类型是可选类型的一种，使用的过程中和非可选类型无异。它们之间唯一的区别是，隐式解析可选类型是你告诉对 Swift 编译器，我在运行时访问时，值不会为 nil。 

```swift
var age0: Int//不可选
var age1: Int!//可选值 隐式解包，使用的时候不需要再进行解包的操作了，如果age1为nil了 则崩溃。
var age2: Int?//可选值
```

## 可选链 

- 可选项后面加问号
- 如果可选项不为 nil，**返回一个可选项结果**，否则返回 nil

```swift
var str: String? = "adb"
let count = str?.count
if let count = count {
  let lastIndex = count - 1
}
```

我们都知道在OC 中我们给一个 nil 对象发送消息什么也不会发生， Swift 中没有办法向一个 nil 对象直接发送消息，但是借助可选链可以达到类似的效果。我们看下面两段代码

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

( `a ?? b` ) 将对可选类型 a 进行空判断，如果 a 包含一个值就进行解包，否则就返回 一个默认值 b。

- 表达式 a 必须是 Optional 类型 
- 默认值 b 的类型必须要和 a 存储值的类型保持一致 

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

