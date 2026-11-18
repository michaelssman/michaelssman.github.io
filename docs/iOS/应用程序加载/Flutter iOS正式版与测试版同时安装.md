# Flutter iOS 正式版与测试版同时安装

## 1. 当前配置与数据边界

| 项目 | 正式版 | 测试版 |
| --- | --- | --- |
| Flutter flavor / Xcode Scheme | `prod` | `beta` |
| Bundle Identifier | `com.m.jizhang.www` | `com.m.jizhang.www.test` |
| 桌面显示名 | 小木记账 | 小木记账测试 |
| 环境配置文件 | `ios/Flutter/Prod.xcconfig` | `ios/Flutter/Beta.xcconfig` |

两个 Scheme 共用 `Runner` Target 和业务代码，工程只保留带环境后缀的六套构建配置。运行和打包必须通过 `--flavor prod` 或 `--flavor beta` 明确选择环境；在 Xcode 中选择同名 Scheme。

**当前两个 flavor 未自动切换后端。** 未传入 `API_BASE_URL` 时，都使用项目的默认接口。用相同账号访问同一后端，仍会访问同一份云端数据；测试 App 的安装隔离不能保护服务端数据。需要隔离云端测试时，先准备独立测试后端，再按第 5 节传入地址。

保留正式版的 Bundle Identifier，可以继续更新已有 App；不要为了测试临时修改正式版标识，也不要通过卸载正式版清理测试问题。

## 2. 在 Xcode 中配置两套环境

当前工程已经配置完成。以下步骤用于理解配置关系，或在另一个 Flutter 项目中建立相同结构。

先打开工作区：

```sh
open "ios/Runner.xcworkspace"
```

### 创建 Configuration 和 Scheme

在 Xcode 左侧选择 `Runner` Project，打开 **Info → Configurations**，从已有的 Debug、Profile、Release 分别复制环境配置。保持编译模式前缀，flavor 后缀使用小写：

| Scheme | Run / Test / Analyze | Profile | Archive |
| --- | --- | --- | --- |
| `prod` | `Debug-prod` | `Profile-prod` | `Release-prod` |
| `beta` | `Debug-beta` | `Profile-beta` | `Release-beta` |

在 **Product → Scheme → Manage Schemes** 中创建 `prod`、`beta`，Target 均选择 `Runner`，勾选 **Shared**，并按表格设置各操作的 Build Configuration。共享 Scheme 文件应纳入 Git，其他电脑和 Flutter 命令才能使用。

`beta/prod` 决定 App 身份；`Debug/Profile/Release` 决定编译模式。测试版可以使用 Release，正式版也可以使用 Debug 调试。`--flavor beta --release` 对应 `beta` Scheme 下的 `Release-beta`。[Flutter iOS flavors 指南](https://docs.flutter.dev/deployment/flavors-ios)

### 集中设置标识和显示名

`ios/Flutter/Prod.xcconfig`：

```xcconfig
APP_BUNDLE_IDENTIFIER = com.m.jizhang.www
PRODUCT_BUNDLE_IDENTIFIER = $(APP_BUNDLE_IDENTIFIER)
APP_DISPLAY_NAME = 小木记账
```

`ios/Flutter/Beta.xcconfig`：

```xcconfig
APP_BUNDLE_IDENTIFIER = com.m.jizhang.www.test
PRODUCT_BUNDLE_IDENTIFIER = $(APP_BUNDLE_IDENTIFIER)
APP_DISPLAY_NAME = 小木记账测试
```

`APP_BUNDLE_IDENTIFIER` 只定义主 App 的身份，再映射给 Xcode 的 `PRODUCT_BUNDLE_IDENTIFIER`。自动化可以覆盖前者，不必改写环境配置，也不会将同一个标识应用到所有 Pods。

`Runner/Info.plist` 中的 `CFBundleIdentifier` 使用 `$(PRODUCT_BUNDLE_IDENTIFIER)`，`CFBundleDisplayName` 使用 `$(APP_DISPLAY_NAME)`。`PRODUCT_NAME` 与可执行文件名保持原值，不必为两个 App 复制 Target 或改动代码引用。

### 连接配置文件

本工程为六个环境配置分别提供入口，例如 `ios/Flutter/Debug-beta.xcconfig`：

```xcconfig
#include? "Pods/Target Support Files/Pods-Runner/Pods-Runner.debug-beta.xcconfig"
#include "Generated.xcconfig"
#include "Beta.xcconfig"
```

其他五个入口按对应的模式和环境加载 Pods 配置及 `Prod.xcconfig` / `Beta.xcconfig`。在 Xcode 的 Configurations 中，将 Runner 的每个环境配置关联到相应 Flutter 配置入口。

`ios/Flutter/` 共保留九个 `.xcconfig` 文件：

| 类型 | 文件 | 维护方式 |
| --- | --- | --- |
| 环境身份 | `Prod.xcconfig`、`Beta.xcconfig` | 修改 App 标识和名称时维护 |
| 构建入口 | `Debug-prod`、`Profile-prod`、`Release-prod`、`Debug-beta`、`Profile-beta`、`Release-beta` | 各自加载对应 Pods 和环境配置 |
| 自动生成 | `Generated.xcconfig` | 由 Flutter 生成，不手工编辑 |

Xcode 的 `Flutter` 组内用 `Environments` 收纳两份环境配置，用 `Build Configurations` 收纳六个构建入口；它们只是项目导航分组，文件仍位于 `ios/Flutter/`。

检查 Xcode Build Settings 中是否存在硬编码覆盖；当前 Runner 的 `PRODUCT_BUNDLE_IDENTIFIER` 使用继承值，由环境配置决定。在新项目中建立上述结构时，完成 Scheme、Runner 和测试 Target 的配置关联后，移除不再引用的无后缀构建配置、原 `Runner` Scheme 及对应配置文件，避免维护重复入口。

## 3. 同步 CocoaPods 与签名

### CocoaPods

`ios/Podfile` 的 `project 'Runner'` 映射只维护六个环境配置；`Debug-prod`、`Debug-beta` 映射到 `:debug`，其余 Profile、Release 配置映射到 `:release`。修改后执行：

```sh
flutter pub get
(cd ios && pod install)
```

继续使用 `.xcworkspace` 打开工程。不要直接修改 `Pods/` 中的生成配置。

### 真机签名

在 Runner 的 **Signing & Capabilities** 中检查 Team 和自动签名设置，并分别检查正式、测试配置的 Bundle Identifier。新测试标识需要由当前开发团队注册和签名；使用手动签名时，为其创建或选择匹配的描述文件。已存在的正式标识继续使用原团队，避免误改签名归属。[Apple App ID 注册步骤](https://developer.apple.com/help/account/identifiers/register-an-app-id/)

本地真机调试不要求先创建 App Store Connect 应用记录；若两款 App 都通过 TestFlight 分发，则各自需要匹配 Bundle Identifier 的应用记录。TestFlight 是分发方式，不会自动创建独立 App 身份或切换后端。[Apple 分发准备说明](https://developer.apple.com/documentation/xcode/preparing-your-app-for-distribution)

本工程已有 JPush 集成，本次环境拆分未更换其原生配置，也未替两个 App 开通 APNs。正式版和测试版的远程推送需分别核验 App ID 能力、描述文件及推送平台配置，不能仅凭编译成功认定推送可用。本地还款提醒不依赖 APNs，但仍需要系统通知授权。

## 4. 日常运行与打包

先用 `flutter devices` 获取设备 ID，将下方 `<设备ID>` 替换为真实值。

```sh
# 正式版：Release 模式，安装后可从桌面独立打开
flutter run --flavor prod --release --no-resident -d <设备ID>

# 测试版：同样使用 Release，作为独立 App 安装
flutter run --flavor beta --release --no-resident -d <设备ID>

# 测试版：连接 Flutter 调试工具运行
flutter run --flavor beta --debug -d <设备ID>
```

`--no-resident` 适用于安装启动后退出 Flutter 工具的场景。需要断点或热重载时使用 Debug 命令，并保持工具连接。

需要生成 IPA 时：

```sh
flutter build ipa --flavor prod --release
flutter build ipa --flavor beta --release
```

IPA 导出仍需符合分发方式的签名和描述文件；执行构建命令不代表已上传 TestFlight。分发步骤见[多环境支持](多环境支持.md)。不要依靠产物文件名判断环境，发布前核对 App 内的实际 Bundle Identifier；构建下一个环境前保存上一份需分发的产物。

在 Xcode 中也可从顶部选择 `prod` / `beta` Scheme 再 Run；新 Scheme 的 Run 默认是 Debug。要从 Xcode 安装可脱离工具启动的测试包，在 Edit Scheme 中将该次 Run 配置改为对应的 `Release-beta`；长期保留的默认设置以工程约定为准。

### 自动化测试的独立身份

真机 XCTest 自动化复用 `beta` Scheme 和 `Release-beta` 配置，但使用独立 Bundle Identifier `com.m.jizhang.www.automation`，避免写入手动测试 App 或正式 App 的本机账本。它不需要额外的 Scheme 或 `.xcconfig` 文件。

Flutter 测试构建传入 `--flavor beta`，并通过进程环境变量 `FLUTTER_XCODE_APP_BUNDLE_IDENTIFIER=com.m.jizhang.www.automation` 覆盖身份；后续 `xcodebuild test` 同时指定 `-scheme beta -configuration Release-beta` 和 `APP_BUNDLE_IDENTIFIER=com.m.jizhang.www.automation`。不要直接用命令行覆盖 `PRODUCT_BUNDLE_IDENTIFIER`，该设置会同时作用于依赖目标。模拟器的 Flutter 集成测试也传入 `--flavor beta` 和独立标识，使用 Debug 模式。完整测试入口和数据清理边界以项目 README 的设备自动化章节为准。

## 5. 指定独立后端

本工程在 Dart 的 `lib/core/config/api_config.dart` 中读取构建参数 `API_BASE_URL`。此参数与 Bundle Identifier 分开控制；接口地址不是密码，但 Token、私钥等凭据不能通过构建常量写入 App。

下面地址仅为占位示例，需替换为已部署且满足项目 HTTPS 校验要求的真实服务：

```sh
flutter run --flavor beta --release --no-resident -d <设备ID> \
  --dart-define=API_BASE_URL=https://test-api.example.com

flutter build ipa --flavor prod --release \
  --dart-define=API_BASE_URL=https://api.example.com
```

切换后端需要重新构建。使用 Xcode 继续构建时，要检查 Flutter 上一次生成的构建参数；切换 Scheme 本身不会清除或重设 `--dart-define`。建议涉及接口切换时统一通过 Flutter 命令显式传入地址。

## 6. 检查配置与安装结果

不安装到设备即可检查构建设置：

```sh
xcodebuild -workspace ios/Runner.xcworkspace -scheme prod \
  -configuration Release-prod -showBuildSettings \
  | rg 'PRODUCT_BUNDLE_IDENTIFIER =|APP_DISPLAY_NAME ='

xcodebuild -workspace ios/Runner.xcworkspace -scheme beta \
  -configuration Release-beta -showBuildSettings \
  | rg 'PRODUCT_BUNDLE_IDENTIFIER =|APP_DISPLAY_NAME ='
```

输出可能包含依赖 Target，核对 `Runner` 的设置是否与第 1 节一致。无签名验证可用 `flutter build ios --flavor beta --release --no-codesign`，但其产物不能直接作为已签名 App 安装到真机。

配置检查、无签名构建、真机安装和服务功能验收是不同层次；只有实际执行的步骤才能作为验证结果。
