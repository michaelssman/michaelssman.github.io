# Herdr 多项目终端配置

内容整理自 Dave Ebbelaar 的 [Herdr 完整指南视频](https://www.youtube.com/watch?v=Shqtk_2Jd3c)及文中官方资料，按操作主题编排。

## 1. 理解 Herdr 会话

### 1.1 本机 Server 在哪里？

**本机 Herdr Server 是运行在这台 Mac 上的后台服务，不在云端。** “Server”描述它的职责，不表示它是一台云服务器。

| 部分 | 作用 |
| --- | --- |
| Client | 终端中看到的 Herdr 界面 |
| Server | 后台管理各工作区的面板、Shell 和 Agent 进程 |
| 本机 socket | Client 与 Server 通信的入口，不是互联网地址 |

```bash
herdr status
```

本机默认会话 socket 为 `~/.config/herdr/herdr.sock`。Herdr 在本机运行，不等于模型也在本机运行：Codex、OMP 将请求发到哪里，由它们自己的模型提供方配置决定。

### 1.2 Workspace、Tab 与 Pane

```text
Session（会话，例如 default）
├─ Workspace / Space（项目，例如 java_demo）
│  ├─ Tab（标签，例如后端开发）
│  │  ├─ Pane（面板，运行 Codex）
│  │  └─ Pane（面板，运行测试）
│  └─ Tab（标签，例如查看代码）
└─ Workspace（项目，例如 flutter_demo）
```

## 2. 安装、备份与启动

以下命令在本机 **zsh / Bash 终端**执行，是 Shell 命令。`$(date ...)` 把当前时间填入备份目录名。

修改 Herdr、Agent 集成或 Auto Title 插件前，先备份涉及的配置；备份只留在本机：

```bash
herdr_backup="$HOME/.local/state/herdr-setup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$herdr_backup"
chmod 700 "$herdr_backup"
for file in \
  ".config/herdr/config.toml" \
  ".codex/config.toml" \
  ".codex/hooks.json" \
  ".codex/herdr-agent-state.sh" \
  ".omp/agent/extensions/herdr-omp-agent-state.ts" \
  ".config/herdr-auto-title/config.env"; do
  if [ -f "$HOME/$file" ]; then
    mkdir -p "$herdr_backup/$(dirname "$file")"
    cp -p "$HOME/$file" "$herdr_backup/$file"
    chmod 600 "$herdr_backup/$file"
  fi
done
```

`for` 逐个处理文件，`if -f` 只备份已存在的文件，`cp -p` 保留文件属性；目录权限 `700`、文件权限 `600` 将备份限制为当前用户访问。

安装并查看版本：

```bash
brew install herdr
herdr --version
herdr --help
```

在普通 Shell 中运行以下命令，首次创建默认会话，之后连接已有会话：

```bash
herdr
```

## 3. Herdr 配置与快捷键

### 3.1 config.toml 与重载

文件：`~/.config/herdr/config.toml`。

下方 `cmd+t`、`cmd+w` 等绑定需要外层终端先放行按键。使用 Ghostty 时，按 [Ghostty 的 Herdr 快捷键设置](Ghostty.md#herdr-keybindings)配置；这里保留 Herdr 接收按键后的动作。

Herdr 使用 `config.toml` 管理主题、侧栏、快捷键和行为。可以向 Agent 描述需要的效果，让它结合官方配置文档修改，但仍要校验配置。

```toml
# 本机配置已完成，直接进入工作区。
onboarding = false

[terminal]
default_shell = "/bin/zsh"
shell_mode = "login"

[theme.custom]
red = "#4e82ef"
teal = "#4e82ef"
yellow = "#a78bfa"
active_row_bg = "#45475a"

[keys]
prefix = "ctrl+b"
new_tab = ["prefix+c", "cmd+t"]
close_tab = ["prefix+shift+x", "cmd+w"]
goto = ["prefix+g", "cmd+k"]
previous_tab = ["prefix+p", "ctrl+alt+left"]
next_tab = ["prefix+n", "ctrl+alt+right"]
previous_workspace = "ctrl+alt+up"
next_workspace = "ctrl+alt+down"
cycle_pane_next = ["prefix+tab", "alt+up"]
cycle_pane_previous = ["prefix+shift+tab", "alt+down"]

[[keys.command]]
key = ["cmd+shift+g", "prefix+d"]
type = "popup"
command = "cd \"${HERDR_ACTIVE_PANE_CWD:-.}\" && exec lazygit"
description = "Git status"
width = "90%"
height = "85%"

[ui]
window_title = "{workspace} | {tab}"
show_agent_labels_on_pane_borders = true
agent_panel_sort = "priority"
prompt_new_tab_name = false
status_indicators = "dots"
copy_on_select = false

[ui.sidebar.agents]
row_gap = 1
rows = [["state_icon", "workspace"], ["tab"]]

[ui.sidebar.spaces]
row_gap = 1
rows = [["state_icon", "workspace"], ["branch", "git_status"]]

[ui.toast]
delivery = "herdr"

[ui.sound]
enabled = false
```

这里将 Shell 设为登录式 zsh，保留原有窗口标题、Agent 边框标签、应用内通知和静音。侧栏第一行显示状态和项目，第二行显示标签或 Git 分支；工作区额外保留 `git_status`。`copy_on_select = false` 表示选中文字后显式复制，不自动覆盖剪贴板。

修改后先检查，再重载正在运行的服务：

```bash
herdr config check
herdr server reload-config
```

看到 `config: ok` 和 `status: applied` 后，配置文件及服务端已接受变更。**在当前 Herdr 客户端再按 `Ctrl+b → Shift+r`**，使客户端外观、快捷键和选中服务端一起重载；无需停止服务。[配置参考](https://herdr.dev/tui/docs/config-reference/)

### 3.2 日常快捷键与鼠标

| 操作 | 快捷键 |
| --- | --- |
| 查看当前全部按键 | `Ctrl+b → ?` |
| 设置 | `Ctrl+b → s` |
| 重载当前客户端与服务端配置 | `Ctrl+b → Shift+r` |
| 切换工作区 | `Ctrl+b → w` |
| 搜索工作区、标签或 Agent | `Cmd+K` / `Ctrl+b → g` |
| 新建标签 | `Cmd+T` / `Ctrl+b → c` |
| 关闭标签及其中程序 | `Cmd+W` / `Ctrl+b → Shift+x` |
| 上一个 / 下一个标签 | `Ctrl+Option+←/→` / `Ctrl+b → p/n` |
| 上一个 / 下一个工作区 | `Ctrl+Option+↑/↓` |
| 跳到第 1～9 个标签 | `Ctrl+b → 1`～`9` |
| 重命名标签 | `Ctrl+b → Shift+t` |
| 左右 / 上下分屏 | `Ctrl+b → v/-` |
| 左 / 下 / 上 / 右面板 | `Ctrl+b → h/j/k/l` |
| 循环切换面板 | `Option+↑/↓` / `Ctrl+b → Tab/Shift+Tab` |
| 放大 / 还原当前面板 | `Ctrl+b → z` |
| 调整分屏尺寸 | 拖动边界，或 `Ctrl+b → r` |
| 显示 / 收起侧栏 | `Ctrl+b → b` |
| Lazygit 浮动窗口 | `Cmd+Shift+G` / `Ctrl+b → d` |
| 进入滚动与复制模式 | `Ctrl+b → [` |
| 跳转通知目标 | `Ctrl+b → o`，有可用通知目标时使用 |
| 暂时离开，后台继续 | `Ctrl+b → q` |

复制模式用方向键或 `h/j/k/l` 移动，`v` 开始选择，`y` 复制，`q` 退出；`Esc` 先取消选择或搜索，再按一次退出。鼠标选中后可用 `Ctrl+C` 复制。默认鼠标模式下用 Ctrl+单击打开网页链接。快捷键无效时，按“系统是否截获 → Ghostty 是否截获 → Herdr 是否重载”的顺序检查。

作者原配置使用 `Ctrl+方向键`，需要到系统设置 → 键盘 → 键盘快捷键 → Mission Control 取消四个冲突项。本机用其他组合，因此没有修改系统级快捷键。

提示音可在 Herdr Settings 中开启，或将 `[ui.sound] enabled` 改为 `true`；本机保持静音。`Ctrl+b → o` 跳的是通知目标，不能将它解释为无条件查找全部已完成 Agent。

`Cmd+K` 打开全局跳转窗口，可搜索工作区、标签和 Agent；视频演示先按 `/` 再输入关键字。

## 4. 工作区、项目与 worktree

多个有关联的仓库可以放在同一个 Session 中，例如一个产品的后端、移动端和管理文档；完全独立的工作也可另建命名会话。

### 4.1 使用现有工作区

```bash
herdr workspace list
```

首次配置一台新机器时，可执行：

```bash
herdr workspace create --cwd "/Users/michael/Documents/java_demo" --label "java_demo"
herdr workspace create --cwd "/Users/michael/Documents/flutter_demo" --label "flutter_demo"
```

### 4.2 单独的命名会话

在普通 Shell 中执行，避免在 Herdr 面板内再嵌套一层 TUI：

```bash
herdr session list
herdr --session app
# 以后重新连接同一会话：
herdr session attach app
```

可以让 `app` 会话管理后端、移动端等有关联的工作区，也可以继续使用目前的默认会话。创建新 Session 不会自动搬走旧 Session 中的工作区和进程；本次保留现有组织方式，没有新建重复项目。

### 4.3 添加已有 Git worktree

先确认它确实属于源仓库：

```bash
git -C "/Users/michael/Desktop/yuncai/kjxy/ios-kjxy" worktree list
```

例如源仓库为 `/Users/michael/Desktop/yuncai/kjxy/ios-kjxy`，已有 worktree 为 `/Users/michael/Desktop/yuncai/kjxy/refactor1.0`：

```bash
herdr worktree open \
  --cwd "/Users/michael/Desktop/yuncai/kjxy/ios-kjxy" \
  --path "/Users/michael/Desktop/yuncai/kjxy/refactor1.0" \
  --label "重构1.0"
```

- `--cwd` 确定源仓库。
- `--path` 指向已存在的 worktree。
- `--label` 设置显示名称。

需要新建 worktree 时可用 `Ctrl+b → Shift+g` 打开 Herdr 新建界面。

## 5. Agent 集成与状态

### 5.1 安装 Codex / OMP 集成

完成备份后运行：

```bash
herdr integration install codex
herdr integration install omp
herdr integration status
```

安装会写入 `~/.codex/herdr-agent-state.sh`、注册 `hooks.json` 的 `SessionStart` 事件，并确保 `config.toml` 中的 `[features] hooks = true`。

该 hook 向 Herdr 本机 socket 报告 Codex 会话身份，供重启后恢复对话使用；Codex 的工作状态仍由 Herdr 检测界面判断。

| 集成 | 写入或修改的文件 | 作用 |
| --- | --- | --- |
| Codex | `~/.codex/herdr-agent-state.sh`、`hooks.json`、`config.toml` | 注册 SessionStart，启用 hooks，记录原生会话身份 |
| OMP | `~/.omp/agent/extensions/herdr-omp-agent-state.ts` | 报告状态及原生会话，支持后续恢复 |

### 5.2 识别 Agent 工作状态

也可以在 Menu → Settings 的 Integrations 安装或更新 Agent 集成，并查看主题、状态指示和声音设置。

需要区分“屏幕上识别到了 Codex”和“已安装集成”。以本机 **Herdr 0.9.5** 为准，Codex v10 hook 只报告原生会话身份，工作状态主要由屏幕检测；OMP v10 扩展同时报告生命周期和会话。不能笼统说所有 Agent 都靠 hook 上报全部状态。

| 状态 | 含义 |
| --- | --- |
| `working` | 正在处理任务 |
| `blocked` | 等待问题回答或操作授权 |
| `done` | 在你查看别处时完成，尚未查看 |
| `idle` | 已查看，等待下一条提示词 |
| `unknown` | 无法可靠判断，不能据此认定完成 |

## 6. 用 Herdr skill 分派任务

Skill 是操作说明：主 Agent 读取后，可以通过 CLI 创建面板、启动另一个 harness、传递任务、等待状态变化并读取结果。视频演示 Codex 担任协调与评审者，让另一个 Claude 会话审核代码；具体模型及推理档位只是当时的示例。

适合的分工包括：规划 → 实现 → 评审；让另一种模型给第二意见；在旁边运行测试或开发服务器。每个 Agent 都在可见的终端会话中，用户可以切过去检查进度。视频还展示通过 CLI 在面板间传递消息，子任务完成后通知协调者继续；这需要委派流程显式安排消息与等待，不是任意 Agent 完成都会自动唤醒其他 Agent。Herdr 提供控制与通信能力，任务拆分和最终验收仍由主 Agent 和用户决定。

### 6.1 安装与更新

本次已在 Codex 技能目录安装与本机版本一致的官方 `herdr/SKILL.md`，并与 `herdr --skill` 输出核对。新技能会在后续对话轮次可用；已经运行的其他 Agent 若未发现它，可在任务结束后新开会话。

以后无需额外下载工具，也可以从本机二进制导出官方技能；若目录已经有自己的修改，先备份和比较：

```bash
mkdir -p "$HOME/.codex/skills/herdr"
herdr --skill > "$HOME/.codex/skills/herdr/SKILL.md"
```

作者的通用安装方法为 `npx skills add herdrdev/herdr --skill herdr -g`。本机采用 0.9.5 配套内容，避免仓库最新技能与已安装 CLI 不一致。[官方技能说明](https://herdr.dev/tui/docs/agent-skill/)

Integration、Skill、Plugin 三者独立：集成负责会话关联，技能教 Agent 操作 Herdr，插件给 Herdr 增加自动命名等功能。装了其中一项不等于另外两项也安装了。

### 6.2 可直接交给 Agent 的描述

在 **Herdr 面板内启动的 Codex** 中输入：

```text
使用 Herdr skill，在当前项目旁边创建一个面板，启动名为 reviewer 的 Codex。
让它只审核当前 Git diff，重点检查正确性、兼容性和测试遗漏，不修改文件。
保留我的焦点，等待它完成，读取结果后由你核查，最后向我报告有效问题。
遇到需要授权的操作先汇报；不要关闭现有面板或停止 Herdr Server。
```

实际开发时给清楚的任务范围、文件归属和验收标准。先用一个开发 Agent + 一个只读评审 Agent 熟悉流程，再增加并发；不要无目的同时启动许多会话。跨 harness 使用需要相应工具已经安装、登录并具有可用额度。每种需要主动操作 Herdr 的 harness 也必须加载该技能。本机 OMP 的 `skills.enableCodexUser = true`，复用 `~/.codex/skills/herdr`，不再重复安装同名副本。

### 6.3 理解底层命令

只在 Herdr 管理的面板中操作，先检查环境：

```bash
if [ "${HERDR_ENV:-}" = 1 ]; then
  herdr agent list
  herdr pane split --current --direction right --cwd "$PWD" --no-focus
else
  printf "%s\n" "请先在 Herdr 面板内启动 Agent，不在外部接管当前会话。"
fi
```

`split` 返回 JSON，其中 `result.pane.pane_id` 是新面板 ID。后续必须使用返回的真实值，不能照抄示例中的 `w1:p2`：

```bash
# 将下面的实际面板ID替换为 split 返回值
herdr agent start reviewer --kind codex --pane "实际面板ID"
herdr agent prompt reviewer "只审核当前 Git diff，不修改文件。" --wait --timeout 120000
herdr agent read reviewer --source recent-unwrapped --lines 120
```

Pane 命令控制普通终端，例如测试与开发服务器；Agent 命令还会检查智能体身份和工作状态。`--no-focus` 保留用户焦点，`--wait` 等待 idle、done 或 blocked；后两种情况的含义要结合实际输出判断。不得关闭自己未创建的面板，也不得把停止 Server 当作委派结束后的清理步骤。

## 7. Auto Title 自动命名

这是作者配套指南补充的第三方 Herdr 插件，用本地会话信息命名标签，不调用额外 LLM。当前插件默认模式在首次启动可能重命名已有 Pane，因此本机先设保护模式：

```bash
mkdir -p "$HOME/.config/herdr-auto-title"
```

在 `~/.config/herdr-auto-title/config.env` 写入：

```dotenv
HERDR_AUTO_TITLE_SESSION_ONLY=true
```

作者指南还安装 Go；当前 Auto Title 稳定版在 Apple Silicon 上优先下载预编译程序，只有源码构建路径才需要 Go。本次已安装 Go，今后单纯复用稳定版插件不必额外安装它。[Auto Title 安装说明](https://github.com/kryptamine/herdr-auto-title#install)

再安装稳定分支并启动插件：

```bash
herdr plugin install kryptamine/herdr-auto-title --ref stable
herdr plugin action invoke herdr.auto-title.restart
herdr plugin list
```

本次稳定版为 **0.22.2**。普通下载入口超时，Go 构建依赖站也连接超时，因此从 GitHub 官方 Releases API 下载程序与 `SHA256SUMS`，同时核对 SHA-256 和 API digest。随后下载相同版本的官方源码，使用 Herdr 官方支持的本地插件加载方式：

```text
~/.local/share/herdr-plugins/herdr-auto-title-v0.22.2/
├─ herdr-plugin.toml   官方版本清单
├─ herdr-auto-title    已校验的 macOS arm64 发布程序
└─ …                  同版本官方源码与许可证
```

```bash
herdr plugin link "$HOME/.local/share/herdr-plugins/herdr-auto-title-v0.22.2"
herdr plugin action invoke herdr.auto-title.restart
herdr plugin list
```

`plugin link` 不运行构建命令，因此必须先放好已校验的可执行程序。本次程序 SHA-256 为 `52926392defee3e27a2d9aa84a274737064a8018c2a9dc2ae66c8cf02db3d60b`。来源为[官方 0.22.2 Release](https://github.com/kryptamine/herdr-auto-title/releases/tag/v0.22.2)及[该版本源码](https://github.com/kryptamine/herdr-auto-title/tree/v0.22.2)，没有修改插件逻辑或系统 DNS/hosts，也没有永久改变 Git 网络设置。[Herdr install / link 区别](https://herdr.dev/tui/docs/plugins/#install-and-link)

此模式只镜像 Agent 已有的会话名称，没有可用名称时保留现状，保护原来的手工命名。普通 Shell 不会自动改成目录或进程名称；这与作者默认模式不同。`prompt_new_tab_name = false` 省去新建标签时的命名弹窗；手工重命名仍可以使用。

**本次是本地链接安装，`plugin update` 不会更新它。** 网络恢复后，可转为 GitHub 托管安装，保留自动命名配置：

```bash
herdr plugin unlink herdr.auto-title
herdr plugin install kryptamine/herdr-auto-title --ref stable
herdr plugin action invoke herdr.auto-title.restart
```

转为托管安装后，未来才使用 `herdr plugin update herdr.auto-title`，随后执行 restart。若安装失败，重新 `plugin link` 上面的已有目录即可恢复注册。停用时执行 `herdr plugin disable herdr.auto-title`；它不删除源码和配置。

不要为重启插件运行 `herdr server stop`。[插件配置及名称保护说明](https://github.com/kryptamine/herdr-auto-title#configuration)

## 8. 离开、关闭、恢复与升级

| 目的 | 操作 | 结果 |
| --- | --- | --- |
| 暂时离开 | `Ctrl+b → q` | 分离客户端，后台任务继续 |
| 回到默认会话 | 普通 Shell 中 `herdr` | 重新连接 |
| 回到命名会话 | `herdr --session app` | 连接或创建该会话 |
| 关闭当前面板 | `Ctrl+b → x` | 结束该面板及程序 |
| 关闭当前标签 | `Cmd+W` / `Ctrl+b → Shift+x` | 结束标签中的面板 |
| 关闭当前工作区 | `Ctrl+b → Shift+d` | 结束该工作区中的面板，保留项目文件 |
| 停止命令指向的 Server | `herdr server stop` | 结束该服务管理的全部面板进程 |
| 停止命名会话 | `herdr session stop app` | 结束 app 会话中的面板进程 |

`herdr server stop` 按命令继承的会话环境路由，不跟随用户当前聚焦的界面；外部普通 Shell 默认指向 `default`，Herdr 面板内则继承该面板的会话。要操作指定命名会话，使用显式的 `herdr session stop app`。

Mac 重启会结束原进程。Herdr 默认启用 Agent 会话恢复，依赖有效的集成记录与 Agent 自身会话；它是新进程恢复对话，不是旧进程继续运行。无法恢复时回到相应目录的新 Shell。实验性 pane history 只是保存屏幕内容，可能保存敏感终端输出，本机没有开启。[会话恢复说明](https://herdr.dev/tui/docs/session-state/)

Homebrew 安装由 Homebrew 升级：

```bash
brew upgrade herdr
herdr --version
herdr status
herdr integration status
```

兼容的旧 Server 可以继续工作；不要为了应用外观设置停止它。确需更换服务端时，在全部任务结束后才考虑停止和重启。`herdr update --handoff` 是另一种安装路径的实验功能，不适用于本机 Homebrew 安装。[TUI 安装与升级](https://herdr.dev/tui/docs/install/)

若以后使用远程服务器，可在普通终端运行 `herdr --remote 你的SSH别名`，此时界面在本机，面板进程在远端。先确认普通 SSH 能登录；本机这次没有配置远程机器。[SSH 与持久化](https://herdr.dev/tui/docs/persistence-remote/)

## 9. 配置记录与排查

2026-11-14 配置时，修改前已备份到 `~/.local/state/herdr-setup/20261114-010133`。备份只保存在本机；仓库中只保存操作说明。

- Herdr 配置校验与热重载通过。
- Codex Herdr skill 与本机二进制输出一致，OMP 复用 Codex 用户技能；`herdr agent list` 查询成功。
- Auto Title 0.22.2 已完成官方发布文件校验、本地插件注册并运行；restart 返回成功且后台进程存在。保留已有名称的配置已写入。更新方式见第 7 节。

日常开始工作：在终端运行 `herdr` → `Cmd+K` 找项目 → 新建标签 → 确认项目目录 → 运行 `codex` 或 `omp`。Herdr 中的代码浏览和 Git 审核操作见 [Neovim](Neovim.md) 与 [Lazygit](lazygit.md)。

| 现象 | 检查方法 |
| --- | --- |
| `Cmd+T` 仍创建外层终端标签 | 检查终端是否已放行快捷键；Ghostty 的操作见 [快捷键设置](Ghostty.md#herdr-keybindings) |
| Herdr 颜色或快捷键还是旧的 | `herdr config check`，然后 `Ctrl+b → Shift+r` |
| 自动命名没有变化 | 是否启用插件、会话是否有可用名称；手工名称和普通 Shell 在保护模式下会保留 |
| 更新二进制后服务行为没变 | `herdr status` 比较 client/server，先评估任务再决定是否重启 |

查看配置与备份目录：

```bash
open "$HOME/.config/herdr"
open "$HOME/.local/state/herdr-setup"
```

恢复时选择本次日期对应的备份，先比较当前文件，避免覆盖之后的新改动；恢复 Herdr 配置后重新校验并重载。不要把整个旧 Codex 配置不加比较地覆盖回去。
