# contentOffset和contentInset

scrollView.contentOffset.y

滑动多少 contentOffset.y就改变多少  是相对于最原始的位置

[self.tableView setContentInset:UIEdgeInsetsMake(offsetY, 0, 0, 0)];

设置了setContentInset  `[self.tableView setContentInset:UIEdgeInsetsMake(offsetY, 0, 0, 0)];
`那么 contentOffset.y 一开始就是设置的offsetY  从一开始就偏移了。


```
- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
    NSLog(@"%.4f",scrollView.contentOffset.y);
}
```