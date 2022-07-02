# 简单的 IR 语法： 

## 数组 

```
[<elementnumber> x <elementtype>] 
//example 
alloca [24 x i8], align 8 24个i8都是0 
alloca [4 x i32] === array 
```

i8:8位的整型

i32:32位的整型

i64:64位的整型

## 结构体 

```
%swift.refcounted = type { %swift.type*, i64 } 
//表示形式
%T = type {<type list>} //这种和C语言的结构体类似
```

## 指针类型 

```
<type> * 
//example
i64* //64位的整形
```

## getelementptr 指令 

LLVM中我们获取数组和结构体的成员，通过 getelementptr ，语法规则如下： 









































































