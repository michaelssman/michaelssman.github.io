# CocoaPods原理

![image-20210918142536466](CocoaPods原理.assets/image-20210918142536466.png)

## 使用pod search搜索不到时

删除`/Users/用户名/Library/Caches/CocoaPods`下的`search_index.json`检索索引文件，然后pod search就会重新生成最新的。就可以搜索到自己刚才的库。

pod search 的时候就是在search_index.json中查找的。

使用的时候要在Podfile文件中添加source指定源地址。

## 远程spec索引库

使用的时候 pod setup**更新本地索引库**，把远程索引库pod到本地。

## 本地spec索引库

本地索引库地址：/Users/用户名/.cocoapods/repos。里面有master、trunk、cocoapods、清华镜像等，master是github上的索引。

向cocoapods上面上传代码和拉取代码。

`pod search AFNetworking`就是在`.cocoapods/repos`本地资源库找到索引`AFNetworking.podspec.json`。

本地索引库里面很多.spec文件，pod search搜索到时候不是直接在本地索引库查找的，有一个检索的索引文件json格式的。键值对。找到之后根据.spec中的框架地址，从github下载源码。不是直接从github上找并下载的。

项目里面有一个podfile，根据podfile查找。podfile会在github上找源码 根据GitHub远程索引库（里面有很多索引文件.spec文件，不是源码）。

## 抽成本地库

先抽成本地的，本地的私有索引库。然后提交远程。

### 1、cd到本地文件夹

### 2、`pod lib create GroupShadowTableView`，创建模版

Cloning `https://github.com/CocoaPods/pod-template.git` into `GroupShadowTableView`.从github上面clone一个pod模版，创建仓库。

模版执行完之后，下面就是一些配置。

- What platform do you want to use?? [ iOS / macOS ] 选择iOS
- What language do you want to use?? [ Swift / ObjC ] 输入语言swift/Objc 
- Would you like to include a demo application with your library? [ Yes / No ]是否包含demo 选择Yes
- Which testing frameworks will you use? [ Quick / None ] 测试framework 选None 选其它的会创建其它的模版，和测试框架有关
- Would you like to do view based testing? [ Yes / No ] 基础测试文件 选No
- What is your class prefix? 选择文件前缀  自己定义HH

然后就创建好了，项目会自动打开。里面自动有一个.podspec文件。因为前面选择 了Yes，所以里面有`Delegate`和`Viewcontroller`方便测试。

### 3、拖入文件

Xcode项目中Pods里面的Development Pods的文件夹下有一个GroupShadowTableView文件夹，也就是`ReplaceMe.m`文件所在的位置，在/Lib/GroupShadowTableView/GroupShadowTableView/Classes文件夹中放自己抽取的代码。再把ReplaceMe.m文件删除。

**一定要记得pod install** 不然Development Pods文件夹下没有文件，本地无法使用。

### 4、把依赖的其它第三方引入

`Pods/Development Pods/自己代码文件夹/Pod/.podspec`文件，添加需要的第三方：

```ruby
  s.dependency 'AFNetworking'
  s.dependency 'LGMacroAndCategoryModule'//自己写的也可以引入

  s.prefix_header_contents = '#import "Masonry.h"','#import "UIKit+AFNetworking.h"','#import "LGMacros.h"'
```

**每次修改都需要`pod install`。**

### 5、创建HHSpecs远程索引库

创建https://github.com/michaelssman/HHSpecs.git管理库，创建库文件夹HHUtils，里面创建文件夹0.1.0（tag标签），复制`/Users/michael/Documents/HHLib/HHUtils/Example/Pods/Local Podspecs/HHUtils.podspec.json`文件到文件夹。

### 注

Developer Pods放本地库文件，还未提交远程之前，提交远程之后使用远程库，会删除Developer Pods文件夹下的本地库文件

## Podfile

```ruby
use_frameworks!

platform :ios, '9.0'

target 'LGCommonUIModule_Example' do
  pod 'LGCommonUIModule', :path => '../'
  pod 'LGMacroAndCategoryModule', :path => '../../LGMacroAndCategoryModule'	//本地库
end
```

可以在其它项目中pod刚才做好的本地库，进行使用。

需要在Podfile文件指定路径，Podfile文件里面pod 'GroupShadowTableView', :path => '../'。

`:path`：指定的是本地路径。

`../`：上级文件夹路径。路径是相对于Podfile的路径。

`./`：当前文件夹路径

## 图片资源文件

代码放在Classes文件夹中，图片放在Assets文件夹中

```swift
// 如果你使用了 resource_bundles，加载图片需要使用bundle
@inline(__always)
public func bundleImage(_ imageName: String) -> UIImage {
	  //可以使用组件中的任意一个类来获取 Bundle。
	  //组件中的类是 internal 或 private，需要在主项目中使用时将其改为 public。
    let bundleURL = Bundle(for: pod中的任意类.self).url(forResource: "YourPodName", withExtension: "bundle")!
    let resourceBundle = Bundle(url: bundleURL)!
    return UIImage(named: imageName, in: resourceBundle, compatibleWith: nil) ?? UIImage()
}
```

同时还需要修改Pods/Development Pods/自己代码文件夹/Pod/.podspec文件下的resource_bundles

```ruby
s.resource_bundles = {
    'YourPodName' => ['YourPodName/Assets/*/*.{png,jpeg,jpg,imageset}']
}
```

json文件、xib同样需要配置bundle。

```objective-c
    NSString *bundlePath = [[NSBundle bundleForClass:[self class]].resourcePath stringByAppendingPathComponent:@"/LGHomeModule.bundle"];
    NSString *path = [[NSBundle bundleWithPath:bundlePath] pathForResource:[NSString stringWithFormat:@"Home_TableView_Response_%@", channelId] ofType:@"json"];
```

## 做成远程的

使用码云或者github等，创建一个仓库，仓库名必须跟框架名一样，选择导入已有项目，然后创建。

cd本地仓库文件夹

git remote add origin https://github.com/michael/GroupShadowTableView.git 后面的https地址是github当前仓库地址。
git push -u origin master。提交到远程master（分支名称）。

## .spec

要找远程索引库，向远程索引库提交.spec文件，根据.spec文件中地址找框架源码。本地索引库也有.spec文件，里面也有远程地址。
所以就要修改.spec文件。

```ruby
Pod::Spec.new do |s|
	# 框架名称
  s.name             = 'HHTableListViewController'
  # 版本号
  s.version          = '0.2.0'
  # 描述
  s.summary          = '封装tableView基类'

# This description is used to generate tags and improve search results.
#   * Think: What does it do? Why did you write it? What is the focus?
#   * Try to keep it short, snappy and to the point.
#   * Write the description between the DESC delimiters below.
#   * Finally, don't worry about the indent, CocoaPods strips it!

	# 可以修改也可以不改
  s.description      = '封装tableView基类 刷新自动加载更多'

	# 主页地址，远程库的地址。（如果是私有的，地址只需要写到自己的github地址，不需要写项目具体地址）
  s.homepage         = 'https://github.com/michael/HHTableListViewController'
  # s.screenshots     = 'www.example.com/screenshots_1', 'www.example.com/screenshots_2'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.author           = { '88888888@qq.com' => '88888888@qq.com' }
  
  # s.social_media_url = 'https://twitter.com/<TWITTER_USERNAME>'

  s.ios.deployment_target = '13.0'
  # s.swift_versions        = ['5.0', '5.1', '5.2']
  # 支持混合语言配置
  s.pod_target_xcconfig = {
    'DEFINES_MODULE' => 'YES',
    'SWIFT_VERSION' => '5.0'
  }

  # 重要：框架源码地址。找框架源码的时候就是根据这个找的。这个地址错了就找不到了，可以直接复制仓库地址。
  s.source           = { :git => 'https://github.com/michael/HHTableListViewController.git', :tag => s.version.to_s }
	# 源代码文件（哪些文件是需要的，根据这个去找）。/**/* 代表 ：所有文件，文件夹中的所有文件。
  s.source_files = 'HHTableListViewController/Classes/**/*' # 找的Classes下的文件
  # pch头文件地址
  s.prefix_header_file = ".pch"

  # 资源文件位置
  s.resource_bundles = {
    'HHTableListViewController' => ['HHTableListViewController/Assets/*.{png,jpeg,jpg,imageset}']
  }

  # 如果需要桥接文件
  s.prefix_header_contents = <<-EOS
    #ifdef __OBJC__
      #import "LMBaseModule-Bridging-Header.h"
    #endif
  EOS
  
  # s.public_header_files = 'Pod/Classes/**/*.h'
  # s.frameworks = 'UIKit', 'MapKit'

  # 添加第三方依赖
  s.dependency 'AFNetworking', '~> 4.0'
  s.dependency 'MJRefresh'
  s.dependency 'Masonry'
end
```

把spec文件提交
提交到本地。

终端打印`pod repo`，master显示github上的源地址.

如果用的是码云或者是其它的源地址，要在podfile文件中指定source，写上source ‘https://gifted.com/michael/Spec.git’ 在这里面找。
另外还要有source ‘https://github.com/CocoaPods/Specs.git’ 因为还有其他的第三方在github上。

## 提交

pod repo HHSpec HHGroupShadowTableView.podspec

pod repo 不成功，因为pod库有一个版本号，github上需要打标签。标签tag要和.podspec中的版本号一致。

## 提交到远程spec库

先cd进入当前文件夹

### 检查是否出错

pod spec lint

### 1、推到cocoapod上

pod trunk register 88888888@qq.com 'michael' --description='michaelPro'。注册账号。

pod trunk push HHGroupShadowTableView.podspec --allow-warnings。如果有警告的话 需要在后面添加--allow-warnings去ignore警告。

### 2、推到master上

pod master push HHGroupShadowTableView.podspec --allow-warnings

### 3、提交到自己的私有仓库

在github上创建一个仓库HHSpecs 来管理自己的共有和私有库。

pod repo add HHSpecs https://github.com/michael/HHGroupShadowTableView.git

pod repo push HHSpecs HHGroupShadowTableView.podspec --allow-warnings

提交 pod repo push HHSpec HHTools.podspec，提交的时候会验证.spec本地索引库是否写对。

如果引用其它第三方可能提交不上去，就不使用pod repo push这个指令提交，改为直接复制一个其它的本地索引库文件，然后改一下名字，版本，描述等等，修改.podspec文件。

## 移除本版本

pod trunk delete HHGroupShadowTableView 0.1.0（即：pod trunk delete 库名 版本号）

## Objective-C项目使用Swift库

在 Swift 语言创建的 Pod 库要在 Objective-C 项目中使用时，需要确保几个步骤已经正确完成：

### 1、确保 Pod 支持 Objective-C

使用 `@objc` 关键字来标记那些需要在 Objective-C 中使用的类和方法。

### 2、创建Objective-C和Swift的桥接文件（如果你的项目中还没有）

Swift 项目在构建时会自动生成一个名为 `YourProjectName-Swift.h` 的桥接头文件，用于在 Objective-C 中暴露 Swift 代码。在 Objective-C 项目中，你需要导入这个桥接头文件才能使用 Swift 代码。

- 在Xcode中，尝试创建一个新的Swift文件，Xcode会询问你是否要创建一个桥接头文件。
- 点击“Create Bridging Header”。
- 在桥接头文件中，你不需要导入Alamofire，因为它是通过模块导入的。

### 3、更新 Podspec 文件

确保你的 `.podspec` 文件正确配置了 `s.public_header_files`，以便在安装 Pod 时，能够将 Swift 生成的头文件包含在内。

### 4、使用 use_frameworks!

在你的 Objective-C 项目的 Podfile 中，确保你使用了 `use_frameworks!` 选项，因为 Swift 库需要作为框架来被集成。

```ruby
platform :ios, '10.0'

target 'YourTargetName' do
  use_frameworks!
  pod 'Alamofire', '~> 5.0'
end
```

### 5、在Objective-C中导入

由于Alamofire是一个模块，你可以在Objective-C文件中使用`@import`语句来导入Swift**模块**。

```objc
@import Alamofire;
```

或者，如果你在项目设置中关闭了模块支持，可以使用生成的Swift头文件：

```objc
#import <YourProjectName-Swift.h>
```

其中`YourProjectName`是你的项目名称。如果你的项目名称包含空格或其他特殊字符，它们会被下划线替换。

### 6、调用Alamofire

- 由于Alamofire是纯Swift编写的，为了在Objective-C中使用Alamofire，你可能需要编写一些Swift代码来封装你想要使用的Alamofire功能，然后将这个封装暴露给Objective-C。这通常是通过在Swift类中使用`@objc`标记来实现的。

例如，你可能需要创建一个Swift类来处理网络请求，然后在这个类中使用`@objc`标记来暴露给Objective-C可以理解的方法。

```swift
import Alamofire

@objc class NetworkManager: NSObject {
    @objc func fetchURL(url: String, completion: @escaping (String) -> Void) {
        AF.request(url).response { response in
            if let data = response.data, let utf8Text = String(data: data, encoding: .utf8) {
                completion(utf8Text)
            }
        }
    }
}
```

然后在Objective-C中使用这个封装：

```objc
NetworkManager *manager = [[NetworkManager alloc] init];
[manager fetchURL:@"https://api.example.com" completion:^(NSString *result) {
    NSLog(@"Result: %@", result);
}];
```

### Swift编写的pod库 依赖于 `MJRefresh`，但是 `MJRefresh` 并没有定义模块。

在Swift中，为了能够从静态库中导入没有模块定义的依赖项，需要生成模块映射（module maps）。模块映射是Swift和Objective-C之间互操作的一种机制，它允许Swift代码导入并使用Objective-C代码。

有两种方法可以解决这个问题：

1. 全局设置 `use_modular_headers!` 在你的Podfile中：
   这将为所有的依赖项启用模块化头文件。你可以在Podfile的顶部添加这一行来实现。

   ```ruby
   use_modular_headers!
   ```

2. 为特定的依赖项设置 `:modular_headers => true`：
   如果不想对所有的依赖项使用模块化头文件，可以只为特定的依赖项设置。在Podfile中，找到相关的依赖项，然后添加 `:modular_headers => true` 选项。

   ```ruby
   pod 'MJRefresh', :modular_headers => true
   ```
