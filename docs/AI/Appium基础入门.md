# Appium 基础入门：从环境配置到 iOS 自动化测试

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
| Appium Server | 接收创建会话、查找元素、点击、输入等请求 |
| XCUITest Driver | 将 Appium 请求转换成 iOS 平台上的自动化操作 |
| WebDriverAgent | 配合 XCUITest 在设备上完成操作；真机上需要签名 |
| Appium Python Client | 让 Python 代码调用 Appium |
| Appium Inspector | 查看页面截图、元素树和属性，交互调试定位方式 |
| Session（会话） | 一次客户端与指定设备、App 的自动化连接 |
| Capabilities（会话配置） | 创建会话时指定平台、驱动、设备和 App 等参数 |
| `unittest` | Python 自带测试框架，负责运行用例、断言和报告通过或失败 |

Appium Server、Driver、Inspector 和 Python Client 分别安装。Appium 不要求给业务 App 集成一个 Appium SDK；本文会给控件添加测试标识，方便稳定定位。

来源：[Appium 工作原理](https://appium.io/docs/en/latest/intro/appium/)。

## 2. 准备 Mac 环境

### 2.1 版本与软件清单

| 组件 | 本文采用的要求或选择 |
| --- | --- |
| Node.js | 推荐 **24.x LTS**；Appium 3 官方范围是 `^20.19.0 \|\| ^22.12.0 \|\| >=24.0.0` |
| npm | `>=10`，通常随 Node.js 安装 |
| Appium Server | 3.x |
| XCUITest Driver | 官方矩阵中 `>=10.0.0` 对应 Appium 3 |
| Python | 本文客户端要求 **3.10 及以上** |
| Appium Python Client | 本文固定为核对时已发布的 **6.0.4**，其兼容矩阵要求 Selenium `4.37.0+` |
| iOS Simulator | 安装一个 Xcode 支持的 iOS Runtime，并创建一个 iPhone 模拟器 |
| Appium Inspector | 使用官方发布的独立桌面应用 |

来源：[Appium 系统要求](https://appium.io/docs/en/latest/quickstart/requirements/)、[XCUITest Driver 系统要求](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/system-requirements/)、[Node.js 下载](https://nodejs.org/en/download)。

### 2.2 配置 Xcode

1. 打开 `Xcode → Settings → Components`，安装 iOS 平台支持和一个 iOS Simulator Runtime；部分旧版 Xcode 的入口名为 `Platforms`。
2. 打开 `Window → Devices and Simulators → Simulators`。如果没有可用 iPhone，点击 `+`，选择已安装的 iOS 版本创建一个。
3. 在终端执行以下检查；这些命令可在任意目录执行。

```bash
xcode-select -p
xcodebuild -version
xcrun simctl list devices available
```

**成功标志：**第一条命令指向完整 Xcode 的开发者目录；第二条显示 Xcode 版本；第三条列出至少一个可用 iPhone 模拟器。

如果第一条指向 `/Library/Developer/CommandLineTools`，或指向另一套 Xcode，而你实际使用的是 `/Applications/Xcode.app`，执行：

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -runFirstLaunch
```

Xcode 安装在其他位置时，替换上面的路径。

来源：[Apple：安装 Xcode 组件](https://developer.apple.com/documentation/xcode/downloading-and-installing-additional-xcode-components)、[Apple：Xcode 命令行工具](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)。

### 2.3 安装 Node.js 与 Python

已有满足要求的环境可以继续使用。否则按以下步骤安装：

1. 在 [Node.js 官方下载页](https://nodejs.org/en/download)选择 24.x LTS、macOS 和与你的 Mac 匹配的架构，下载安装包并完成安装。
2. 在 [Python 官方 macOS 下载页](https://www.python.org/downloads/macos/)选择稳定版本的 macOS 安装包并安装。
3. 重新打开终端，执行：

```bash
node --version
npm --version
python3 --version
```

**成功标志：**三条命令均能输出版本，且满足上表要求。尤其确认 `python3` 不是系统附带的旧版 Python。Python 的安装与命令路径说明见 [Python macOS 官方指南](https://docs.python.org/3/using/mac.html)。客户端版本依据 [官方 PyPI 发布](https://pypi.org/project/Appium-Python-Client/)和[兼容矩阵](https://github.com/appium/python-client)。

## 3. 安装 Appium 和 iOS 驱动

以下命令在任意目录执行：

```bash
npm install -g appium@3
appium --version
appium driver install xcuitest
appium driver list --installed
appium driver doctor xcuitest
```

各条命令依次完成：安装 3.x Server、查看版本、安装 iOS 驱动、查看已安装驱动、检查 iOS 自动化依赖。

**成功标志：**Appium 显示 `3.x.x`；驱动列表包含 `xcuitest`；Doctor 的必要依赖检查通过。

来源：[安装 Appium](https://appium.io/docs/en/latest/quickstart/install/)、[XCUITest Driver 安装与检查](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/system-requirements/)。

## 4. 创建教程目录和 Python 环境

本教程将文件放在 `~/Documents/AppiumStarter`。以下命令会在你的 Mac 上创建一个新的学习目录。

```bash
mkdir -p "$HOME/Documents/AppiumStarter"
cd "$HOME/Documents/AppiumStarter"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "Appium-Python-Client==6.0.4"
python -m pip check
python -m pip show Appium-Python-Client selenium
```

Python Client 会安装它声明需要的 Selenium 依赖。

**成功标志：**`pip check` 没有报告依赖冲突；`pip show` 显示两个包的版本及位于 `.venv` 内的安装位置。

以后每次新开终端执行 Python 示例，先运行：

```bash
cd "$HOME/Documents/AppiumStarter"
source .venv/bin/activate
```

后文区分两个终端：**终端 A 持续运行 Appium Server；终端 B 执行构建、配置生成和 Python 测试。** 环境变量只在设置它的终端及子进程中生效。

来源：[Appium Python Client 安装与兼容矩阵](https://github.com/appium/python-client)、[Python 虚拟环境](https://docs.python.org/3/library/venv.html)。

## 5. 创建一个可被测试的 iOS App

### 5.1 在 Xcode 创建示例工程

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

### 5.2 构建 Simulator 专用的 `.app`

在终端 B 中执行：

```bash
cd "$HOME/Documents/AppiumStarter"
source .venv/bin/activate
xcrun simctl list devices available
```

从列表中复制刚才使用的模拟器 UDID，也就是设备名称后括号中的唯一标识。将下面双引号中的说明替换为真实值，然后执行构建：

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

## 6. 启动 Server 并生成会话配置

### 6.1 在终端 A 启动 Server

新开终端 A，执行：

```bash
cd "$HOME/Documents/AppiumStarter"
mkdir -p artifacts
appium --address 127.0.0.1 --port 4723 --log "$PWD/artifacts/appium.log"
```

保持这个终端运行。本文把服务限定在本机地址，Inspector 和 Python 都从同一台 Mac 连接。

在终端 B 检查：

```bash
curl --fail http://127.0.0.1:4723/status
```

**成功标志：**Server 日志显示监听地址及已加载的 XCUITest Driver；状态接口返回 JSON，其中 `value.ready` 为 `true`。这只证明服务可接收请求，设备和 App 的启动会在创建 Session 时验证。

本文使用 Server 的默认根路径，因此客户端 URL 是 `http://127.0.0.1:4723`。

来源：[Appium Server 启动](https://appium.io/docs/en/latest/quickstart/install/)、[Server 参数](https://appium.io/docs/en/latest/reference/cli/server/)。

### 6.2 在终端 B 生成配置文件

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

## 7. 用 Inspector 建立第一次连接

### 7.1 安装并填写连接信息

从 [Appium Inspector 官方 Releases](https://github.com/appium/appium-inspector/releases)下载适合当前 Mac 架构的 `.dmg`。

本文使用独立桌面应用，Server 仍由终端 A 中的命令运行。

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

来源：[Inspector 安装](https://appium.github.io/appium-inspector/latest/quickstart/installation/)、[Inspector 创建 Session](https://appium.github.io/appium-inspector/latest/quickstart/starting-a-session/)。

### 7.2 检查元素并尝试点击

1. 在截图或元素树中选中“加一”按钮，检查其属性中能找到 `counter.increment` 标识。
2. 使用元素搜索，定位策略选 `accessibility id`，值填 `counter.increment`，确认只匹配到目标按钮。
3. 对该元素执行 Tap，刷新截图和元素树，确认计数变为 `1`。
4. 查询 `counter.value`，检查 `label` 属性为 `1`。
5. 点击 Inspector 的结束会话按钮，释放当前 Session，然后继续下一节。

优先按稳定的 accessibility identifier 定位；需要定位更复杂的结构时，再研究 iOS Predicate 或 Class Chain。坐标和较长的 XPath 容易受布局或层级变化影响。

本示例通过 `label` 检查数字文本。XCUITest 的 `name` 可能来自 identifier，也可能来自 label；不要假设页面文字永远等于 `name`。

**同一台设备在本教程中一次只交给一个客户端操作。** 先结束 Inspector 会话，再运行 Python 测试。

来源：[XCUITest 元素属性](https://appium.github.io/appium-xcuitest-driver/latest/reference/element-attributes/)、[XCUITest 元素定位](https://appium.github.io/appium-xcuitest-driver/latest/reference/locator-strategies/)。

## 8. 编写并运行第一个自动化测试

### 8.1 创建测试文件

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

等待超时或断言不成立都会让测试失败。这里没有设置隐式等待，避免与显式等待叠加后产生难以预期的等待时间；签名或构建错误仍需按日志修复。

来源：[Appium Python Client](https://github.com/appium/python-client)、[Selenium 等待策略](https://www.selenium.dev/documentation/webdriver/waits/)、[Python unittest 清理机制](https://docs.python.org/3/library/unittest.html#unittest.TestCase.addCleanup)。

### 8.2 执行测试

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

第一次跑通后，还可以暂时把 Swift 按钮逻辑改成 `count += 2`，按第 5.3 节重新构建。模拟器保持启动，在终端 B 执行以下命令，明确安装这次的新产物后再测试：

```bash
xcrun simctl install "$APPIUM_SIM_UDID" \
  "$PWD/build/Build/Products/Debug-iphonesimulator/AppiumDemo.app"
python -m unittest -v test_counter.py
```

用例应失败。恢复 `count += 1`，再次构建、安装和测试，应恢复通过。这能验证断言确实发现了功能偏差。

### 8.3 记录实际版本

在终端 B 执行：

```bash
python -m pip freeze > requirements.lock.txt
node --version > artifacts/node-version.txt
npm --version > artifacts/npm-version.txt
appium --version > artifacts/appium-version.txt
appium driver list --installed > artifacts/drivers.txt
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

## 9. 切换到 iPhone 真机

真机仍使用同一套 Server、Inspector 和 Python 测试。新增的准备工作是：**设备连接、开发者模式、业务 App 签名，以及 WDA 签名。** 以下采用先由 Xcode 安装业务 App、再由 Appium 按 Bundle ID 启动的方式。

### 9.1 准备设备并安装业务 App

1. 用 USB 连接 iPhone，解锁，确认“信任此电脑”。
2. 在 `Xcode → Window → Devices and Simulators → Devices` 中确认设备连接完成，复制该设备的 Identifier（UDID）。它与前面的模拟器 UDID 不同。
3. 对 iOS 16 及以上设备，在 `设置 → 隐私与安全性 → 开发者模式` 中启用，按系统要求重启并确认。若入口未出现，先完成 Xcode 与设备配对。
4. 按 XCUITest Driver 的设备配置要求，在设备 `设置 → 开发者` 中启用 `Enable UI Automation`。
6. 选择已连接的 iPhone 作为运行目标，按 `⌘R`，处理 Xcode 或设备提示的开发者信任要求，直到计数器 App 能在手机上正常运行。随后停止 Xcode 的运行任务。

如果设备提示开发者不受信任，进入 `设置 → 通用 → VPN 与设备管理`，在“开发者 App”中选择对应团队并信任，再重新运行。

**成功标志：**你已经能够用 Xcode 在这台手机上安装并运行 App。记录 Target 中的实际 Bundle Identifier，下一步会使用。

来源：[XCUITest 真机配置](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/device-setup/)、[Apple：在设备上运行 App](https://developer.apple.com/documentation/xcode/building-and-running-an-app)、[Apple：开发者模式](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)。

### 9.2 配置 WDA 签名

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

如果 WDA 提示开发者不受信任，按第 9.1 节的设备“VPN 与设备管理”路径，确认 WDA 所用签名团队的信任状态后再重试。

这些手工修改位于驱动附带的 WDA 工程中，升级 Driver 或 WDA 后可能需要重新设置。记录 Team 和 Bundle ID，并在升级后重新验证。Xcode 为实际 XCTest Runner 包生成 `.xctrunner` 后缀，签名描述文件需要覆盖最终生成的标识。后面的 `APPIUM_WDA_BUNDLE_ID` 填此处 Target 设置的基础 Bundle Identifier，不要自行再追加 `.xctrunner`。

记录所用 **Team ID** 和 **WDA Bundle ID**。Team ID 可以从 Apple Developer 账号的会员信息中查看；也可在已配置签名的 WDA Target 的 Build Settings 中搜索 `Development Team`，查看其实际标识值。

如果当前账号不能完成自动签名，需要使用该账号允许的 Bundle ID、设备注册和描述文件，具体操作以官方 WDA 签名指南为准。单纯增加等待时间不会修复签名失败。

来源：[XCUITest：WDA 签名与描述文件](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/provisioning-profile/)、[完整手工配置](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/provisioning-profile/full-manual-config/)。

### 9.3 生成真机会话配置

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

这里没有 `appium:app`，因此 Appium 不负责安装业务 App；它按 `appium:bundleId` 启动已经安装的真机版本。以后修改业务 App 后，先用 Xcode 重新部署，再执行测试。

`xcodeOrgId` 与 `xcodeSigningId` 配合设置 WDA 的签名 Team 和证书类型；`updatedWDABundleId` 必须与该 Team 可用的描述文件匹配。本文采用 `Apple Development`，如果团队使用其他有效开发签名身份，应与实际配置保持一致。

来源：[XCUITest：App 与 WDA Capabilities](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/)。

### 9.4 连接和运行

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

## 10. 将示例接到自己的 iOS 项目

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

只有 `.xcodeproj` 时，使用 `xcodebuild -list -project "YourApp.xcodeproj"`。沿用第 5.3 节的模拟器 destination 和明确的 `-derivedDataPath`，但最终 `.app` 名称以实际 Product Name 为准。

## 11. 常见问题排查

排查顺序建议为：**Server 是否可连接 → Driver 是否加载 → 设备是否可用 → WDA 是否启动 → App 是否启动 → 元素是否可定位 → 业务断言是否成立。**

| 现象 | 优先检查与处理 |
| --- | --- |
| `appium: command not found` | 重新打开终端；检查 Node/npm 安装及 `npm prefix -g` 对应的 `bin` 是否在 PATH 中 |
| npm 报 `EACCES` | 当前全局安装目录不可写；按下面的用户目录配置处理 |
| Driver 提示 Appium 版本不兼容 | 对照 Server 与 XCUITest Driver 的兼容要求，确认实际安装版本 |
| Doctor 报 Xcode/SDK 不可用 | 检查 `xcode-select -p`、Xcode 首次启动和 Components 下载状态 |
| `ECONNREFUSED 127.0.0.1:4723` | Server 未启动或端口不一致；先执行本机 `/status` 检查 |
| HTTP 404 / 找不到路由 | 检查 Inspector Remote Path 为 `/`，Python URL 与 Server 的 base path 一致 |
| 找不到 `.app` 或安装失败 | 使用 Server 机器上的绝对路径；确认构建成功、包的平台和目标设备一致 |
| 指定模拟器不存在 | 检查 UDID 与 `simctl list devices available` 输出；必要时下载 Runtime、创建模拟器 |
| 真机不可用 | 解锁设备，检查 USB、信任、开发者模式及 Xcode 设备准备状态 |
| WDA 构建失败 / `xcodebuild` 返回 65 | 开启 `appium:showXcodeLog` 并查看第一条具体 Xcode 错误；检查 Team、签名、描述文件、SDK，而不是只看退出码 |
| WDA 已安装但不能启动 | 检查开发者信任、UI Automation 设置和设备连接；在 Xcode 中直接运行 WDA Test 定位问题 |
| 元素找不到 / 等待超时 | 查看失败截图和 XML，确认当前页面、弹窗、可见状态、标识唯一性以及安装的是否是最新测试包 |
| 初始计数不是 `0` | 确认配置包含 `forceAppLaunch: true`，Swift 示例使用内存状态，并已结束其他客户端的会话 |
| `ModuleNotFoundError: appium` | 重新激活 `.venv`，用同一环境中的 `python -m pip show Appium-Python-Client` 检查 |
| 4723 端口已占用 | 使用 `lsof -nP -iTCP:4723 -sTCP:LISTEN` 查看占用者；若是自己开的旧 Server，回到该终端按 `Ctrl+C` 停止 |

### npm 全局安装权限的处理

如果通过 Node 官网安装包安装 Node，且全局安装 Appium 时遇到 `EACCES`，可以按 npm 官方方法将全局包目录改到用户目录。该设置会影响之后这个用户执行的 npm 全局安装：

```bash
mkdir -p "$HOME/.local"
npm config set prefix "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
npm install -g appium@3
appium --version
```

为了让新终端也生效，用文本编辑器打开或创建 `~/.zprofile`，添加一行 `export PATH="$HOME/.local/bin:$PATH"`，保存后重新打开终端。已经使用 Node 版本管理器时，沿用其全局包管理方式，避免额外混入另一套 prefix 配置。

来源：[npm：全局安装权限错误](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally/)、[XCUITest 故障排查](https://appium.github.io/appium-xcuitest-driver/latest/troubleshooting/)。

## 12. 完成检查与官方资料

完成入门后，应能独立确认以下结果：

- [ ] Appium Server、XCUITest Driver 已安装，并记录实际版本。
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
