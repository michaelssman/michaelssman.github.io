# Herdr 多项目终端配置

## 1. 安装与启动

```bash
brew install herdr
herdr --version
```

在 普通 Shell 中运行：

```bash
herdr
```

首次启动会创建默认会话；以后执行同一命令连接已有会话。

### Server 在哪里运行？

**按本文方式在 Mac 上启动的 Herdr Server，就是运行在这台 Mac 上的后台服务，不在云端。** “Server”表示程序承担服务端职责，并不意味着它是一台云服务器。

| 部分 | 作用 |
| --- | --- |
| Client（客户端） | 终端里看到的 Herdr 界面，用来查看和操作工作区 |
| Server（后台服务） | 在后台管理终端面板、其中运行的程序和智能体会话 |

可以理解为：后台服务负责维持工作现场，客户端是查看和操作这个现场的窗口。按 `Ctrl+b → q` 分离客户端后，后台服务和任务仍可运行；执行 `herdr server stop` 会停止该会话中的面板程序，具体操作见第 5 节。**Mac 关机后，本机服务和任务也会停止。**

在 Mac 的普通终端执行以下命令，检查当前状态：

```bash
herdr status
```

服务运行时，输出的 `server` 部分会显示 `status: running`、服务端版本及 `socket`。本机默认会话的 socket 路径为 `~/.config/herdr/herdr.sock`；socket 是客户端与后台服务之间的本机通信入口，不是云端网址。版本和运行状态以命令的实际输出为准。

**Herdr 在本机运行，不等于 AI 模型也在本机运行。** Herdr 管理会话；Codex、OMP 等工具将模型请求发往哪里，取决于各自的模型与服务提供方配置。如果另外连接了远程机器，需要区分本机与远程会话，不能把所有任务都当成本机任务。

## 2. 本机配置

配置文件：`~/.config/herdr/config.toml`。

```toml
onboarding = false

[terminal]
default_shell = "/bin/zsh"
shell_mode = "login"

[keys]
prefix = "ctrl+b"

[ui]
window_title = "{workspace} | {tab}"
show_agent_labels_on_pane_borders = true

[ui.toast]
delivery = "herdr"

[ui.sound]
enabled = false
```

- 使用登录式 zsh，让新面板加载本机 PATH 等登录环境配置。
- 保留官方默认快捷键；Ghostty 标签标题显示当前工作区和 Herdr 标签。

修改后先检查，再重载正在运行的服务：

```bash
herdr config check
herdr server reload-config
```

### Codex 会话集成

本机已安装 Herdr 官方 Codex 集成。重新配置时，先备份现有文件，再安装：

```bash
herdr_backup="$HOME/.local/state/herdr-setup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$herdr_backup"
chmod 700 "$herdr_backup"
for name in config.toml hooks.json herdr-agent-state.sh; do
  if [ -f "$HOME/.codex/$name" ]; then
    cp -p "$HOME/.codex/$name" "$herdr_backup/$name"
    chmod 600 "$herdr_backup/$name"
  fi
done
herdr integration install codex
herdr integration status
```

安装会写入 `~/.codex/herdr-agent-state.sh`、注册 `hooks.json` 的 `SessionStart` 事件，并确保 `config.toml` 中的 `[features] hooks = true`。模型等现有设置保留。本机 Herdr 0.9.3 的集成状态为 `codex: current (v8)`。

该 hook 向 Herdr 本机 socket 报告 Codex 会话身份，供重启后恢复对话使用；Codex 的工作状态仍由 Herdr 检测界面判断。集成对以后新启动的 Codex 生效。[官方集成说明](https://herdr.dev/docs/integrations/#codex)、[本机版本的 hook 实现](https://github.com/herdrdev/herdr/blob/v0.9.3/src/integration/assets/codex/herdr-agent-state.sh)

## 3. 管理本机项目

### 首次添加工作区

查看已有工作区：

```bash
herdr workspace list
```

**以下命令只用于创建缺少的工作区，不要每次启动都执行。**

```bash
herdr workspace create --cwd "/Users/michael/Documents/flutter_demo" --label "flutter_demo"
herdr workspace create --cwd "/Users/michael/Documents/java_demo" --label "java_demo"
```

每条命令创建一个工作区及其首个标签、Shell 面板。

### 添加已有 Git worktree

例如，源仓库为 `/Users/michael/Desktop/yuncai/kjxy/ios-kjxy`，已有需求 worktree 为 `/Users/michael/Desktop/yuncai/kjxy/refactor1.0`，在普通 Shell 中执行：

```bash
herdr worktree open \
  --cwd "/Users/michael/Desktop/yuncai/kjxy/ios-kjxy" \
  --path "/Users/michael/Desktop/yuncai/kjxy/refactor1.0" \
  --label "重构1.0"
```

- `--cwd`：源仓库的工作目录，用于确定 worktree 所属的 Git 仓库。
- `--path`：该仓库中已经存在的 worktree 目录。
- `--label`：该工作区在 Herdr 中显示的名称。

## 4. 日常操作

| 操作 | 快捷键 |
|---|---|
| 查看当前全部快捷键 | `Ctrl+b → ?` |
| 切换工作区 | `Ctrl+b → w` |
| 搜索并跳转到面板或 Agent | `Ctrl+b → g` |
| 新建标签 | `Ctrl+b → c` |
| 上一个 / 下一个标签 | `Ctrl+b → p` / `n` |
| 跳转到第 1～9 个标签 | `Ctrl+b → 1`～`9` |
| 重命名标签 | `Ctrl+b → Shift+t` |
| 左右 / 上下分屏 | `Ctrl+b → v` / `-` |
| 向左 / 下 / 上 / 右切换面板 | `Ctrl+b → h/j/k/l` |
| 放大 / 还原当前面板 | `Ctrl+b → z` |
| 显示 / 收起侧栏 | `Ctrl+b → b` |
| 进入滚动与复制模式 | `Ctrl+b → [` |

复制模式中用方向键或 `h/j/k/l` 移动，`v` 开始选择，`y` 复制，`Esc` 取消选择或退出。默认鼠标模式下，用 **Ctrl+单击** 打开网页链接。

## 5. 离开、关闭与恢复

| 目的 | 操作 | 结果 |
|---|---|---|
| 暂时离开 | `Ctrl+b → q` | 客户端分离，所有工作区的后台任务继续运行 |
| 重新连接 | 在普通 Shell 执行 `herdr` | 回到已有默认会话 |
| 关闭当前面板 | `Ctrl+b → x` | 结束该面板及其程序 |
| 关闭当前标签 | `Ctrl+b → Shift+x` | 结束标签中的面板 |
| 关闭当前工作区 | `Ctrl+b → Shift+d` | 结束该工作区中的面板，保留项目文件 |
| 停止整个默认会话 | `herdr server stop` | 结束默认会话中**全部工作区**的面板进程 |

## 6. 升级与排查

Homebrew 安装使用 Homebrew 升级：

```bash
brew upgrade herdr
herdr --version
herdr status
```

升级二进制后，兼容的旧后台服务可能继续运行。需要应用新的服务端功能时，先结束所有任务，再执行 `herdr server stop`，然后重新启动 `herdr`；停止服务会终止面板中的程序。[官方升级说明](https://herdr.dev/docs/install/)、[排查说明](https://herdr.dev/docs/troubleshooting/)

| 现象 | 检查或处理 |
|---|---|
| `herdr` 找不到 | 新开 Ghostty 标签，执行 `command -v herdr`；本机安装路径为 `/opt/homebrew/bin/herdr` |
| 配置修改没有生效 | 执行 `herdr server reload-config`；检查配置路径及启动警告 |
| 更新后行为仍像旧版本 | 用 `herdr status` 比较客户端与服务端，按上文步骤在任务结束后重启服务 |

默认未启用中文输入实验选项。相关设置见[官方 IME 说明](https://herdr.dev/docs/configuration/#ime-cursor-tracking)。日志位于 `~/.config/herdr/`，排查时优先查看 `herdr-client.log` 和 `herdr-server.log`。

查看本机配置和本次修改前的 Codex 备份：

```bash
open "$HOME/.config/herdr"
open "$HOME/.local/state/herdr-setup/20261015-213836"
```
