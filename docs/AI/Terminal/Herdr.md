# Herdr 多项目终端配置

## 1. 视频全部知识点

### 1.1 整套工作流（00:00）

| 工具 | 负责什么 |
| --- | --- |
| Herdr integration | 将 Agent 原生会话与 Herdr 关联，支持状态识别或对话恢复 |
| Herdr skill | 教 Agent 使用 Herdr CLI 分派任务、读取其他 Agent 的输出 |
| zoxide + fzf | 根据目录名称快速进入项目 |

### 1.2 安装、后台服务与持久会话（01:00）

Herdr 的模型类似 tmux：终端窗口显示的是客户端，后台 Server 管理真正的 Shell、Agent 和进程。关闭窗口或退出终端应用后，只要本机服务仍在，任务可以继续；重新运行 Herdr，能回到相同布局和会话。

### 1.4 Space、Tab 与 Pane（05:30）

```text
Session（会话，例如 default）
├─ Workspace / Space（项目，例如 java_demo）
│  ├─ Tab（标签，例如后端开发）
│  │  ├─ Pane（面板，运行 Codex）
│  │  └─ Pane（面板，运行测试）
│  └─ Tab（标签，例如查看代码）
└─ Workspace（项目，例如 flutter_demo）
```

通常一个仓库对应一个工作区，一个工作区可以有多个标签，每个标签又可以分屏。左侧 Spaces 展示项目，Agents 集中展示实际运行的智能体；普通 Shell 不会因为创建了一个标签就自动变成 Agent。

鼠标可以点击工作区、标签或面板切换，拖动分屏边界调整尺寸，右键使用分屏、重命名和关闭菜单。可以先用鼠标熟悉结构，再学快捷键。进入项目最基本的方法仍是复制路径并执行 `cd`。

### 1.5 连接编码智能体（08:21）

视频从 Menu → Settings 查看主题、状态指示和声音，并在 Integrations 安装或更新 Agent 集成。命令行也能完成同样的安装。

需要区分“屏幕上识别到了 Codex”和“已安装集成”。以本机 **Herdr 0.9.5** 为准，Codex v10 hook 只报告原生会话身份，工作状态主要由屏幕检测；OMP v10 扩展同时报告生命周期和会话。不能笼统说所有 Agent 都靠 hook 上报全部状态。

| 状态 | 含义 |
| --- | --- |
| `working` | 正在处理任务 |
| `blocked` | 等待问题回答或操作授权 |
| `done` | 在你查看别处时完成，尚未查看 |
| `idle` | 已查看，等待下一条提示词 |
| `unknown` | 无法可靠判断，不能据此认定完成 |

### 1.6 多项目与命名会话（09:19）

视频继续创建第二个项目、启动另一个 Agent，再演示退出和重新连接。多个有关联的仓库可以放在同一个 Session 中，例如一个产品的后端、移动端和管理文档；完全独立的工作也可另建命名会话。

`herdr` 连接默认会话；`herdr --session demo` 连接或创建 `demo`。`herdr session list` 查看会话，`herdr --help` 查本机支持的命令。新工作区、新标签和分屏的起始目录可能不同，先运行 `pwd` 确认，不要假设总在用户主目录。

### 1.7 配色、间距与 config.toml（12:32）

Herdr 使用 `config.toml` 管理主题、侧栏、快捷键和行为。可以向 Agent 描述需要的效果，让它结合官方配置文档修改，但仍要校验配置。

作者的颜色语义是：蓝色代表“需要看一下”（等待输入或完成），紫色代表“还在工作”；每个侧栏条目分两行，并按需要关注的优先级排序。字段名 `red`、`yellow`、`teal` 是主题颜色标识，不要求最终颜色必须是红、黄、青。

作者公开配置关闭声音；视频口头提到完成时的提示音和跳转热键，是可选工作方式，不代表本机已经开启声音。

### 1.8 默认前缀与直接快捷键（13:39）

默认前缀是 `Ctrl+b`：按下、松开，再按动作键。例如 `Ctrl+b → c` 创建标签，不是三个键一起按。

作者给常用动作加上直接按键：`Cmd+T` 新标签、`Cmd+W` 关标签、`Cmd+K` 全局跳转，方向键组合切换标签或项目。全局跳转窗口可以搜索工作区、标签和 Agent，视频演示先按 `/` 再输入关键字。快捷键可以同时保留前缀版本和直接版本。

本机保留 `Ctrl+b`，没有改成作者欧洲键盘上的 `§`；把作者的 `Ctrl+方向键` 改为 **`Ctrl+Option+方向键`**，保留 macOS Mission Control 原快捷键。视频提到的“全局唤起终端”和“跳到完成 Agent”没有给出具体键值，不应凭字幕猜测；后文给出官方功能与可选设置。

### 1.9 Herdr skill 与多 Agent 委派（17:48）

Skill 是操作说明：主 Agent 读取后，可以通过 CLI 创建面板、启动另一个 harness、传递任务、等待状态变化并读取结果。视频演示 Codex 担任协调与评审者，让另一个 Claude 会话审核代码；具体模型及推理档位只是当时的示例。

适合的分工包括：规划 → 实现 → 评审；让另一种模型给第二意见；在旁边运行测试或开发服务器。每个 Agent 都在可见的终端会话中，用户可以切过去检查进度。视频还展示通过 CLI 在面板间传递消息，子任务完成后通知协调者继续；这需要委派流程显式安排消息与等待，不是任意 Agent 完成都会自动唤醒其他 Agent。Herdr 提供控制与通信能力，任务拆分和最终验收仍由主 Agent 和用户决定。

`blocked` 表示需要处理问题，不是成功完成；等待超时也不代表提示词没发出去，不能直接重复发送。多个 Agent 同时改同一批文件仍可能冲突，需要事先分配文件范围或使用独立 Git worktree。

### 1.11 zoxide 快速进入目录（24:39）

zoxide 根据访问记录匹配目录。`z java_demo` 直接跳到最匹配的目录；**`zi` 是字母 i，不是字幕识别出的 `zy`**，它用 fzf 打开交互搜索列表。首次访问仍需要完整路径，之后才会记住。

日常流程可以是：新建 Herdr 标签 → `z flutter_demo` → `codex` 或 `omp`。目录导航是 Shell 工具能力，不是 Herdr 创建工作区的替代命令；在现有工作区中 `cd` 不会自动变成另一个工作区。

## 2. 安装前备份与工具准备

以下命令在本机 **zsh / Bash 终端**执行，是 Shell 命令。`$(date ...)` 把当前时间填入备份目录名。

修改前先备份实际涉及的配置，不把账号凭据复制到知识库：

```bash
herdr_backup="$HOME/.local/state/herdr-setup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$herdr_backup"
chmod 700 "$herdr_backup"
for file in \
  ".config/herdr/config.toml" \
  "Library/Application Support/com.mitchellh.ghostty/config.ghostty" \
  ".zshrc" \
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

首次安装相关工具：

```bash
brew install herdr zoxide fzf fd bat eza
brew install --cask ghostty
```

已安装的工具不必重装。`fd` 用于查找文件，`bat` 和 `eza` 是辅助阅读工具。代码浏览和差异审核工具的安装、备份分别见 [Neovim](Neovim.md) 和 [Lazygit + Delta](lazygit.md)。

作者指南还安装 Go；当前 Auto Title 稳定版在 Apple Silicon 上优先下载预编译程序，只有源码构建路径才需要 Go。本次已安装 Go，今后单纯复用稳定版插件不必额外安装它。[Auto Title 安装说明](https://github.com/kryptamine/herdr-auto-title#install)

## 3. Ghostty 配置

本机使用已有文件：

```text
~/Library/Application Support/com.mitchellh.ghostty/config.ghostty
```

可以用 `Cmd+,` 打开 Ghostty 当前配置文件，或定位本机文件：

```bash
open -R "$HOME/Library/Application Support/com.mitchellh.ghostty/config.ghostty"
```

本次配置如下，含作者公开的配色与按键让渡：

```ini
# 将这些快捷键交给 Herdr / Neovim。
keybind = super+t=unbind
keybind = super+w=unbind
keybind = super+k=unbind
keybind = super+e=unbind
keybind = super+shift+g=unbind
background = #1D1E27
foreground = #FDFDFD
font-size = 14
window-padding-x = 10
window-padding-y = 8
cursor-style = bar
cursor-style-blink = false
scrollback-limit = 100000
macos-option-as-alt = true
palette = 0=#282A2B
palette = 1=#F3977F
palette = 2=#5ADECD
palette = 3=#F272A2
palette = 4=#886F97
palette = 5=#C574DD
palette = 6=#79E6F3
palette = 7=#FDFDFD
palette = 8=#415844
palette = 9=#FF4971
palette = 10=#18E3C8
palette = 11=#FF8037
palette = 12=#556FFF
palette = 13=#B0D143
palette = 14=#3FDCEE
palette = 15=#BEBEC1
```

`super` 在 macOS 对应 Command；`unbind` 让外层终端不再截获按键。`macos-option-as-alt` 使 Option 作为 Alt 传入终端程序。`scrollback-limit` 单位是**字节**，不是“保留多少行”。[Ghostty 配置参考](https://ghostty.org/docs/config/reference)

校验与生效：

```bash
ghostty +validate-config
```

无输出、退出码为 0 表示校验通过。在 Ghostty 按 **`Cmd+Shift+,`** 重载。释放快捷键后，普通 Ghostty Shell 中 `Cmd+T` 不再创建 Ghostty 标签；进入 Herdr 后才由 Herdr 处理。需要外层新窗口时可使用 Ghostty 菜单。

## 4. Herdr 配置、集成与自动命名

### 4.1 本机完整 config.toml

文件：`~/.config/herdr/config.toml`。

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

修改后执行：

```bash
herdr config check
herdr server reload-config
```

看到 `config: ok` 和 `status: applied` 后，配置文件及服务端已接受变更。**在当前 Herdr 客户端再按 `Ctrl+b → Shift+r`**，使客户端外观、快捷键和选中服务端一起重载；无需停止服务。[配置参考](https://herdr.dev/tui/docs/config-reference/)

### 4.2 Codex / OMP 官方集成

完成备份后运行：

```bash
herdr integration install codex
herdr integration install omp
herdr integration status
```

本次两项均验证为 **`current (v10)`**。只为实际使用的工具安装；列表中其他 Agent 显示 `not installed` 不代表故障。

| 集成 | 写入或修改的文件 | 作用 |
| --- | --- | --- |
| Codex | `~/.codex/herdr-agent-state.sh`、`hooks.json`、`config.toml` | 注册 SessionStart，启用 hooks，记录原生会话身份 |
| OMP | `~/.omp/agent/extensions/herdr-omp-agent-state.ts` | 报告状态及原生会话，支持后续恢复 |

Codex v10 会清理 Herdr 自己旧的回合状态 hooks，只保留 SessionStart；这是 0.9.5 的官方兼容性修复，不是删除其他工具的 hooks。本次已比较备份，确认其他 hooks 与非 Herdr 的 Codex 设置保留。等待当前任务结束后，新开 Agent 会话使用新集成，不为更新 hooks 强行结束任务。[官方集成说明](https://herdr.dev/tui/docs/integrations/)、[v0.9.5 说明](https://github.com/herdrdev/herdr/blob/v0.9.5/CHANGELOG.md)

### 4.3 Auto Title 自动命名

这是作者配套指南补充的第三方 Herdr 插件，用本地会话信息命名标签，不调用额外 LLM。当前插件默认模式在首次启动可能重命名已有 Pane，因此本机先设保护模式：

```bash
mkdir -p "$HOME/.config/herdr-auto-title"
```

在 `~/.config/herdr-auto-title/config.env` 写入：

```dotenv
HERDR_AUTO_TITLE_SESSION_ONLY=true
```

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

## 5. 项目、会话与 worktree

### 5.1 本机 Server 在哪里？

**本机 Herdr Server 是运行在这台 Mac 上的后台服务，不在云端。** “Server”描述它的职责，不表示它是一台云服务器。

| 部分 | 作用 |
| --- | --- |
| Client | Ghostty 中看到的 Herdr 界面 |
| Server | 后台管理各工作区的面板、Shell 和 Agent 进程 |
| 本机 socket | Client 与 Server 通信的入口，不是互联网地址 |

```bash
herdr status
```

本机默认会话 socket 为 `~/.config/herdr/herdr.sock`。Herdr 在本机运行，不等于模型也在本机运行：Codex、OMP 将请求发到哪里，由它们自己的模型提供方配置决定。

### 5.2 使用现有工作区

```bash
herdr workspace list
```

本机已有 `java_demo`、`flutter_demo` 等工作区，无需重复创建。首次配置一台新机器时，可执行：

```bash
herdr workspace create --cwd "/Users/michael/Documents/java_demo" --label "java_demo"
herdr workspace create --cwd "/Users/michael/Documents/flutter_demo" --label "flutter_demo"
```

每条命令创建工作区及其首个标签、Shell 面板。进入某个面板后：

```bash
pwd
cd "/Users/michael/Documents/flutter_demo"
codex
# 或运行 omp
```

`pwd` 是 print working directory，显示当前目录；`cd` 修改当前 Shell 所在目录。Java 与 Flutter 不必移动到同一个物理文件夹中。

### 5.3 单独的命名会话

在普通 Shell 中执行，避免在 Herdr 面板内再嵌套一层 TUI：

```bash
herdr session list
herdr --session app
# 以后重新连接同一会话：
herdr session attach app
```

可以让 `app` 会话管理后端、移动端等有关联的工作区，也可以继续使用目前的默认会话。创建新 Session 不会自动搬走旧 Session 中的工作区和进程；本次保留现有组织方式，没有新建重复项目。

### 5.4 添加已有 Git worktree

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

`--cwd` 确定源仓库，`--path` 指向已存在的 worktree，`--label` 设置显示名称。以后再添加另一个已有 worktree，使用它自己的路径重复此命令，不覆盖原工作区。需要新建 worktree 时可用 `Ctrl+b → Shift+g` 打开 Herdr 新建界面，明确新分支和目录；“打开已有 worktree”不会代替创建分支。

## 6. 日常快捷键与鼠标

下表对应**本机配置**，`→` 表示先按前缀、松开，再按后一个键；Option 就是 Alt。

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

可选补充：视频提到全局唤起终端，但未展示配置。Ghostty 官方可使用 `keybind = global:ctrl+grave_accent=toggle_quick_terminal` 设置快速终端；这是另一项全局快捷键，可能需要系统授权，本机未启用。可先用 Spotlight 打开 Ghostty，再运行 `herdr`。[Ghostty 快捷键说明](https://ghostty.org/docs/config/keybind)

提示音可在 Herdr Settings 中开启，或将 `[ui.sound] enabled` 改为 `true`；本机保持静音。`Ctrl+b → o` 跳的是通知目标，不能将它解释为无条件查找全部已完成 Agent。

## 7. 用 Herdr skill 分派任务

### 7.1 安装与更新

本次已在 Codex 技能目录安装与本机版本一致的官方 `herdr/SKILL.md`，并与 `herdr --skill` 输出核对。新技能会在后续对话轮次可用；已经运行的其他 Agent 若未发现它，可在任务结束后新开会话。

以后无需额外下载工具，也可以从本机二进制导出官方技能；若目录已经有自己的修改，先备份和比较：

```bash
mkdir -p "$HOME/.codex/skills/herdr"
herdr --skill > "$HOME/.codex/skills/herdr/SKILL.md"
```

作者的通用安装方法为 `npx skills add herdrdev/herdr --skill herdr -g`。本机采用 0.9.5 配套内容，避免仓库最新技能与已安装 CLI 不一致。[官方技能说明](https://herdr.dev/tui/docs/agent-skill/)

Integration、Skill、Plugin 三者独立：集成负责会话关联，技能教 Agent 操作 Herdr，插件给 Herdr 增加自动命名等功能。装了其中一项不等于另外两项也安装了。

### 7.2 可直接交给 Agent 的描述

在 **Herdr 面板内启动的 Codex** 中输入：

```text
使用 Herdr skill，在当前项目旁边创建一个面板，启动名为 reviewer 的 Codex。
让它只审核当前 Git diff，重点检查正确性、兼容性和测试遗漏，不修改文件。
保留我的焦点，等待它完成，读取结果后由你核查，最后向我报告有效问题。
遇到需要授权的操作先汇报；不要关闭现有面板或停止 Herdr Server。
```

实际开发时给清楚的任务范围、文件归属和验收标准。先用一个开发 Agent + 一个只读评审 Agent 熟悉流程，再增加并发；不要无目的同时启动许多会话。跨 harness 使用需要相应工具已经安装、登录并具有可用额度。每种需要主动操作 Herdr 的 harness 也必须加载该技能。本机 OMP 的 `skills.enableCodexUser = true`，复用 `~/.codex/skills/herdr`，不再重复安装同名副本。

### 7.3 理解底层命令

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

## 8. zoxide、fzf 与 Shell 辅助工具

在 `~/.zshrc` 末尾加入以下内容。已有同类初始化时合并，不重复添加：

```zsh
export BAT_THEME="TwoDark"
export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border --cycle'
if [[ -t 0 && -t 1 ]] && command -v fzf >/dev/null; then
  source <(fzf --zsh)
fi
command -v zoxide >/dev/null && eval "$(zoxide init zsh)"
alias ll='eza -la'
alias tree='eza --tree'
```

本机已有 PATH、Java、Flutter 和 `VISUAL` 设置，均保留；没有把系统 `ls`、`cat` 全局替换。需要带语法色阅读文件时直接使用 `bat 文件名`；`ll` 和 `tree` 分别显示详细目录和目录树。

新开一个 Shell 后使用：

```bash
cd "/Users/michael/Documents/java_demo"
cd "/Users/michael/Documents/flutter_demo"
z java_demo
zi
```

`zi` 中输入关键字、方向键选择、Enter 进入目录、Esc 取消。视频还演示输入 `z 目录关键字` 后按 Tab 补全；它依赖 zsh 补全初始化，本机已有 `compinit`。第一次记录后，其他新 Shell 也能使用记录。也可以显式初始化常用项目：

```bash
zoxide add "/Users/michael/Documents/java_demo"
zoxide add "/Users/michael/Documents/flutter_demo"
zoxide add "/Users/michael/Documents/michaelssman.github.io"
zoxide query java_demo
```

本次已初始化上述目录，并在新的登录式 zsh 中验证 `z java_demo`、`z flutter_demo` 返回正确路径。若老面板提示找不到 `z`，它尚未加载修改后的 `.zshrc`；在空闲 Shell 中 `source "$HOME/.zshrc"` 或新建面板即可，不要把此命令输入运行中的 Agent 对话。[zoxide 安装与 Shell 初始化](https://github.com/ajeetdsouza/zoxide#installation)、[fzf Shell 集成](https://github.com/junegunn/fzf#setting-up-shell-integration)

## 9. 离开、关闭、恢复与升级

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

## 10. 本次配置记录与验证

本次修改前已备份到 `~/.local/state/herdr-setup/20261114-010133`。备份只保存在本机；仓库中只保存操作说明。

- Herdr 配置校验与热重载通过。
- Codex Herdr skill 与本机二进制输出一致，OMP 复用 Codex 用户技能；`herdr agent list` 查询成功。
- zoxide 0.10.0 / fzf 0.75.0 已初始化，Java、Flutter 项目跳转通过。
- Auto Title 0.22.2 已完成官方发布文件校验、本地插件注册并运行；restart 返回成功且后台进程存在。保留已有名称的配置已写入。更新方式见第 4.3 节。

日常开始工作：打开 Ghostty → `herdr` → `Cmd+K` 找项目 → 新建标签 → `pwd` 检查目录 → 运行 `codex` 或 `omp`。代码浏览和 Git 审核的操作见 [Neovim](Neovim.md) 与 [Lazygit](lazygit.md)。

| 现象 | 检查方法 |
| --- | --- |
| `Cmd+T` 仍创建 Ghostty 标签 | Ghostty 配置是否重载、是否编辑了另一份文件 |
| Herdr 颜色或快捷键还是旧的 | `herdr config check`，然后 `Ctrl+b → Shift+r` |
| 新 Shell 没有 `z` / `zi` | 检查工具路径、`.zshrc` 初始化和 fzf 是否安装 |
| 自动命名没有变化 | 是否启用插件、会话是否有可用名称；手工名称和普通 Shell 在保护模式下会保留 |
| 更新二进制后服务行为没变 | `herdr status` 比较 client/server，先评估任务再决定是否重启 |

查看配置与备份目录：

```bash
open "$HOME/.config/herdr"
open "$HOME/.local/state/herdr-setup"
```

恢复时选择本次日期对应的备份，先比较当前文件，避免覆盖之后的新改动；恢复 Herdr/Ghostty 配置后分别重载。不要把整个旧 Codex 配置不加比较地覆盖回去。
