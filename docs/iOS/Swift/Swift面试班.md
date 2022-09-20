
### throws 和 rethrows 的有哪些用法？


`Swift` 中`throw`和`rethrows`关键字用于异常处理（Error handling)，都是用在函数中.

`throws`关键字首先用在函数申明中，放在返回类型的前面，明确一个函数或者方法可以抛出错误
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
- 相比较 `throws` 明确函数发生的错误， `rethrows` 更像是传递错误（错误需要处理与否取决于当前参数是否会发生错误）





