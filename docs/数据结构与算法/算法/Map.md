# Map字典

## 数据分组

有一个列表List，里面`字段1`的值相同的为一组。`字段1`为key，value为`字段1的值相同`的列表。

- 遍历List
- 如果Map里面key为`字段1`的value不存在，则创建key为`字段1`的value为空数组
- key为`字段1`的value数组添加item

## 查找是否有重复数据值并获取重复值的下标

使用字典，key：数据属性值，value：数据在数组中的下标。

从字典中根据key取value，如果value有值则有重复的数据。可以得到重复的值的下标：当前下标和value（上一个下标）。

示例：**多单位换算比例不能重复**，要求检测单位的换算比例中是否存在重复，并返回重复项的下标，若无重复返回特殊标记。

复杂度

- 时间：O(n)
- 空间：O(n)

```swift
import Foundation

func findFirstDuplicateRateInObjects(_ objects: [[String: Any]], key: String = "count") -> (Int, Int)? {
    var seen: [String: Int] = [:]
    for (i, obj) in objects.enumerated() {
        //忽略空字符串
        if let r = obj[key] as? String, !r.isEmpty {
            if let first = seen[r] {
                return (first + 1, i + 1)
            }
            seen[r] = i
        }
    }
    return nil
}

// 使用示例
// key是数据的值：2.0，3.0，2.0 value是下标：2，3，4
let objects: [[String: Any]] = [
    ["name": "A", "count": ""],
    ["name": "B", "count": "2.0"],
    ["name": "C", "count": "3.0"],
    ["name": "D", "count": "2.0"]
]
if let dupObj = findFirstDuplicateRateInObjects(objects) {
    print("objects 重复：辅助单位\(dupObj.0) 和 辅助单位\(dupObj.1)")//输出下标2和4
} else {
    print("objects NO DUPLICATE")
}
```

