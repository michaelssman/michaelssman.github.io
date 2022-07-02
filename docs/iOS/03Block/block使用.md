# block

block作为参数

写法：

包括下面三个部分

1. 先写返回值
2. 然后小括号，小括号里面是上尖号
3. 然后是block传的参数 需要加括号

## 应用场景：

网络请求或者在一些异步代码中有先后顺序的情况下。

### 例如：

1、 网络请求成功之后，再利用请求的结果数据去做其它操作。
2、 希望一些代码的执行有先后顺序，先执行一些代码，执行完毕出来结果之后再执行另一些代码。
方法的声明

```
//带参数
+ (void)get_my_trade_moneySuccess:(void (^)(NSString *total_money))block;
//不带参数
- (void)methodNameWithDone:(void(^)())Done;
```

#### 注：

方法的声明，参数最好带上参数名，调用的时候，可以直接使用。有参数名也比较清晰明了。一看就知道是什么意思。

方法的实现
```
+ (void)get_my_trade_mosneySuccess:(void (^)(NSString *))block {
    /*
     这里面写方法的实现，并且在需要的时候调用block。
     */
    
    block(@"block块的参数");
    
}
```
## 带有返回值和参数的block

```objective-c
- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.

		//调用 
    [self block_test:^NSString *(NSString *par) {
        NSLog(@"传的参数%@",par);
        return par;
    }];
    
}

//定义
- (void)block_test:(NSString * (^)(NSString *par))blck {
    NSLog(@"block_test打印block的返回值：%@",blck(@"dddd"));
}
```

打印结果

```
	传的参数dddd
	block_test打印block的返回值：dddd
```

### 注：

在调用方法中
使用return的话是退出block方法，不会退出整个方法。

```
- (void)myMethod {
     [self methodNameWithDone:^{
        return ;
    }]; 
//下面有代码的话， 就继续执行。
//如果想结束的话应该把return放到外面
  /*
     [self methodNameWithDone:^{
    }]; 
        return ;
*/
}
```