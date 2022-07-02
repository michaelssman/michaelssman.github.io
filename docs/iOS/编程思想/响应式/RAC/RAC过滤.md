# takeUntil

给takeUntil传的是哪个信号，那么当这个信号发送信号或sendCompleted，就不能再接受源信号的内容了。

##### `takeUntil` 标记

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

