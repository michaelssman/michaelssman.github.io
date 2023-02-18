# swift多线程

__dependencies：一个数组，保存与之依赖的任务

任务执行的条件：任务的state是否是isReady

所有的任务添加到队列中 调度的方式是：所有任务会形成一个链表

## 任务

### 1、BlockOperation

```swift
let operation = BlockOperation{
  print(#function)
}
operation.start()
```

### 2、DispatchWorkItem

```swift
let workItem = DispatchWorkItem{
  print(#function)
}
workItem.perform()
```

#### DispatchWorkItem

```swift
lazy var workItem : DispatchWorkItem = {
  return DispatchWorkItem{
    sleep(1)
    guard self.workItem.isCancelled == false else{
      return
    }
    print(#function)
  }
}()

func testWotkItem() {
  DispatchQueue.global().async(execute: workItem)
}
```

#### group组

```swift
// MARK: 组
func testGroup() {
  let workItem1 = DispatchWorkItem{
    print(1)
  }
  let workItem2 = DispatchWorkItem{
    print(2)
  }
  let workItem3 = DispatchWorkItem{
    print(3)
  }
  workItem1.notify(queue: .global(), execute: workItem3)//1通知执行3
  workItem2.notify(queue: .global(), execute: workItem1)//2通知执行1
  DispatchQueue.global().async(execute: workItem2)//开始执行2
  //        打印结果 2 1 3
  //        DispatchGroup
}
```

## Thread

```swift
for i in 0...10 {
  Thread.detachNewThread {
    print(i)
  }
}
```

```swift
class ObjectForThread {
    func threadTest() {
        let thread = Thread(target: self, selector: #selector(threadWorker), object: nil)
        thread.start()
        print(#function)
    }
    
    @objc func threadWorker() {
        print(#function)
    }
}

let obj = ObjectForThread()
obj.threadTest()
```

## BlockOperation

```swift
class ObjectForThread {
    func threadTest() {
        let operation = BlockOperation(block: {[weak self] in
            self?.threadWorker()
            return
        })
        let queue = OperationQueue()
        queue.addOperation(operation)
        print("threadTest")
    }
    
    @objc func threadWorker() {
        print("threadWorker")
    }
}

let obj = ObjectForThread()
obj.threadTest()
```

## 继承Operation

```swift
class HHOperation: Operation {
    override func main() {
        sleep(1)
        print("HHOperation")
    }
}

class ObjectForThread {
    func threadTest() {
        let operation = HHOperation()
        //Operation完成的回调
        operation.completionBlock = { () -> Void in
            print("--- operation.completionBlock ---")
        }
        let queue = OperationQueue()
        queue.addOperation(operation)
        print("threadTest")
    }
}
///打印结果：
///threadTest
///HHOperation
///--- operation.completionBlock ---
```

## GCD

### asyncAfter

```swift
DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
  print("Are we there yet?")
}
```

### DispatchGroup-wait

```swift
let workingGroup = DispatchGroup()
let workingQueue = DispatchQueue(label: "request_queue")

workingGroup.enter()
workingQueue.async {
  Thread.sleep(forTimeInterval: 1)
  print("接口 A 数据请求完成")
  workingGroup.leave()
}

workingGroup.enter()
workingQueue.async {
  Thread.sleep(forTimeInterval: 1)
  print("接口 B 数据请求完成")
  workingGroup.leave()
}

print("我是开始执行的，异步操作里的打印后执行")

workingGroup.wait()
print("接口 A 和接口 B 的数据请求都已经完毕，开始合并两个接口的数据")

//    执行结果：
//    我是开始执行的，异步操作里的打印后执行
//    接口 A 数据请求完成
//    接口 B 数据请求完成
//    接口 A 和接口 B 的数据请求都已经完毕，开始合并两个接口的数据
```

### DispatchGroup-notify

```swift
let workingGroup = DispatchGroup()
let workingQueue = DispatchQueue(label: "request_queue")

workingGroup.enter()
workingQueue.async {
  Thread.sleep(forTimeInterval: 1)
  print("接口 A 数据请求完成")
  workingGroup.leave()
}

workingGroup.enter()
workingQueue.async {
  Thread.sleep(forTimeInterval: 1)
  print("接口 B 数据请求完成")
  workingGroup.leave()
}

print("我是最开始执行的，异步操作里的打印后执行")

workingGroup.notify(queue: workingQueue) {
  print("接口 A 和接口 B 的数据请求都已经完毕，开始合并两个接口的数据")
}
print("验证不阻塞")

//执行结果：
//我是最开始执行的，异步操作里的打印后执行
//验证不阻塞
//接口 A 数据请求完成
//接口 B 数据请求完成
//接口 A 和接口 B 的数据请求都已经完毕，开始合并两个接口的数据
```

### DispatchSource

dispatch source是一个监视某些类型事件的对象。当这些事件发生时，它自动将一个 task 放入一个dispatch queue的执行例程中。

#### DispatchSourceTimer

```swift
var seconds = 10
let timer : DispatchSourceTimer = DispatchSource.makeTimerSource(flags: [], queue: DispatchQueue.global())

timer.schedule(deadline: .now(), repeating: 1.0)
timer.setEventHandler {
  seconds -= 1
  if seconds < 0 {
    timer.cancel()
  } else {
    print(seconds)
  }
}
timer.resume()

//        9
//        8
//        7
//        6
//        5
//        4
//        3
//        2
//        1
//        0
```

## 死锁

```swift
let queue = DispatchQueue(label: "label")
queue.async {
  print("in queue async")//串行队列正在执行的task1
  queue.sync {
    print("in queue sync")//串行队列将要同步执行task2 串行队列把task2加入串行队列 task1要等task2执行完 task2又要等task1
  }
}
```

### synchronized

```swift
func synchronized(_ obj: AnyObject, closure:()->()) {
    objc_sync_enter(obj)
    closure()
    objc_sync_exit(obj)
}
```

### 安全的array

加锁解锁。

```swift
var array = Array(0...10000)
let lock = NSLock()

func getLastItem() -> Int? {
    lock.lock()
    var temp: Int? = nil
    if array.count > 0 {
        temp = array[array.count - 1]
    }
    lock.unlock()
    return temp
}
func removeLastItem () {
    lock.lock()
    array.removeLast()
    lock.unlock()
}
```

