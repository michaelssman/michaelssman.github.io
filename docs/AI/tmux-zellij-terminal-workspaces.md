# tmux 与 Zellij：终端复用器入门与开发工作区管理

> 适用场景：使用 Ghostty 和 Codex CLI，同时处理多个项目、需求或 Git worktree，希望减少终端标签混乱。
>
> 本文是概念与操作入门，不是完整的自动化环境配置手册。命令以工具已经安装为前提；示例项目名称和目录需要替换为实际值。命令依据官方文档整理，未在你的本机环境执行。

## 1. tmux 和 Zellij 是什么？

**tmux 和 Zellij 都可以作为终端复用器使用：在一个终端界面中，组织多个终端程序，并支持会话的分离与重新连接。** tmux 使用“会话—窗口—面板”组织程序；Zellij 将自己定位为终端工作区，提供标签、面板和布局等能力。[1] [2] [3]

可以把它们理解为“终端里的工作区管理器”，而不是另一个代码编辑器。

它们主要解决两类问题：一类是同时管理多个 Shell、开发服务、日志和交互程序；另一类是暂时断开终端界面后，重新连接仍在运行的会话。[1] [6]

**基本分工：Ghostty 提供终端界面，tmux 或 Zellij 组织工作区，Codex CLI 等程序运行在工作区里面。**[1] [3] [10] [12]

## 2. 为什么多项目开发需要它们？

只依靠 Ghostty 标签管理任务时，工作环境可能逐渐变成这样：

```text
Ghostty 标签栏
├── 项目 A：登录功能
├── 项目 A：登录功能的 Shell
├── 项目 A：支付问题修复
├── 项目 A：开发服务
├── 项目 B：代码重构
├── 项目 B：测试
└── 其他日志、临时命令……
```

这是一个示例：标签数量不断增长，但“项目、需求、程序”混在同一层级里，查找时需要反复辨认。

可以改为下面的组织约定：

```text
项目 A：一个会话
├── 登录功能：一个窗口或标签
│   ├── Codex CLI
│   ├── Shell / Git 检查
│   └── 测试或开发服务
└── 支付问题修复：另一个窗口或标签
    ├── Codex CLI
    └── Shell / Git 检查

项目 B：另一个会话
└── 代码重构：一个窗口或标签
    ├── Codex CLI
    └── 测试
```

**关键不是把几十个 Ghostty 标签原样搬到另一个标签栏，而是先按“项目 → 需求 → 程序”分层。**

## 3. 先理解三层结构

### 3.1 Session、Window / Tab、Pane

两者的入门概念可以这样对应。[1] [2] [3] [9]

| 层级 | tmux 中的名称 | Zellij 中的名称 | 本文建议用途 |
| --- | --- | --- | --- |
| 工作区分组 | Session，会话 | Session，会话 | 一个项目 |
| 会话内部的工作页面 | Window，窗口 | Tab，标签 | 一个需求或 worktree |
| 页面中的终端区域 | Pane，面板 | Pane，面板 | Codex、Shell、测试、日志等 |

其中，tmux 的 Window 是终端内部的逻辑窗口，**不是 macOS 的独立应用窗口**。[1]

“一个项目对应一个会话”是组织建议，不是工具强制规则。任务规模较大时，也可以让每个 worktree 单独对应一个会话。

### 3.2 与 Ghostty、Git worktree、Codex CLI 的关系

| 工具 | 主要职责 |
| --- | --- |
| Ghostty | 终端模拟器，提供显示和交互界面。[10] |
| tmux / Zellij | 管理会话、窗口或标签、面板，以及终端程序的组织与连接。[1] [3] [6] |
| Git worktree | 为同一个 Git 仓库提供多个工作目录，便于同时检出和处理不同分支。[11] |
| Codex CLI | 在终端中读取、修改代码和运行开发工具的编程智能体。[12] |

推荐把“物理代码目录”和“终端组织层级”分开理解：

```text
Ghostty 中的一个终端界面
└── 连接到会话：ecommerce
    ├── 标签 / 窗口：feature-login
    │   ├── 面板：Codex CLI
    │   ├── 面板：Shell
    │   └── 面板：测试
    └── 标签 / 窗口：fix-payment
        ├── 面板：Codex CLI
        └── 面板：Shell

代码目录（通过 Git worktree 另行管理）
├── ecommerce-main/
├── ecommerce-login/
└── ecommerce-payment/
```

**给标签起名为 `feature-login`，不等于创建 worktree 或自动切换目录。** 仍需让对应面板进入正确的工作目录，或在后续布局配置中明确设置目录。[6] [9] [11]

## 4. tmux：以命令和前缀快捷键管理终端

tmux 既能通过快捷键交互操作，也能通过命令和脚本管理会话、窗口与面板。[1] [2]

### 4.1 基本会话命令

下面这些命令在普通终端 Shell 中执行。先任选一种方式创建或连接会话，不需要把整段逐行连续执行。[1] [2]

```bash
# 创建一个名为 project-a 的新会话并进入
# 如果同名会话已经存在，改用下面的连接命令
tmux new -s project-a

# 查看已有会话
tmux ls

# 连接已有会话
tmux attach -t project-a

# 存在就连接，不存在就创建
tmux new -A -s project-a
```

从当前会话暂时离开，使用 **Detach（分离）**：按下 `Ctrl+b`，松开，再按 `d`。这会返回外层 Shell，而不是结束会话内的程序。[1]

### 4.2 常用快捷键

以下按 tmux 默认键位整理。`Ctrl+b → c` 表示先按 `Ctrl+b`，松开后再按 `c`，不是同时按三个键。[1] [2]

| 操作 | 默认快捷键 |
| --- | --- |
| 新建窗口 | `Ctrl+b → c` |
| 重命名当前窗口 | `Ctrl+b → ,` |
| 下一个 / 上一个窗口 | `Ctrl+b → n` / `Ctrl+b → p` |
| 左右分屏 | `Ctrl+b → %` |
| 上下分屏 | `Ctrl+b → "` |
| 切换到相邻面板 | `Ctrl+b → 方向键` |
| 放大当前面板 / 恢复布局 | `Ctrl+b → z` |
| 打开会话选择树 | `Ctrl+b → s` |
| 打开窗口选择树 | `Ctrl+b → w` |
| 分离当前连接 | `Ctrl+b → d` |
| 查看快捷键帮助 | `Ctrl+b → ?` |

对于“标签太多、难以查找”的问题，**`Ctrl+b → s` 和 `Ctrl+b → w` 比单纯增加分屏更重要**：它们提供会话、窗口的树形选择入口。[1]

### 4.3 一个工作页面的示例

```text
当前会话：project-a
当前窗口：feature-login

┌───────────────────────┬───────────────────────┐
│ Codex CLI             │ Shell / Git 检查      │
│                       │                       │
├───────────────────────┴───────────────────────┤
│ 测试 / 开发服务 / 日志                         │
└───────────────────────────────────────────────┘
```

这是布局示意，不是执行上面的创建命令后会自动出现的配置。需要自行分屏、进入目录并启动程序。

## 5. Zellij：以标签、模式和布局组织终端工作区

Zellij 提供终端工作区、布局和插件机制；快捷键按模式组织，可以自定义。对初学者，建议先按当前界面的操作提示使用，再逐步记忆键位。[3] [5] [9]

**不要把某张截图中的按键提示理解成所有版本都通用的快捷键。** 界面提示、键位预设和自定义配置可能不同。[5]

### 5.1 基本会话命令

以下命令在普通终端 Shell 中执行，按当前需要选择一条。[4]

```bash
# 创建或连接名为 project-a 的会话
zellij attach --create project-a

# 列出会话；也可能显示可恢复的已退出会话
zellij list-sessions

# 连接指定会话
zellij attach project-a
```

如果连接的是已退出、但有恢复数据的会话，Zellij 可能进入“会话重建”，而不是连接原来的运行进程。[7]

### 5.2 在会话中管理标签和分屏

下面的命令在 **Zellij 会话内的 Shell 面板**中执行，不要输入到 Codex 的对话框。日常操作也可以使用界面提示对应的快捷键。[6]

```bash
# 新建名为 feature-login 的标签
zellij action new-tab --name feature-login

# 在当前面板右侧新增面板，形成左右分屏
zellij action new-pane --direction right

# 在当前面板下方新增面板，形成上下分屏
zellij action new-pane --direction down

# 重命名当前标签
zellij action rename-tab feature-login

# 分离当前连接，让会话继续在后台运行
zellij action detach
```

这些也是独立的操作示例，不要求连续执行全部命令。执行新建标签或面板后，注意当前焦点已经可能改变。[6]

### 5.3 键位和配置以本机为准

可以查看本机版本及其默认配置；下面的配置命令只输出文本，不会覆盖现有配置文件。[4]

```bash
zellij --version
zellij setup --dump-config
```

开始阶段，先掌握“新建标签、分屏、重命名、切换会话、Detach”即可。固定布局和插件可以放到第二阶段学习。

## 6. tmux 与 Zellij 怎么选？

下表侧重操作方式，不对稳定性、性能或插件数量做没有统一测试依据的星级排名。[1] [2] [3] [5] [7] [9]

| 比较项 | tmux | Zellij |
| --- | --- | --- |
| 基本层级 | Session → Window → Pane | Session → Tab → Pane |
| 交互方式 | 前缀快捷键、命令提示符、Shell 命令 | 模式化键位、界面操作、Shell 命令 |
| 查找工作区 | 会话与窗口选择树 | 内置会话管理器 |
| 布局组织 | 通过布局命令和脚本组织窗口与面板 | 通过布局文件组织标签与面板 |
| 临时断开与重连 | 支持 Detach / Attach | 支持 Detach / Attach |
| 退出后的恢复 | 不应将普通 Attach 当作跨重启恢复 | 内置会话重建，但不是恢复原进程内存 |

**针对 Ghostty + Codex CLI + 多项目 / 多 worktree 的使用场景，建议先试 Zellij。** 这是基于希望降低标签管理和入门操作负担的取舍，不是认定它在所有方面都优于 tmux。

已经习惯 tmux 的前缀键、希望用脚本精确控制终端，或工作环境已有 tmux 配置时，继续使用 tmux 同样合理。

起步阶段选择一种即可，不必同时叠加 tmux 和 Zellij。

## 7. 适合多 worktree 的组织方案

### 7.1 优先方案：项目对应会话，worktree 对应标签

```text
会话：ecommerce
├── 标签 / 窗口：main
├── 标签 / 窗口：feature-login
│   ├── Codex
│   ├── Shell
│   └── Tests
└── 标签 / 窗口：fix-payment
    ├── Codex
    └── Shell

会话：backend-api
├── 标签 / 窗口：main
└── 标签 / 窗口：refactor-auth
    ├── Codex
    ├── Shell
    └── Tests
```

命名建议采用“会话写项目名，标签写任务名，面板写用途”。避免所有标签都叫 `zsh`、`codex` 或 `terminal`，也不要在每一层重复完整项目名。

任务非常多、需要独立开关整个任务环境时，可以改成“每个 worktree 一个会话”，例如 `ecommerce-login`、`ecommerce-payment`。两种方式都只是工作约定。

### 7.2 让同一任务的面板进入同一个 worktree

假设已经存在登录功能对应的 worktree：`~/code/ecommerce-login`。

在 Codex 面板中执行：[12]

```bash
cd "$HOME/code/ecommerce-login" && codex
```

另开一个 Shell 面板，明确进入相同目录，再检查代码状态：[11]

```bash
cd "$HOME/code/ecommerce-login" && git status
```

测试或开发服务面板同样先进入该目录，再运行项目实际使用的命令。服务端口、数据库等共享资源需要另行规划，**worktree 不是容器，也不是完整的运行环境隔离机制**。[11]

即使标签名称正确，也建议启动任务前核对当前路径与分支。不要仅凭标签名判断 Codex 将修改哪个目录。

### 7.3 保持 Ghostty 外层简单

建议先保留少量 Ghostty 窗口或标签，把项目和任务的日常切换交给 tmux / Zellij。两层标签都可以使用，但需要明确各层职责。

这套方案的最小组合是：

```text
Ghostty
  + tmux 或 Zellij（二选一）
  + Git worktree
  + Codex CLI
```

提示符主题、目录搜索和额外插件不是建立这套组织方式的前提，先把会话命名与目录对应关系固定下来。

## 8. 使用前必须明确的边界

### 8.1 Detach 不等于 Quit，也不等于关闭面板

**Detach 只是断开当前终端连接；退出会话、结束进程或关闭面板属于不同操作。** 临时离开但希望任务继续运行时，优先使用明确的 Detach 操作。[1] [6]

### 8.2 关闭 Ghostty 后，任务不是无条件保留

任务能否继续，取决于会话服务端和程序是否仍在运行，以及关闭操作和配置的行为。例如，Zellij 提供 `on_force_close` 设置，用来选择收到关闭信号时执行分离还是退出。[1] [8]

建议先用一个无关紧要的测试会话确认本机行为，再依赖它保留长时间运行的任务。

### 8.3 跨重启恢复布局，不等于恢复原进程

正在运行的会话可以重新连接；机器重启后，原进程已经结束。Zellij 的会话重建可恢复标签、面板和记录下来的命令，并通过确认后重新运行命令，但不是让进程从原内存状态继续执行。[1] [7]

对于 Codex 等应用，应用自身的历史记录、任务恢复机制与终端布局恢复也是两件事。不要把“界面重新出现”当成“原任务仍在执行”。

### 8.4 SSH 任务要在远程机器的复用器里运行

要保护远程任务，应先 SSH 到远程机器，再在那里启动 tmux 或 Zellij，并在其面板内运行任务。只在本地复用器中打开 SSH 客户端，并不会把远端程序自动纳入远程持久会话。[1] [6]

### 8.5 分层工作区不等于原生二级标签或固定侧边栏

本文的“项目 → 任务 → 程序”是对会话、窗口或标签、面板的组织方式，并不表示 Ghostty 会出现两排原生标签。[1] [3] [10]

tmux 的树形选择界面和 Zellij 的会话管理器可以辅助切换；它们不能直接等同于始终固定在左侧的项目目录树。具体的侧边栏、文件浏览与布局需求，需要单独选择配置或插件方案。[1] [3] [7] [9]

## 9. 核心结论与参考资料

**先解决分类，再增加工具：项目用会话分组，需求或 worktree 用窗口 / 标签区分，同一任务中的程序用面板并排展示。**

对当前工作流，可以先从 Zellij 的一个项目会话开始；熟悉创建、切换和分离后，再考虑可复用布局和自动化启动脚本。

以下为本文所用的官方文档，核对日期为 **2026-10-13**。在线文档可能包含比本机版本更新的功能，实际使用以已安装版本的帮助信息和配置为准。

| 编号 | 资料 |
| --- | --- |
| 1 | [tmux 官方入门指南][1] |
| 2 | [tmux 官方手册（OpenBSD）][2] |
| 3 | [Zellij 官方用户指南][3] |
| 4 | [Zellij 会话命令与配置输出][4] |
| 5 | [Zellij 快捷键配置][5] |
| 6 | [Zellij CLI Actions][6] |
| 7 | [Zellij 会话重建与恢复限制][7] |
| 8 | [Zellij 命令行配置选项][8] |
| 9 | [Zellij 布局][9] |
| 10 | [Ghostty 官方文档][10] |
| 11 | [Git worktree 官方文档][11] |
| 12 | [Codex CLI 官方文档][12] |

[1]: https://github.com/tmux/tmux/wiki/Getting-Started
[2]: https://man.openbsd.org/tmux
[3]: https://zellij.dev/documentation/
[4]: https://zellij.dev/documentation/commands.html
[5]: https://zellij.dev/documentation/keybindings.html
[6]: https://zellij.dev/documentation/cli-actions.html
[7]: https://zellij.dev/documentation/session-resurrection.html
[8]: https://zellij.dev/documentation/command-line-options.html
[9]: https://zellij.dev/documentation/layouts.html
[10]: https://ghostty.org/docs
[11]: https://git-scm.com/docs/git-worktree
[12]: https://developers.openai.com/codex/cli/
