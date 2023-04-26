网络中间层

面向协议

只需要实现Moya协议，不直接操作网络库。完成网络配置信息。

Provider发起网络请求



## 网络请求数据转模型

```swift
/// 定义模型类
import Foundation
struct ReminderData: Codable {
    var data: [Reminder]
}
struct Reminder: Codable {
    var remindTxt: String = ""
    var remindTime: String = ""
    var enabled: Bool = false
  
  	// 关键字“repeat”在这里不能用作标识符
		// 如果这个名字是不可避免的，使用反号转义
    var `repeat`: Bool = false
  
	  //数组里面的元素也得是Codable
    var repeatWeekDays: Array? = [Int]()
    var reminderId: Int
}


/// 转模型
JSONDecoder().decode(ReminderData.self, from: r as! Data)
```

