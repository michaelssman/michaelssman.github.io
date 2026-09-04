# CocoaPods 原理与私有组件发布

本文以 `PWUtils` 源码仓库和 `PWSpecs` Specs 仓库为例，说明 CocoaPods 的核心
解析模型，以及组件的本地开发、发布和接入流程。

## 一、核心解析模型

CocoaPods 按以下链路安装组件：

```text
Podfile
  -> Specs Source
  -> 选择名称和版本匹配的 Podspec
  -> 根据 Podspec 的 source 和 tag 下载源码
  -> 解析源码、资源和依赖
  -> 生成 Pods 工程
  -> 写入 Podfile.lock
```

核心文件和仓库的职责：

| 对象 | 职责 |
| --- | --- |
| `Podfile` | 声明依赖、Specs Source、平台版本和集成方式 |
| `Podspec` | 描述组件版本、源码地址、文件范围、资源和依赖 |
| 源码仓库 | 保存组件源码，并通过 Git tag 固定发布版本 |
| Specs 仓库 | 保存 Podspec 索引，不保存组件源码 |
| `Podfile.lock` | 固定解析版本和 Specs 来源，保证开发机与 CI 结果一致 |

使用私有 Specs 时，在 `Podfile` 顶部同时声明私有源和官方 CDN：

```ruby
source 'https://github.com/michaelssman/PWSpecs.git'
source 'https://cdn.cocoapods.org/'
```

Source 顺序会影响同名 Pod 的解析结果，因此私有源放在官方 CDN 前面。

## 二、PWUtils 与 PWSpecs

当前仓库关系：

```text
PWUtils
  - 私有源码仓库
  - 保存组件源码和 PWUtils.podspec
  - 使用 Git tag 固定发布版本

PWSpecs
  - 可公开读取的 Specs 仓库
  - 保存 PWUtils/<version>/PWUtils.podspec.json

消费项目
  - 从 PWSpecs 解析 PWUtils 的版本和 Podspec
  - 通过 SSH 下载 PWUtils 对应 tag 的源码
```

以 `0.5.4` 为例，PWSpecs 中的目录结构为：

```text
PWSpecs/
└── PWUtils/
    └── 0.5.4/
        └── PWUtils.podspec.json
```

开发机和 CI 需要具备 `git@github.com:michaelssman/PWUtils.git` 的 SSH 读取权限。

## 三、本地组件开发

Example 工程通过 Development Pod 引用仓库根目录：

```ruby
target 'PWUtils_Example' do
  pod 'PWUtils', :path => '../'
end
```

`:path` 相对于 `Example/Podfile`。修改源码后可以直接构建；Podspec、源码文件列表
或资源列表发生变化时，重新安装依赖：

```shell
cd Example
pod install
```

本地开发的权威文件是：

- `PWUtils.podspec`
- `PWUtils/Classes/`
- `PWUtils/Assets/`

`Example/Pods/Local Podspecs/`、`Pods.xcodeproj` 和
`Pods/Target Support Files/` 均由 CocoaPods 生成。

## 四、Podspec

PWUtils 当前 Podspec 的核心配置：

```ruby
Pod::Spec.new do |s|
  s.name             = 'PWUtils'
  s.version          = '0.5.4'
  s.summary          = 'Reusable Swift and Objective-C utilities and UIKit components for iOS.'
  s.description      = <<-DESC
    PWUtils is an iOS component library written in Swift and Objective-C.
    It provides reusable networking, persistence, UIKit, photo selection,
    diagnostics, runtime, and Foundation utilities for application projects.
  DESC

  s.homepage = 'https://github.com/michaelssman/PWUtils'
  s.license  = { :type => 'MIT', :file => 'LICENSE' }
  s.author   = { 'michael' => 'michael' }
  s.source   = {
    :git => 'git@github.com:michaelssman/PWUtils.git',
    :tag => s.version.to_s
  }

  s.ios.deployment_target = '12.0'
  s.swift_versions        = ['5.0']
  s.requires_arc          = true

  s.source_files = 'PWUtils/Classes/**/*.{h,m,swift}'
  s.resource_bundles = {
    'PWUtils' => ['PWUtils/Assets/*/*.{png,jpeg,jpg,imageset}']
  }

  s.dependency 'Alamofire', '5.10.2'
  s.dependency 'RxSwift', '6.5.0'
  s.dependency 'RxCocoa', '6.5.0'
  s.dependency 'SnapKit', '5.6.0'
  s.dependency 'MBProgressHUD', '1.2.0'
  s.dependency 'MJRefresh'
  s.dependency 'FMDB'
end
```

关键约束：

- `s.version`、Git tag 和 Specs 版本目录保持一致。
- `s.source_files` 只匹配需要参与编译的源码。
- `s.resource_bundles` 覆盖组件使用的全部资源。
- `s.swift_versions` 声明支持的 Swift 语言模式。
- 依赖版本结合兼容范围和可重复构建要求确定。

### 资源读取

资源安装后位于 `PWUtils.bundle`，运行时从组件 Bundle 定位：

```swift
import UIKit

private final class PWUtilsBundleToken {}

public func pwImage(named name: String) -> UIImage? {
    let frameworkBundle = Bundle(for: PWUtilsBundleToken.self)
    let resourceBundle = frameworkBundle
        .url(forResource: "PWUtils", withExtension: "bundle")
        .flatMap(Bundle.init(url:)) ?? frameworkBundle

    return UIImage(named: name, in: resourceBundle, compatibleWith: nil)
}
```

JSON、XIB、Storyboard 和字体采用相同的 Bundle 定位方式。

## 五、消费项目接入

推荐 Podfile：

```ruby
source 'https://github.com/michaelssman/PWSpecs.git'
source 'https://cdn.cocoapods.org/'

platform :ios, '12.0'
use_modular_headers!

target 'YourApp' do
  pod 'PWUtils', '~> 0.5.4'
end
```

PWUtils 包含 Swift 与 Objective-C 代码，并依赖 FMDB、MJRefresh、MBProgressHUD
等 Objective-C Pod。静态库集成使用 `use_modular_headers!` 为依赖生成模块映射。
需要 Framework 集成的项目可以使用 `use_frameworks!`。

首次安装或需要更新 Specs 时执行：

```shell
pod install --repo-update
```

普通安装执行 `pod install`；需要重新解析 PWUtils 版本时执行：

```shell
pod update PWUtils
```

应用项目提交 `Podfile.lock`。其中的 `SPEC REPOS` 可以确认 PWUtils 来自 PWSpecs：

```yaml
SPEC REPOS:
  https://github.com/michaelssman/PWSpecs.git:
    - PWUtils
```

## 六、发布 PWUtils

发布顺序为：更新 Podspec、本地验证、推送源码 tag、远端 lint、推送 Spec、消费端
验收。

### 1. 更新 Podspec

修改 `s.version`、依赖、源码范围和资源配置，并查看 CocoaPods 的解析结果：

```shell
pod ipc spec PWUtils.podspec
```

### 2. 本地 lint

```shell
pod lib lint PWUtils.podspec \
  --private \
  --allow-warnings \
  --use-libraries \
  --use-modular-headers
```

### 3. 验证 Example

```shell
cd Example
pod install
cd ..

xcodebuild \
  -workspace Example/PWUtils.xcworkspace \
  -scheme PWUtils-Example \
  -configuration Debug \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO \
  build
```

### 4. 提交源码并创建 tag

以 `0.5.4` 为例：

```shell
git add PWUtils.podspec PWUtils README.md Example/Podfile Example/Podfile.lock
git commit -m 'chore(release): prepare PWUtils 0.5.4'
git pull --rebase origin main

git tag -a 0.5.4 -m 'PWUtils 0.5.4'
git push origin main
git push origin 0.5.4
```

### 5. 远端 lint

`pod spec lint` 按 Podspec 的 `source` 和 `tag` 下载远端源码：

```shell
pod spec lint PWUtils.podspec \
  --private \
  --allow-warnings \
  --use-libraries \
  --use-modular-headers \
  --sources=https://cdn.cocoapods.org/
```

### 6. 注册 PWSpecs

每台发布机器注册一次：

```shell
pod repo add PWSpecs https://github.com/michaelssman/PWSpecs.git
```

### 7. 推送 Spec

```shell
pod repo push PWSpecs PWUtils.podspec \
  --use-json \
  --no-overwrite \
  --allow-warnings \
  --use-libraries \
  --use-modular-headers \
  --sources=https://cdn.cocoapods.org/
```

发布版本由不可变的 version、tag 和 Spec 组成。修复内容通过新的语义化版本发布。

## 七、发布验收

验证 Specs 仓库：

```shell
pod repo lint PWSpecs
```

在不配置 `:path` 的空白项目中使用“消费项目接入”一节的 Podfile，然后执行：

```shell
pod install --repo-update
```

验收结果应同时满足：

- 安装到预期的 PWUtils 版本。
- `Podfile.lock` 显示 PWUtils 来自 PWSpecs。
- 能通过 SSH 下载 tag 对应的源码。
- 应用工程和 Example 工程均可构建。
- 开发机与 CI 的安装结果一致。

## 八、Swift 与 Objective-C 互操作

PWUtils 是 Swift 与 Objective-C 混编组件：

- 暴露给 Objective-C 的 Swift 类型继承 `NSObject`，并使用 `@objc` 或
  `@objcMembers` 标记可见 API。
- Objective-C 调用方通过 `@import PWUtils;` 或
  `#import <PWUtils/PWUtils-Swift.h>` 导入 Swift API。
- `PWUtils-Swift.h` 由编译器生成，不属于 Podspec 的公开头文件列表。
- 混编 Pod 使用模块和公开头文件互操作，不配置应用 target 的 Bridging Header。

## 九、发布检查清单

- [ ] Podspec 的名称、版本、source 和 tag 一致。
- [ ] deployment target、Swift 版本、源码范围和资源配置正确。
- [ ] `pod lib lint` 通过。
- [ ] Example 安装依赖并构建成功。
- [ ] 源码提交和 tag 已推送到远端。
- [ ] `pod spec lint` 从远端 tag 验证通过。
- [ ] Spec 已推送到 PWSpecs。
- [ ] `pod repo lint PWSpecs` 通过。
- [ ] 空白消费项目能够安装并构建。
- [ ] `Podfile.lock` 中的版本与 Specs 来源正确。

## 参考资料

- [CocoaPods Private Pods](https://guides.cocoapods.org/making/private-cocoapods.html)
- [CocoaPods Podfile Syntax](https://guides.cocoapods.org/syntax/podfile.html)
- [CocoaPods Podspec Syntax](https://guides.cocoapods.org/syntax/podspec.html)
- [CocoaPods Command-line Reference](https://guides.cocoapods.org/terminal/commands.html)
