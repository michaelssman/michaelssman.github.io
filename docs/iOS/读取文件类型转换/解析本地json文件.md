# 解析本地json文件

```
+ (NSMutableArray *)getJsonData {
    NSArray *jsonArray = [[NSArray alloc]init];
    NSData *fileData = [[NSData alloc]init];
    NSString *path = [[NSBundle mainBundle] pathForResource:<#json文件名#> ofType:@"json"];
    fileData = [NSData dataWithContentsOfFile:path];
    NSMutableArray *array = [[NSMutableArray alloc]initWithCapacity:0];
    jsonArray = [NSJSONSerialization JSONObjectWithData:fileData options:NSJSONReadingMutableLeaves error:nil];
    for (NSDictionary *dict in jsonArray) {
/*
数据处理
*/
        [array addObject:dict];
    }
    return array;
}
```
