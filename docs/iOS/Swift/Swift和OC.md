创建swift文件，使用ProjectName-Bridging-Header桥接文件。一组暴露给swift的头文件。类似散头文件，通过一个头文件映射一组头文件。

swift的framework默认创建了一个散头文件module.modulemap。



OC调swift通过 -Swift.h文件。把swift代码翻译了头文件。编译的时候放到macho中变成OC符号。
