### as!

向下强制类型转换，如果转换失败会报错

```swift
class Auto {}
class Car: Auto {}
let auto: Auto = Car()
let car = auto as! Car
```

### as?

向下强制类型转换，只是as?在转换失败之后会返回nil对象，转换成功之后返回一个可选类型(optional)，需要我们拆包使用。

```swift
let auto: Auto = Car()
if let car = auto as? Car {
   print("这是Car")
}
else {
  print("这不是Car")
}
```