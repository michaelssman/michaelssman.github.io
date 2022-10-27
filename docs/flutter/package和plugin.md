# package和plugin

## package包

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

相册可以做一个plugin，iOS、android。例：image_picker。

注：需要在XCode中info.plist配置权限。

使用的第三方的话需要在XCode中pod install。原生中也会有代码。

## 包和插件（plugin）区别

是否包含原生代码

插件plugin不仅包含dart代码，自带example，还包含android和iOS代码，example里的iOS可以写代码。

plugin上传和package一样