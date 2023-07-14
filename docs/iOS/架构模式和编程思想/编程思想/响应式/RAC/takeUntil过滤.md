# takeUntil

给takeUntil传的是哪个信号，那么当这个信号发送信号或sendCompleted，就不能再接受源信号的内容了。

`takeUntil`需要一个信号作为标记，当标记的信号发送数据，就停止。

```objective-c
(void)takeUntil {
    RACSubject *subject = [RACSubject subject];
    RACSubject *subject2 = [RACSubject subject];
    [[subject takeUntil:subject2] subscribeNext:^(id x) {
        NSLog(@"%@", x);
    }];
    // 发送信号
    [subject sendNext:@1];
    [subject sendNext:@2];
    [subject2 sendNext:@3];  // 1
    //    [subject2 sendCompleted]; // 或2
    [subject sendNext:@4];
}
```

## UITableViewCell复用时的问题

`UITableViewCell`和`UICollectionViewCell`复用使用`RAC`的问题,解决复用`cell`中信号的办法就是在`cell`里面创建的信号加上`takeUntil:cell.rac_prepareForReuseSignal`来让`cell`在每次重用的时候都去
 disposable创建的信号(解绑信号)

```objectivec
- (UITableViewCell *)tableView:(nonnull UITableView *)tableView cellForRowAtIndexPath:(nonnull NSIndexPath *)indexPath {
    UITableViewCell * cell = [tableView dequeueReusableCellWithIdentifier:@"TableViewCell"];

    @weakify(self);
    [[RACObserve(cell.textLabel, text) takeUntil:cell.rac_prepareForReuseSignal] subscribeNext:^(id x) {
        @strongify(self);
        NSLog(@"%@", self);
    }];

    return cell;
}
```
