# defer

## defer执行时机

当前作用域结束后随之执行。

defer {} 里的代码会在当前*代码块*返回的时候执行，无论当前*代码块*是从哪个分支return 的，即使程序抛出错误，也会执行。 

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
>End of function
>Second defer
>First defer

## 使用场景有哪些 

### closeFile

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

### 在使用指针的时候

```swift
    let count = 2
    let pointer = UnsafeMutablePointer<Int>.allocate(capacity: count)
    pointer.initialize(repeating: 0, count: count)
    defer {//方法运行结束后调用，管理析构 释放
        pointer.deinitialize(count: count)
        pointer.deallocate()
    }
```

### 请求网络的时候

在进行网络请求的时候，可能有不同的分支进行回调函数的执行

```swift
func netRquest(completion: () -> Void) {
    defer {
        self.isLoading = false
        completion()
    }
    guard error == nil else { return }
}
```

## defer使用注意事项 

defer要在guard前面


比如下面这段代码

```swift
//test()//调用test，如果guard返回了，就不会执行defer，所以要避免这样写
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