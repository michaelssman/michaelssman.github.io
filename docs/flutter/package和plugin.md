# package和plugin

## package包

package包地址：`pub.dev`

没有android和iOS代码。

发布包在`pubspec.yaml`配置

flutter工程使用的，类似iOS中的pod第三方库。

## 资源

如果有UI的资源时，

## 发布

终端进到package，

1. 检查包

   `flutter packages pub publish --dry-run `

2. 指定服务器发布

   `flutter packages pub publish --server=https://pub.dartlang.org`

## plugin插件

自带example，带有iOS和android

example里的iOS可以写代码。

plugin上传和package一样

相册可以做一个plugin，iOS、android。