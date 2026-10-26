# Ghostty + Herdr 多项目终端配置

Herdr 是终端工作区管理器：一个界面管理多个项目、分屏和 Codex CLI，关闭客户端后，后台任务仍可继续运行。

本文采用 **一个默认会话 → 每个项目一个 Workspace（工作区）→ 标签 → 面板**。

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
herdr workspace create --cwd "/Users/michael/Documents/HHLib" --label "HHLib"
herdr workspace create --cwd "/Users/michael/Documents/java_demo" --label "java_demo"
herdr workspace create --cwd "/Users/michael/.codex/skills" --label "skills"
```

每条命令创建一个工作区及其首个标签、Shell 面板。

### 打开已有 Git worktree

同一个仓库同时开发多个需求时，可以把每个已有 worktree 加入 Herdr，作为独立工作区归到源仓库下面。

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

#### 已有一个 worktree，再添加另一个

**第二个 worktree 已创建，只需加入 Herdr：** 再执行一次 `open`，`--cwd` 仍指向同一个源仓库，`--path` 换成第二个 worktree 的实际目录，`--label` 换成它的显示名称。例如：

```bash
herdr worktree open \
  --cwd "/Users/michael/Desktop/yuncai/kjxy/ios-kjxy" \
  --path "/Users/michael/Desktop/yuncai/kjxy/task-2" \
  --label "需求2"
```

### 分屏与运行 Codex

推荐每个工作区使用一个 `main` 标签：上方运行 Codex，下方左右分别执行 Git/Shell 命令和测试/查看日志。

1. 单击上方面板，确认当前目录后运行 Codex：

   ```bash
   pwd
   codex
   ```

Herdr 可检测面板中的 Codex，并在侧栏显示任务状态。面板负责运行程序，工作区负责组织项目；创建工作区本身不会启动 Codex 或测试。[快速开始](https://herdr.dev/docs/quick-start/)

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

复制模式中用方向键或 `h/j/k/l` 移动，`v` 开始选择，`y` 复制，`Esc` 取消选择或退出。鼠标拖选默认自动复制。默认鼠标模式下，用 **Ctrl+单击** 打开网页链接。[键盘说明](https://herdr.dev/docs/keyboard/)、[鼠标操作](https://herdr.dev/docs/quick-start/)

## 5. 离开、关闭与恢复

| 目的 | 操作 | 结果 |
|---|---|---|
| 暂时离开 | `Ctrl+b → q` | 客户端分离，所有工作区的后台任务继续运行 |
| 重新连接 | 在普通 Shell 执行 `herdr` | 回到已有默认会话 |
| 关闭当前面板 | `Ctrl+b → x` | 结束该面板及其程序 |
| 关闭当前标签 | `Ctrl+b → Shift+x` | 结束标签中的面板 |
| 关闭当前工作区 | `Ctrl+b → Shift+d` | 结束该工作区中的面板，保留项目文件 |
| 停止整个默认会话 | `herdr server stop` | 结束默认会话中**全部工作区**的面板进程 |

关闭 Ghostty 窗口也会断开客户端，Herdr 后台服务继续运行。日常离开优先使用 `Ctrl+b → q`；**Herdr 的分离键是 `q`，现有 Zellij 配置的分离键是 `d`。**

关闭面板、标签或工作区前，先保存并结束其中的任务。普通面板关闭可能立即执行，不能依赖每次都有确认提示。

后台服务停止或电脑重启后，再次运行 `herdr` 可恢复已保存的布局和目录，但原来的测试、服务等进程已经结束。支持的 Agent 会话能否自动恢复，还取决于官方集成是否提供有效会话引用；布局恢复不等于进程一直运行。[会话与恢复](https://herdr.dev/docs/session-state/)、[关闭行为](https://herdr.dev/docs/cli-reference/#tabs)

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
| 快捷键无反应 | 确认没有嵌套 Zellij，先用英文输入源，再用 `Ctrl+b → ?` 查看实际绑定 |
| 配置修改没有生效 | 执行 `herdr server reload-config`；检查配置路径及启动警告 |
| 中文候选框位置异常 | 本机尚未验证 GUI 中文输入；官方提供实验性 IME 光标跟踪选项，可按实际问题单独启用 |
| 更新后行为仍像旧版本 | 用 `herdr status` 比较客户端与服务端，按上文步骤在任务结束后重启服务 |

默认未启用中文输入实验选项。相关设置见[官方 IME 说明](https://herdr.dev/docs/configuration/#ime-cursor-tracking)。日志位于 `~/.config/herdr/`，排查时优先查看 `herdr-client.log` 和 `herdr-server.log`。

查看本机配置和本次修改前的 Codex 备份：

```bash
open "$HOME/.config/herdr"
open "$HOME/.local/state/herdr-setup/20261015-213836"
```
