# pubspec.yaml

里面的格式，缩进都要对齐。

```yaml
# 项目名称，必填字段，package包名
name: flutter_demo
# 项目描述，非必填字段
description: A new Flutter project.

# 包发布到哪里去 none代表不发布 可以指定发布的服务器位置 默认到pub.dev服务器
publish_to: 'none' # Remove this line if you wish to publish to pub.dev

# 项目的版本号+构建号
version: 1.0.0+1

# dart版本
environment:
  sdk: ">=3.1.3 <4.0.0"

# 三方SDK
dependencies:
  flutter:
    # flutter最新版本
    sdk: flutter
#    #指定版本
#    version:

  # The following adds the Cupertino Icons font to your application.
  # Use with the CupertinoIcons class for iOS style icons.
  cupertino_icons: ^1.0.2
  dio: ^4.0.4 #^表示大版本不变的写法。相当于'>=4.0.4 < 5.0.0'。pub get就会小版本更新
  # dio: 4.0.1 指定4.0.1
  # dio: any 任意版本
  # dio: '>3.0.1' 大于3.0.1（不包含3.0.1）注意：需要加引号
  http: ^0.13.4
  # 本地的包package
  flutter_package:
    path: ../flutter_package

# 开发环境依赖库 调试用的 打包时不会打包进去
dev_dependencies:
  flutter_test:
    sdk: flutter

  # The "flutter_lints" package below contains a set of recommended lints to
  # encourage good coding practices. The lint set provided by the package is
  # activated in the `analysis_options.yaml` file located at the root of your
  # package. See that file for information about deactivating specific lint
  # rules and activating additional ones.
  flutter_lints: ^2.0.0

# For information on the generic Dart part of this file, see the
# following page: https://dart.dev/tools/pub/pubspec

# The following section is specific to Flutter.
flutter:

  uses-material-design: true
  # 设置资源image 字体
  # To add assets to your application, add an assets section, like this:
  assets:
  	 #注意：格式不能错，assets前面多一个空格都不可以。
     - images/
     - images/account_icon/
     - acc/

  # example:
  # fonts:
  #   - family: Schyler
  #     fonts:
  #       - asset: fonts/Schyler-Regular.ttf
  #       - asset: fonts/Schyler-Italic.ttf
  #         style: italic
  #   - family: Trajan Pro
  #     fonts:
  #       - asset: fonts/TrajanPro.ttf
  #       - asset: fonts/TrajanPro_Bold.ttf
  #         weight: 700
  #
  # For details regarding fonts from package dependencies,
  # see https://flutter.dev/custom-fonts/#from-packages
```

## flutter引用外部包

Flutter外部包网站：https://pub.dev/
Flutter使用pubspec文件管理应用程序的assets(资源，如图片、package等)。

引用外部包的方法
在**pubspec.yaml**，添加依赖项，如添加`english_words`包和`http`包

```yaml
dependencies:
  flutter:
    sdk: flutter
  english_words: ^3.1.0
    
  # The following adds the Cupertino Icons font to your application.
  # Use with the CupertinoIcons class for iOS style icons.
  cupertino_icons: ^1.0.2
  http: ^0.13.4  
```

`^`后面表示框架的版本

## 关于import

在您输入时，Android Studio会为您提供有关库导入的建议。然后它将呈现灰色的导入字符串，让您知道导入的库尚未使用（到目前为止）

使用http的时候

- as关键字 给库起别名

​		http里有get请求，其它库可能也有get方法，http.get

​		目的：防止类名方法名称冲突

- 导入库，默认是整个文件中的都会导入

​		show：执行需要导入的内容

​		hide：需要隐藏的内容，不导的内容。

## dart版本兼容

项目/wechat_demo/pubspec.yaml

```
# dart SDK兼容版本
environment:
  sdk: ">=2.12.0 <3.0.0"
```

然后`Pub get`

## Put get

安装依赖，在项目根目录下，执行命令：

```
flutter pub get
```

在`External Libraries`下的` Dart Packages`里面就能看到新导入的包。



iOS还需要`pod install`。