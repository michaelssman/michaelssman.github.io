# associatedtype

## 关联类型的作用

给协议中用到的类型定义一个占位名称


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


## 