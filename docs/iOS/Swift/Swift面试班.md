### class 、struct的区别?
###### 
**区别:**


class 是类, 引用类型,可以继承;
struct 是结构体,值类型, 结构体不可以继承;
struct在小数据模型传递和拷贝时比 class 要更安全，在多线程和网络请求时保证数据不被修改;
```swift
let queue = DispatchQueue.global()

var teachers = ["Cat", "Hank", "Kody"]

queue.async {
    let count = animals.count
    for index in 0 ..< count {
        print("\(teachers[index])")
        Thread.sleep(forTimeInterval: 1)
    }
}

queue.async {
    Thread.sleep(forTimeInterval: 0.5)
    teachers.remove(at: 0)
}
```
原因就是我们在读取数组第二个元素时，第一个元素被移除掉了，所以会打印出来`pig`。然后当读取第三个元素时，数组內已无第三个元素，所以就会越界crash。那么是不是就意味着值类型并不是线程安全的呢？


```swift
//捕获列表
//var teachers = teachers
queue.async { [teachers] in
    let count = teachers.count
    for index in 0 ..< count {
        print("\(teachers[index])")
        Thread.sleep(forTimeInterval: 1)
    }
}

```
通过对这段代码的修改我们就可以得到想要的结果，并且不会crash。因为此时在新的线程中会`copy`出一份新的`teachers`。所以当线程会`copy`值类型内容时是线程安全的，其他情况会存在线程不安全的隐患，我们使用时应当注意。




### Swift中defer 使用场景有哪些 


定义：


`defer` {} 里的代码会在当前_代码块_返回的时候执行，无论当前_代码块_是从哪个分支 return 的，即使程序抛出错误，也会执行。


如果多个 defer 语句出现在同一作用域中，则它们出现的顺序与它们执行的顺序相反，也就是先出现的后执行。


这里我们看一个简单的例子：
```swift
func f() {
    defer { print("First defer") }
    defer { print("Second defer") }
    print("End of function")
}
f()
```
>结果输出
End of function
Second defer
First defer


defer能做什么？
```swift
func append(string: String, terminator: String = "\n", toFileAt url: URL) throws {
    // The data to be added to the file
    let data = (string + terminator).data(using: .utf8)!

    // If file doesn't exist, create it
    guard FileManager.default.fileExists(atPath: url.path) else {
        try data.write(to: url)
        return
    }
            

    // If file already exists, append to it
    let fileHandle = try FileHandle(forUpdating: url)
    fileHandle.seekToEndOfFile()
    fileHandle.write(data)
    fileHandle.closeFile()
}

let url = URL(fileURLWithPath: NSHomeDirectory() + "/Desktop/swift.txt")
try append(string: "iOS面试突击", toFileAt: url)
try append(string: "Swift", toFileAt: url)
```
这里有时候如果当前方法中多次出现 `closeFile` ,那么我们就可以使用 `defer` 
```swift
func append(string: String, terminator: String = "\n", toFileAt url: URL) throws {
    // The data to be added to the file
    let data = (string + terminator).data(using: .utf8)!
            
     defer{
     	fileHandle.closeFile()
     }

    // If file doesn't exist, create it
    guard FileManager.default.fileExists(atPath: url.path) else {
        try data.write(to: url)
        return
    }

    // If file already exists, append to it
    let fileHandle = try FileHandle(forUpdating: url)
    fileHandle.seekToEndOfFile()
    fileHandle.write(data)
    
}

let url = URL(fileURLWithPath: NSHomeDirectory() + "/Desktop/swift.txt")
try append(string: "iOS面试突击", toFileAt: url)
try append(string: "Swift", toFileAt: url)try append(string: "Line 1", toFileAt: url)
try append(string: "Line 2", toFileAt: url)
```
这样我们就不仅能够统一处理当前关闭文件的功能，还能防止因为忘记 `closeFile` 而造成的资源浪费。


比如我们在使用指针的时候
```swift
let count = 2
let pointer = UnsafeMutablePointer<Int>.allocate(capacity: count)
pointer.initialize(repeating: 0, count: count)

defer {
    pointer.deinitialize(count: count)
    pointer.deallocate()
}

```
比如我们在进行网络请求的时候，可能有不同的分支进行回调函数的执行
```swift
func netRquest(completion: () -> Void) {
  defer {
    self.isLoading = false
    completion()
  }
  guard error == nil else { return } 
}
```


**defer使用注意事项** 


比如下面这段代码
```swift
func test() {
  guard false else { return }
  defer {
    print("defer excute")
  }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619594226033-16e0c21a-cf01-40a9-91f1-70e085765b8a.png#height=180&id=KKlE0&margin=%5Bobject%20Object%5D&name=image.png&originHeight=360&originWidth=2930&originalType=binary&size=63377&status=done&style=none&width=1465)


同样的，有的 `Swift` 初学者在刚开始写 `Swift` 的时候可能会写这样的代码![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619594354142-6bbb8408-897f-449e-b64a-f162b14a0336.png#height=265&id=voagE&margin=%5Bobject%20Object%5D&name=image.png&originHeight=530&originWidth=2924&originalType=binary&size=91973&status=done&style=none&width=1462)


**一道关于defer的面试题** 
```swift
var a = 1
func add() -> Int {
    defer {
        a = a + 1
    }
    return a
}

var tmp = add()
print(tmp)
```
大家说上述我们打印出来的是多少？结果是 1
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619595840724-b0b50cd7-337f-405a-a263-0a02fce9b6a6.png#height=446&id=K4fhp&margin=%5Bobject%20Object%5D&name=image.png&originHeight=892&originWidth=2308&originalType=binary&size=223286&status=done&style=none&width=1154)
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619595924970-b88518ed-f418-41d5-97a7-a0ed0a27018c.png#height=306&id=WYbto&margin=%5Bobject%20Object%5D&name=image.png&originHeight=612&originWidth=2120&originalType=binary&size=110084&status=done&style=none&width=1060)
当然当前 a 的值肯定是改变了的，这里我们打印 `a` 的值就可以看到 `a` 是 2.


### throws 和 rethrows 的有哪些用法？


`Swift` 中`throw`和`rethrows`关键字用于异常处理（Error handling)，都是用在函数中.


`throws`关键字首先用在函数申明中，放在返回类型的前面，明确一个函数或者方法可以抛出错误
这个时候我们是不是就可以用协议来做？什么意思那？






![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575604182-cb866244-88ea-4cae-8635-49a357a2833c.jpeg#height=284&id=oH0zp&originHeight=284&originWidth=2370&originalType=binary&status=done&style=none&width=2370)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575608122-7d9503ec-1ed3-4546-ba93-04f8e7c1d352.jpeg#height=978&id=Bes6Z&originHeight=978&originWidth=2736&originalType=binary&status=done&style=none&width=2736)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575608104-eff7f952-5f7f-4e1b-9e49-d0defa05066c.jpeg#height=1272&id=Ia4iM&originHeight=1272&originWidth=1922&originalType=binary&status=done&style=none&width=1922)
完成之后，我们该如何使用它：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575600274-52845210-f0ae-4525-a20d-70af9ddd87af.jpeg#height=576&id=yH4Uo&originHeight=576&originWidth=2302&originalType=binary&status=done&style=none&width=2302)


大家可以看到这里面在处理的过程中会有很多错误发生，我在编写的时候都通过`print`来代替了，是不是很不专业啊。


这里我们来通过`Swift`中的错误处理来合理表达一个错误：
`Swift`提供`Error`协议来标识当前应用程序发生错误的情况，`Error`的定义如下：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575603874-d2b986f9-18d6-4568-b8fa-208d5fdadfe4.jpeg#height=130&id=yUb2O&originHeight=130&originWidth=882&originalType=binary&status=done&style=none&width=882)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575603993-ef9f87f5-e3e2-4310-b77e-05cc83897f73.jpeg#height=280&id=jH3Fh&originHeight=280&originWidth=800&originalType=binary&status=done&style=none&width=800)


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


于此同时，编译器会告诉我们当前的我们的 `function` 并没有声明成 `throws` ，所以修改代码之后就能得出这样的结果了:
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575608203-3b864450-24f0-4423-929c-58aa0f34f922.jpeg#height=1170&id=XkvJJ&originHeight=1170&originWidth=3056&originalType=binary&status=done&style=none&width=3056)


这个时候会有一个问题，那就是当前的 `value` 也会默认调用 `jsonMap` 的方法，意味着也会有错误抛出，这里我们先根据编译器的提示，修改代码，使用之后接下来我们来使用一下我们当前编写完成的代码：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575608269-c5c13686-b024-460a-a586-b74bd9038d2b.jpeg#height=1392&id=cMNGN&originHeight=1392&originWidth=2504&originalType=binary&status=done&style=none&width=2504)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575604184-128ca030-bc58-4aeb-9b3e-d38b4e6eb422.jpeg#height=256&id=SKwCW&originHeight=256&originWidth=2208&originalType=binary&status=done&style=none&width=2208)


可以使用 `rethrows` 关键字声明一个函数或方法，以表明仅当其中一个函数参数抛出错误时，该函数或方法才会抛出错误。抛出函数和方法必须至少具有一个抛出函数参数。


比如我们再使用高阶函数的时候 `map` 函数
```swift
public func map<T>(_ transform: (Element) throws -> T) rethrows -> [T]
```
如果调用 `map` 所传递的闭包表达是没有错误抛出的，则它本身不会抛出错误，而且我们再调用的时候不使用 `try` ：
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
- 相比较 `throws` 明确函数发生的错误， `rethrows` 更像是传递错误（错误需要处理与否取决于当前参数是否会发生错误）



**简述associatedtype的作用**


关联类型的作用：给协议中用到的类型定义一个占位名称


还记得我们之前在将 `mutating` 关键字的时候举的一个例子吗？
```swift
struct LGStack{
    private var items = [Int]()
    
    mutating func push(_ item: Int){
        items.append(item)
    }
    
    mutating func pop() -> Int?{
        if items.isEmpty { return nil }
        return items.removeLast()
    }
}
```
这里我们数组的类型是 `Int` ，如果我们想要使用别的类型那？那么我们的代码是不是就可以变换成这样？
```swift
protocol StackProtocol {
    associatedtype Item
}


struct LGStack: StackProtocol{
    
    typealias Item = Int

    private var items = [Item]()
    
    mutating func push(_ item: Item){
        items.append(item)
    }
    
    mutating func pop() -> Item?{
        if items.isEmpty { return nil }
        return items.removeLast()
    }
}
```


### 简述lazy的作用


- 延迟存储属性的初始值在其第一次使用时才进行计算。
- 用关键字`lazy`来标识一个延迟存储属性。



这两句话怎么去理解？
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919529534-66eda18c-36d4-43d1-81c1-1e7ea21fb9d9.jpeg#height=386&id=ta994&originHeight=386&originWidth=1160&originalType=binary&status=done&style=none&width=1160)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919534482-e7735d42-ae5a-4306-a8c4-4dd59367ee5e.jpeg#height=388&id=wpl40&originHeight=388&originWidth=1840&originalType=binary&status=done&style=none&width=1840)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919530173-7963ab58-0a7b-4467-af4b-24d6c554f584.jpeg#height=862&id=eOWWv&originHeight=862&originWidth=1588&originalType=binary&status=done&style=none&width=1588)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919535133-ebdec3b3-e1b7-477a-b824-cdf9611f46a6.jpeg#height=842&id=cKbQR&originHeight=842&originWidth=1536&originalType=binary&status=done&style=none&width=1536)


接下来我们把断点放一下，来看一下当前内存发生了什么变化？
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919535153-ad37d30e-9ab0-4dbc-9d30-f92a031934e4.jpeg#height=1258&id=wnDYy&originHeight=1258&originWidth=1724&originalType=binary&status=done&style=none&width=1724)
这里我们来打印一下使用`lazy` 和不使用`lazy`的时候，当前对象的大小有什么变化？
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919530284-d6cc2f21-cd8c-4dec-9671-0ee17603eeb3.jpeg#height=1170&id=IFhGj&originHeight=1170&originWidth=1762&originalType=binary&status=done&style=none&width=1762)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919537846-eaf16533-a066-4bee-8d5e-086da116792c.jpeg#height=1254&id=MjAhS&originHeight=1254&originWidth=1806&originalType=binary&status=done&style=none&width=1806)


为什么这里会有 8 字节的差距？我们通过`SIL`来查看一下：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919534372-5ca28e0d-dc25-431d-be71-c63a38cebe40.jpeg#height=402&id=oJqN8&originHeight=402&originWidth=2044&originalType=binary&status=done&style=none&width=2044)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919530099-13afac29-799b-4994-b8fa-1b98a6957e6f.jpeg#height=458&id=X24n6&originHeight=458&originWidth=2100&originalType=binary&status=done&style=none&width=2100)


当我们第一访问他的时候发生了什么事情？
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919534438-1b58bae8-50db-4599-baa3-c94e7d767dc9.jpeg#height=786&id=EVXNy&originHeight=786&originWidth=1190&originalType=binary&status=done&style=none&width=1190)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919530484-87628847-cb07-47a8-a7b5-9fe89addad14.jpeg#height=896&id=VkeBh&originHeight=896&originWidth=2046&originalType=binary&status=done&style=none&width=2046)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919538206-f7dd6e4f-e811-4be0-ad1b-bb31d156598a.jpeg#height=1402&id=TgC9K&originHeight=1402&originWidth=2116&originalType=binary&status=done&style=none&width=2116)


在回过头来看我们刚才那两句话，这个时候大家理解清楚了没？同样的，这里其实底层是一个`Optional`，我们可以通过`MemoryLayout`来测量一下需要多少大小？（8字节对齐之后是不是就是32）
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919537673-e30e958a-5736-46ac-93e4-d05928f998d5.jpeg#height=642&id=aMLqW&originHeight=642&originWidth=1668&originalType=binary&status=done&style=none&width=1668)


其次我们在来理解一句话：（体现在PPT上）


如果被标记为 lazy 修饰符的属性同时被多个线程访问并且属性还没有被初始化，则无法保证属性只初始化一次。


这个该怎么理解，其实很简单，比如多线程我们是不是没办法确定当前代码的执行顺序啊！假设有两个线程同时访问我们当前的`age`变量，这个时候都是第一次访问！
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919540343-15123ffd-68d8-4d2d-b65f-75db9b97d935.jpeg#height=1298&id=uSC5M&originHeight=1298&originWidth=2200&originalType=binary&status=done&style=none&width=2200)


当然这里还有一种写法
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919529568-4b1f1db2-2807-4999-9210-dcdfa2f086cf.jpeg#height=326&id=KKHBy&originHeight=326&originWidth=1218&originalType=binary&status=done&style=none&width=1218)
这个和我们之前直接初始化有什么区别吗？这个能保证我们的变量只初始化一次吗？
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606919538160-1cca9aaa-f050-42f6-9d39-98a94228fe30.jpeg#height=1124&id=nCOAP&originHeight=1124&originWidth=2174&originalType=binary&status=done&style=none&width=2174)


### Swift闭包面试详解


闭包是一个捕获了上下文的常量或者是变量的函数


**闭包捕获值** 


在讲闭包捕获值的时候，我们先来回顾一下 Block 捕获值的情形
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
 那么如果我们想要外部的修改能够影响当前 `block` 内部捕获的值，我们只需要对当前的 `i` 添加 `__block` 修饰符
```objectivec
- (void)testBlock{
    __block NSInteger i = 1;
    
    void(^block)(void) = ^{
        NSLog(@"block %ld:", i);
    };
    
    i += 1;
    
    NSLog(@"before block %ld:", i);
    block();
    NSLog(@"after block %ld:", i);
}
```
这里的结果输出的就是： `2, 2, 2` 


那么对于 `Swift` 中的闭包同样会捕获值，这里我们把 OC的例子修改成对应 Swift 的例子来看一下：
```swift
var i = 1
let closure = {
    print("closure \(i)")
}
i += 1
print("before closure \(i)")
closure()
print("after closure \(i)")
```
这里例子输出的结果就和 Block 中的第一个例子不同了，因为当前 `Swift` 值的捕获是在执行的时候再捕获，当代码执行到 `closure()` ，对值进行捕获，I此时的值为几，所以捕获到的 `I` 就是几。


所以下面这个打印的是多少？
```swift
var i = 1
let closure = {
    print("closure \(i)")
}

i += 1

closure()

i += 1

closure()

i += 1

closure()
```
这个时候有人可能会问如果在 `Swift` 中仅仅想要捕获当前变量的瞬时值，该怎么操作那？答案是：捕获列表


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


**什么是捕获列表** 


默认情况下，闭包表达式从其周围的范围捕获常量和变量，并强引用这些值。您可以使用捕获列表来显式控制如何在闭包中捕获值。


在参数列表之前，捕获列表被写为用逗号括起来的表达式列表，并用方括号括起来。如果使用捕获列表，则即使省略参数名称，参数类型和返回类型，也必须使用in关键字。
```swift
var age = 0

var height = 0.0

let closure = { [age] in
    print(age)
    print(height)
}

age = 10

height = 1.85

closure() //输出结果为0, 1.85
```
创建闭包时，将初始化捕获列表中的条目。对于捕获列表中的每个条目，将常量初始化为在周围范围内具有相同名称的常量或变量的值。例如，在下面的代码中，捕获列表中包含age，但捕获列表中未包含height，这使它们具有不同的行为。
![image.png](https://cdn.nlark.com/yuque/0/2020/png/2977480/1607526941323-431b42fc-e399-47a1-9b9d-0c61c37475a8.png#height=430&id=pMKiT&margin=%5Bobject%20Object%5D&name=image.png&originHeight=860&originWidth=1380&originalType=binary&size=97996&status=done&style=none&width=690)
创建闭包时，内部作用域中的 age 会用外部作用域中的 age 的值进行初始化，但它们的值未以任何特殊方式连接。这意味着更改外部作用域中的a的值不会影响内部作用域中的age的值，也不会更改封闭内部的值，也不会影响封闭外部的值。相比之下，只有一个名为height的变量-外部作用域中的height -因此，在闭包内部或外部进行的更改在两个地方均可见。


接下来我们在看下面的例子
```swift
struct LGTeacher {
    var age: Int
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
此时此刻，当前闭包捕获的是 self，他是一个引用类型，所以我们修改当前 `age` 变量的过程中， `closure()` 打印出来的也会改变成 `20` 。这里我们也可以还原当前的捕获捕获过程看一下：
```swift
struct HeapObject {
    var type: UnsafeRawPointer
    var refcount1: UInt32
    var refcount2: UInt32
}

//IR
struct Box<T> {
    var refcounted: HeapObject
    var value: T
}

//ret { i8*, %swift.refcounted* } %5
struct FunctionData<BoxType>{
    var ptr: UnsafeRawPointer //内嵌函数的地址
    var captureValue: UnsafePointer<BoxType>
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
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619422102790-1ad1903c-c6b9-48ab-a63d-77521a9c4ff0.png#height=218&id=CAEjt&margin=%5Bobject%20Object%5D&name=image.png&originHeight=436&originWidth=1866&originalType=binary&size=77275&status=done&style=none&width=933)
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

test()
```
这里打印出来的分别是多少？是 10，11，12 还是 11，21，31？我们来运行一下，结果是第二个。这个不就和我们在上面得出来的结论是相反的嘛？我们上面说过闭包是引用类型，所以当前闭包在运行的时候捕获变量10，放到堆区，那么接下来都是针对堆区的值进行修改。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619441514235-27e59cd2-c2fb-4d7a-ad59-3ab7395f0bb6.png#height=737&id=tOPtE&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1474&originWidth=2746&originalType=binary&size=331691&status=done&style=none&width=1373)
我们通过 `IR` 来分析一下，可以看到的是当前在调用闭包的时候确实发生了内存的分配
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1619441639188-52c546e3-f1ff-426a-a678-dabcd56a96f2.png#height=432&id=jy8Go&margin=%5Bobject%20Object%5D&name=image.png&originHeight=864&originWidth=3168&originalType=binary&size=312379&status=done&style=none&width=1584)
**闭包是引用类型**


我们先通过一个例子来观察一下
```swift
func makeIncrementer() -> () -> Int {
    var runningTotal = 10
    func incrementer() -> Int {
        runningTotal += 1
        return runningTotal
    }
    return incrementer
}

let makeInc = makeIncrementer()

print(makeInc())
print(makeInc())
print(makeInc())

```
这里打印输出的分别是多少？10，11， 12，那么如果我们把当前案例修改一下：
```swift
func makeIncrementer() -> () -> Int {
    var runningTotal = 10
    func incrementer() -> Int {
        runningTotal += 1
        return runningTotal
    }
    return incrementer
}

print(makeIncrementer()())
print(makeIncrementer()())
print(makeIncrementer()())
```
当前的输出结果就编程了：11， 11， 11；这里就类似我们创建了一个实例变量
```swift
class LGTeacher{
	var age = 10
}

let t = LGTeacher()

print(t.age += 1)
print(t.age += 1)
print(t.age += 1)

//或者
print(LGTeacher().age += 1)
print(LGTeacher().age += 1)
print(LGTeacher().age += 1)
```
这里我们也可以通过 `IR` 的分析来看一下他的底层数据结果，最终我们能得出来这样一个结果
```swift
struct HeapObject {
    var type: UnsafeRawPointer
    var refcount1: UInt32
    var refcount2: UInt32
}

//IR
struct Box<T> {
    var refcounted: HeapObject
    var value: T
}

//ret { i8*, %swift.refcounted* } %5
struct FunctionData<BoxType>{
    var ptr: UnsafeRawPointer //内嵌函数的地址
    var captureValue: UnsafePointer<BoxType>
}

struct VoidFunction {
    var f: ()->Int
}
```
所以我们在赋值的过程中其实是在传递地址，所以当前的闭包是引用类型。


### 自动闭包


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


如果我们当前的字符串可能是在某个业务逻辑功能中获取的，比如下面这样写：
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
这个时候我们会发现一个问题，那就是当前的 conditon，无论是 `true` 还是 `false` ,当前的方法都会执行。如果当前的 `doSomething` 是一个耗时的任务操作，那么这里是不是就造成了一定的资源浪费啊。


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
这样的话是不是就能够正常在当前条件满足的时候调用我们当前的 `doSomething` 的方法啊。同样的问题又随之而来了，那就是这里是一个闭包，如果我们这个时候就是传入一个 `String` 怎么办那？
```swift
func debugOutPrint(_ condition: Bool , _ message: @autoclosure () -> String){
    if condition {
        print("lg_debug:\(message)")
    }
}

func doSomething() -> String{
    //do something and get error message
    return "NetWork Error Occured"
}

debugOutPrint(true, doSomething())

debugOutPrint(true, "Application Error Occured")
```
上面我们使用 `@autoclosure` 将当前的表达式声明成了一个自动闭包，不接收任何参数，返回值是当前内部表达式的值。所以实际上我们传入的 `String` 就是放入到一个闭包表达式中，在调用的时候返回。




### 高阶函数


高阶函数的本质也是函数，有两个特点


- 接受函数或者是闭包作为参数
- 返回值是一个函数或者是闭包



这些函数我们常常用来作用于`Array`,`Set`,`Dictionary`中的每一个元素


#### Map函数


`Map`函数作用于`Collection`中的每一个元素，然后返回一个新的`Collection`。


假设我们有一个`String`类型的`Array`，现在我们对集合当中的每一个元素都是小写的。一般我们的代码是不是会这样写。
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575406669-1f93a6f6-5174-4fbf-865e-bdce72ca595b.jpeg#height=560&id=eiDlG&originHeight=560&originWidth=1558&originalType=binary&status=done&style=none&width=1558)


但是现在有了高阶函数，我们可以这样写：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575399022-c23d41e7-93df-45af-9579-4a2f70395170.jpeg#height=140&id=GJzME&originHeight=140&originWidth=1634&originalType=binary&status=done&style=none&width=1634)


我们先来看一下`Map`的函数原型，这里注意`Map`函数其实是`Sequence`协议的拓展，所以这里我们找到`Sequence`的文件。
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575407069-80b73b0c-62c9-42d4-ad5f-56e05349f1f8.jpeg#height=492&id=Gcrza&originHeight=492&originWidth=2332&originalType=binary&status=done&style=none&width=2332)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575399212-12aa595a-726f-4445-a9aa-a090dceca53c.jpeg#height=194&id=XvaPC&originHeight=194&originWidth=1376&originalType=binary&status=done&style=none&width=1376)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575448387-77e165f7-1f20-45b6-a00d-2df0119922a2.jpeg#height=484&id=Upybp&originHeight=484&originWidth=1840&originalType=binary&status=done&style=none&width=1840)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575400127-e5c60a7f-a225-4e43-b980-e58cdf839934.jpeg#height=670&id=TZrad&originHeight=670&originWidth=2502&originalType=binary&status=done&style=none&width=2502)


这样一对比是不是相比较我们之前的方式和方法，看起来就非常的简洁，接下来我们看一下源码到底是如何作用于每一个元素的：
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610003790001-7f40a7e0-cd55-425d-aa35-649e4c337cb9.png#height=669&id=pUTJe&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1338&originWidth=2114&originalType=binary&size=245231&status=done&style=none&width=1057)


#### flatMap函数


我们先来看一下 `flatMap` 的定义 
```swift
public func flatMap<SegmentOfResult : Sequence>(_ transform: (Element) throws -> SegmentOfResult) rethrows -> [SegmentOfResult.Element]
```


`flatMap` 中的闭包的参数同样是 `Sequence` 中的元素类型，但其返回类型为 `SegmentOfResult`。在函数体的范型定义中，`SegmentOfResult` 的类型其实就是是 `Sequence`。 而`flatMap` 函数返回的类型是 `SegmentOfResult.Element` 的数组。从函数的返回值来看，与 `map` 的区别在于 `flatMap` 会将 `Sequence` 中的元素进行”压平”，返回的类型会是 `Sequence` 中元素类型的数组，而 `map` 返回的这是闭包返回类型`T`的数组。


我们来看一下源码：
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610023332164-16deb6bd-0fc9-402d-a324-445324783f09.png#height=709&id=AdaJQ&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1418&originWidth=2252&originalType=binary&size=344228&status=done&style=none&width=1126)
相比较我们的 map 来说， flatMap 最主要的两个作用一个是 压平，一个是过滤空值。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610023551143-204c3219-9299-4cc5-a63b-89eac6d84909.png#height=308&id=MSRtD&margin=%5Bobject%20Object%5D&name=image.png&originHeight=616&originWidth=1646&originalType=binary&size=74046&status=done&style=none&width=823)
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610023634735-9fd70d36-b59a-4ffb-a474-01a6d2db04a6.png#height=298&id=blsqs&margin=%5Bobject%20Object%5D&name=image.png&originHeight=596&originWidth=1226&originalType=binary&size=86200&status=done&style=none&width=613)
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610023727167-1fb69797-3f95-425b-86ed-b8414277fe96.png#height=348&id=IiMOK&margin=%5Bobject%20Object%5D&name=image.png&originHeight=696&originWidth=2974&originalType=binary&size=143167&status=done&style=none&width=1487)
但是这里有一个提示，如果说我们当前对有可选值的集合进行操作的时候，可以选择 compactMap ，这个我们后面在说，看完了 Sequence 中的 map 和 flatMap 的区别之后


这里我们可以通过下面的这种方式来区别一下 `map`  & `flatMap`
```swift
let numbers = [1, 2, 3, 4]
let mapped = numbers.map { Array(repeating: $0, count: $0) }
let flatMapped = numbers.flatMap { Array(repeating: $0, count: $0) }
```
我们这里再看一个列子：
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610008129437-0d5245ac-3298-4b67-a8ef-476487ce3a15.png#height=174&id=DQYwH&margin=%5Bobject%20Object%5D&name=image.png&originHeight=348&originWidth=1012&originalType=binary&size=56505&status=done&style=none&width=506)


可以看到这里我们使用 `map` 做集合操作之后，得到的 `reslut` 是一个可选的可选，那么这里其实我们在使用 `result` 的过程中考虑的情况就比较多


通过 `flatMap` 我们就可以得到一个可选值而不是可选的可选
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610022342726-a94a453c-545d-47d9-bbcf-2d11f9cbda0f.png#height=172&id=tqeQU&margin=%5Bobject%20Object%5D&name=image.png&originHeight=344&originWidth=1404&originalType=binary&size=62661&status=done&style=none&width=702)
我们来看一下源码
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610022727731-7f3ec242-1aa2-4b31-a94b-1cc1fc0f64e0.png#height=350&id=hdEZa&margin=%5Bobject%20Object%5D&name=image.png&originHeight=700&originWidth=1368&originalType=binary&size=86116&status=done&style=none&width=684)
`flatMap`  对于输入一个可选值时应用闭包返回一个可选值，之后这个结果会被压平，也就是返回一个解包后的结果。本质上，相比 `map`,`flatMap`也就是在可选值层做了一个解包。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610022796022-429d2b54-f4c2-43c9-9fbc-86f9b3fde4ea.png#height=356&id=Vqa3x&margin=%5Bobject%20Object%5D&name=image.png&originHeight=712&originWidth=1258&originalType=binary&size=85559&status=done&style=none&width=629)


使用 `flatMap` 就可以在链式调用时，不用做额外的解包工作，什么意思那？我们先来看我们使用 `map` 来进行链式调用
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610023041279-4ba0476f-f4be-4b0e-9f77-2a3fea2d107a.png#height=256&id=sM56C&margin=%5Bobject%20Object%5D&name=image.png&originHeight=512&originWidth=1556&originalType=binary&size=89524&status=done&style=none&width=778)
这里我们得到的 `result`是一个可选的可选，而且在调用的过程中如果有必要我们依然需要进行解包的操作
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610023200316-03e2297e-9a5f-44d3-9daf-11349ed6e5bc.png#height=125&id=sRUzj&margin=%5Bobject%20Object%5D&name=image.png&originHeight=250&originWidth=1486&originalType=binary&size=39226&status=done&style=none&width=743)


#### CompactMap函数
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610034372050-a98f3952-22b1-4851-abed-61ec2184c669.png#height=793&id=JhwIw&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1586&originWidth=2588&originalType=binary&size=343281&status=done&style=none&width=1294)


什么时候使用 compactMap


当转换闭包返回可选值并且你期望得到的结果为非可选值的序列时，使用 `compactMap`。
```swift
let arr = [[1, 2, 3], [4, 5]]

let result = arr.map { $0 }
// [[1, 2, 3], [4, 5]]

let result = arr.flatMap { $0 }
// [1, 2, 3, 4, 5]


let arr = [1, 2, 3, nil, nil, 4, 5]

let result = arr.compactMap { $0 }
// [1, 2, 3, 4, 5]
```


什么时候使用 flatMap


当对于序列中元素，转换闭包返回的是序列或者集合时，而你期望得到的结果是一维数组时，使用 `flatMap`。
```swift
let scoresByName = ["Henk": [0, 5, 8], "John": [2, 5, 8]]

let mapped = scoresByName.map { $0.value }
// [[0, 5, 8], [2, 5, 8]] - An array of arrays
print(mapped)

let flatMapped = scoresByName.flatMap { $0.value }
// [0, 5, 8, 2, 5, 8] - flattened to only one array
```


#### filter函数


`filter`就是`Sequence`中默认提供的方法，允许调用者传入一个闭包来过滤集合中的元素：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575433409-b8bd2189-081b-4c96-bc21-b531cc1451fe.jpeg#height=344&id=CAOHx&originHeight=344&originWidth=1996&originalType=binary&status=done&style=none&width=1996)
![](https://cdn.nlark.com/yuque/0/2020/png/2977480/1606575406761-0cb74f05-3ca3-4cd6-ae62-d6cce7dd561f.png#height=662&id=D0cTj&originHeight=662&originWidth=1080&originalType=binary&status=done&style=none&width=1080)


#### for...Each


对于集合类型的元素，有时候不必要每次都通过`for`循环来去做遍历，`Sequence`同样提供了高阶函数来公供我们使用：
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575399295-07fe8aec-e371-4980-9816-6de23003dfc9.jpeg#height=262&id=E5puS&originHeight=262&originWidth=1970&originalType=binary&status=done&style=none&width=1970)


大家猜一下，他的实现是啥？


那这个时候可![](https://cdn.nlark.com/yuque/0/2020/png/2977480/1606575399117-495d146b-349d-4b49-a4f7-d7fd693cdb43.png#height=287&id=cEYej&originHeight=287&originWidth=1145&originalType=binary&status=done&style=none&width=1145)能有人会问了，如果我想记录一下当前的元素`index`该如何去做，难道要重新设计一个变量，然后自己做累加吗？


No，我觉得`Swift`魅力也就在于此，函数式编程
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575433425-7d19246a-a0ad-426d-add1-a5a5260a7d96.jpeg#height=324&id=Q1HjZ&originHeight=324&originWidth=1802&originalType=binary&status=done&style=none&width=1802)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575448381-92341d87-e176-436e-9ccb-28feb0cf23ce.jpeg#height=238&id=hgiOY&originHeight=238&originWidth=2502&originalType=binary&status=done&style=none&width=2502)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575407076-7ae94fa9-31f1-4d75-a020-a2746bed0777.jpeg#height=654&id=xmun8&originHeight=654&originWidth=1378&originalType=binary&status=done&style=none&width=1378)
![](https://cdn.nlark.com/yuque/0/2020/jpeg/2977480/1606575448336-8250c633-f2c3-47e3-913d-285a8fc58be2.jpeg#height=654&id=rj0mO&originHeight=654&originWidth=2432&originalType=binary&status=done&style=none&width=2432)
![](https://cdn.nlark.com/yuque/0/2020/png/2977480/1606575406684-392e48ca-f0bd-47e9-9538-2bd6a65b2a06.png#height=527&id=uikQn&originHeight=527&originWidth=1235&originalType=binary&status=done&style=none&width=1235)
![](https://cdn.nlark.com/yuque/0/2020/png/2977480/1606575406691-4f248c54-ca65-4fdd-8780-e563bffa5514.png#height=407&id=AeE2z&originHeight=407&originWidth=1174&originalType=binary&status=done&style=none&width=1174)
![](https://cdn.nlark.com/yuque/0/2020/png/2977480/1606575433364-68e3b864-7eee-4735-a39c-bf964d246dbb.png#height=440&id=wbn8Y&originHeight=440&originWidth=1113&originalType=binary&status=done&style=none&width=1113)


#### Reduce 函数


我们可以使用 reduce 函数合并集合中所有元素创建一个新值。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610029551497-7c3a565c-b813-414b-b085-cfc1b1b6bcbf.png#height=203&id=LNsWa&margin=%5Bobject%20Object%5D&name=image.png&originHeight=406&originWidth=1378&originalType=binary&size=42666&status=done&style=none&width=689)
![image.png](https://cdn.nlark.com/yuque/0/2021/png/2977480/1610030946200-9cb713d5-28b3-4c74-a960-491103239f76.png#height=430&id=d0fqz&margin=%5Bobject%20Object%5D&name=image.png&originHeight=860&originWidth=2080&originalType=binary&size=182147&status=done&style=none&width=1040)
为了更好的理解当前 `reduce` 的工作原理，我们来试着实现一下 `map` , `flatMap` , `filter` 函数
```swift
func customMap(collection: [Int], transform: (Int) -> Int) -> [Int] {
    return collection.reduce([Int]()){
        var arr: [Int] = $0
        arr.append(transform($1))
       return arr
    }
}

let result = customMap(collection: [1, 2, 3, 4, 5]) {
    $0 * 2
}

print(result)
```
当然这里因为参数是不可变的，所以我们总是需要转换一下，我们也可以借助下面这个函数来实现这样的方式
```swift
func customMap(collection: [Int], transform: (Int) -> Int) -> [Int] {
    return collection.reduce(into: [Int]()){
        $0.append(transform($1))
    }
}

let result = customMap(collection: [1, 2, 3, 4, 5]) {
    $0 * 2
}

print(result)
```
那么自然而然我们也就可以通过这样的方式来实现 map 提供的功能
```swift
var arr = [1, 2, 3, 4, 5]

let result = arr.reduce([Int]()){
    var array = Array($0)
    array.append($1 * 2)
    return array
}

print(result)
```
所以下面的写法也是等价的
```swift
var arr = [1, 2, 3, 4, 5]

let resutl = arr.reduce(into: [Int]()) { (array, element) in
    array.append(element * 2)
}

print(resutl)
```
如何找出一个数组中的最大值
```swift
let result = [1, 2, 3, 4, 5].reduce(0) {
   return  $0 < $1 ? $1 : $0
}

print(result)
```


又或者我们如何通过 `reduce` 函数逆序
```swift
let result = [1, 2, 3, 4, 5].reduce([Int]()){
    return [$1] + $0
}

print(result)
```







