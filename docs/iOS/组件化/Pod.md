# Pod

## 使用brew安装cocoapods

brew install cocoapods

## sudo gem install cocoapods --pre

更新Cocoapods

## pod init

初始化pod

## pod install

每当更新Podfile去新添加或删除或更新某个或某些pod时，使用pod install。

每次你运行pod install的时候，都会在Podfile.lock文件里写入你安装的pod的版本号。这个文件会锁定你安装的pod的版本。

运行pod install时，Cocoapods只会按照Podfile.lock中列出的版本号来安装对应版本的pod；对于Podfile.lock文件中未列出的，Cocoapods会根据Podfile中的描述（pod ‘xxx’, '～1.0' ）去安装相应的版本。

pod install 命令功能：

1. 安装并显示Podfile指定的第三方库以及对应的版本号，
   当然，如果Podfile删除了某个库，执行pod install 命令的时候也会删除对应的库。
   命令执行完毕后，新增的库会绿色显示，删除的话会红色显示。
2. 显示项目中安装的第三方库对应的名字和版本号。如果之前已经安装过了某个第三方库，则只显示库的名字和版本号，不进行更新操作。

注意：从CocoaPods 1.0开始，默认情况下`pod install`不会发生`pod repo update`。

### pod install --no-repo-update

`pod install --no-repo-update`，删除某一个库的时候，可能删除不干净，需要在后面添加`--no-repo-update`

### pod install --repo-update

`pod install --repo-update`安装并更新库。本地仓库repo里面可能没有想要安装的库，需要从远端更新这个库。

## pod update

更新pod的所有库。

`pod update *podname*`：更新某个pod至最新版本。

`pod update`：更新所有Podfile中的pod。

update命令并不会理会Podfile.lock中的版本信息（新版本仍然遵守在Podfile中做的限制）。

所以，正确的用法是，当你往Podfile中添加了一个pod，记得用pod install；只有当你确定要更新某个或全部pod时，使用pod update。

`pod update --no-repo-update`

注：不建议加入--no-repo-update 参数，若添加后仅从本地Cocoapods库中查找SDK，不再更新线上SDK。如果本地存在SDK会直接使用本地SDK版本(不是线上最新版本)，若本地不存在SDK会产生错误。 也不建议使用 pod install 命令，此命令不会更新最新版本SDK。

## pod outdated

可以使用pod outdated命令来查看有哪些pod有了更新的版本。这个命令会检查Podfile.lock中列出的pod的版本。

## pod repo list

查看源。有多个

## pod repo remove trunk

移除trunk（主干）这个

## pod repo update

`pod repo update master` 升级本机过时的 pod 库。

## 添加私有仓库spec

终端 直接clone仓库到文件

```
git clone https://github.com/CocoaPods/Specs.git ~/.cocoapods/repos/trunk
git clone https://mirrors.tuna.tsinghua.edu.cn/git/CocoaPods/Specs.git ~/.cocoapods/repos/trunk
```

或者执行命令

```
pod repo add showself-spec http://192.168.84.67/ios/lib/showself_pods_spec.git

pod repo add scienjoyspecs http://192.168.84.67/ios/github/scienjoyspecs.git
```

注意：

需要让运维在`gitlab`对应的仓库给自己加上权限。

## 设置源

**在Podfile开头处添加源：**

```
source 'https://github.com/CocoaPods/Specs.git'
source 'https://github.com/huicuihui/HHSpecs.git'

自有库
source 'http://192.168.84.67/ios/lib/showself_pods_spec.git'

github 库
source 'http://192.168.84.67/ios/github/scienjoyspecs.git'
```
