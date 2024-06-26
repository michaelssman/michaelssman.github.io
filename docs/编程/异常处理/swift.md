# swift错误处理

## Error错误表示

在 swift 中如果要定义一个表示错误的类型，只要遵循 Error 协议就可以。

通常用枚举或结构体来表示错误类型，枚举用的多些，因为它能更直观的表达当前错误类型的每种错误细节。

```swift
enum VendingMachineError: Error {
    case invalidSelection
    case insufficientFunds(coinsNeeded: Int)
    case outOfStock
}
```

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

