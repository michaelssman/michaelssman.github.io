# DisposeBag

`disposeBag`用于管理**订阅的生命周期**，当对象被销毁时，所有订阅也被正确地取消，**防止内存泄漏**。

确保`disposeBag`在类的生命周期中被正确地初始化和维护是很重要的。

在你的代码中，取消网络请求的逻辑已经实现。在`Observable.create`闭包中，你返回了一个`Disposables.create`，其中调用了`request.cancel()`。这样，当你的Observable被订阅者取消订阅时，上传请求也会随之取消。

要实际执行取消操作，你需要持有返回的`Observable`的订阅，并在需要取消时，调用订阅的`.dispose()`方法。下面是一个简单的例子说明如何使用这个函数：

```swift
// 假设这是你的ViewModel或者Controller中的代码
let disposeBag = DisposeBag()

// 保存这个上传操作的订阅
let subscription = upload("path/to/upload", image: yourImage, headers: yourHeaders)
    .subscribe(
        onNext: { response in
            // 处理成功响应
        },
        onError: { error in
            // 处理错误
        },
        onCompleted: {
            // 处理完成
        }
    )

// 将订阅添加到disposeBag中，以便于管理
subscription.disposed(by: disposeBag)

// 当你需要取消上传时
subscription.dispose() // 这将触发Disposables.create中的request.cancel()
```

通过调用`subscription.dispose()`，将调用你在`Disposables.create`中定义的取消逻辑。

请注意，`dispose()`方法会从`disposeBag`中移除订阅，如果你还想要在后面的某个时间点重新订阅，你需要重新创建这个订阅并再次添加到`disposeBag`中。如果你只是想暂时取消订阅，但保持它在`disposeBag`中，可以使用`.takeUntil()`操作符来控制订阅的生命周期。

## cell重用

```swift
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "CustomCell", for: indexPath) as! CustomCell

    cell.headerView.dateButton.rx.tap
        .subscribe(onNext: { [weak self] in
            self?.selectedIndex?(1)
        })
        .disposed(by: cell.cellDisposeBag) // 绑定到 Cell 的 DisposeBag

    return cell
}
```

