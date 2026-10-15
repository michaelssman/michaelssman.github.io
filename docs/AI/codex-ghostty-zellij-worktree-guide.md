# Codex CLI + Ghostty + Zellij 多项目配置指南

| ** 层级**       | **对应内容**       | **示例**                           |
| --------------- | ------------------ | ---------------------------------- |
| Session（会话） | 一个项目           | iOS 客户端、Java 后端、Flutter App |
| Tab（标签）     | 一个需求或worktree | 登录改造、支付功能、问题修复       |
| Pane（面板）    | 该需求使用的程序   | Codex、Git/Shell、Tests/Logs       |

## 1. 本机项目与日常入口

完成第 2～4 节配置后，在 Ghostty 的外层 Shell 中按需执行一条：

```bash
zellij --layout "$HOME/.config/zellij/layouts/flutter_demo.kdl" attach --create flutter_demo
zellij --layout "$HOME/.config/zellij/layouts/HHLib.kdl" attach --create HHLib
zellij --layout "$HOME/.config/zellij/layouts/java_demo.kdl" attach --create java_demo
zellij --layout "$HOME/.config/zellij/layouts/michaelssman.github.io.kdl" attach --create michaelssman.github.io
zellij --layout "$HOME/.config/zellij/layouts/skills.kdl" attach --create skills
```

`attach --create` 在会话不存在时创建，存在时重连。布局只用于创建初始结构；重连不会重复添加标签，也不会用更新后的布局覆盖已有会话。这里统一使用完整布局路径，避免含点的项目名被当成文件路径而无法找到布局。[官方命令说明](https://zellij.dev/documentation/commands.html)

每个会话初始只有 `main` 标签，三个面板都打开 Shell：

```text
┌──────────────────────────────────┐
│ Codex（约 70%，先打开 Shell）     │
├─────────────────┬────────────────┤
│ Git / Shell     │ Tests / Logs   │
└─────────────────┴────────────────┘
```

上方面板执行 `pwd` 确认目录，再运行 `codex` 或 `codex resume`。下方用于手动执行 Git、构建、测试和日志命令。布局不自动启动 Codex 或业务程序。

`HHLib` 是目录容器，本身不是 Git 仓库；`PWUtils`、`PWSpecs` 才是其中的仓库。单独修改组件时，应进入对应子目录再运行 Codex，例如：

```bash
cd "/Users/michael/Documents/HHLib/PWUtils"
git status --short --branch
codex
```

也可以按第 5 节为子仓库新建标签，让三个面板都进入相同目录。维护整个组件目录组时可从 `HHLib` 启动 Codex，但 Git 命令仍需在具体仓库内执行。

## 2. 安装与配置前准备

### 2.1 检查工具

仅当 Zellij 尚未安装时执行：

```bash
brew install zellij
zellij --version
```

### 2.2 备份与创建目录

修改已有配置前先备份：

```bash
zellij_backup="$HOME/.local/state/zellij-setup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$zellij_backup"
if [ -d "$HOME/.config/zellij" ]; then
  cp -R "$HOME/.config/zellij" "$zellij_backup/zellij"
fi
mkdir -p "$HOME/.config/zellij/layouts"
```

| 文件 | 用途 |
| --- | --- |
| `~/.config/zellij/config.kdl` | 快捷键、复制、分离与恢复设置 |
| `~/.config/zellij/layouts/codex-workspace.kdl` | 通用三面板布局，用于新增任务标签 |
| `~/.config/zellij/layouts/<项目名>.kdl` | 项目的初始 `main` 标签和工作目录 |

下节给出完整文件内容。可用 `nano "文件路径"` 打开，粘贴后按 `Ctrl+O`、回车保存，`Ctrl+X` 退出；已有文件先核对差异再修改。

## 3. 全局配置与布局

### 3.1 `config.kdl`

编辑 `~/.config/zellij/config.kdl`：

```kdl
// 默认把按键交给面板内的程序；Ctrl+b 后执行一次操作，再自动回到 Locked。
// 保留 Ctrl+g 给 Codex 外部编辑器，保留 Alt 组合键给终端文字编辑。
default_mode "locked"
default_layout "codex-workspace"
mouse_mode true
scroll_mode_sync false
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
        bind "Ctrl b" { Write 2; SwitchToMode "Locked"; }
        bind "Esc" "Enter" { SwitchToMode "Locked"; }
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

这里使用自定义前缀键：`clear-defaults=true` 清除默认键位，Locked 中只拦截 `Ctrl+b`，让 `Ctrl+g`、Alt 等按键交给内部程序。连续按两次 `Ctrl+b` 会向内部发送一次 Ctrl+b；`Write 2` 中的 `2` 是该控制键的字节值。[快捷键配置](https://zellij.dev/documentation/keybindings-binding.html)、[按键动作](https://zellij.dev/documentation/keybindings-possible-actions.html)

`scroll_mode_sync false` 避免鼠标滚动自动切换到 Scroll / Normal，保留 Locked 的按键透传；需要键盘滚动时用 `Ctrl+b → s`。[滚动模式](https://zellij.dev/documentation/keybindings-modes.html)

`pbcopy` 使用 macOS 剪贴板；`detach` 在关闭终端连接时保留会话；序列化用于重建布局、目录和命令，不额外保存终端画面与滚动记录。不启动 Web 服务，不显示版本更新说明。[配置选项](https://zellij.dev/documentation/options.html)

### 3.2 通用三面板布局

编辑 `~/.config/zellij/layouts/codex-workspace.kdl`：

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

上方面板不设置固定 `name`，便于显示 Codex 等程序提供的动态标题。通用布局也不写固定目录，方便用于普通项目、子仓库或 worktree。[布局语法](https://zellij.dev/documentation/creating-a-layout.html)

### 3.3 生成五个项目布局

以下整段在 Shell 执行，为第 1 节的五个目录生成同名布局。目录不存在时停止；已存在的布局保留，不覆盖其内容。

```bash
/bin/bash <<'ZELLIJ_SETUP'
set -eu
layout_dir="$HOME/.config/zellij/layouts"
mkdir -p "$layout_dir"

while IFS='|' read -r project_name project_directory; do
  if [ ! -d "$project_directory" ]; then
    printf '目录不存在：%s\n' "$project_directory" >&2
    exit 1
  fi
  layout_file="$layout_dir/$project_name.kdl"
  if [ -e "$layout_file" ]; then
    printf '保留已有布局：%s\n' "$layout_file"
    continue
  fi
  cat > "$layout_file" <<LAYOUT
layout {
    tab name="main" cwd="$project_directory" {
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
}
LAYOUT
  printf '已生成：%s\n' "$layout_file"
done <<'PROJECTS'
flutter_demo|/Users/michael/Documents/flutter_demo
HHLib|/Users/michael/Documents/HHLib
java_demo|/Users/michael/Documents/java_demo
michaelssman.github.io|/Users/michael/Documents/michaelssman.github.io
skills|/Users/michael/.codex/skills
PROJECTS
ZELLIJ_SETUP
```

换电脑或增加项目时，先修改末尾 `会话名|绝对目录` 清单。生成后若需要改目录，编辑对应 `.kdl`；重新运行脚本会保留旧文件。

## 4. 配置检查与首次使用

逐个解析全局配置和六个布局；这些命令不会启动项目会话：

```bash
zellij --version
for layout_name in codex-workspace flutter_demo HHLib java_demo michaelssman.github.io skills; do
  zellij --config "$HOME/.config/zellij/config.kdl" \
    --layout "$HOME/.config/zellij/layouts/$layout_name.kdl" \
    setup --check || break
done
zellij action new-tab --help
```

全部应成功解析，并显示所用配置和布局目录。解析通过只表示配置有效，不代表项目能构建或快捷键已通过实际验收。[配置检查命令](https://zellij.dev/documentation/commands.html)

选择第 1 节的项目启动命令，在三个面板分别执行 `pwd`；Git 仓库还应执行：

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

`HHLib` 根目录和其他非 Git 目录不要求这些 Git 命令成功。需要操作仓库时，先进入实际仓库或新建对应标签。

首次使用时检查：面板目录正确；`Ctrl+b → j / k` 能切换焦点；`Ctrl+b → f` 能全屏和恢复；`Ctrl+b → d` 分离后，用同一启动命令可以重连。最后在 Codex 中确认中文输入、`Ctrl+g` 和常用 Alt 组合键正常。

## 5. 新增任务或子仓库标签

先打开目标项目会话，在其 **Git / Shell 面板**查看已有标签：

```bash
zellij action query-tab-names
```

例如，在 `HHLib` 会话中为 `PWUtils` 新建三面板标签：

```bash
task_directory="/Users/michael/Documents/HHLib/PWUtils"
git -C "$task_directory" status --short --branch
zellij action new-tab \
  --name "PWUtils" \
  --cwd "$task_directory" \
  --layout "$HOME/.config/zellij/layouts/codex-workspace.kdl"
```

换成 `PWSpecs` 时，同时替换标签名和路径。其他项目同理，`--cwd` 可以直接指向原项目目录；用于不同分支时才指向独立 worktree。

`new-tab` 不按名字去重，重复运行会重复创建。通用布局未固定目录，因此三个面板均使用 `--cwd`；创建后再次核对 `pwd`。若从外层 Shell 操作，使用 `zellij --session HHLib action new-tab ...` 明确目标，并保持目标会话已连接。[新增标签参数](https://zellij.dev/documentation/cli-actions.html#new-tab)

当前会话的新增标签会由会话恢复机制保存。若希望以后全新创建会话时也包含这些标签，在对应项目布局中增加 `tab name="..." cwd="..." { ... }`，复用其三面板结构即可。

## 6. 快捷键与 Codex

`Ctrl+b → h` 表示先按 Ctrl+b，松开后按 h。下表对应本文配置：

| 操作 | 按键 |
| --- | --- |
| 左、下、上、右切换面板 | `Ctrl+b → h / j / k / l`，也可用方向键 |
| 前一个 / 后一个标签 | `Ctrl+b → [` / `Ctrl+b → ]` |
| 第 1～5 个标签 | `Ctrl+b → 1～5` |
| 当前面板全屏 / 恢复 | `Ctrl+b → f` |
| 放大 / 缩小当前面板 | `Ctrl+b → +` / `Ctrl+b → -` |
| 重命名标签 | `Ctrl+b → r`，Enter 完成，Esc 取消 |
| 分离当前连接 | `Ctrl+b → d` |
| 进入滚动模式 | `Ctrl+b → s` |
| 滚动模式逐行 / 翻页 | `j / k` 或上下键；PageDown / PageUp |
| 退出滚动并回到底部 | Esc、q 或 Ctrl+b |
| 前缀后取消操作 | Esc 或 Enter |
| 向内部程序发送 Ctrl+b | 连续按两次 Ctrl+b |

也可以鼠标点击标签和面板。已经在 Zellij 内时，用会话管理器切换项目，或先分离再执行启动命令，避免把项目会话层层嵌套。

本机现有 Codex `[tui]` 设置为 `terminal_title = ["activity", "project-name"]`，继续保留。上方动态面板标题与固定的任务标签名各有用途；外层 Ghostty 标题还取决于当前聚焦面板和是否有手动标题覆盖。标题里的空闲状态不代表构建或测试通过，结果应查看命令退出状态和测试报告。

## 7. 离开、关闭与恢复

| 情况 | 操作与边界 |
| --- | --- |
| 临时离开（推荐） | `Ctrl+b → d` 分离，原会话和任务继续运行 |
| 关闭一个面板 | 先退出其中的 Codex 或其他程序，再在 Shell 输入 `exit` |
| 关闭一个任务标签 | 先保存并结束其中的任务，再在该标签的 Shell 执行 `zellij action close-tab`；该标签的全部面板会关闭 |
| 回到项目 | 使用第 1 节相同命令重连 |
| 查看会话 | `zellij list-sessions` |
| 恢复会话 | `zellij attach 会话名` |
| 会话管理器、切换项目 | `Ctrl+b → w`，选择已有会话 |
| 关闭 Ghostty 窗口 | 本配置请求 detach；需要保留工作时优先主动分离 |
| Mac 重启或会话已退出 | 有恢复记录时可重建布局、目录和命令，不能恢复原进程内存 |

**结束整个项目会话**：先保存改动，按 `Ctrl+b → d` 返回外层 Shell，再执行：

```bash
zellij kill-session michaelssman.github.io
```

将 `michaelssman.github.io` 替换为目标会话名。该命令会终止指定会话的全部标签、面板及其中正在运行的任务，其他项目会话不受影响。关闭 Ghostty 窗口或分离连接不会达到相同效果；会话中最后一个面板关闭后，会话也会结束。

结束会话后仍可能保留恢复记录；`zellij list-sessions` 中标记为 `EXITED` 表示会话已结束。重建时按界面提示确认要重新运行的程序，不能恢复已结束的原进程；机器睡眠、网络中断也可能影响正在运行的任务。[会话恢复说明](https://zellij.dev/documentation/session-resurrection.html)

## 9. 常见问题

| 现象 | 检查与处理 |
| --- | --- |
| 首次出现欢迎浮窗 | 按 Esc 关闭，再操作项目面板 |
| 修改布局后界面没变化 | 已有会话不会重新套用初始布局；向当前会话增加标签用 `new-tab` |
| 新标签目录错误 | 检查 `--cwd`，使用未固定目录的通用布局，并在三个面板分别执行 `pwd` |
| 新增标签报空间不足 | 先 attach 目标会话并扩大窗口，再在其 Shell 面板执行新增命令 |

查看配置或备份目录：

```bash
open "$HOME/.config/zellij"
open "$HOME/.local/state/zellij-setup"
```
