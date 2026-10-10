# Bugly iOS 符号表上传工具

适用于本机任意 iOS App 的 Xcode `.xcarchive` 归档，不限定项目名称或版本。此工具独立使用，无需旧的固定版本上传脚本、清单或历史结果。

**本次仅完成工具通用化，尚未实际上传符号表。**

## 开始使用

在 macOS 终端运行：

```sh
python3 "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py"
```

按提示操作：

1. 从 `~/Library/Developer/Xcode/Archives` 扫描到的列表中选择 App，可多选。列表按 Bundle ID 分组；正式包、测试包使用不同 Bundle ID 时分别显示。
2. 为每个 App 选择归档，可多选版本。App 和归档都支持 `1,3`、`1-3` 或 `all`。归档按日期倒序排列，直接回车选择第 `1` 项，即最新归档；“最新”指归档时间，不按版本号大小判断。
3. 选择 Bugly 官方上传工具。脚本自动检查自身目录、自身目录下的 `tools/` 和 `~/Downloads`，也检查这些目录下以 `bugly` 开头的一级子目录中的上传 JAR；找到多个候选时必须选择一份，也可用 `--tool` 指定。
4. 按提示输入每个 App 对应的 Bugly App ID、App Key，App Key 输入时不回显。同一 Bundle ID 的多个版本在本次运行中复用输入，不永久保存。
5. 查看桌面生成的脱敏结果，再到 Bugly 网页核对对应 App、版本和符号 UUID。

上传前会核验主应用二进制与主应用 dSYM 的全部架构及 UUID，必须完全匹配。仅上传主应用 dSYM；归档、二进制和原始 dSYM 保持不变，转换过程使用临时副本。

## 先查看或核验

只列出本机归档，不上传：

```sh
python3 "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py" --list
```

核验所有扫描到的归档，不读取凭据、不上传：

```sh
python3 "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py" --check
```

`--check` 仅核验归档，不检查 Java 能否执行，也不检查网络。只有同时传入 `--tool` 时，才额外检查该工具 ZIP/JAR 的文件结构是否可读取；通过核验不代表工具已运行或上传服务可用。

只核验指定归档：

```sh
python3 "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py" \
  --check \
  --archive "/绝对路径/Example.xcarchive"
```

## 指定归档、工具和结果目录

将下面示例路径替换为真实路径；路径中的空格应保留在双引号内。

`--archive` 会直接使用指定的归档，不再显示 App/版本选择菜单。同一 Bundle ID 可指定多份归档，本次输入的凭据会复用。`--archive` 与 `--archives-dir` 不能同时使用。

```sh
python3 "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py" \
  --archive "/绝对路径/AppOne.xcarchive" \
  --archive "/绝对路径/AppTwo.xcarchive" \
  --tool "/绝对路径/buglyqq-upload-symbol.jar" \
  --output-dir "/Users/michael/Desktop"
```

也可扫描自定义归档根目录，`--archives-dir` 可重复：

```sh
python3 "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py" \
  --archives-dir "/绝对路径/归档目录一" \
  --archives-dir "/绝对路径/归档目录二"
```

| 参数 | 用途 |
| --- | --- |
| `--list` | 只列出归档，不上传 |
| `--check` | 核验指定归档；未指定时核验所有扫描到的归档，不读取凭据、不上传 |
| `--archive` | 指定 `.xcarchive` 路径，可重复 |
| `--archives-dir` | 指定扫描根目录，可重复 |
| `--tool` | 指定 Bugly 官方上传工具 ZIP 或 JAR |
| `--output-dir` | 指定脱敏结果的父目录，默认桌面 |

## 结果判定与凭据

官方工具退出码为 `0`，并且输出同时包含 `statusCode: 0` 和“上传成功”，脚本才记录工具上传成功。**工具成功仍需网页核验**：到正确的 Bugly App 中确认版本和符号 UUID 与脱敏结果一致；不能只看进程退出码或网页版本名称。

App ID、App Key 仅在运行时输入，不永久保存，不写入结果或配置文件。官方 Java 工具通过命令行参数接收凭据，因此工具运行期间，本机有相应权限的进程可能查到这些参数。不要把 Key 贴进聊天或终端命令，也不要保存包含原始参数的进程输出。

## 常见阻塞

| 情况 | 处理方式 |
| --- | --- |
| 没有找到归档 | 在 Xcode Organizer 确认归档位置，使用 `--archive` 指向具体归档，或用 `--archives-dir` 指定目录 |
| 缺少主应用 dSYM | 找到该发布包对应的完整归档或原始符号表；重新编译产生的 UUID 可能不同，不能替代旧发布包 |
| UUID 或架构不匹配 | 停止该归档上传，确认选择了同一次构建的二进制和 dSYM；不要修改 UUID 绕过检查 |
| dSYM 中存在符号链接 | 使用该构建完整、独立的原始 dSYM；脚本不会跟随链接把其他位置的文件带入上传副本 |
| 缺少 Java | 安装可运行官方上传工具的 Java 运行环境，先执行 `java -version` 确认，再重试 |
| 缺少官方上传工具 | 从 Bugly 获取官方符号上传工具，放入脚本目录、脚本目录的 `tools/` 或 `~/Downloads`，也可通过 `--tool` 指定 ZIP/JAR |
| 网络失败或返回失败 | 查看脱敏结果中的错误，确认网络和该 App 的 App ID、App Key，再重新选择失败的归档上传 |
| 工具成功但网页未核实 | 保留脱敏结果，在 Bugly 对照 App、版本、UUID 完成人工核验后再确认交付完成 |

打开说明或在 Finder 中定位工具：

```sh
open "/Users/michael/Desktop/Bugly符号表上传工具/README.md"
open -R "/Users/michael/Desktop/Bugly符号表上传工具/bugly_upload.py"
```
