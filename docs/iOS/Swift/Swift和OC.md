# swift和OC互调

## Swift项目创建OC文件

使用`项目名-Bridging-Header`桥接文件。一组暴露给swift的头文件。类似散头文件，通过一个头文件映射一组头文件。

swift的framework默认创建了一个散头文件module.modulemap。

TRAGETS --> Build Setting --> Objective-C Bridging Header

## OC调swift

通过`项目名 -Swift.h`文件。把swift代码翻译了头文件。编译的时候放到macho中变成OC符号。
