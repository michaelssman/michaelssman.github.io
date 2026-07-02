# swift错误处理

## Error错误表示

```swift
// MARK: - 自定义错误类型
enum SpeechError: Error, LocalizedError {
    case permissionDenied
    case languageNotSupported(String)
    case recognizerUnavailable
    case audioEngineBusy
    case requestCreationFailed
    case recognitionFailed(String)
    
    var errorDescription: String? {
        switch self {
        case .permissionDenied:
            return "未获得麦克风或语音识别权限"
        case .languageNotSupported(let language):
            return "当前设备暂不支持\(language)识别"
        case .recognizerUnavailable:
            return "当前设备暂时无法使用语音识别"
        case .audioEngineBusy:
            return "音频引擎正忙"
        case .requestCreationFailed:
            return "创建识别请求失败"
        case .recognitionFailed(let msg):
            return "识别失败：\(msg)"
        }
    }
}
```

它是一个 Swift 枚举，并且遵循两个协议：

- `Error`：表示这个类型可以作为错误被 `throw` 抛出。
- `LocalizedError`：表示这个错误可以提供本地化的错误描述。

```swift
case languageNotSupported(String)
```

当前设备不支持某种语言识别。这里带了一个 `String` 关联值，用来保存具体语言，例如 `"zh-CN"`。

```swift
case recognitionFailed(String)
```

识别过程失败，并携带具体失败信息。

下面这个属性来自 `LocalizedError`：

```swift
var errorDescription: String?
```

它根据不同错误返回对应的中文提示：

```swift
switch self
```

根据当前错误类型匹配不同分支。例如：

```swift
case .languageNotSupported(let language):
    return "当前设备暂不支持\(language)识别"
```

如果错误是：

```swift
SpeechError.languageNotSupported("英文")
```

那么错误描述就是：

```
当前设备暂不支持英文识别
```

实际使用时可以这样：

```swift
throw SpeechError.permissionDenied
```

或者：

```swift
let error = SpeechError.recognitionFailed("网络异常")
print(error.localizedDescription)
```

因为它遵循了 `LocalizedError`，所以 `localizedDescription` 会使用 `errorDescription` 返回的内容。

## 抛出错误

函数、方法和初始化器都可以抛出错误。需要在参数列表后面，返回值前面加 throws 关键字。

```swift
func canThrowErrors() throws -> String
```

```swift
struct Item {
    var price: Int
    var count: Int
}
class VendingMachine {
    var inventory = [
        "Candy Bar": Item(price: 12, count: 7),
        "Chips": Item(price: 10, count: 4),
        "Pretzels": Item(price: 7, count: 11)
    ]
    var coinsDeposited = 0
    func vend(itemNamed name: String) throws {
        guard let item = inventory[name] else {
            throw VendingMachineError.invalidSelection
        }
        guard item.count > 0 else {
            throw VendingMachineError.outOfStock
        }
        guard item.price <= coinsDeposited else {
            throw VendingMachineError.insufficientFunds(coinsNeeded: item.price - coinsDeposited)
        }
        coinsDeposited -= item.price
        var newItem = item
        newItem.count -= 1
        inventory[name] = newItem
        print("Dispensing \(name)")
    }
}

let favoriteSnacks = [
    "Alice": "Chips",
    "Bob": "Licorice",
    "Eve": "Pretzels"
]
func buyFavoriteSnack(person: String, vendingMachine: VendingMachine) throws {
    let snackName = favoriteSnacks[person] ?? "Candy Bar"
    try vendingMachine.vend(itemNamed: snackName)
}
```

### Do-Catch 做错误处理

使用 do-catch 块对错误进行捕获，当在调用一个 throws 声明的函数或方法时，把调用语句放在 do 语句块中，**do块中抛出错误，**同时 do 语句块后面紧接着使用 catch 语句块。

```swift
do {
    try <#throwing expression#>
} catch <#pattern#> {
    <#statements#>
} catch <#pattern#> where <#condition#> {
    <#statements#>
} catch <#pattern#> {
    <#statements#>
}
```

```swift
var vendingMachine = VendingMachine()
vendingMachine.coinsDeposited = 8
do {
    try buyFavoriteSnack(person: "Alice", vendingMachine: vendingMachine)
    print("Success! Yum.")
} catch VendingMachineError.invalidSelection {
    print("Invalid Selection")
} catch VendingMachineError.outOfStock {
    print("Out of Stock")
} catch VendingMachineError.insufficientFunds(let coinsNeeded) {
    print("Insufficient Funds. Please insert an additional \(coinsNeeded) coins")
} catch {
    print("Unexpected error: \(error).")
}
```

### try?

try?会将错误转换为可选值，当调用`try?`＋函数或方法语句时候，如果函数或方法抛出错误，程序不会发崩溃，而返回一个nil，如果没有抛出错误则返回可选值。

```swift
func someThrowingFunction() throws -> Int {
    //...
    return 1
}
let x = try? someThrowingFunction()
let y: Int?
do {
   y = try someThrowingFunction()
} catch {
    y = nil
}
```

### try!

如果确信一个函数或者方法不会抛出错误，可以使用 try! 来中断错误的传播。但是如果错误真的发生了，你会得到一个运行时错误。

```swift
let photo = try! loadImage(atPath: "./Resources/JohnAppleseed.jpg")
```

