tableView的tableHeaderView一旦设置了，再修改tableHeaderView的frame，是不会改变的。但是可以设置tableHeaderView的view的frame。
```
    UIView *myHeaderView = [[UIView alloc]initWithFrame:CGRectMake(0, 0, kscreenWidth, 55)];
    myHeaderView.backgroundColor = [UIColor blueColor];
    [UIView animateWithDuration:1.5 animations:^{
        /*
         使用beginUpdates endUpdates 可使动画流畅一点点。（没测试过）
         */
        [self.tableView beginUpdates];
        myHeaderView.frame = CGRectMake(0, 0, kscreenWidth, 0);
        [self.tableView setTableHeaderView:myHeaderView];
        [self.tableView endUpdates];
    }];
```
#####  更改tableview的header的高度
1 先设置headerView的view的frame
```
headerV.frame = CGRectMake(0, 0, kscreenWidth, 100);
```
2 再设置tableView的tableHeaderView为创建的view
```
self.tableView.tableHeaderView = headerV;
```