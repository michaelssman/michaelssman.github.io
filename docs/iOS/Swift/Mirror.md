## 元类型、AnyClass、Self （self） 

- AnyObject：代表任意类的实例（instance），类的类型，仅类遵守的协议。 

```swift
    class LGTeacherM{
        var age = 18
    }

    var t = LGTeacherM()
    var t1: AnyObject = t//AnyObject代表当前实例类型
    var t2:AnyObject = LGTeacherM.self//代表LGTeacherM类型
```

- Self：用在方法返回值，协议
- Any：代表任意类型，包括 funcation 类型或者 Optional 类型 
- AnyClass：代表任意实例的类型

类：LGTeacherM

元类：LGTeacherM.Type类型 通过LGTeacherM.self获取

# Swift Runtime 

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

# Mirror的基本⽤法

所谓反射就是可以动态获取类型、成员信息，在运⾏时可以调⽤⽅法、属性等⾏为的特性。在使⽤OC开发时很少强调其反射概念，因为OC的Runtime要⽐其他语⾔中的反射强⼤的多。但是 Swift 是⼀⻔类型安全的语⾔，不⽀持我们像 OC 那样直接操作，它的标准库仍然提供了反射机制来让我们访问成员信息，

Swift 的反射机制是基于⼀个叫 Mirror 的结构体来实现的。你为具体的实例创建⼀个 Mirror 对象，然后就可以通过它查询这个实例 

⽤法介绍 

```swift
    //⾸先通过构造⽅法构建⼀个Mirror实例，这⾥传⼊的参数是 Any，也就意味着当前可以是类，结 构体，枚举等
    let mirror = Mirror(reflecting: LGTeacher.self)
    //接下来遍历 children 属性，这是⼀个集合
    for pro in mirror.children{
        //然后我们可以直接通过 label 输出当前的名称，value 输出当前反射的值
        print("\(pro.label):\(pro.value)")
    }
```

**Mirror用法：json解析**

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

# 错误处理

## ERROR

这⾥我们来通过 Swift 中的错误处理来合理表达⼀个错误： 

Swift 提供 Error 协议来标识当前应⽤程序发⽣错误的情况， Error 的定义如下：

使⽤ try 关键字还有两个要注意的点，⼀个还是 try! ,⼀个是 try? 

try? :返回的是⼀个可选类型，这⾥的结果就是两类，⼀类是成功，返回具体的字典值；⼀类就错误，但是具体哪⼀类错误我们不关系，统⼀返回了⼀个nil。这样我们当前的错误也不会向上传播~

try! 这⾥其实在写这句代码的时候你就有蜜汁⾃信，这⾏代码绝对不会发⽣错误，也就意味着这句代码就是 to be or not to be ，要么⽣，要么死。

## do catch

第⼆种⽅式就是捕获并处理当前的异常：这⾥我们使⽤ do...catch 













