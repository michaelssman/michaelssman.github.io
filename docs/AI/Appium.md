# Appium：自动化测试

第 1～11 节是从零搭建与编写计数器测试的通用教程。**本机已有环境时，直接查看第 12 节，无需重新安装；当前业务真机验收的隧道启动、暂停和恢复步骤见第 12.5 节。**

## 1. 先认识各个组件

Appium 将平台的 UI 自动化能力通过 WebDriver 协议提供给测试脚本。iOS 的调用关系如下：

```text
Python 测试脚本 / Appium Inspector
                ↓ HTTP / WebDriver
Appium Server（Mac，本文使用 127.0.0.1:4723）
                ↓
XCUITest Driver（安装在 Appium 环境中的 iOS 驱动）
                ↓
WebDriverAgent（WDA，运行在模拟器或真机上的测试组件）
                ↓ XCTest / XCUIAutomation
被测 iOS App
```

| 名称 | 在本文中的作用 |
| --- | --- |
| Appium Server | 命令行服务，接收创建会话、查找元素、点击、输入等请求 |
| XCUITest Driver | 驱动扩展，将 Appium 请求转换成 iOS 平台上的自动化操作 |
| WebDriverAgent（WDA） | 设备端测试组件，包含 Xcode 工程；运行在模拟器或 iPhone 上，配合 XCUITest 完成操作 |
| Appium Python Client | 让 Python 代码调用 Appium |
| Appium Inspector | 本文使用独立图形应用，查看页面截图、元素树和属性，交互调试定位方式 |
| Session（会话） | 一次客户端与指定设备、App 的自动化连接 |
| Capabilities（会话配置） | 创建会话时指定平台、驱动、设备和 App 等参数 |
| `unittest` | Python 自带测试框架，负责运行用例、断言和报告通过或失败 |

Appium Server、Driver、Inspector 和 Python Client 分别安装，WDA 随 XCUITest Driver 提供。本文安装方式中，只有 Inspector 会出现在 macOS 的“应用程序”中；Server、Driver 和 WDA 不是独立的 macOS 图形应用。

日常测试先在终端启动 Server，再通过 Inspector 或 Python 创建会话。默认流程由 Appium 构建并启动 WDA；使用预安装 WDA 时，还需按设备和驱动要求准备 Remote XPC 调试隧道，见第 8.5、12.5 节。首次真机签名配置见第 8 节。

来源：[Appium 工作原理](https://appium.io/docs/en/latest/intro/appium/)、[XCUITest Driver 与 WDA](https://appium.github.io/appium-xcuitest-driver/latest/overview/)。

## 2. 安装 Appium 和 iOS 驱动

本节命令都在 Mac 终端执行。先核对已有工具，只安装缺少或不兼容的部分。

### 2.1 准备 Xcode 和目标设备支持

1. 安装支持目标 iOS 版本的完整 Xcode，首次打开并完成其要求的协议确认和组件安装。仅安装 Command Line Tools 不够；`xcodebuild`、`simctl` 等工具需要完整 Xcode。
2. 在 `Xcode → Settings → Locations → Command Line Tools` 中选择实际使用的 Xcode。
3. 按目标平台安装需要的组件。运行模拟器时，在 Xcode 的 `Settings → Components` 中安装相应 iOS Simulator Runtime；真机测试不要求额外下载模拟器 Runtime，但必须完成 Xcode 的设备支持准备。
4. 在终端核对：

```bash
xcode-select -p
xcodebuild -version
xcrun --sdk iphoneos --show-sdk-version
```

**成功标志：**开发工具路径指向完整 Xcode 内的 `Contents/Developer`，而非 `/Library/Developer/CommandLineTools`；版本和 iPhoneOS SDK 查询成功。设备系统、Xcode、macOS 和驱动需要相互兼容，按 [XCUITest 官方兼容矩阵](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/system-requirements/) 核对，不能只比较 Appium 版本。

例如，XCUITest Driver `11.1.2～12.12.4` 对应的 WDA 范围支持 Xcode `16.0～27.x`；iOS 27 要求 Driver `>=11.1.2`、WDA `>=14.1.1`。已满足兼容要求的环境可继续使用，不必为了教程重新安装或升级。真机的配对、开发者模式及签名在第 8 节配置。

来源：[Apple：命令行工具选择](https://developer.apple.com/documentation/xcode/configuring-command-line-tools-settings)、[Xcode 专用命令行工具](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference)、[安装 Xcode 组件](https://developer.apple.com/documentation/xcode/downloading-and-installing-additional-xcode-components)。

### 2.2 检查或安装 Node.js

Appium 3 的 Node.js 要求为 `^20.19.0 || ^22.12.0 || >=24.0.0`，npm 要求为 `>=10`；官方推荐 LTS（长期支持）版本。先执行：

```bash
command -v node
node --version
npm --version
```

已有 Homebrew、版本管理器或其他方式安装的 Node，只要满足上述要求就直接复用，不覆盖现有安装或调整其 PATH。仅在缺少兼容 Node 时，使用下面的独立安装方案：将官方 Node.js `24.21.0` LTS 安装到用户目录，自动区分 Apple Silicon 与 Intel Mac，并校验下载文件的 SHA-256。

```bash
bash <<'SH'
set -euo pipefail
node_version=24.21.0
case "$(uname -m)" in
  arm64) node_arch=arm64 ;;
  x86_64) node_arch=x64 ;;
  *) echo "不支持当前 Mac 架构" >&2; exit 1 ;;
esac
node_name="node-v${node_version}-darwin-${node_arch}"
node_parent="$HOME/.local/share/nodejs"
node_bin="$HOME/.local/bin"
node_target="$node_parent/$node_name"

for node_path in "$node_target" "$node_bin/node" "$node_bin/npm" "$node_bin/npx"; do
  if [ -e "$node_path" ] || [ -L "$node_path" ]; then
    echo "已有文件或链接，请先检查现有安装：$node_path" >&2
    exit 1
  fi
done

node_tmp=$(mktemp -d)
trap 'rm -rf "$node_tmp"' EXIT
cd "$node_tmp"
curl --fail --location "https://nodejs.org/dist/v${node_version}/${node_name}.tar.gz" -o "$node_name.tar.gz"
curl --fail --location "https://nodejs.org/dist/v${node_version}/SHASUMS256.txt" -o SHASUMS256.txt
awk -v file="$node_name.tar.gz" '$2 == file {print; found=1} END {if (!found) exit 1}' SHASUMS256.txt > node.sha256
shasum -a 256 -c node.sha256
tar -xzf "$node_name.tar.gz"
mkdir -p "$node_parent" "$node_bin"
mv "$node_name" "$node_target"
for node_command in node npm npx; do
  ln -s "$node_target/bin/$node_command" "$node_bin/$node_command"
done
SH
```

校验应输出对应归档的 `OK`；已有目标目录或同名链接时，脚本会停止，不覆盖原有安装。安装完成后，在当前终端执行：

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v node
node --version
npm --version
```

采用上述独立安装方案时，Node 应显示 `v24.21.0`、npm 主版本不低于 `10`。为让新终端也生效，在 `~/.zprofile` 中添加一行 `export PATH="$HOME/.local/bin:$PATH"`，并核对 `~/.zshrc` 是否再次调整 PATH。复用已有 Node 的用户保留原有 Node 路径；重新打开终端后用 `command -v node` 和版本命令确认实际生效的安装。

### 2.3 安装缺少的 Server 和驱动

如果已有 `appium` 命令，先执行 `appium --version` 和 `appium driver list --installed`。Appium 3 与 XCUITest Driver 10 及以上配套；已有兼容版本时直接运行下方检查命令，不重复安装。新环境按顺序执行：

```bash
# 仅在尚未安装 Server 时执行；安装在用户目录，不修改 npm 全局 prefix。
export PATH="$HOME/.local/bin:$PATH"
npm install -g --prefix "$HOME/.local" appium@3

# 仅在尚未安装 XCUITest Driver 时执行。
appium driver install xcuitest
```

如果 Server 安装在 `~/.local`，也要在 `~/.zprofile` 中保留一行 `export PATH="$HOME/.local/bin:$PATH"`，确保新终端能找到 Appium；已有这行时不要重复添加。重新打开终端后执行 `command -v node` 和 `command -v appium`，确认仍使用预期的 Node，且 Appium 入口可用。复用已有其他路径的 Server 时无需添加此设置。

随后检查：

```bash
appium --version
appium driver list --installed
appium driver doctor xcuitest
```

Server 的 npm 安装目录与驱动目录不同；驱动默认安装在 `~/.appium`，若设置过 `APPIUM_HOME`，则以该目录为准。启动 Server 和安装驱动时应使用同一环境。[Appium 环境变量](https://appium.io/docs/en/latest/reference/cli/env-vars/)

**成功标志：**Appium 显示 `3.x.x`；驱动列表包含 `xcuitest`；Doctor 的必要依赖检查通过。

Doctor 会区分必要依赖与可选功能。本文让 Appium 通过 Xcode 构建并启动 WDA，原生页面入门不要求额外安装 `ffmpeg`、`go-ios`、`applesimutils` 或 Remote XPC 工具；按实际使用的录像、设备交互及 WDA 启动方式补充。Doctor 通过不代表真机签名或会话已经通过，仍需完成第 8 节的连接验证。

来源：[Appium 系统要求](https://appium.io/docs/en/latest/quickstart/requirements/)、[安装 Appium](https://appium.io/docs/en/latest/quickstart/install/)、[Node.js 官方下载](https://nodejs.org/en/download)、[XCUITest Driver 安装与兼容检查](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/system-requirements/)。

## 3. 创建教程目录和 Python 环境

Appium Python Client 6.x 要求 Python `>=3.10`、Selenium `>=4.37.0`。可以复用满足要求的 Python；下面以 [Homebrew](https://brew.sh/) 的 Python 3.13 为例，文件放在 `~/Documents/AppiumStarter`。未安装 Homebrew 时先按其官网完成安装；已有 Python 3.13 时跳过 `brew install`。若该目录已有虚拟环境，先激活并检查版本，不覆盖重建。

```bash
brew install python@3.13
mkdir -p "$HOME/Documents/AppiumStarter"
cd "$HOME/Documents/AppiumStarter"
"$(brew --prefix python@3.13)/bin/python3.13" -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install "Appium-Python-Client==6.0.6"
python -m pip check
python -m pip show Appium-Python-Client selenium
```

Python Client 会安装它声明需要的 Selenium 依赖。这里固定客户端版本作为新环境示例；已有兼容环境可保留，通过检查后按第 7.3 节记录实际依赖。

**成功标志：**`python --version` 显示 `3.13.x`；`pip check` 没有报告依赖冲突；`pip show` 显示两个包的版本及位于 `.venv` 内的安装位置。

以后每次新开终端执行 Python 示例，先运行：

```bash
cd "$HOME/Documents/AppiumStarter"
source .venv/bin/activate
```

后文区分两个终端：**终端 A 持续运行 Appium Server；终端 B 执行构建、配置生成和 Python 测试。** 当前业务真机使用预安装 WDA，另开终端 C 保持调试隧道运行，见第 12.5 节。环境变量只在设置它的终端及子进程中生效。

来源：[Appium Python Client 安装与兼容矩阵](https://github.com/appium/python-client)、[客户端 6.0.6](https://pypi.org/project/Appium-Python-Client/6.0.6/)、[Homebrew Python 3.13](https://formulae.brew.sh/formula/python@3.13)、[Python 虚拟环境](https://docs.python.org/3/library/venv.html)。

## 4. 创建一个可被测试的 iOS App

### 4.1 在 Xcode 创建示例工程

选择 `File → New → Project → iOS → App`，填写：

| 选项 | 值 |
| --- | --- |
| Product Name | `AppiumDemo` |
| Interface | `SwiftUI` |
| Language | `Swift` |
| Organization Identifier | 使用你自己的标识，例如 `com.example`；真机签名时使用你能注册的唯一标识 |
| Storage | `None`，如果模板提供该选项 |
| Testing System | 如果模板提供该选项，选择 `None`；本示例的测试在 Python 中运行 |
| 保存位置 | `~/Documents/AppiumStarter` |

完成后，应得到 `~/Documents/AppiumStarter/AppiumDemo/AppiumDemo.xcodeproj`。保留 Xcode 生成的 App 入口文件，将工程中的 `ContentView.swift` 替换为：

```swift
import SwiftUI

struct ContentView: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 24) {
            Text("计数器演示")
                .font(.title)

            Text(String(count))
                .accessibilityIdentifier("counter.value")

            Button("加一") {
                count += 1
            }
            .accessibilityIdentifier("counter.increment")
        }
        .padding()
    }
}
```

这里的两个 `accessibilityIdentifier` 是供测试定位使用的稳定名称，在同一页面中保持唯一。

如果接入的是 UIKit 页面，对应写法是给实际控件设置属性，例如：

```swift
incrementButton.accessibilityIdentifier = "counter.increment"
valueLabel.accessibilityIdentifier = "counter.value"
```

UIKit 片段只说明标识设置方式，不是本文 SwiftUI 示例需要额外添加的代码。

来源：[Apple：创建 App 工程](https://developer.apple.com/documentation/xcode/creating-an-xcode-project-for-an-app)、[SwiftUI accessibilityIdentifier](https://developer.apple.com/documentation/swiftui/view/accessibilityidentifier%28_%3A%29)、[UIKit UIAccessibilityIdentification](https://developer.apple.com/documentation/uikit/uiaccessibilityidentification)。

### 4.2 构建 Simulator 专用的 `.app`

在终端 B 中执行：

```bash
cd "$HOME/Documents/AppiumStarter"
source .venv/bin/activate
xcrun simctl list devices available
```

从列表中选择一个可用的 iPhone 模拟器，复制其 UDID，也就是设备名称后括号中的唯一标识。将下面双引号中的说明替换为真实值，然后执行构建：

```bash
export APPIUM_SIM_UDID="替换为模拟器的UDID"

xcodebuild \
  -project "AppiumDemo/AppiumDemo.xcodeproj" \
  -scheme "AppiumDemo" \
  -configuration Debug \
  -sdk iphonesimulator \
  -destination "platform=iOS Simulator,id=$APPIUM_SIM_UDID" \
  -derivedDataPath "$PWD/build" \
  build

test -d "build/Build/Products/Debug-iphonesimulator/AppiumDemo.app"
```

**成功标志：**构建输出 `BUILD SUCCEEDED`，最后的目录检查退出码为 `0`。可以紧接着执行 `echo $?` 查看上一条命令的退出码。

本文明确设置了构建产物目录，因此 `.app` 的位置确定为：

```text
~/Documents/AppiumStarter/build/Build/Products/Debug-iphonesimulator/AppiumDemo.app
```

**模拟器包和真机包不能混用。** `.ipa` 通常用于真机；本文模拟器测试使用按 `iphonesimulator` SDK 构建的 `.app`。

来源：[Apple：命令行构建](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)、[XCUITest Driver App 配置](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/)。

## 5. 启动 Server 并生成会话配置

### 5.1 在终端 A 启动 Server

新开终端 A，执行：

```bash
cd "$HOME/Documents/AppiumStarter"
mkdir -p artifacts
appium --address 127.0.0.1 --port 4723 --log "$PWD/artifacts/appium.log"
```

保持这个终端运行。本文把服务限定在本机地址，Inspector 和 Python 都从同一台 Mac 连接。

在终端 B 检查：

```bash
curl --noproxy '*' --fail http://127.0.0.1:4723/status
```

**成功标志：**Server 日志显示监听地址及已加载的 XCUITest Driver；状态接口返回 JSON，其中 `value.ready` 为 `true`。这只证明服务可接收请求，设备和 App 的启动会在创建 Session 时验证。

本文使用 Server 的默认根路径，因此客户端 URL 是 `http://127.0.0.1:4723`。

来源：[Appium Server 启动](https://appium.io/docs/en/latest/quickstart/install/)、[Server 参数](https://appium.io/docs/en/latest/reference/cli/server/)。

### 5.2 在终端 B 生成配置文件

继续使用设置过 `APPIUM_SIM_UDID` 的终端 B。在教程目录、Python 虚拟环境已激活的情况下，完整复制执行：

```bash
python - <<'PY'
import json
import os
from pathlib import Path

app_path = Path("build/Build/Products/Debug-iphonesimulator/AppiumDemo.app").resolve()
if not app_path.is_dir():
    raise SystemExit(f"找不到模拟器 App，请先完成构建：{app_path}")

caps = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:udid": os.environ["APPIUM_SIM_UDID"],
    "appium:app": str(app_path),
    "appium:noReset": True,
    "appium:forceAppLaunch": True,
}
Path("caps.simulator.json").write_text(
    json.dumps(caps, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print("已生成 caps.simulator.json")
PY

cat caps.simulator.json
```

这会把 UDID 和 `.app` 的真实绝对路径写进配置。**检查输出中没有残留“替换为……”字样。** JSON 文件中的路径不会自动展开 `~` 或 `$HOME`，因此这里由 Python 生成绝对路径。

| 字段 | 含义 |
| --- | --- |
| `platformName` | 标准 WebDriver 字段，值为 `iOS`，不加 `appium:` 前缀 |
| `appium:automationName` | 选择 XCUITest Driver |
| `appium:udid` | 绑定具体模拟器；本例由该设备确定型号和系统版本 |
| `appium:app` | Server 所在 Mac 上的应用包绝对路径，用于安装并启动 App |
| `appium:noReset` | 保留应用数据；不等于重置登录状态或清理数据库 |
| `appium:forceAppLaunch` | 会话启动时重新启动 App；本例的内存计数因此恢复为 `0` |

将 `noReset` 与 `forceAppLaunch` 一起设置，是为了让演示明确保留持久化数据、重新开始进程。实际项目需要另外设计初始账号和数据，不能用重启进程代替数据准备。

来源：[XCUITest Driver Capabilities](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/)。

## 6. 用 Inspector 建立第一次连接

### 6.1 安装并填写连接信息

从 [Appium Inspector 官方 Releases](https://github.com/appium/appium-inspector/releases) 下载桌面安装包。当前 `2026.9.2` 版本要求 macOS 13 或以上：Apple Silicon（M 系列芯片）选择 `arm64` 的 `.dmg`，Intel Mac 选择 `x64` 的 `.dmg`。可在“关于本机”中核对芯片。

打开 `.dmg`，将 Appium Inspector 拖到“应用程序”，然后打开。首次被 macOS 阻止时，按官方安装说明进入 `系统设置 → 隐私与安全性 → 安全性`，针对刚下载的 Inspector 选择“仍要打开”，按提示确认；旧版 macOS 也可在 Finder 中按住 Control 点击应用后选择“打开”。本文使用独立桌面应用，Server 仍由终端 A 中的命令运行。

在新建 Session 页面选择本地 Appium Server，填写：

| 选项 | 值 |
| --- | --- |
| Remote Host | `127.0.0.1` |
| Remote Port | `4723` |
| Remote Path | `/` |
| SSL | 关闭 |
| Capabilities JSON | 粘贴 `caps.simulator.json` 的全部内容 |

点击 `Start Session`。第一次启动可能需要构建和安装 WDA，耗时通常比后续会话长；观察终端 A 的日志判断进度。

**成功标志：**Inspector 出现 App 截图和元素树，画面中可以看到计数器。

来源：[Inspector 系统要求](https://appium.github.io/appium-inspector/latest/quickstart/requirements/)、[Inspector 安装](https://appium.github.io/appium-inspector/latest/quickstart/installation/)、[Inspector 创建 Session](https://appium.github.io/appium-inspector/latest/quickstart/starting-a-session/)。

### 6.2 检查元素并尝试点击

1. 在截图或元素树中选中“加一”按钮，检查其属性中能找到 `counter.increment` 标识。
2. 使用元素搜索，定位策略选 `accessibility id`，值填 `counter.increment`，确认只匹配到目标按钮。
3. 对该元素执行 Tap，刷新截图和元素树，确认计数变为 `1`。
4. 查询 `counter.value`，检查 `label` 属性为 `1`。
5. 点击 Inspector 的结束会话按钮，释放当前 Session，然后继续下一节。

优先按稳定的 accessibility identifier 定位；需要定位更复杂的结构时，再研究 iOS Predicate 或 Class Chain。坐标和较长的 XPath 容易受布局或层级变化影响。

本示例通过 `label` 检查数字文本。XCUITest 的 `name` 可能来自 identifier，也可能来自 label；不要假设页面文字永远等于 `name`。

**同一台设备在本教程中一次只交给一个客户端操作。** 先结束 Inspector 会话，再运行 Python 测试。

来源：[XCUITest 元素属性](https://appium.github.io/appium-xcuitest-driver/latest/reference/element-attributes/)、[XCUITest 元素定位](https://appium.github.io/appium-xcuitest-driver/latest/reference/locator-strategies/)。

## 7. 编写并运行第一个自动化测试

### 7.1 创建测试文件

在 `~/Documents/AppiumStarter` 中创建 `test_counter.py`，内容完整复制如下：

```python
import json
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.client_config import AppiumClientConfig
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CounterTests(unittest.TestCase):
    """验证计数器的初始状态与点击后的业务结果。"""

    def setUp(self):
        config_path = Path(os.environ.get("APPIUM_CAPS_FILE", "caps.simulator.json"))
        caps = json.loads(config_path.read_text(encoding="utf-8"))
        options = XCUITestOptions().load_capabilities(caps)
        client_config = AppiumClientConfig(
            remote_server_addr="http://127.0.0.1:4723",
            timeout=300,
            proxy=Proxy({"proxyType": "direct"}),
        )
        self.driver = webdriver.Remote(
            options=options,
            client_config=client_config,
        )
        # 创建成功后立即登记清理，断言失败也会结束会话。
        self.addCleanup(self.driver.quit)
        self.wait = WebDriverWait(self.driver, 15)

    def test_increment(self):
        value_locator = (AppiumBy.ACCESSIBILITY_ID, "counter.value")
        button_locator = (AppiumBy.ACCESSIBILITY_ID, "counter.increment")

        try:
            value = self.wait.until(EC.visibility_of_element_located(value_locator))
            self.assertEqual(value.get_attribute("label"), "0")

            button = self.wait.until(EC.element_to_be_clickable(button_locator))
            button.click()

            # 等待目标状态，每轮重新查找元素，避免依赖点击前的旧引用。
            self.wait.until(
                lambda driver: driver.find_element(*value_locator).get_attribute("label") == "1"
            )
            self.assertEqual(
                self.driver.find_element(*value_locator).get_attribute("label"),
                "1",
            )
        except Exception:
            self.save_failure_evidence()
            raise

    def save_failure_evidence(self):
        """尽量保留失败画面和元素树，取证失败时保留原始测试异常。"""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        try:
            output = Path("artifacts") / f"{self._testMethodName}-{stamp}"
            output.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            print(f"无法创建取证目录：{error}")
            return

        try:
            if not self.driver.save_screenshot(str(output / "screen.png")):
                print("截图保存失败")
        except Exception as error:
            print(f"截图不可用：{error}")

        try:
            (output / "source.xml").write_text(self.driver.page_source, encoding="utf-8")
        except Exception as error:
            print(f"元素树不可用：{error}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

客户端用 `XCUITestOptions` 传递会话配置。`AppiumClientConfig` 的 `timeout=300` 是单次 HTTP 请求的等待上限，为首次 WDA 构建留出时间。`WebDriverWait(..., 15)` 则反复检查页面条件；其等待过程中的每次请求仍受 HTTP 超时约束，因此 15 秒不是整个测试的硬性总时限。

本例的 `proxyType: direct` 仅让 Python 客户端直连本机 Appium，避免终端的 HTTP 代理将 `127.0.0.1` 请求转发后返回 `502 Bad Gateway`，不会修改系统代理。若改用远程 Server，再按该服务器的网络要求配置。[Selenium ClientConfig](https://www.selenium.dev/selenium/docs/api/py/_modules/selenium/webdriver/remote/client_config.html)

等待超时或断言不成立都会让测试失败。这里没有设置隐式等待，避免与显式等待叠加后产生难以预期的等待时间；签名或构建错误仍需按日志修复。

来源：[Appium Python Client](https://github.com/appium/python-client)、[Selenium 等待策略](https://www.selenium.dev/documentation/webdriver/waits/)、[Python unittest 清理机制](https://docs.python.org/3/library/unittest.html#unittest.TestCase.addCleanup)。

### 7.2 执行测试

确认终端 A 的 Server 仍在运行，并且 Inspector 已结束会话。在终端 B 执行：

```bash
cd "$HOME/Documents/AppiumStarter"
source .venv/bin/activate
export APPIUM_CAPS_FILE="caps.simulator.json"
python -m unittest -v test_counter.py
```

**成功标志：**模拟器自动启动 App、点击“加一”，终端最后输出 `OK`。以下仅为成功输出的形式示意：

```text
test_increment (test_counter.CounterTests.test_increment) ... ok

Ran 1 test in ...s

OK
```

可以再次执行同一条测试命令。测试失败时会输出堆栈，并尽量在 `artifacts/` 下保存截图和元素树；若创建 Session 本身失败，尚无可用设备会话，主要查看 `artifacts/appium.log`。

第一次跑通后，还可以暂时把 Swift 按钮逻辑改成 `count += 2`，按第 4.2 节重新构建。模拟器保持启动，在终端 B 执行以下命令，明确安装这次的新产物后再测试：

```bash
xcrun simctl install "$APPIUM_SIM_UDID" \
  "$PWD/build/Build/Products/Debug-iphonesimulator/AppiumDemo.app"
python -m unittest -v test_counter.py
```

用例应失败。恢复 `count += 1`，再次构建、安装和测试，应恢复通过。这能验证断言确实发现了功能偏差。

### 7.3 记录实际版本

在终端 B 执行：

```bash
python -m pip freeze > requirements.lock.txt
node --version > artifacts/node-version.txt
npm --version > artifacts/npm-version.txt
appium --version > artifacts/appium-version.txt
appium driver list --installed --json > artifacts/drivers.json
xcodebuild -version > artifacts/xcode-version.txt
```

`requirements.lock.txt` 可用于在另一套同类 Python 虚拟环境中执行 `python -m pip install -r requirements.lock.txt`。Server、Driver 和 Xcode 的版本另外记录；Python 依赖锁定并不能锁定整套设备环境。

本阶段目录大致如下：

```text
AppiumStarter/
├── AppiumDemo/                 # Xcode 示例工程
├── .venv/                     # Python 虚拟环境
├── build/                     # Xcode 构建产物
├── caps.simulator.json        # 模拟器会话配置
├── test_counter.py            # 自动化测试
├── requirements.lock.txt      # 实际 Python 依赖版本
└── artifacts/                 # Server 日志、版本记录与失败证据
```

## 8. 切换到 iPhone 真机

真机仍使用同一套 Server、Inspector 和 Python 测试。新增的准备工作是：**设备连接、开发者模式、业务 App 签名，以及 WDA 签名。** 以下采用先由 Xcode 安装业务 App、再由 Appium 按 Bundle ID 启动的方式。

### 8.1 准备设备并安装业务 App

1. 用 USB 连接 iPhone，解锁，确认“信任此电脑”。
2. 在 `Xcode → Window → Devices and Simulators → Devices` 中确认设备连接完成，复制该设备的 Identifier（UDID）。它与前面的模拟器 UDID 不同。
3. 对 iOS 16 及以上设备，在 `设置 → 隐私与安全性 → 开发者模式` 中启用，按系统要求重启并确认。若入口未出现，先完成 Xcode 与设备配对。
4. 按 XCUITest Driver 的设备配置要求，在设备 `设置 → 开发者` 中启用 `Enable UI Automation`。
5. 在 `Xcode → Settings → Apple Accounts` 中添加账号；选择业务 App 的 Target → Signing & Capabilities，启用 `Automatically manage signing`，选择 Team，并设置该账号可注册的唯一 Bundle Identifier。
6. 选择已连接的 iPhone 作为运行目标，按 `⌘R`，处理 Xcode 或设备提示的开发者信任要求，直到计数器 App 能在手机上正常运行。随后停止 Xcode 的运行任务。

如果设备提示开发者不受信任，进入 `设置 → 通用 → VPN 与设备管理`，在“开发者 App”中选择对应团队并信任，再重新运行。

**成功标志：**你已经能够用 Xcode 在这台手机上安装并运行 App。记录 Target 中的实际 Bundle Identifier，下一步会使用。

来源：[XCUITest 真机配置](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/device-setup/)、[Apple：在设备上运行 App](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)、[Apple：开发者模式](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)。

### 8.2 配置 WDA 签名

WDA 是独立的测试组件。**业务 App 能签名成功，不代表 WDA 自动具有可用的签名配置。**

付费开发者团队可以使用官方的自动配置路线，通过下一节的签名 Capabilities 让 Appium 构建 WDA。为了便于初次定位签名问题，下面先用 Xcode 验证一次；免费 Apple Account 按官方指南使用手工配置路线。

在终端 B 执行以下命令，打开当前安装的 XCUITest Driver 附带的 WDA 工程：

```bash
appium driver run xcuitest open-wda
```

在打开的 Xcode 工程中：

1. 找到 `WebDriverAgentRunner` Target，打开 `Signing & Capabilities`。
2. 启用自动签名，选择能在该 iPhone 上运行开发构建的 Team。
3. 设置该 Team 可签名的唯一 Bundle Identifier，例如 `com.yourcompany.AppiumStarterWDA`。这里是 WDA 的标识，与业务 App 的 Bundle ID 不同。
4. 选择 `WebDriverAgentRunner` Scheme 和同一台 iPhone，执行 `Product → Test`（`⌘U`）。
5. 如果出现签名、描述文件或设备信任错误，在这里处理，直到 WDA 能安装并启动。WDA 作为服务保持运行时，不需要等它像普通单元测试一样自行结束。
6. 验证后停止 Xcode 中的 WDA 测试任务，让下一步由 Appium 管理启动。

如果 WDA 提示开发者不受信任，按第 8.1 节的设备“VPN 与设备管理”路径，确认 WDA 所用签名团队的信任状态后再重试。

这些手工修改位于驱动附带的 WDA 工程中，升级 Driver 或 WDA 后可能需要重新设置。记录 Team 和 Bundle ID，并在升级后重新验证。Xcode 为实际 XCTest Runner 包生成 `.xctrunner` 后缀，签名描述文件需要覆盖最终生成的标识。后面的 `APPIUM_WDA_BUNDLE_ID` 填此处 Target 设置的基础 Bundle Identifier，不要自行再追加 `.xctrunner`。

记录所用 **Team ID** 和 **WDA Bundle ID**。Team ID 可以从 Apple Developer 账号的会员信息中查看；也可在已配置签名的 WDA Target 的 Build Settings 中搜索 `Development Team`，查看其实际标识值。

如果当前账号不能完成自动签名，需要使用该账号允许的 Bundle ID、设备注册和描述文件，具体操作以官方 WDA 签名指南为准。单纯增加等待时间不会修复签名失败。

来源：[XCUITest：WDA 签名与描述文件](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/provisioning-profile/)、[完整手工配置](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/provisioning-profile/full-manual-config/)。

### 8.3 生成真机会话配置

在终端 B、教程目录和已激活的虚拟环境中，先替换并执行以下四行。值分别来自前两步记录的信息：

```bash
export APPIUM_DEVICE_UDID="替换为iPhone真机UDID"
export APPIUM_APP_BUNDLE_ID="替换为AppiumDemo的实际BundleIdentifier"
export APPIUM_TEAM_ID="替换为签名使用的TeamID"
export APPIUM_WDA_BUNDLE_ID="替换为WDA签名使用的BundleIdentifier"
```

然后生成配置：

```bash
python - <<'PY'
import json
import os
from pathlib import Path

caps = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:udid": os.environ["APPIUM_DEVICE_UDID"],
    "appium:bundleId": os.environ["APPIUM_APP_BUNDLE_ID"],
    "appium:xcodeOrgId": os.environ["APPIUM_TEAM_ID"],
    "appium:xcodeSigningId": "Apple Development",
    "appium:updatedWDABundleId": os.environ["APPIUM_WDA_BUNDLE_ID"],
    "appium:noReset": True,
    "appium:forceAppLaunch": True,
    "appium:showXcodeLog": True,
}
Path("caps.device.json").write_text(
    json.dumps(caps, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print("已生成 caps.device.json")
PY

cat caps.device.json
```

这里没有 `appium:app`，因此 Appium 不负责安装业务 App；它按 `appium:bundleId` 启动已经安装的真机版本。以后修改业务 App 后，先用 Xcode 重新部署，再执行测试。已指定真实 UDID 时可以省略 `appium:platformVersion`；若显式填写，必须与设备实际系统版本一致，设备升级后及时更新。

`xcodeOrgId` 与 `xcodeSigningId` 配合设置 WDA 的签名 Team 和证书类型；`updatedWDABundleId` 必须与该 Team 可用的描述文件匹配。本文采用 `Apple Development`，如果团队使用其他有效开发签名身份，应与实际配置保持一致。

也可以在教程目录创建 `wda-signing.xcconfig`，集中保存 Xcode 签名设置：

```text
DEVELOPMENT_TEAM = 替换为签名使用的TeamID
CODE_SIGN_STYLE = Automatic
CODE_SIGN_IDENTITY = Apple Development
```

此时用 `appium:xcodeConfigFile` 指向该文件的绝对路径，替代 JSON 中的 `appium:xcodeOrgId` 和 `appium:xcodeSigningId`，保留 `appium:updatedWDABundleId`。Xcode 自动管理的描述文件应配合 `Automatic` 签名；描述文件还必须覆盖目标设备、实际 App ID 和所用开发证书。

来源：[XCUITest：App 与 WDA Capabilities](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/)。

### 8.4 连接和运行

1. 保持终端 A 的 Appium Server 运行。
2. Inspector 中保留相同的 Host、Port、Path，将配置替换为 `caps.device.json` 的内容，点击 `Start Session`。
3. 确认 Inspector 展示的是指定 iPhone 上的 App，能找到两个计数器元素，然后结束 Inspector Session。
4. 在终端 B 执行：

```bash
export APPIUM_CAPS_FILE="caps.device.json"
python -m unittest -v test_counter.py
```

**成功标志：**目标 iPhone 自动打开计数器，点击后显示 `1`，终端输出 `OK`。回到模拟器时，将 `APPIUM_CAPS_FILE` 改回 `caps.simulator.json`。

设备、Xcode 或驱动版本变化后，应重新验证 Session 能否建立。入门阶段保持一台设备、一套配置、顺序执行，先取得稳定结果。

### 8.5 使用预安装 WDA 时的调试隧道

`appium:usePreinstalledWDA: true` 表示直接启动设备上已安装并签名的 WDA，跳过本次会话的 Xcodebuild 构建启动过程。它与 `usePrebuiltWDA` 不同，不能仅因 WDA 已安装就省略连接准备。

本机业务验收使用 iOS `27.0.1` 和预安装 WDA，需要先建立 Remote XPC 调试隧道；该版本的预安装启动路径不能依靠缺少隧道时的 `devicectl` 回退。默认 Xcodebuild 路径和模拟器不应照搬这项前置。隧道命令、检查方法及停止恢复流程见第 12.5 节。

来源：[预安装 WDA 的真机要求](https://appium.github.io/appium-xcuitest-driver/latest/guides/run-preinstalled-wda/)、[Remote XPC 隧道](https://appium.github.io/appium-xcuitest-driver/latest/guides/remotexpc-tunnels-real-devices/)。

## 9. 将示例接到自己的 iOS 项目

计数器跑通后，可以按下面的顺序迁移到实际项目：

1. **替换被测 App。** 模拟器重新构建业务工程，将配置中的 `appium:app` 改成该模拟器包的绝对路径；真机先安装开发测试包，再修改 `appium:bundleId`。
2. **选择一条短流程。** 例如打开列表、进入详情、检查标题。先明确初始页面、操作步骤和预期内容。
3. **添加稳定控件标识。** 在 UIKit 或 SwiftUI 中给涉及的按钮、输入框和结果控件设置 accessibility identifier，并重新构建安装。
4. **在 Inspector 验证定位。** 确认每个关键标识能唯一找到目标，再将对应 ID 写入 Python 测试。
5. **替换断言。** 验证真正的结果，例如保存后出现指定记录、错误时展示正确提示；只有点击成功并不能证明业务正确。
6. **准备初始数据。** 明确测试账号、角色、环境和清理方式。`noReset` 保留的数据会影响后续测试，每条用例需要可说明的起点。
7. **保留运行证据。** 记录应用构建版本、设备、用例结果与失败证据；先跑稳定，再接入团队 CI。

实际工程使用 `.xcworkspace` 时，将构建命令中的 `-project` 改成 `-workspace` 并填写工作区路径，Scheme 使用该工程真实的构建 Scheme。先在业务工程目录执行下面的命令查看信息，其中路径需要替换：

```bash
xcodebuild -list -workspace "YourApp.xcworkspace"
```

只有 `.xcodeproj` 时，使用 `xcodebuild -list -project "YourApp.xcodeproj"`。沿用第 4.2 节的模拟器 destination 和明确的 `-derivedDataPath`，但最终 `.app` 名称以实际 Product Name 为准。

## 10. 常见问题排查

排查顺序建议为：**Server 是否可连接 → Driver 是否加载 → 设备是否可用 → WDA 是否启动 → App 是否启动 → 元素是否可定位 → 业务断言是否成立。**

| 现象 | 优先检查与处理 |
| --- | --- |
| `appium: command not found` | 检查 `$HOME/.local/bin` 是否在 PATH 中；用 `command -v node`、`command -v appium` 确认当前使用的安装 |
| npm 报 `EACCES` | 检查报错路径与权限；安装 Appium 时显式传入 `--prefix "$HOME/.local"`，按下面说明定位 |
| Driver 提示 Appium 版本不兼容 | 对照 Server 与 XCUITest Driver 的兼容要求，确认实际安装版本 |
| Doctor 报 Xcode/SDK 不可用 | 检查 `xcode-select -p`、Xcode 首次启动和 Components 下载状态 |
| Inspector 首次打不开 | 确认安装包来自官方 Releases、架构正确，按第 6.1 节处理 macOS 的首次打开提示 |
| `ECONNREFUSED 127.0.0.1:4723` | Server 未启动或端口不一致；先执行本机 `/status` 检查 |
| HTTP 404 / 找不到路由 | 检查 Inspector Remote Path 为 `/`，Python URL 与 Server 的 base path 一致 |
| 找不到 `.app` 或安装失败 | 使用 Server 机器上的绝对路径；确认构建成功、包的平台和目标设备一致 |
| 指定模拟器不存在 | 检查 UDID 与 `simctl list devices available` 输出；必要时下载 Runtime、创建模拟器 |
| 真机不可用 | 解锁设备，检查 USB、信任、开发者模式及 Xcode 设备准备状态 |
| WDA 构建失败 / `xcodebuild` 返回 65 | 开启 `appium:showXcodeLog` 并查看第一条具体 Xcode 错误；检查 Team、签名、描述文件、SDK，而不是只看退出码 |
| WDA 已安装但不能启动 | 检查开发者信任、UI Automation 设置和设备连接；在 Xcode 中直接运行 WDA Test 定位问题 |
| 预安装 WDA 提示隧道不可用，或找不到设备的 Remote XPC 服务 | 按第 12.5 节启动隧道并查询目标设备条目；只有 4723 的 `/status` 正常，不能证明真机隧道已就绪 |
| 元素找不到 / 等待超时 | 查看失败截图和 XML，确认当前页面、弹窗、可见状态、标识唯一性以及安装的是否是最新测试包 |
| 初始计数不是 `0` | 确认配置包含 `forceAppLaunch: true`，Swift 示例使用内存状态，并已结束其他客户端的会话 |
| `ModuleNotFoundError: appium` | 重新激活 `.venv`，用同一环境中的 `python -m pip show Appium-Python-Client` 检查 |
| 4723 端口已占用 | 使用 `lsof -nP -iTCP:4723 -sTCP:LISTEN` 查看占用者；若是自己开的旧 Server，回到该终端按 `Ctrl+C` 停止 |

### npm 全局安装权限的处理

本文使用 `npm install -g --prefix "$HOME/.local" appium@3`，Appium 命令位于 `$HOME/.local/bin`。若仍报 `EACCES`，先检查错误中列出的目录：可能是目标目录不可写，也可能是 npm 缓存存在权限问题。根据具体路径修复权限后重试，无需修改 npm 的全局 prefix 配置。新终端找不到命令时，按第 2 节检查 PATH。

来源：[npm：全局安装权限错误](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally/)、[XCUITest 故障排查](https://appium.github.io/appium-xcuitest-driver/latest/troubleshooting/)。

## 11. 完成检查与官方资料

完成入门后，应能独立确认以下结果：

- [ ] Appium Server、XCUITest Driver 已安装，并记录实际版本。
- [ ] 完整 Xcode 已完成首次准备，命令行工具选择与目标 iOS 的兼容关系已核对。
- [ ] Doctor 必要依赖检查通过，`/status` 可访问。
- [ ] Simulator 专用 `.app` 构建成功，配置绑定了指定模拟器。
- [ ] Inspector 能看到 App，并通过 accessibility id 定位控件。
- [ ] Python 测试能重复执行，并通过断言验证 `0 → 1`。
- [ ] 人为引入计数错误时测试会失败，恢复后重新通过。
- [ ] 如果需要真机，已完成业务 App 与 WDA 签名，同一条用例在指定 iPhone 上通过。

进一步阅读时，以实际安装版本对应的官方文档为准：

| 资料 | 用途 |
| --- | --- |
| [Appium Quickstart](https://appium.io/docs/en/latest/quickstart/) | Server 入门入口；官方通用示例包含其他平台，本文已按 iOS 调整 |
| [XCUITest Driver 文档](https://appium.github.io/appium-xcuitest-driver/latest/) | iOS 环境、真机配置、定位策略和平台扩展 |
| [XCUITest Capabilities](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/) | 查询会话参数的意义、默认值和适用范围 |
| [Appium Inspector](https://appium.github.io/appium-inspector/latest/) | 查看元素、配置会话和交互调试 |
| [Appium Python Client](https://github.com/appium/python-client) | 客户端安装、API 示例、Python/Selenium 兼容关系 |
| [Selenium 等待策略](https://www.selenium.dev/documentation/webdriver/waits/) | 编写能等待页面状态变化的测试 |

## 12. 本机已配置的真机环境

以下组件版本于 **2026-10-13** 核验；**2026-10-14** 补充当前业务验收的预安装 WDA 流程。现有兼容组件直接复用，目标设备为 USB 连接的 iPhone 11（iOS `27.0.1`）。

| 组件 | 实际版本 |
| --- | --- |
| Node.js / npm | `26.7.0` / `12.0.2` |
| Appium Server / XCUITest Driver / WebDriverAgent | `3.7.0` / `12.12.3` / `16.12.8` |
| Python / Appium Python Client / Selenium | `3.13.5` / `6.0.6` / `4.49.0` |
| Xcode | `27.0`（`27A266a`） |
| iPhone / iOS | iPhone 11 / `27.0.1` |
| Appium Inspector | `2026.9.2`，Apple Silicon 桌面版 |

本机使用 Homebrew 路径中的 Node 和 Appium；不要为了与第 2 节的新环境示例一致而重复安装。可以这样核对实际入口：

```bash
command -v node
command -v appium
npm root -g
appium driver list --installed
```

本次入口为 `/opt/homebrew/bin/node`、`/opt/homebrew/bin/appium`，Server 包位于 `/opt/homebrew/lib/node_modules/appium`，驱动位于 `~/.appium/node_modules/appium-xcuitest-driver`。需要打开 WDA 工程时使用 `appium driver run xcuitest open-wda`。

### 12.1 AppiumStarter 真机连接检查（Xcodebuild 路径）

本节的 `ios_real_device.json` 未设置 `usePreinstalledWDA`，使用默认 Xcodebuild 启动。当前业务验收另用预安装 WDA 配置，按第 12.5 节准备隧道，不能只执行本节步骤。

1. 用 USB 连接并解锁 iPhone，保持开发者模式开启。首次连接按第 8 节处理信任和签名。
2. 在终端 A 启动服务；已运行时复用现有服务，不要重复启动：

```bash
cd "$HOME/Documents/AppiumStarter"
./start_appium.command
```

3. 在终端 B 执行：

```bash
cd "$HOME/Documents/AppiumStarter"
curl --noproxy '*' --fail http://127.0.0.1:4723/status
.venv/bin/python -B smoke_test.py --caps ios_real_device.json
```

**成功标志：**手机打开系统“设置”，脚本输出 `验证通过：应用已在前台，窗口尺寸 375 × 812。`，随后输出会话已关闭，退出码为 `0`。

也可以在 Finder 打开教程目录，双击 `start_appium.command` 和 `run_real_device_check.command`，按同样顺序运行。脚本直接使用 `.venv`，无须手动激活环境。

```bash
open "$HOME/Documents/AppiumStarter"
```

服务仅监听 `127.0.0.1:4723`，不会随系统自动启动。使用结束后，在终端 A 按 `Control + C` 停止。

### 12.2 使用桌面 Inspector

打开应用：

```bash
open "/Applications/Appium Inspector.app"
```

本机已保存配置 **`iPhone 11 - 真机设置`**。在 `Saved Capability Sets` 中选择它，确认 Host `127.0.0.1`、Port `4723`、Path `/`、SSL 关闭，再点击 `Start Session`。已实际验证桌面版可以显示 iPhone 的“设置”截图和元素树。

重新创建配置时，将 `~/Documents/AppiumStarter/ios_real_device.json` 的完整内容粘贴到 JSON 编辑区，保存 JSON，再使用 `Save As…` 保存为便于识别的名称。

同一台 iPhone 一次只由一个客户端操作。结束 Inspector Session 后再运行 Python，避免与现有会话竞争设备。

### 12.3 切换到业务 App

当前 `ios_real_device.json` 使用 `appium:bundleId: com.apple.Preferences`，只用于检查自动化连接。先通过 Xcode 在这台 iPhone 上安装业务 App，再把这个字段改成业务 App 的真实 Bundle Identifier；应用显示名称不能代替 Bundle ID。Inspector 中保存的配置是独立副本，修改本地 JSON 后，还要在 Inspector 中同步修改对应字段，或导入新配置并另存为业务 App 的名称。

本机已经复用现有 Team、开发签名和描述文件验证 WDA；设备标识和签名配置保留在本机 JSON 和 Inspector 配置中。更换设备、Team 或更新 iOS 后重新核对配置，`appium:platformVersion` 当前为 `27.0.1`。本机真机使用 `wdaLocalPort: 8101`、`mjpegServerPort: 9101` 及独立 `derivedDataPath`，避免与模拟器的 WDA 端口、构建目录混用。

`smoke_test.py` 只检查会话、应用前台状态和窗口尺寸。业务点击、输入及结果断言需要按第 9 节接入实际页面；`noReset: true` 会保留应用数据，测试账号和初始数据需要另行准备。

### 12.4 已验证结果与文件

以下是 AppiumStarter 连接检查的验证范围；当前业务 App 验收使用的连接方式见第 12.5 节。

- Doctor 必要检查通过；`ffmpeg` 和 `applesimutils` 未安装，属于可选功能依赖。
- 真机已连续两次完成创建会话、打开“设置”、确认前台状态与窗口尺寸、关闭会话。
- 真机截图与元素树接口验证通过，取得有效 PNG 和包含 140 个元素的 XML；连接检查后已关闭会话。
- 桌面 Inspector 已安装，安装包通过官方 SHA-256 校验；已保存真机配置、显示设备画面与元素树，并正常结束 Session。
- AppiumStarter 连接检查采用 USB/Xcodebuild 启动 WDA；Remote XPC 的崩溃日志等高级功能未验证。
- 连接检查脚本不包含计数器 Demo、业务用例或模拟器测试，不能用连接检查通过代替这些验收结果。

本地文件：

| 路径（相对 `~/Documents/AppiumStarter`） | 用途 |
| --- | --- |
| `start_appium.command` | 启动服务，日志写到 `artifacts/appium.log` |
| `run_real_device_check.command` | 双击运行真机连接检查 |
| `smoke_test.py` | Python 连接检查示例 |
| `ios_real_device.json` | 当前真机、目标 App、WDA 签名配置 |
| `.venv` / `requirements.txt` | Python 环境及已安装依赖版本 |
| `ios_simulator.json` / `run_ios_check.command` | 保留的模拟器配置及入口 |
| `artifacts/environment-20261013.json` | 本次环境版本记录 |
| `artifacts/real-device-smoke-20261013.log` | 真机检查通过日志 |
| `artifacts/inspector-api-check-20261013/` | 真机截图、元素树及接口验证记录 |
| `artifacts/appium-20261013.log` | 本次配置验证的 Server 日志 |
| `artifacts/setup-backup-*` | 配置修改前的本地备份 |

环境恢复与双击使用说明见本地 `README.md`。设备标识、签名材料、日志和测试截图仅用于本地排障，不应随公开学习文档一起提交。

### 12.5 当前业务真机验收：隧道、暂停与恢复

本机业务会话使用 `appium:usePreinstalledWDA: true`。手机上已准备好签名 WDA 时，按以下顺序恢复验收；WDA 被卸载或签名失效时，先重新准备 WDA。`ios_real_device.json` 是第 12.1 节的连接检查配置，不会因启动隧道而自动变成业务配置。

1. 用数据线连接并解锁 iPhone，确认 Xcode 能识别设备。
2. 在终端 A 启动或复用 Appium Server，命令见第 12.1 节；Server 使用普通用户运行。
3. 新开终端 C，执行调试隧道命令，并保持该终端运行：

```bash
sudo appium driver run xcuitest tunnel-creation
```

这条命令为 Mac 与真机建立 Remote XPC 调试通道。`sudo` 用于创建和配置系统网络隧道接口，密码仅在本机终端输入。

4. 在终端 B 检查两个服务。隧道注册服务默认端口为 `42314`；如果启动日志显示其他端口，替换下方端口：

```bash
curl --noproxy '*' --fail http://127.0.0.1:4723/status
curl --noproxy '*' --fail http://127.0.0.1:42314/remotexpc/tunnels
```

**成功标志：**Appium 状态接口正常；隧道列表含目标 iPhone 的 UDID、隧道地址及服务信息。空列表只表示注册服务在运行，不代表设备就绪。然后使用已配置好的业务 Capabilities 创建新会话，核对 App 截图和元素树；不要复用拔线前的旧 Session ID。

5. 需要抓包时打开 Reqable，并按其当前显示的 IP 和端口核对手机 Wi-Fi 手动代理；切换网络后地址可能变化。抓包不是 Appium 点击、输入的必要条件。

**午休或下班暂停：**先结束当前测试和会话，确认无待保存表单；在终端 C 按 `Control + C` 停止隧道，然后可关闭终端、拔下手机。不再使用 Server 时也可在终端 A 按 `Control + C`。停止 Reqable 后，如果手机继续使用该 Wi-Fi，应关闭手动代理，避免手机仍向已停止的代理发送请求。

**下午或重启后恢复：**重新连接并解锁手机，重复以上步骤。已停止的服务需要重启；仍运行的服务先检查再复用，不重复启动。拔线后即使隧道终端还开着，也要重新核对注册列表；连接失效时停止旧隧道并重建。

来源：[官方 tunnel-creation 命令及管理员权限说明](https://appium.github.io/appium-xcuitest-driver/latest/reference/scripts/#tunnel-creation)、[隧道检查与运行顺序](https://appium.github.io/appium-xcuitest-driver/latest/guides/remotexpc-tunnels-real-devices/)。
