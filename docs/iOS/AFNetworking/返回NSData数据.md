# 网络请求返回NSData数据的解析问题

afn返回的数据是NSData的情况下，没法解析。`responseObject`是返回的数据。需要转成相应的字典（或数组）类型。

## 下面是直接将请求到的数据解析

```
NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseObject options:0 error:nil];
```
### 如果要对请求到的数据进行字符串的替换，例如要将`\"`替换成`\\"`就需要使用下面的方法：

```
获得的json先转换成字符串
NSString *receiveStr = [[NSString alloc]initWithData:responseObject encoding:NSUTF8StringEncoding];

将字符串进行替换
        NSString *resultStr = [receiveStr stringByReplacingOccurrencesOfString:@"\\\"" withString:@"\\\\\\\""];

字符串再生成NSData
NSData * data = [resultStr dataUsingEncoding:NSUTF8StringEncoding];

 再解析  
        NSDictionary *jsonDict = [NSJSONSerialization JSONObjectWithData:data options:NSJSONReadingMutableLeaves error:nil];
```