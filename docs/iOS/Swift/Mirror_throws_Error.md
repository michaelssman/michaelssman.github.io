# Mirror_throws_error

## 类型

### self

**.self: 如果T是实例对象，T.self返回的就是他本身；如果T是类，T.self 返回的就是元类型**

```swift
// MARK: self在方法中的表现
//类LGTeacherM
//元类LGTeacherM.Type类型 通过LGTeacherM.self获取
class LGTeacherM{
    var age = 18
    func test(){
        print(self)//在实例方法中代表当前实例对象
    }
    static func test1(){
        print(self)//在类方法中self是LGTeacherM这个类型本身
    }
}

var t = LGTeacherM()
let t3 = t.self//返回t本身
let t4 = t.self.self//返回t本身
```

### Self

#### 1、Self作为方法返回值

```swift
class LGTeacherSelf{
  static let age = 18
  func test() -> Self {//Self作为方法返回类型 Self指当前实例对象
    return self//当前实例对象
  }
  func haha() {
    print(#function)
  }
}

let t = LGTeacherSelf()
t.test().haha()
```

#### 2、Self在属性中

```swift
class LGPersonP {
  //类型属性
  static let age = 5
  //存储属性
  let age1 = age
  var age2 = age
  //let age3 = self.age//报错，self经过初始化才可以得到，为定义时想要访问需要使用Self
  lazy var age3 = Self.age
}

let p = LGPersonP()
print(p.age3)
```

#### 3、Self在协议中

```swift
protocol MyProtocol {
  func get() -> Self//Self指遵循协议的类型
}
class LGPersonM: MyProtocol{
  func get() -> Self {//此时Self指的就是LGPersonM类型
    return self
  }
}

func testSelf_Protocol() {
  let p: MyProtocol = LGPersonM()//p的静态类型是MyProtocol
  print(p.get())//返回遵循协议的类的类型
}
```

### AnyObject

代表任意类的实例（instance）的类型，任意类的类型，仅类遵守的协议。 

```swift
class LGTeacherM{
  var age = 18
}

// MARK: AnyObject
protocol MyProtocol0: AnyObject{//MyProtocol0只能够被class遵守，结构体不行
}
extension LGTeacherM: MyProtocol0{}

var t = LGTeacherM()
var t1: AnyObject = t//AnyObject代表当前实例对象的类型。返回t本身
var t2:AnyObject = LGTeacherM.self//代表LGTeacherM类的类型（元类型）
```

### Any

代表任意类型，包括 funcation 类型或者 Optional 类型 

```swift
// 等价于 OC的id，Any比AnyObject更广泛
// Any: 代表任意类型，包括 funcation 类型或者 Optional 类型
//var array0:[AnyObject] = [1,"fds"]//1是基本类型
var array:[Any] = [1, "HHH"]

class LGTeacherM{
  var age = 18
}
let t = LGTeacherM()
let t6: Any = t
```

### AnyClass

**AnyClass 代表任意实例的类型，类的类型 AnyClass = AnyObject.Type**

类：LGTeacherM

元类：LGTeacherM.Type类型 通过LGTeacherM.self获取

```swift
class LGTeacherM{
  var age = 18
}

var t = LGTeacherM()
let t5: AnyClass = LGTeacherM.self//LGTeacherM.Type
let t7: AnyClass = type(of: t)//LGTeacherM.Type
```

### type(of: <##T##>)

```swift
func test_typeof() {
    //获取某个值的动态类型（真实类型）
    func test(_ value: Any){//value静态类型是Any，但此时传的ageM是Int类型
        print(type(of: value))
    }
    
    let ageM = 10
    test(ageM) //打印Int
}		
```

### Type

实例对象的Type没有意义，类才可以Type

## Swift Runtime 

我们⽤下⾯这段代码来测试⼀下：

```swift
class LGTeacher{
    var age: Int = 18
    func teach(){
        print("teach")
    }
}
//let t = LGTeacher()
func test(){
    var methodCount:UInt32 = 0
    let methodlist = class_copyMethodList(LGTeacher.self, &methodCount)
    for i in 0..<numericCast(methodCount) {
        if let method = methodlist?[i]{
            let methodName = method_getName(method);
            print("⽅法列表:\(String(describing: methodName))")
        }else{
            print("not found method");
        }
    }
    var count:UInt32 = 0
    let proList = class_copyPropertyList(LGTeacher.self, &count)
    for i in 0..<numericCast(count) {
        if let property = proList?[i]{
            let propertyName = property_getName(property);
            print("属性成员属性:\(String(utf8String: propertyName)!)")
        }else{
            print("没有找到你要的属性");
        }
    }
}
```

运⾏这段代码你会发现，当前不管是我们的⽅法列表还是我们的属性列表，此次此刻都是为空的。 

上节课，我们学过 @objc 的标识，如果这个时候我们将我们当前的⽅法和属性添加上，会发⽣什么？ 

此刻代码会输出我们当前的 teach ⽅法和 age 属性。但是此刻对于我们的 OC 来说是没有办法使⽤的： 

### 结论

- 对于纯 Swift 类来说，⽅法和属性不加任何修饰符的情况下。这个时候其实已经不具备我们所谓的Runtime 特性了，这和我们在上⼀节课的⽅法调度（V-Table调度）是不谋⽽合的。 
- 对于纯 Swift 类，⽅法和属性添加 @objc 标识的情况下，当前我们可以通过 Runtime API 拿到，但是在我们的 OC 中是没法进⾏调度的。 
- 对于继承⾃ NSObject 类来说，如果我们想要动态的获取当前的属性和⽅法，必须在其声明前添加@objc 关键字，否则也是没有办法通过 Runtime API 获取的。 
- 纯swift类没有动态性，但在⽅法、属性前添加dynamic修饰，可获得动态性。 
- 继承⾃NSObject的swift类，其继承⾃⽗类的⽅法具有动态性，其它⾃定义⽅法、属性想要获得动态性，需要添加dynamic修饰。 
- 若⽅法的参数、属性类型为swift特有、⽆法映射到objective－c的类型(如Character、Tuple)，则此⽅法、属性⽆法添加dynamic修饰(编译器报错) 

## Mirror

所谓反射就是可以动态获取类型、成员信息，在运⾏时可以调⽤⽅法、属性等⾏为的特性。

在使⽤OC开发时很少强调其反射概念，因为OC的Runtime要⽐其他语⾔中的反射强⼤的多。

Swift 是⼀⻔类型安全的语⾔，不⽀持像 OC 那样直接操作，它的标准库仍然提供了反射机制来让我们访问成员信息。

Swift 的反射机制是基于⼀个叫 Mirror 的结构体来实现的。为具体的实例创建⼀个 Mirror 对象，然后就可以通过它查询这个实例 

### ⽤法介绍 

```swift
//⾸先通过构造⽅法构建⼀个Mirror实例，这⾥传⼊的参数是 Any，也就意味着当前可以是类，结 构体，枚举等
let mirror = Mirror(reflecting: LGTeacher.self)
//接下来遍历 children 属性，这是⼀个集合
for pro in mirror.children{
  //然后我们可以直接通过 label 输出当前的名称，value 输出当前反射的值
  print("\(pro.label):\(pro.value)")
}
```

### Mirror用法：json解析

```swift
func testJson(_ mirrorObj: Any) -> Any {
    let mirror = Mirror(reflecting: mirrorObj)
    guard !mirror.children.isEmpty else { return mirrorObj }
    var result: [String: Any] = [:]
    for child in mirror.children{
        if let key = child.label{
            result[key] = testJson(child.value)
        } else {
            print("No Keys")
        }
    }
    return result
}
```

如果想要所有的对象都具有这个功能，可以将上面方法声明为一个协议。

```swift
protocol JSONMap{//定义一个协议
    func jsonMap() -> Any
}
extension JSONMap{
    func jsonMap() -> Any {
        let mirror = Mirror(reflecting: self)
        guard !mirror.children.isEmpty else { return self }
        var result: [String: Any] = [:]
        for child in mirror.children{
            if let value = child.value as? JSONMap {
                if let key = child.label{
                    result[key] = value.jsonMap
                } else {
                    print("No Keys")
                }
            } else {
                print("Value not conform JSONMap Protocol")
            }
        }
        return result
    }
}

extension LGTeacherMirror: JSONMap{}
extension Int: JSONMap{}
extension String: JSONMap{}
var resutl = LGTeacherMirror().jsonMap()
```

## throws 和 rethrows 的有哪些用法？


`Swift` 中`throw`和`rethrows`关键字用于异常处理（Error handling)，都是用在函数中.

`throws`关键字首先用在函数申明中，**放在返回类型的前面**，明确一个函数或者方法可以抛出错误
这个时候我们是不是就可以用协议来做？什么意思那？

```swift
// MARK: Mirror用法：json解析
func testJson(_ mirrorObj: Any) -> Any {
    let mirror = Mirror(reflecting: mirrorObj)
    guard !mirror.children.isEmpty else { return mirrorObj }
    //字典
    var result: [String: Any] = [:]
    for child in mirror.children{
        if let key = child.label{
            result[key] = testJson(child.value)
        } else {
            print("No Keys")
        }
    }
    return result
}
```

```swift
// MARK: 想要所有的对象都具有这个功能，将方法声明为一个协议
protocol JSONMap{//定义一个协议
    func jsonMap() throws -> Any//jsonMap函数返回一个Any类型
}
```

testJson方法里面的功能是通用的，不需要每一个遵循JSONMap的都自己实现，可以给这个JSONMap协议一个默认的实现。

```swift
// MARK: 想要所有的对象都具有这个功能，将方法声明为一个协议
protocol JSONMap{//定义一个协议
    func jsonMap() throws -> Any//jsonMap函数返回一个Any类型
}
// extension 给协议添加一个默认的实现
extension JSONMap{
    func jsonMap() throws -> Any {
        let mirror = Mirror(reflecting: self)
        guard !mirror.children.isEmpty else { return self }
        var result: [String: Any] = [:]
        for child in mirror.children{
            if let value = child.value as? JSONMap {
                if let key = child.label{
                    result[key] = try? value.jsonMap//可能会出错
                } else {
                   return JSONMapError.emptyKey
                }
            } else {
                return JSONMapError.notConformProtocol
            }
        }
        return result
    }
}
```

完成之后，我们该如何使用它：

```swift
extension LGTeacherMirror: JSONMap{}
//因为value也需要递归，所以需要对当前常见类型和自定义类型遵循JSONMap协议，这样value才能嵌套解析。
extension Int: JSONMap{}
extension String: JSONMap{}

var tm = LGTeacherMirror()
//在调用的时候如果不处理这个错误，依然可以用try来继续抛出错误
var tt = try? tm.jsonMap()
// 捕获错误
do{
    try tm.jsonMap()
}catch{
//    error
}
```

## 错误处理

## Error

处理的过程中会有很多错误发生，通过`print`来代替了，不是很不专业。

这里我们来通过`Swift`中的错误处理来合理表达一个错误：

`Swift`提供`Error`协议来标识当前应用程序发生错误的情况，`Error`的定义如下：

```swift
// MARK: ERROR
enum JSONMapError: Error{//遵循ERROR协议
    case emptyKey
    case notConformProtocol
}
```

### try

使⽤ try 关键字还有两个要注意的点，⼀个还是 try! ,⼀个是 try? 

try? :返回的是⼀个可选类型，这⾥的结果就是两类，⼀类是成功，返回具体的字典值；⼀类就错误，但是具体哪⼀类错误我们不关系，统⼀返回了⼀个nil。这样我们当前的错误也不会向上传播~

try! 这⾥其实在写这句代码的时候你就有蜜汁⾃信，这⾏代码绝对不会发⽣错误，也就意味着这句代码就是 to be or not to be ，要么⽣，要么死。

### do catch

第⼆种⽅式就是捕获并处理当前的异常：这⾥我们使⽤ do...catch 


接下来我们把代码修改一下：

```swift
public protocol Error{}

enum JsonMapError: Error{
	case emptyKey
    case notConformProtocol
}

extension LGJsonMap{
	func jsonMap() throws -> Any{
    	let mirror = Mirror(reflecting: Self)
        
        guard !mirror.children.isEmpty else { return self }
        
        var result: [String: Any] = [:]
        
        for child in mirror.children{
        	if let value = child.value as? LGJsonMap{
            	if let key = child.label{
                	result[key] = value.jsonMap()
                }else{
                	throw JsonMapError.emptyKey
                }
            }else{
            	throw JsonMapError.notConformProtocol
            }
        }
        return result
}
```

1. 通过throw抛出程序中的错误。
2. throws代表当前函数有错误发生，使用时需要使用try或者do catch来处理错误。

于此同时，编译器会告诉我们当前的我们的 `function` 并没有声明成 `throws` ，所以修改代码之后就能得出这样的结果了:

这个时候会有一个问题，那就是当前的 `value` 也会默认调用 `jsonMap` 的方法，意味着也会有错误抛出，这里我们先根据编译器的提示，修改代码，使用之后接下来我们来使用一下我们当前编写完成的代码：

```swift
// MARK: 想要所有的对象都具有这个功能，将方法声明为一个协议
protocol JSONMap{//定义一个协议
    func jsonMap() throws -> Any//jsonMap函数返回一个Any类型，也需要定义throws关键字
}
// extension 给协议添加一个默认的实现
extension JSONMap{
    func jsonMap() throws -> Any {//这里也要定义throws关键字
        let mirror = Mirror(reflecting: self)
        guard !mirror.children.isEmpty else { return self }
        var result: [String: Any] = [:]
        for child in mirror.children{
            if let value = child.value as? JSONMap {
                if let key = child.label{
                    result[key] = try? value.jsonMap//可能会出错，通过try关键字来抛出错误
                } else {
                   return JSONMapError.emptyKey
                }
            } else {
                return JSONMapError.notConformProtocol
            }
        }
        return result
    }
}
```


可以使用 `rethrows` 关键字声明一个函数或方法，以表明仅当其中一个函数**参数**抛出错误时，该函数或方法才会抛出错误。抛出函数和方法必须至少具有一个抛出函数**参数**。


比如我们再使用高阶函数的时候 `map` 函数

```swift
public func map<T>(_ transform: (Element) throws -> T) rethrows -> [T]
```

如果调用 `map` 所传递的闭包表达是没有错误抛出的，则它本身不会抛出错误，而且我们再调用的时候不使用 `try` 

```swift
let a = [1, 2, 3]

func f1(n: Int) -> Int {
    return n * n
}

let a1 = a.map(f1)
```

但是如果当前调用 `map` 的时候传递的闭包表达式是有错误发生的，这个时候就必须使用 `try` 

```swift
let a = [1, 2, 3]
enum CustomError: Error {
    case illegalArgument
}

func f2(n: Int) throws -> Int {
    guard n >= 0 else {
        throw CustomError.illegalArgument
    }
    return n*n
}


do {
    let a2 = try a.map(f2)
} catch {
    // ...
}
```

可能有同学会问那如果再这个过程中把 `rethrow` 替换成 `throw` 会有什么区别那？

```swift
func test(f:(Int) throws -> ()) throws {
    try f(10)
}
func test2(f:(Int) throws -> ()) rethrows {
    try f(10)
}
```

-  这里如果我们调用 `test` 函数，就必须使用 `try` 关键字，这其实很明显增加了代码量，因为当前在调用明确没有错误发生时还要进行错误处理
-  相比较 `throws` 明确函数发生的错误， `rethrows` 更像是传递错误（错误需要处理与否取决于当前参数是否会发生错误）













