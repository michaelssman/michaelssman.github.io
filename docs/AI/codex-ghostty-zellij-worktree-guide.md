# Codex CLI + Ghostty + Zellij + Git worktree 开发环境配置手册

| **层级**        | **对应内容**       | **示例**                           |
| --------------- | ------------------ | ---------------------------------- |
| Session（会话） | 一个项目           | iOS 客户端、Java 后端、Flutter App |
| Tab（标签）     | 一个需求或worktree | 登录改造、支付功能、问题修复       |
| Pane（面板）    | 该需求使用的程序   | Codex、Git/Shell、Tests/Logs       |

## 1. 本机快速开始

### 1.1 打开项目会话

在 Ghostty 的外层 Shell 中，按当前项目任选一条：

```bash
zellij --layout kjxy attach --create kjxy
```

```bash
zellij --layout lmerp attach --create lmerp
```

`attach --create` 在会话不存在时创建，存在时连接。项目布局只在首次创建时应用；重新连接不会重复添加初始标签，也不会用更新后的布局替换已有标签。

已经在 Zellij 内时，按 `Ctrl+b`，松开后按 `w`，通过会话管理器切换项目；也可先按 `Ctrl+b → d` 分离，再执行上述命令。

### 1.2 核对目录，再运行 Codex

选择目标需求标签，在 Codex 面板的 Shell 中执行：

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

目录和分支应对应第 2 节的目标 worktree。新任务运行：

```bash
codex
```

继续已有任务时，运行 `codex resume`，从选择器中确认并恢复对应对话。测试与日志命令在 `Tests / Logs` 面板中按项目实际要求手动执行。

临时离开按 `Ctrl+b → d`；下次执行相同的项目启动命令即可重连。所有快捷键见第 7 节。

## 2. 层级、文件与现有工作区

Session 是项目工作区，tab 是需求工作区，pane 是运行程序的终端面板。

```text
Ghostty
└── Zellij
    ├── session：kjxy
    │   ├── tab：ios26-adaptation
    │   ├── tab：refactor1.0
    │   └── tab：tiku2.4
    └── session：lmerp
        ├── tab：release
        └── tab：purchase-optimization

每个 tab：
┌──────────────────────────────────┐
│ Codex                            │
├─────────────────┬────────────────┤
│ Git / Shell     │ Tests / Logs   │
└─────────────────┴────────────────┘
```

| 配置文件 | 用途 |
| --- | --- |
| `~/.config/zellij/config.kdl` | 自定义快捷键、鼠标、复制和恢复设置 |
| `~/.config/zellij/layouts/codex-workspace.kdl` | 新增单个需求 tab 使用的三面板布局 |
| `~/.config/zellij/layouts/kjxy.kdl` | `kjxy` 项目的初始标签和目录 |
| `~/.config/zellij/layouts/lmerp.kdl` | `lmerp` 项目的初始标签和目录 |

本机布局引用以下已存在的 worktree；分支为 2026-10-14 核对结果，开始工作前仍应重新检查：

| Session | Tab | 工作目录 | 当时所在分支 |
| --- | --- | --- | --- |
| `kjxy` | `ios26-adaptation` | `/Users/michael/Desktop/yuncai/kjxy/ios-kjxy` | `feature/ios26-adaptation` |
| `kjxy` | `refactor1.0` | `/Users/michael/Desktop/yuncai/kjxy/refactor1.0` | `feature/refactor1.0` |
| `kjxy` | `tiku2.4` | `/Users/michael/Desktop/yuncai/kjxy/tiku2.4` | `feature/tiku2.4` |
| `lmerp` | `release` | `/Users/michael/Desktop/yuncai/LMERPDocument/iOS-LMERPDocument` | `release` |
| `lmerp` | `purchase-optimization` | `/Users/michael/Desktop/yuncai/LMERPDocument/purchaseModuleOptimization` | `feature/purchaseModuleOptimization` |

## 3. 安装与备份

### 3.1 检查已有工具

新环境先检查：

```bash
command -v brew
command -v codex
git --version
zellij --version
```

仅在尚未安装 Zellij 时安装。

```bash
CURL_SSL_BACKEND=secure-transport \
HOMEBREW_NO_AUTO_UPDATE=1 \
HOMEBREW_NO_INSTALL_CLEANUP=1 \
HOMEBREW_CURL_RETRIES=1 \
brew install zellij

zellij --version
```

### 3.2 修改前备份

本次实施前的备份目录为 `~/.local/state/zellij-setup/20261014-101940/`。以后修改配置前，可在 Shell 中执行：

```bash
zellij_backup="$HOME/.local/state/zellij-setup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$zellij_backup"
if [ -d "$HOME/.config/zellij" ]; then
  cp -R "$HOME/.config/zellij" "$zellij_backup/zellij"
fi
mkdir -p "$HOME/.config/zellij/layouts"
```

查看配置目录或备份：

```bash
open "$HOME/.config/zellij"
open "$HOME/.local/state/zellij-setup"
```

下面给出完整文件内容。新环境可用 `nano "文件绝对路径"` 创建并粘贴，按 `Ctrl+O` 保存、回车确认、`Ctrl+X` 退出；已有文件先备份并核对差异。

## 4. 全局配置与通用布局

### 4.1 `config.kdl`

文件位置：`~/.config/zellij/config.kdl`。以下与本机保存的配置一致：

```kdl
// 默认把按键交给面板内的程序；Ctrl+b 后执行一次操作，再自动回到 Locked。
// 保留 Ctrl+g 给 Codex 外部编辑器，保留 Alt 组合键给终端文字编辑。
default_mode "locked"
default_layout "codex-workspace"
mouse_mode true
pane_frames true
copy_command "pbcopy"
on_force_close "detach"

// 只保存布局和命令信息，不额外持久化终端画面与滚动记录。
session_serialization true
serialize_pane_viewport false
web_server false
show_release_notes false

keybinds clear-defaults=true {
    locked {
        bind "Ctrl b" { SwitchToMode "Normal"; }
    }
    normal {
        bind "Ctrl b" "Esc" "Enter" { SwitchToMode "Locked"; }
        bind "h" "Left" { MoveFocus "Left"; SwitchToMode "Locked"; }
        bind "j" "Down" { MoveFocus "Down"; SwitchToMode "Locked"; }
        bind "k" "Up" { MoveFocus "Up"; SwitchToMode "Locked"; }
        bind "l" "Right" { MoveFocus "Right"; SwitchToMode "Locked"; }
        bind "[" { GoToPreviousTab; SwitchToMode "Locked"; }
        bind "]" { GoToNextTab; SwitchToMode "Locked"; }
        bind "1" { GoToTab 1; SwitchToMode "Locked"; }
        bind "2" { GoToTab 2; SwitchToMode "Locked"; }
        bind "3" { GoToTab 3; SwitchToMode "Locked"; }
        bind "4" { GoToTab 4; SwitchToMode "Locked"; }
        bind "5" { GoToTab 5; SwitchToMode "Locked"; }
        bind "f" { ToggleFocusFullscreen; SwitchToMode "Locked"; }
        bind "r" { SwitchToMode "RenameTab"; TabNameInput 0; }
        bind "s" { SwitchToMode "Scroll"; }
        bind "+" { Resize "Increase"; SwitchToMode "Locked"; }
        bind "-" { Resize "Decrease"; SwitchToMode "Locked"; }
        bind "w" {
            LaunchOrFocusPlugin "zellij:session-manager" {
                floating true
                move_to_focused_tab true
            }
            SwitchToMode "Locked";
        }
        bind "d" { Detach; }
    }
    renametab {
        bind "Enter" { SwitchToMode "Locked"; }
        bind "Esc" { UndoRenameTab; SwitchToMode "Locked"; }
    }
    scroll {
        bind "j" "Down" { ScrollDown; }
        bind "k" "Up" { ScrollUp; }
        bind "PageDown" { PageScrollDown; }
        bind "PageUp" { PageScrollUp; }
        bind "Esc" "q" "Ctrl b" { ScrollToBottom; SwitchToMode "Locked"; }
    }
}
```

这里使用精简的自定义键位：默认 Locked，按 `Ctrl+b` 解锁，普通操作后回到 Locked；重命名与滚动模式需要明确结束。它不是直接启用官方 Unlock-First 预设。`clear-defaults=true` 清除默认按键，Locked 中只拦截 `Ctrl+b`，让 `Ctrl+g`、Alt 组合键继续交给面板内程序。

`copy_command "pbcopy"` 使用 macOS 剪贴板；`session_serialization` 保存可用于重建的布局、目录和命令信息，`serialize_pane_viewport false` 不额外保存终端画面。`web_server false` 关闭 Web 服务，`show_release_notes false` 避免首启版本说明浮层。配置含义参见 [Zellij Options](https://zellij.dev/documentation/options)、[快捷键配置](https://zellij.dev/documentation/keybindings)。

### 4.2 `codex-workspace.kdl`

文件位置：`~/.config/zellij/layouts/codex-workspace.kdl`：

```kdl
// 单个需求的三面板布局；工作目录由启动目录或 new-tab --cwd 指定。
layout {
    pane size=1 borderless=true {
        plugin location="zellij:tab-bar"
    }
    pane size="70%" focus=true
    pane size="30%" split_direction="vertical" {
        pane name="Git / Shell"
        pane name="Tests / Logs"
    }
    pane size=2 borderless=true {
        plugin location="zellij:status-bar"
    }
}
```

这是三个终端面板，加上顶部标签栏和底部状态栏：上方约 70% 用于 Codex，下方约 30% 横向并排放置 Git / Shell 与 Tests / Logs。上方面板默认取得焦点，且不设置固定 `name`，以显示程序提供的动态标题；本文仍将其称为 Codex 面板。三个面板都先打开 Shell，工作目录来自启动位置或 `new-tab --cwd`。布局不自动运行 Codex、构建或测试。[布局语法](https://zellij.dev/documentation/creating-a-layout)

## 5. 项目初始布局与新项目接入

### 5.1 `kjxy.kdl` 完整示例

文件位置：`~/.config/zellij/layouts/kjxy.kdl`：

```kdl
// 项目会话的初始布局；只在创建新会话时应用。
layout {
    tab_template name="worktree" {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        pane size="70%" focus=true
        pane size="30%" split_direction="vertical" {
            pane name="Git / Shell"
            pane name="Tests / Logs"
        }
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }
    worktree name="ios26-adaptation" cwd="/Users/michael/Desktop/yuncai/kjxy/ios-kjxy" focus=true
    worktree name="refactor1.0" cwd="/Users/michael/Desktop/yuncai/kjxy/refactor1.0"
    worktree name="tiku2.4" cwd="/Users/michael/Desktop/yuncai/kjxy/tiku2.4"
}
```

`tab_template` 复用三面板结构；末尾每个 `worktree` 定义一个标签及其绝对工作目录。路径必须是已经存在的目录，Zellij 不负责创建 Git worktree。

### 5.2 `lmerp.kdl`

本机已保存 `~/.config/zellij/layouts/lmerp.kdl`。重新搭建时，使用上面完整模板，将最后三行 `worktree` 定义替换为下面两行，再保存为 `lmerp.kdl`：

```kdl
worktree name="release" cwd="/Users/michael/Desktop/yuncai/LMERPDocument/iOS-LMERPDocument" focus=true
worktree name="purchase-optimization" cwd="/Users/michael/Desktop/yuncai/LMERPDocument/purchaseModuleOptimization"
```

这两行位于 `layout { ... }` 内，与 `tab_template` 同级。其他机器需替换为实际目录，不应直接沿用本机绝对路径。

### 5.3 接入另一个项目

1. 在该项目的现有工作区运行 `git worktree list`，确认待加入的目录与分支。
2. 复制 `kjxy.kdl` 为新的布局文件，例如 `newproject.kdl`。以下 `-n` 会保留已存在的目标文件：

   ```bash
   cp -n "$HOME/.config/zellij/layouts/kjxy.kdl" \
     "$HOME/.config/zellij/layouts/newproject.kdl"
   nano "$HOME/.config/zellij/layouts/newproject.kdl"
   ```

3. 保留完整 `tab_template`，删除末尾原项目的三行 `worktree`，为新项目每个现有目录添加一行。至少保留一行，且只给一个标签设置 `focus=true`。例如：

   ```kdl
   worktree name="main-workspace" cwd="/替换为新项目工作区的绝对路径" focus=true
   ```

4. 保存后解析检查，再在外层 Shell 创建会话：

   ```bash
   zellij --layout newproject setup --check
   zellij --layout newproject attach --create newproject
   ```

布局文件名和 session 名在本方案中保持一致。进入各 tab 后执行第 1.2 节的目录与分支检查。

修改初始布局只影响以后的新会话；向当前已运行的项目加入需求，应使用下一节的 `new-tab`，不必结束整个项目会话。

## 6. 在项目中新增需求标签

目标 worktree 必须已经存在，并属于该项目。先按第 1 节打开目标项目会话，让它保持客户端连接；以下以 `kjxy` 为例，在其中的 **Git / Shell 面板**查看已有标签：

```bash
zellij --session kjxy action query-tab-names
```

确认目标需求尚未加入后，在同一 Shell 中填写实际标签名和目录：

```bash
task_tab="替换为需求标签名"
task_directory="/替换为现有worktree的绝对路径"

git -C "$task_directory" rev-parse --show-toplevel
git -C "$task_directory" branch --show-current
```

确认输出正确，再添加：

```bash
zellij --session kjxy action new-tab \
  --name "$task_tab" \
  --cwd "$task_directory" \
  --layout "$HOME/.config/zellij/layouts/codex-workspace.kdl"
```

`--session` 明确指定项目；`--cwd` 指定三个面板的工作目录；`--layout` 使用单需求布局。新增 `lmerp` 的需求时，先打开 `lmerp` 会话，再将 `--session kjxy` 改为 `--session lmerp`。

**重复执行会新增重复 tab，不会按名称去重。** 本机 `0.45.1` 在没有客户端连接的纯后台会话中新建布局可能报 `Not enough room`，因此保持目标项目已打开再新增。若从另一个外层 Shell 执行，也应先在一个终端 attach 目标会话。新增后检查三个面板的 `pwd`，并在 Codex 面板确认分支后开始工作。[Zellij CLI Actions](https://zellij.dev/documentation/cli-actions)

希望将这个需求纳入以后新建项目会话的初始结构时，再把对应 `worktree name=... cwd=...` 行补入项目布局；当前会话已有的 tab 不会因此再次创建。

## 7. Codex 与日常快捷键

`Ctrl+b → h` 表示先按 `Ctrl+b`，松开后再按 `h`。下表对应本文自定义配置，不能与 Zellij 默认快捷键表混用。

| 操作 | 按键 |
| --- | --- |
| 向左、下、上、右切换面板 | `Ctrl+b → h / j / k / l`，也可用方向键 |
| 前一个 / 后一个标签 | `Ctrl+b → [` / `Ctrl+b → ]` |
| 直接选择第 1～5 个标签 | `Ctrl+b → 1～5` |
| 当前面板全屏 / 恢复 | `Ctrl+b → f` |
| 放大 / 缩小当前面板 | `Ctrl+b → +` / `Ctrl+b → -` |
| 重命名当前标签 | `Ctrl+b → r`，输入后按 `Enter`；`Esc` 取消 |
| 打开会话管理器、选择项目 | `Ctrl+b → w` |
| 分离当前连接 | `Ctrl+b → d` |
| 进入滚动模式 | `Ctrl+b → s` |
| 滚动模式逐行 / 翻页 | `j / k` 或上下键；`PageDown / PageUp` |
| 退出滚动并回到输入状态 | `Esc`、`q` 或 `Ctrl+b` |
| 解锁后取消操作，回到 Locked | `Ctrl+b`、`Esc` 或 `Enter` |

也可用鼠标点击 tab 或面板。Ghostty 保留原有窗口和标签设置；进入 Zellij 后，项目内分屏由 Zellij 管理。

在正确的 worktree 中，按目的选择 Codex 命令：

| 目的 | 命令 |
| --- | --- |
| 新开对话 | `codex` |
| 从选择器恢复当前目录的历史对话 | `codex resume` |
| 确认最近一次对话就是当前任务后直接恢复 | `codex resume --last` |
| 当前目录找不到目标时查看其他目录的对话 | `codex resume --all`，选择时核对目录 |

在 Codex 输入框按 **`Ctrl+g`** 打开 `VISUAL` 指定的外部编辑器，未设置 `VISUAL` 时使用 `EDITOR`；保存并关闭编辑器后，文字返回输入框，再确认发送。本文配置在 Locked 中保留此按键与 Alt 文字移动，沿用原有编辑器和 Ghostty 配置。[Codex CLI 自定义](https://learn.chatgpt.com/docs/cli-customization)、[Codex 命令参考](https://learn.chatgpt.com/docs/cli/reference)

### 7.1 查看当前 Codex 的动态标题

上方 Codex 面板使用程序提供的标题，保留这三层不同的用途：

| 位置 | 显示内容 |
| --- | --- |
| Zellij 需求 tab | 保留 `refactor1.0`、`tiku2.4` 等固定需求名称 |
| Codex 面板标题 | 显示当前程序提供的动态状态；面板不设置固定名称 |
| 外层 Ghostty 标签或窗口标题 | 自动标题未被覆盖时，可接收当前聚焦面板经 Zellij 传出的标题 |

本机 Codex 已配置 `terminal_title = ["activity", "git-branch", "thread-name"]`，本轮沿用该设置，无需重复添加。状态文字由 Codex 决定；显示空闲不代表测试通过或业务任务成功，结果仍应查看对话、命令退出状态和验证证据。

已有会话不会自动套用修改后的布局。本机已按明确的面板 ID，就地清除两个项目中五个 Codex 用途面板的固定名称，保留原进程；尚未启动 Codex 的 Shell 可能暂时沿用初始标题，直到程序发送新的标题更新。

切换到某个需求 tab 后，聚焦上方 Codex 面板，外层标题才对应这个任务；聚焦下方 Shell 或日志面板时，外层标题可能跟随它们变化。**单个 Ghostty tab 不会同时汇总内部多个需求的运行状态。**

如果外层 Ghostty 标签仍被手动名称固定，该名称会覆盖终端传来的动态标题。仅在出现这种情况时，按 macOS Ghostty `1.3.1` 的界面操作：选中该标签，打开 **View → Change Tab Title...**，删除全部文字留空，按 `Enter`（内联编辑）或 `OK`（弹窗）保存，即可恢复自动标题，无需重启。这里清除的是 Ghostty 的手动标题，不需要修改 Zellij 的需求 tab 名称。[Ghostty 标题对话框](https://ghostty.org/docs/config/keybind/reference#prompt_tab_title)、[清除手动标签标题](https://ghostty.org/docs/config/keybind/reference#set_tab_title)

## 8. 离开、重连与重启后的恢复

| 状态 | 操作与边界 |
| --- | --- |
| 暂时离开，原会话仍在运行 | `Ctrl+b → d` 分离；执行 `zellij attach kjxy` 或 `zellij attach lmerp` 重连 |
| 切换到另一个项目 | `Ctrl+b → w` 打开会话管理器，选择目标 session |
| 关闭 Ghostty 窗口 | 本配置 `on_force_close "detach"` 请求分离；需要保留工作时优先显式 detach |
| 电脑重启或会话进程已结束 | 有保存数据时可重建标签、目录与命令；不能恢复原进程内存或正在进行的网络请求 |
| Codex 进程已结束 | 先核对 worktree，再运行 `codex resume` 恢复对话 |

查看会话：

```bash
zellij list-sessions
```

列表可能包含可恢复的已退出会话。重连存在恢复数据的项目后，按界面提示确认需要重新运行的程序。若恢复数据不可用，但 worktree 仍在，可用项目初始布局重新创建会话，再手动添加后续需求 tab。

Detach 的持续运行依赖 Mac、Zellij 服务进程和任务本身仍可运行；机器睡眠、重启或依赖网络中断不能靠 detach 保证任务继续。布局恢复也不能代替保存文件、Git 提交或 Codex 对话恢复。[会话重建机制](https://zellij.dev/documentation/session-resurrection)

本机没有配置开机或新终端自动进入 Zellij，打开 Ghostty 后按第 1 节手动连接。

## 9. Git worktree 的创建与结束

本次终端配置直接使用第 2 节已有目录。以下是以后新增需求时的手动流程；**新增 Zellij tab 本身不会创建分支或 worktree**。

### 9.1 为新需求创建分支和目录

先明确所属仓库、需求分支名和基线分支。基线由项目发布规则决定，不能仅从当前所在分支推断。把下列四个值替换为本次已确认的实际值：

```bash
project_repo="/替换为该项目现有工作区的绝对路径"
task_directory="/替换为准备新建的需求目录绝对路径"
task_branch="feature/替换为需求名"
base_ref="origin/替换为已确认的基线分支"
```

以 `origin` 远端为例，更新引用并检查基线：

```bash
git -C "$project_repo" worktree list
git -C "$project_repo" fetch origin
git -C "$project_repo" rev-parse --verify "${base_ref}^{commit}"
```

确认基线存在、需求分支尚未创建且目标目录未被使用，再执行：

```bash
git -C "$project_repo" worktree add -b "$task_branch" "$task_directory" "$base_ref"
git -C "$task_directory" status --short --branch
```

若需求分支已经存在，先从 `git worktree list` 判断它是否已在其他目录检出：已有目录直接复用；仅当尚未检出时，使用下面命令，**不再加 `-b`**：

```bash
git -C "$project_repo" worktree add "$task_directory" "$task_branch"
```

创建成功后，按项目文档准备该 worktree 的依赖和本地配置，再按第 6 节添加需求 tab。构建、测试、服务端口和日志路径按实际工程设置，不从其他 worktree 自动复制。

### 9.2 需求结束后的清理

1. 先完成项目要求的评审、验证与合并，保存需要保留的改动；停止该需求的 Codex、测试、日志和其他进程。
2. 在目标需求 tab 的 Shell 中执行 `zellij action close-tab`，关闭该 tab。该操作会关闭其全部面板，因此应先完成上一步。
3. 在外层 Shell 或其他保留的工作区重新设置下面三个变量，替换为本次要清理的真实值。不同 Shell 不共享第 9.1 节设置的变量，关闭 tab 后不能假定它们仍存在：

   ```bash
   project_repo="/替换为该项目仍保留的工作区绝对路径"
   task_directory="/替换为本次要删除的需求目录绝对路径"
   task_branch="feature/替换为本次已结束的需求名"

   git -C "$project_repo" worktree list
   git -C "$task_directory" rev-parse --show-toplevel
   git -C "$task_directory" status --short --branch
   git -C "$task_directory" ls-files --others --ignored --exclude-standard
   ```

   确认工作区列表、仓库根目录和分支都指向本次结束的需求；最后一条用于发现 Git 忽略的本地文件，需要保留的文件先移出该目录。

4. 确认需求目录可以删除后，从仍保留的仓库工作区执行：

   ```bash
   git -C "$project_repo" worktree remove "$task_directory"
   git -C "$project_repo" worktree list
   ```

   不添加 `--force` 绕过未保存文件的检查；被拒绝时先处理具体原因。删除 worktree 不会同时删除其分支。确实不再需要且已合并的本地分支，可另外执行 `git -C "$project_repo" branch -d "$task_branch"`。

5. 如果项目布局包含这个目录，删除相应 `worktree` 行，避免以后新建会话时引用已删除路径。布局文件不直接修改已保存的会话恢复数据；会话管理器中若还有引用该目录的已退出会话，应在确认不再需要后清理对应恢复记录。

此流程使用 Git 管理 worktree，不直接通过 Finder 或 `rm -rf` 删除关联目录。[Git worktree 生命周期](https://git-scm.com/docs/git-worktree)

## 10. 检查、排错与本机验证记录

### 10.1 配置解析检查

下面只检查配置、布局和实际支持的参数，不启动项目任务：

```bash
zellij --version
zellij --config "$HOME/.config/zellij/config.kdl" --layout codex-workspace setup --check
zellij --config "$HOME/.config/zellij/config.kdl" --layout kjxy setup --check
zellij --config "$HOME/.config/zellij/config.kdl" --layout lmerp setup --check
zellij action new-tab --help
```

`setup --check` 应成功解析配置和布局；它不能证明目录内项目可以构建，也不能代替 Ghostty 中的快捷键与显示验收。

| 现象 | 检查与处理 |
| --- | --- |
| `zellij: command not found` | 用 `command -v brew`、`brew list --versions zellij` 检查安装；新开正常的 Ghostty Shell 再检查 PATH |
| 布局找不到或 KDL 解析失败 | 检查文件名、括号和配置目录；运行上面的 `setup --check`，按报错行定位 |
| 没有出现预期初始标签 | 检查是否连接了已存在的同名会话；修改初始布局不会覆盖它，缺少的需求用 `new-tab` 添加 |
| 新 tab 目录不对 | 检查 `--cwd` 的绝对路径；在三个面板核对 `pwd`，再核对 Git 分支 |
| 新增 tab 报 `Not enough room` | 先 attach 目标 session，让窗口有足够空间，再在其 Git / Shell 面板中执行新增命令；本机不采用无客户端的纯后台新增方式 |
| 重复出现同名 tab | `new-tab` 不去重；先用 `query-tab-names` 检查，关闭重复项前停止其中程序 |
| `Ctrl+g` 或 Alt 被拦截 | 先回到 Locked；核对是否加载本文 `clear-defaults=true` 配置，或是否又嵌套了其他复用器 |
| 按快捷键后文字不输入 | 检查是否仍在重命名或滚动模式，按对应退出键回到 Locked |
| 外部编辑器没有打开 | 在 Shell 检查 `printenv VISUAL`、`printenv EDITOR`，沿用可运行的编辑器命令；此问题与会话恢复分开排查 |
| Codex 恢复了错误任务 | 先核对当前目录，使用 `codex resume` 选择，不直接假定 `--last` 就是目标 |
| Codex 状态没有出现在标题中 | 聚焦上方 Codex 面板，确认其未设置固定 pane 名称；外层 Ghostty 若仍显示手动名称，按第 7.1 节清除标题覆盖 |
| 恢复会话后目录不存在 | 先检查原 worktree 是否被移动或删除；修正项目布局，再为存在的目录建立标签 |

### 10.2 2026-10-14 本机记录

| 项目 | 状态 |
| --- | --- |
| Zellij 安装 | Homebrew 安装 `0.45.1`，版本命令已核验 |
| 配置文件 | `config.kdl`、通用布局、`kjxy.kdl`、`lmerp.kdl` 已保存 |
| 配置与布局解析 | `setup --check` 已通过 |
| 现有 worktree | 已核对两个项目、五个目录的仓库关系和当时分支 |
| Ghostty、Shell 与 Codex 配置 | 沿用现有设置；未新增自动启动 |
| Git 操作 | 本次配置未创建、搬迁或删除 worktree，未创建分支或提交代码 |
| 安装时的项目会话与面板 | 首次创建时，`kjxy` 有 3 个 tab，`lmerp` 有 2 个 tab；15 个终端面板的目录均与目标 worktree 一致，当时运行程序为 `/bin/zsh` |
| 安装验证的任务范围 | 当时没有在这些面板运行 Codex 或业务构建、测试命令；该记录不代表后续面板的实时运行状态 |
| 新增需求 tab | 已连接客户端的临时会话中，`new-tab --cwd` 通过；带空格路径的三个终端面板目录均匹配 |
| 键盘与重连验证 | 临时会话通过 PTY（伪终端）测试：`Ctrl+b` 前缀、面板与标签切换、全屏、中文标签重命名、打开会话管理器；detach/attach 后面板 ID、目录、标签名及测试进程均保留 |
| 按键与文本透传 | 临时面板按原始字节收到 `Ctrl+g`、Alt+h 和中文 UTF-8 文本；这不代表已验收 Ghostty 输入法或实际 Codex 编辑器交互 |
| Ghostty 输入交互 | 仍未人工验收：中文输入法、实际 Codex `Ctrl+g` 外部编辑器与 Alt 文字移动 |
| 动态标题验证 | PTY 模拟的 `Working → Ready` 状态切换通过，现有 Codex 面板动态标题已恢复；实际 Ghostty 外层仍显示“云课堂”，清除其手动标题覆盖后的显示效果待确认 |
| 运行会话标题更新 | 三份布局已取消上方面板的固定名称并通过解析；现有五个对应面板已就地清名，ID、目录、运行命令与退出状态保持不变；正在运行的 Codex 面板已恢复其真实动态标题 |
| 机器重启后的会话重建 | 未执行重启验证 |

安装阶段的测试专用会话已清理，保留 `kjxy` 与 `lmerp` 两个项目会话。安装验证记录保存在 `~/.local/state/zellij-setup/20261014-101940/verification.json`。

动态标题调整的验证记录位于 `~/.local/state/zellij-title-fix/20261014-121539/verification.json`，同目录保存调整前的三份布局备份。

首次进入项目后，依次确认：各 tab 的目录和分支正确；三个面板正常；`Ctrl+b` 能切换、分离和重连；Locked 中 `Ctrl+g` 与 Alt 文字移动保持原行为。通过这些检查后再依赖该会话承载长时间运行的任务。
