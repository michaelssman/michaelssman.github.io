# 数组中元素排序：

res为需要排序对数组， 数组中元素为NEWModel类型对对象、是一个模型。 下面代码的作用就是根据createDate去排序。

```
           [res sortUsingComparator:^NSComparisonResult(id  _Nonnull obj1, id  _Nonnull obj2) {
                return [((NEWModel *)obj2).createDate compare: ((NEWModel *)obj1).createDate];
            }];
```
```

    [arr sortUsingComparator:^NSComparisonResult(id  _Nonnull obj1, id  _Nonnull obj2) {
        //降序排序  最大的在前面 第一个元素是最大的
        return [obj2 compare: obj1];
        //升序排序  最小的在前面 最后一个元素是最大的
        return [obj1 compare: obj2];
    }];
```

# 遍历数组 对数组进行增删改查操作

遍历数组可以使用`enumerateObjectsUsingBlock`方法， `*stop = YES;`可以结束循环遍历。  这种方法可以对数组进行增删改操作而不会崩溃报错。

```
    [dataSourceArray enumerateObjectsUsingBlock:^(NEWModel * obj, NSUInteger idx, BOOL * _Nonnull stop) {
        //数据源是否在区间之内
        if ((([obj.createDate compare:timeArray.firstObject] == 0) || ([obj.createDate compare:timeArray.firstObject] == 1)) && (([obj.createDate compare:timeArray.lastObject] == 0) ||([obj.createDate compare:timeArray.lastObject] == -1))) {
            //服务器删除数据的情况
            BOOL isDelete = YES;
            for (NEWModel *new in res) {
                if ([((NEWModel *)obj).articleID isEqual:new.articleID]) {
                    //更新数据
                    isDelete = NO;
                    //*stop = YES;
                    [dataSourceArray replaceObjectAtIndex:idx withObject:new];
                    break;
                }
            }
            if (isDelete) {
                //*stop = YES;
                [dataSourceArray removeObject:obj];
            }
        }
    }];
```
注：
`*stop = YES;`,这句话会终止遍历数组， 所以数组遇到`*stop = YES;`便会停止，后面元素就没法遍历了。 所以需要把`*stop = YES;`给注掉。
注：
该方法会存在删除数据会删不干净的情况，最好的方法就是使用一个临时的数组去做增删改操作，结束之后再把临时数组的数据赋给该数组。
#####
dataSourceArray赋值的时候如果直接这样`dataSourceArray = @[@"元素1",@"元素2",@"元素3"].copy;`会出错。
应该`dataSourceArray = [NSMutableArray arrayWithArray:@[@"元素1",@"元素2",@"元素3"]];`

# 数组倒序

有时候需要把数组反过来，第一个元素为最后一个元素，最后一个元素为第一个元素。获取顺序相反的数组。

```
NSArray *ret = [[<#array#> reverseObjectEnumerator] allObjects];
```
# 在数组中从前面插入一个数组

在数组的前面插入一个数组

```
                //判断要插入的数组是否为空，为空的就不用插入了
                if (<#要插入的数组的count#>) {
                    [<#原来的数组#> insertObjects:<#要插入的数组#> atIndexes:[NSIndexSet indexSetWithIndexesInRange:NSMakeRange(0, <#要插入的数组的元素个数#>)]];
                }
```
# 从数组中删除数据 删除的数据是另一个数组中的元素。

```
    NSMutableArray *array = [NSMutableArray arrayWithObjects:@"1",@"2",@"3",@"2", nil];
    NSArray *arr = @[@"2"];
    [array removeObjectsInArray:arr];
    NSLog(@"%@",array);
```
结果
```
(lldb) po array
<__NSArrayM 0x604000256200>(
1,
3
)
```