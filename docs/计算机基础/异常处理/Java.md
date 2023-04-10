# 异常

异常处理代码和业务代码分离，使程序更优雅，更好的容错性，高健壮性。

### try catch finally

```java
public static void main(String[] args) {
    //将可能出错的代码放到try代码块里面
    try {
        //两个数求商
        int num1 = 12;
        int num2 = 0;
        System.out.println("两个数的商为：" + num1/num2);
    } catch (Exception ex) {//程序将异常封装成一个对象，用Exception接收
        System.out.println("程序出现了错误");
    } finally {
        System.out.println("程序无论是否出现异常，这个逻辑都必须执行");
    }
    //上面的代码出错了，下面的代码仍然可以执行
    System.out.println("下面的代码1");
    System.out.println("下面的代码2");
    System.out.println("下面的代码3");
}
```

try-catch执行情况

1. try块中的代码没有出现异常

   不执行catch块代码，执行catch块后面的代码

2. try块中代码出现异常，catch中异常类型匹配（相同或者父类）

   Java会生成相应的异常对象，java异常寻找匹配的catch块，执行catch块代码，执行catch块后面的代码。try块中尚未执行的语句不会执行。

3. try块中代码出现异常，catch中异常类型不匹配，相当于捕捉不到

   不执行catch块代码，不执行catch块后面的代码，程序会中断运行。