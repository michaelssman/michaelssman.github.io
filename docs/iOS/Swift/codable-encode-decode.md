# Codable 自定义编解码

## 1. Codable 是什么

`Codable` 是 Swift 标准库提供的协议，用来让类型支持编码和解码。

它本质上是两个协议的组合：

```swift
typealias Codable = Encodable & Decodable
```

含义：

- `Decodable`：把 JSON、Plist 等外部数据解码成 Swift 模型。
- `Encodable`：把 Swift 模型编码成 JSON、Plist 等外部数据。

常见用法：

```swift
struct User: Codable {
    let id: Int
    let name: String
}

let user = try JSONDecoder().decode(User.self, from: jsonData)
let data = try JSONEncoder().encode(user)
```

如果属性都能自动编解码，Swift 会自动生成 `init(from:)` 和 `encode(to:)`。

## 2. 什么时候需要自定义 Codable

以下情况通常需要手写 `init(from:)` 或 `encode(to:)`。

### 2.1 JSON 字段名和 Swift 属性名不一致

接口返回：

```json
{
  "user_id": 1001,
  "user_name": "Alice"
}
```

Swift 模型想写成：

```swift
struct User {
    let id: Int
    let name: String
}
```

这种情况可以只写 `CodingKeys`。

### 2.2 字段类型不稳定

接口有时返回数字：

```json
{ "id": 1001 }
```

有时返回字符串：

```json
{ "id": "1001" }
```

这种情况通常需要自定义 `init(from:)`。

### 2.3 解码时需要默认值

接口可能缺字段：

```json
{ "name": "Alice" }
```

但模型希望：

```swift
id = 0
```

可以在 `init(from:)` 中处理。

### 2.4 编码时不想输出某些字段

例如本地缓存字段、临时 UI 状态字段，不希望提交给接口。

这种情况需要自定义 `encode(to:)`。

### 2.5 JSON 结构和模型结构不同

接口结构：

```json
{
  "user": {
    "id": 1001,
    "name": "Alice"
  }
}
```

模型想直接写：

```swift
struct User {
    let id: Int
    let name: String
}
```

这种情况需要在 `init(from:)` 中处理嵌套容器。

## 3. CodingKeys

自定义编解码通常都会配合 `CodingKeys`。

```swift
struct User: Codable {
    let id: Int
    let name: String

    enum CodingKeys: String, CodingKey {
        case id = "user_id"
        case name = "user_name"
    }
}
```

作用：

- 定义 JSON 字段名和 Swift 属性名之间的映射。
- 控制哪些字段参与编码和解码。

如果属性不写进 `CodingKeys`，它默认不会参与自定义编解码。

## 4. init(from decoder:) 是什么

`init(from decoder:)` 来自 `Decodable`。

它的作用是：把外部数据解码成当前 Swift 类型。

方法签名：

```swift
init(from decoder: Decoder) throws
```

你通常不会手动调用它，而是通过 `JSONDecoder` 间接触发：

```swift
let user = try JSONDecoder().decode(User.self, from: data)
```

执行这行代码时，Swift 会自动调用：

```swift
User.init(from: decoder)
```

## 5. init(from:) 基础写法

示例 JSON：

```json
{
  "id": 1001,
  "name": "Alice",
  "age": 20
}
```

模型：

```swift
struct User: Codable {
    let id: Int
    let name: String
    let age: Int

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case age
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        age = try container.decode(Int.self, forKey: .age)
    }
}
```

这段代码做了三件事：

1. 从 `decoder` 里取出 keyed container。
2. 按 `CodingKeys` 读取字段。
3. 把读取到的值赋给属性。

## 6. container 是什么

这一行很常见：

```swift
let container = try decoder.container(keyedBy: CodingKeys.self)
```

可以把 `container` 理解成一个 JSON 字典读取器。

如果 JSON 是：

```json
{
  "id": 1001,
  "name": "Alice"
}
```

那么：

```swift
container.decode(Int.self, forKey: .id)
container.decode(String.self, forKey: .name)
```

就类似于读取：

```swift
json["id"]
json["name"]
```

只是 Swift 会同时做类型检查和错误处理。

## 7. decode 和 decodeIfPresent 的区别

### decode

```swift
let id = try container.decode(Int.self, forKey: .id)
```

特点：

- 字段必须存在。
- 字段不能是 `null`。
- 类型必须正确。
- 不满足就抛错。

适合必填字段。

### decodeIfPresent

```swift
let nickname = try container.decodeIfPresent(String.self, forKey: .nickname)
```

特点：

- 字段不存在时返回 `nil`。
- 字段是 `null` 时返回 `nil`。
- 字段存在但类型错误时仍然会抛错。

适合可选字段。

## 8. 给缺失字段默认值

示例：

```swift
struct User: Codable {
    let id: Int
    let name: String
    let age: Int

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case age
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        age = try container.decodeIfPresent(Int.self, forKey: .age) ?? 0
    }
}
```

当 JSON 中没有 `age` 时：

```json
{
  "id": 1001,
  "name": "Alice"
}
```

最终：

```swift
age = 0
```

## 9. 宽松解码：类型不稳定的统一处理

实际接口中，经常会遇到同一个字段类型不稳定：

```json
{ "id": 1001 }
{ "id": "1001" }
{ "enabled": true }
{ "enabled": 1 }
{ "enabled": "true" }
```

遇到这种情况，可以把常见转换集中封装到 `KeyedDecodingContainer` 中：

```swift
extension KeyedDecodingContainer {
    func decodeLossyInt(forKey key: Key) -> Int? {
        if let value = try? decodeIfPresent(Int.self, forKey: key) {
            return value
        }
        if let value = try? decodeIfPresent(String.self, forKey: key) {
            return Int(value.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        return nil
    }

    func decodeLossyString(forKey key: Key) -> String? {
        if let value = try? decodeIfPresent(String.self, forKey: key) {
            return value
        }
        if let value = try? decodeIfPresent(Int.self, forKey: key) {
            return "\(value)"
        }
        if let value = try? decodeIfPresent(Double.self, forKey: key) {
            return "\(value)"
        }
        if let value = try? decodeIfPresent(Bool.self, forKey: key) {
            return value ? "true" : "false"
        }
        return nil
    }

    func decodeLossyBool(forKey key: Key) -> Bool? {
        if let value = try? decodeIfPresent(Bool.self, forKey: key) {
            return value
        }
        if let value = try? decodeIfPresent(Int.self, forKey: key) {
            return value != 0
        }
        if let value = try? decodeIfPresent(String.self, forKey: key) {
            let normalized = value.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()

            if ["true", "1", "yes"].contains(normalized) {
                return true
            }
            if ["false", "0", "no"].contains(normalized) {
                return false
            }
        }
        return nil
    }
}
```

使用：

```swift
id = container.decodeLossyInt(forKey: .id) ?? 0
enabled = container.decodeLossyBool(forKey: .enabled) ?? false
name = container.decodeLossyString(forKey: .name) ?? ""
```

如果字段缺失、为 `null` 或无法转换，就返回 `nil`，再由调用处用 `??` 给默认值。

## 10. func encode(to encoder:) 是什么

`encode(to:)` 来自 `Encodable`。

它的作用是：把当前 Swift 模型编码成外部数据。

方法签名：

```swift
func encode(to encoder: Encoder) throws
```

你通常不会手动调用它，而是通过 `JSONEncoder` 间接触发：

```swift
let data = try JSONEncoder().encode(user)
```

执行这行代码时，Swift 会自动调用：

```swift
user.encode(to: encoder)
```

## 11. encode(to:) 基础写法

```swift
struct User: Codable {
    let id: Int
    let name: String
    let age: Int?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case age
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(name, forKey: .name)
        try container.encodeIfPresent(age, forKey: .age)
    }
}
```

## 12. encode 和 encodeIfPresent 的区别

### encode

```swift
try container.encode(name, forKey: .name)
```

用于非可选值，或者你希望明确写出该字段。

### encodeIfPresent

```swift
try container.encodeIfPresent(age, forKey: .age)
```

当 `age == nil` 时，不输出 `age` 字段。

例如：

```swift
let user = User(id: 1001, name: "Alice", age: nil)
```

编码结果：

```json
{
  "id": 1001,
  "name": "Alice"
}
```

不会输出：

```json
{
  "age": null
}
```

## 13. 编码时排除某些字段

例如模型里有一个本地 UI 状态，不想提交给接口：

```swift
struct User: Codable {
    let id: Int
    let name: String
    var isSelected: Bool

    enum CodingKeys: String, CodingKey {
        case id
        case name
    }
}
```

`isSelected` 没有写进 `CodingKeys`，因此不会参与编码和解码。

如果 `isSelected` 需要默认值，可以写：

```swift
struct User: Codable {
    let id: Int
    let name: String
    var isSelected: Bool

    enum CodingKeys: String, CodingKey {
        case id
        case name
    }

    init(id: Int, name: String, isSelected: Bool = false) {
        self.id = id
        self.name = name
        self.isSelected = isSelected
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        isSelected = false
    }
}
```

## 14. 字段名映射示例

JSON：

```json
{
  "user_id": 1001,
  "user_name": "Alice"
}
```

Swift：

```swift
struct User: Codable {
    let id: Int
    let name: String

    enum CodingKeys: String, CodingKey {
        case id = "user_id"
        case name = "user_name"
    }
}
```

如果只是字段名不同，不需要手写 `init(from:)` 和 `encode(to:)`，只写 `CodingKeys` 就够了。

## 15. 嵌套 JSON 解码示例

JSON：

```json
{
  "user": {
    "id": 1001,
    "name": "Alice"
  }
}
```

模型想直接写：

```swift
struct User: Codable {
    let id: Int
    let name: String
}
```

可以这样解码：

```swift
struct User: Codable {
    let id: Int
    let name: String

    enum RootKeys: String, CodingKey {
        case user
    }

    enum UserKeys: String, CodingKey {
        case id
        case name
    }

    init(from decoder: Decoder) throws {
        let rootContainer = try decoder.container(keyedBy: RootKeys.self)
        let userContainer = try rootContainer.nestedContainer(
            keyedBy: UserKeys.self,
            forKey: .user
        )

        id = try userContainer.decode(Int.self, forKey: .id)
        name = try userContainer.decode(String.self, forKey: .name)
    }
}
```

## 16. 完整通用示例

这个示例把前面的点组合起来：字段类型不稳定时复用第 9 节的 `decodeLossy...` 方法，编码时用 `encodeIfPresent` 控制可选字段。

JSON 可能是：

```json
{
  "id": "1001",
  "name": "Alice",
  "enabled": 1,
  "age": null
}
```

模型：

```swift
struct User: Codable {
    let id: Int
    let name: String
    let enabled: Bool
    let age: Int?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case enabled
        case age
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = container.decodeLossyInt(forKey: .id) ?? 0
        name = container.decodeLossyString(forKey: .name) ?? ""
        enabled = container.decodeLossyBool(forKey: .enabled) ?? false
        age = container.decodeLossyInt(forKey: .age)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(name, forKey: .name)
        try container.encode(enabled, forKey: .enabled)
        try container.encodeIfPresent(age, forKey: .age)
    }
}
```

使用：

```swift
let user = try JSONDecoder().decode(User.self, from: data)
let encodedData = try JSONEncoder().encode(user)
```

## 17. 常见错误

### 17.1 手写 init(from:) 后，普通 init 消失

如果你写了：

```swift
init(from decoder: Decoder) throws
```

Swift 可能不会再自动生成你想要的成员初始化方法。

需要自己补：

```swift
init(id: Int, name: String) {
    self.id = id
    self.name = name
}
```

### 17.2 CodingKeys 漏字段

如果属性需要参与编解码，但没有写进 `CodingKeys`，它不会被读取或写出。

### 17.3 decodeIfPresent 不能处理类型错误

`decodeIfPresent` 只能处理字段不存在或字段为 `null`。

如果字段存在但类型错误，仍然会抛错。

需要兼容类型错误时，可以用：

```swift
try? container.decodeIfPresent(...)
```

或封装 `decodeLossy...` 方法。

### 17.4 encodeIfPresent 不会输出 null

如果你希望输出：

```json
{ "age": null }
```

不能使用 `encodeIfPresent`。

可以使用：

```swift
try container.encodeNil(forKey: .age)
```

## 18. 实践建议

### 简单字段名映射

只写 `CodingKeys`。

### 需要默认值

自定义 `init(from:)`。

### 接口类型不稳定

封装 `decodeLossyInt`、`decodeLossyString`、`decodeLossyBool`。

### 不想编码某些字段

不要把字段写入 `CodingKeys`，或自定义 `encode(to:)`。

### 需要稳定输出指定字段

自定义 `encode(to:)`，明确写出每个字段。

## 19. 一句话总结

`init(from:)` 负责“怎么把外部数据读进模型”。

`encode(to:)` 负责“怎么把模型写成外部数据”。

普通场景让 Swift 自动生成即可；当字段名、字段类型、默认值、嵌套结构或输出规则不符合默认行为时，再手写自定义编解码。
