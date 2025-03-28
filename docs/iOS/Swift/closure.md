# closure

## 函数是引用类型

函数本身也有自己的类型，它由形式参数类型，返回类型组成。

```swift
func addTwoInts(_ a: Int, _ b: Int) -> Int {
  return a + b
}

func addTwoInts(_ a: Double, _ b: Double) -> Double {//同名函数，参数和返回值不同
  return a + b
}

var a: (Double, Double) -> Double = addTwoInts//a变量名后面需要加函数类型
a(10, 20)
var b = a
b(20 ,30)
```

## 闭包是引用类型 

```swift
func makeIncrementer() -> () -> Int {//返回值是一个函数（返回值函数：没有参数、返回值是Int）
    var runningTotal = 10
    func incrementer() -> Int {
        runningTotal += 1 //把runningTotal捕获到堆区
        return runningTotal
    }
    return incrementer
}
//makeInc 引用类型
let makeInc = makeIncrementer()

print(makeInc())//11
print(makeInc())//12
print(makeInc())//13

//如果把上面调用案例修改一下：
//makeIncrementer()这里就类似我们创建了一个实例变量
print(makeIncrementer()())//11
print(makeIncrementer()())//11
print(makeIncrementer()())//11
```

## 闭包捕获值 

**捕获值相当于在堆区开辟内存空间，创建一个实例变量，捕获的值当作这个实例变量的属性。**


先来回顾一下 Block 捕获值的情形

```objectivec
- (void)testBlock{
    NSInteger i = 1;
    
    void(^block)(void) = ^{
        NSLog(@"block %ld:", i);
    };
    
    i += 1;
    
    NSLog(@"before block %ld:", i);
    block();
    NSLog(@"after block %ld:", i);
}
```

这里输出的结果是： `2, 1, 2` 。这是因为当前我们的应用程序执行到 `i += 1` 的时候，其实当前 `block` 已经捕获了当前 i 的瞬时变量的值，相当与在其内做了一次：

```objectivec
NSInteger tmp = i = 1
```

如果想要外部的修改能够影响当前 `block` 内部捕获的值，只需对当前的 `i` 添加 `__block` 修饰符

```objectivec
- (void)testBlock{
    __block NSInteger i = 1;
    
    void(^block)(void) = ^{
        NSLog(@"block %ld:", i);
    };
    
    i += 1;
    
    NSLog(@"before block %ld:", i);	//2
    block();												//2
    NSLog(@"after block %ld:", i);	//2
}
```


那么对于 `Swift` 中的闭包同样会捕获值，这里我们把 OC的例子修改成对应 Swift 的例子来看一下：

```swift
var i = 1
let closure = {
    print("closure \(i)")
}
i += 1
print("before closure \(i)")	//2
closure()											//2
print("after closure \(i)")		//2
```

这里例子输出的结果就和 Block 中的第一个例子不同了，因为当前 `Swift` 值的捕获是在**执行的时候再捕获**，当代码执行到 `closure()` ，对值进行捕获，此时`i`的值为几，捕获到的 `i` 就是几。


所以下面这个打印的是多少？

```swift
var i = 1
let closure = {
    print("closure \(i)")
}

i += 1
closure()//2

i += 1
closure()//3

i += 1
closure()//4
```

如果在 `Swift` 中想要捕获当前变量的瞬时值，该怎么操作那？答案是：捕获列表


我们来看下面这段代码

```swift
var i = 1
let closure = { [i] in
    print("closure \(i)")
}
i += 1
print("before closure \(i)")
closure()
print("after closure \(i)")
```

这个打印出来的结果就是: `2, 1, 2` 。

### 捕获列表 


默认情况下，闭包表达式从其周围的范围捕获常量和变量，并强引用这些值。可以使用捕获列表来显式控制如何在闭包中捕获值。

在参数列表之前，捕获列表被写为用逗号括起来的表达式列表，并用方括号括起来。

**如果使用捕获列表，则即使省略参数名称、参数类型和返回类型，也必须使用in关键字。**

```swift
var age = 0
var height = 0.0

let closure = { [age] in//捕获列表 从上下文中查找同名的变量或常量 age使用变量或常量字面量的值，闭包内部访问的是age的值。闭包内不能修改age 捕获列表默认是let。
    print(age)
    print(height)
}

age = 10
height = 1.85

closure() //输出结果为0, 1.85
```

创建闭包时，将初始化捕获列表中的条目。对于捕获列表中的每个条目，将常量初始化为在周围范围内具有相同名称的常量或变量的值。例如，在上面的代码中，捕获列表中包含age，但捕获列表中未包含height，这使它们具有不同的行为。

创建闭包时，内部作用域中的 age 会用外部作用域中的 age 的值进行初始化，但它们的值未以任何特殊方式连接。这意味着更改外部作用域中的age的值不会影响内部作用域中的age的值，也不会更改封闭内部的值，也不会影响封闭外部的值。相比之下，只有一个名为height的变量（外部作用域中的height），因此在闭包内部或外部进行的更改在两个地方均可见。


接下来我们在看下面的例子

```swift
struct LGTeacher {
    var age: Int
  	//test()返回值是一个函数（闭包）
    func test() -> () -> Int{
        return {
            self.age
        }
    }
}

var t = LGTeacher(age: 10)
let closure = t.test()
t.age = 20
print(closure())
```

结构体 LGTeacher  的实例⽅法 `test()`  返回⼀个捕获了 self 实例本身的闭包， `LGTeacher`  为值类型，因此 // 1 ⾏代码执⾏完成后，闭包 `closure`  复制了⼀份存储在变量 `t`  中  `LGTeacher`  实例，那么当存储在变量 t 的 LGTeacher 实例改名为 b 时，闭包 closure 所捕获的 Demo 实例不变，名字仍为 a ，因此输出结果为: 10 。


如果我们把上面的例子换一下：

```swift
class LGTeacher {
    var age: Int
    init(age: Int) {
        self.age = age
    }
    func test() -> () -> Int {
        return {
            self.age
        }
    }
}

var t = LGTeacher(age: 10)
let closure = t.test() 
t.age = 20
print(closure())
```

此时此刻，当前闭包捕获的是 self，他是一个引用类型，所以我们修改当前 `age` 变量的过程中， `closure()` 打印出来的也会改变成 `20` 。这里我们也可以还原当前的捕获捕获过程看一下闭包本质：

## 闭包本质

闭包是一个`函数`加上`捕获了上下文的常量或者变量`。

这里我们也可以通过 `IR` 的分析来看一下他的底层数据结构，最终我们能得出来这样一个结果

```swift
//实例对象内存地址
struct HeapObject {
    var type: UnsafeRawPointer//metadata
    var refcount1: UInt32
    var refcount2: UInt32
}

//IR
struct Box<T> {
    var refcounted: HeapObject
    var value: T								//捕获的值
}

//闭包本质
//ret { i8*, %swift.refcounted* } %5
//数据结构 ： 闭包的执行地址  + 捕获变量堆空间的地址
struct FunctionData<BoxType>{
    var ptr: UnsafeRawPointer 							//内嵌函数的地址
    var captureValue: UnsafePointer<BoxType>//捕获的值
}

struct VoidFunction {
    var f: ()->Int
}
//
//
var f = VoidFunction(f: closure)
//
let ptr = UnsafeMutablePointer<VoidFunction>.allocate(capacity: 1)
ptr.initialize(to: f)
//
let ctx = ptr.withMemoryRebound(to: FunctionData<Box<LGTeacher>>.self, capacity: 1){
    $0.pointee
}

print(ctx.ptr)
print(ctx.captureValue)
print("end")
```

所以我们在赋值的过程中其实是在传递地址，所以当前的闭包是引用类型。

接下来我们在来看一个例子：

```swift
func test() {
    var age = 10
    func closure() -> () -> Int {
        return {
           age += 1
           return age
        }
    }
    let c = closure()
    print(c())
    age = 20
    print(c())
    age = 30
    print(c())
}

test()//11，21，31
```

这里打印出来的分别是多少？是 10，11，12 还是 11，21，31？我们来运行一下，结果是第二个。这个不就和我们在上面得出来的结论是相反的嘛？我们上面说过闭包是引用类型，所以当前闭包在运行的时候捕获变量10，放到堆区，那么接下来都是针对堆区的值进行修改。
通过 `IR` 分析，可以看到的是当前在调用闭包的时候确实发生了内存的分配

## 自动闭包

一种用来把实际参数传递给函数表达式打包的闭包，不接受任何实际参数，当其调用时，返回内部表达式的值。 

好处：用普通表达式代替闭包的写法，语法糖的一种。


- 使用`@autoclosure`关键字能简化闭包调用形式
- 使用`@autoclosure`关键字能延迟闭包的执行

我们先来看下面这个例子

```swift
func debugOutPrint(_ condition: Bool , _ message: String){
    if condition {
        print("lg_debug:\(message)")
    }
}

debugOutPrint(true, "Application Error Occured")
```

上述代码会在当前 `conditon` 为 `true` 的时候，打印我们当前的错误信息，也就意味着 `false` 的时候当前条件不会执行。


如果我们当前的message字符串可能是在某个业务逻辑功能中获取的，比如下面这样写：

```swift
func debugOutPrint(_ condition: Bool , _ message: String){
    if condition {
        print("lg_debug:\(message)")
    }
}

func doSomething() -> String{
    //do something and get error message
    return "NetWork Error Occured"
}

debugOutPrint(true, doSomething())
```

这个时候我们会发现一个问题，那就是当前的 conditon，无论是 `true` 还是 `false` ,当前的方法`doSomething`都会执行。如果当前的 `doSomething` 是一个耗时的任务操作，那么这里就造成了资源浪费。


这个时候我们想到的是把当前的参数修改成一个闭包，

```swift
func debugOutPrint(_ condition: Bool , _ message: () -> String){
    if condition {
        print("lg_debug:\(message)")
    }
}

func doSomething() -> String{
    //do something and get error message
    return "NetWork Error Occured"
}

debugOutPrint(true, doSomething())
```

这样就能在当前条件满足的时候调用我们当前的 `doSomething` 的方法。同样的问题又随之而来了，那就是这里是一个闭包，如果我们这个时候就是传入一个 `String` 怎么办那？

```swift
//如果是debug模式，则打印错误信息
func debugOutPrint(_ condition: Bool , _ message: @autoclosure () -> String){
    if condition {
        print("lg_debug:\(message)")
    }
}

func doSomething() -> String{
  	//耗时操作
    //do something and get error message
    return "NetWork Error Occured"
}

//第二个参数 希望既能接受字符串 又能接受一个闭包表达式 所以需要@autoclosure修饰
debugOutPrint(true, doSomething())
debugOutPrint(true, "Application Error Occured")
```

上面我们使用 `@autoclosure` 将当前的表达式声明成了一个自动闭包，**不接收任何参数，返回值是当前内部表达式的值**。所以**实际上我们传入的 `String` 就是放入到一个闭包表达式中，在调用的时候返回。**

## 尾随闭包 

当闭包表达式作为函数的最后一个参数，如果当前的闭包表达式很长，我们可以通过尾随闭包的书写方式来提高代码的可读性。 

```swift
    //尾随闭包
    func test(_ a: Int, _ b: Int, _ c: Int, by: (_ item1: Int, _ item2: Int, _ item3: Int) -> Bool) -> Bool{
        return by(a, b, c)
    }
    //直接传闭包 可读性不好
    test(10, 20, 30, by: {(_ item1: Int, _ item2: Int, _ item3: Int) -> Bool in
        return (item1 + item2 < item3)
    })
    //尾随闭包
    test(10, 20, 30) { item1, item2, item3 in
        return (item1 + item2 < item3)
    }
```

其中闭包表达式是 Swift 语法。使用闭包表达式能更简洁的传达信息。当然闭包表达式的好处有很多： 

- 利用上下文推断参数和返回值类型 
- 单表达式可以隐式返回，既省略 return 关键字 
- 参数名称的简写（比如我们的 $0） 
- 尾随闭包表达式

```swift
    var array = [1, 2, 3]
    array.sort(by: {(item1 : Int, item2: Int) -> Bool in return item1 < item2 })
    array.sort(by: {(item1, item2) -> Bool in return item1 < item2 })//闭包省略参数类型
    array.sort(by: {(item1, item2) in return item1 < item2 })//省略闭包返回值类型：-> Bool
    array.sort{(item1, item2) in item1 < item2 }//单表达式可以隐式返回，既省略 return 关键字
    array.sort{ return $0 < $1 }//参数名称的简写（比如编译器起好名字 $0）
    array.sort{ $0 < $1 }
    array.sort(by: <)
```

## 逃逸闭包

当闭包作为一个实际参数传递给一个函数的时候，并且是在函数返回之后调用，我们就说这个闭包逃逸了。

当我们声明一个接受闭包作为形式参数的函数时，你可以在形式参数前写 @escaping 来明确闭包是允许逃逸的。 

闭包生命周期比原函数长。

- 作为函数的**参数**传递 
- 当前闭包在函数内部**异步**执行或者**被存储** 
- 函数结束，闭包被调用，生命周期结束 
- 不会产生循环引用，函数作用域内释放 
- 编译器更多性能优化 （retain， relsase） 
- 上下文的内存保存再栈上，不是堆上 

注意：**可选类型默认是逃逸闭包** 

```swift
class LGTeacher{
  var completionHandle: ((Int) -> Void)? //？可选，没有？就必须有一个初始化。闭包作为属性存储
        
  //@escaping表明闭包是逃逸的
  func makeIncrementer(_ amout: Int, handler: @escaping(Int) -> Void) {
    var runningTotal = 10
    runningTotal += amout
    self.completionHandle = handler
    
    //异步网络请求时
    DispatchQueue.global().asyncAfter(deadline: .now() + 0.1) {
      handler(runningTotal)
    }
  }
      
  func dosomething(){
    self.makeIncrementer(10) {
      print($0)
    }
  }
}
    
let t = LGTeacher()
t.dosomething()
t.completionHandle?(10)
```

#### Escaping closure captures non-escaping parameter 'callback'

在 Swift 中，当一个闭包作为参数传递给一个函数，并且在函数结束之后仍然可以被调用时，我们需要在闭包参数前面加上 `@escaping` 标识符来标记它是一个逃逸闭包。

这个错误的意思是说，你正在尝试在一个逃逸闭包中捕获一个非逃逸参数 `callback`，这是不允许的。

要解决这个问题，你可以将 `callback` 参数也标记为逃逸闭包，或者在闭包内部使用 `self.callback` 来避免捕获它。具体的解决方案取决于你的代码逻辑和需求。

```swift
func FaceIDAuthentication(callback: (_ success: Bool)->Void) {
    let context = LAContext()
    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: "请使用Face ID登录") { success, error in
        if success {
            // Face ID验证成功
            callback(true)
        } else {
            // Face ID验证失败
            callback(false)
        }
    }
}
```

### 非逃逸闭包

```swift
func noEscaping(_ f: () -> Void) {
    f()
}

var age = 10
noEscaping {
  age += 20
}
```

```swift
func testBiBao() {
    var age = 20
    
    let closure = {
        age += 10
    }
    
    closure();
    
    {age += 30}()//非逃逸闭包，没有实例空间的分配
    
    print(age)//打印60
}
```

## 闭包表达式 

闭包实现：

```swift
{ (param) -> (returnType) in//in之前定义 参数和返回值类型
	//函数体
}
```

OC 中的 Block 其实是一个匿名函数，所以这个表达式要具备 

- 作用域（也就是大括号） 
- 参数和返回值 
- 函数体（in）之后的代码 

## 1、闭包作为参数

### 闭包的定义

```swift
//定义闭包
var onValueChanged: ((String) -> Void)?

//闭包实现
targetVC.onValueChanged = { [weak self] text in
		self?.label.text = text
}

//调用
onValueChanged?(items)
```

```swift
//closure类型是：参数Int 返回值Int的闭包
//=后面是赋值，闭包定义赋值。
var closure: (Int) -> Int = { (age: Int) in
    return age
}
print("closure\(closure(23))")
```

闭包作为函数的参数 

```swift
    //闭包作为函数参数
    func test(param : () -> Int){
        print(param())
    }
    var age = 10
    test { () -> Int in
        age += 1
        return age
    }
```

## 2、闭包作为可选类型

可以把闭包声明一个可选类型： 

```swift
var closure1: ((Int) -> Int)?
closure1 = nil
```

## 3、闭包作为常量

通过 let 关键字将闭包声明为一个常量（一旦赋值之后就不能改变了）

```swift
    //闭包 常量
    let closure2: (Int) -> Int
    closure2 = {(age: Int) in
        return age
    }
//    closure2 = {(age: Int) in//不能再改变了
//        return age
//    }
```

## 内存

```swift
vc.serialNumber = { [self] serialNumberString in
	guard let strongSelf = self else { return }
	///里面使用strongSelf
}
```

