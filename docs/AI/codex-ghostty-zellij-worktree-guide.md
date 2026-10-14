# Codex CLI + Ghostty + Zellij + Git worktree 开发环境配置手册

---

## 阅读路线

需要先明确三件事：

- 本文基础配置提供任务会话、分屏和会话管理器，**不提供常驻左侧的项目树**。
- 重新连接仍在运行的 session，与电脑重启后重建 session，是两种不同的恢复方式；后者不能把原进程的运行状态原封不动地恢复。
- 前文的 `cw today` 是设想，不是现成命令。本文脚本没有实现它，也不会自动猜测测试命令、日志文件或项目启动方式。

会话管理与恢复机制参见 Zellij 官方资料。[^z-session][^z-restore]

## 1. 最终采用的工作区结构

```text
Ghostty：一个主窗口，通常一个标签即可
└── Zellij 会话管理器：查找、切换任务
    ├── ios--auth
    │   └── work
    │       ├── Codex
    │       ├── Git / Shell
    │       └── Tests / Logs
    ├── ios--payment
    │   └── work：同样的三个面板
    └── backend--api-v2
        └── work：同样的三个面板
```

Zellij 的原生层级是 session、tab 和 pane；布局文件可以定义 tab 与 pane。[^z-layout]

## 2. 安装与环境检查

### 2.1 最少需要什么

```bash
# 先检查现有环境
command -v brew
command -v git
command -v codex

# 安装 Zellij
brew install zellij

# 记录版本，后续排错会用到
git --version
zellij --version
codex --version
```

### 2.2 先做一次最小验证

在 Ghostty 新建一个普通 shell，进入一个现有 worktree 根目录，然后执行：

```bash
# 把下面路径替换为你准备试用的现有工作区
cd "$HOME/你的现有项目路径"

zellij --session ios--trial
```

进入 Zellij 后，在里面运行 `codex`。先验证输入、中文、复制粘贴和终端显示正常，不急着同时开很多任务。

按经典默认键位，`Ctrl + o` 后按 `d` 是 detach；回到外层 shell 后运行：

```bash
zellij attach ios--trial
```

这一步用于验证“离开界面后重新连接”的工作方式。键位若与你选择的预设不同，以底部提示和本机配置为准。[^z-session][^z-command]

## 3. 备份与路径约定

### 3.1 备份将要编辑的文件

下方命令只复制已存在的文件，不修改其内容：

```bash
stamp="$(date +%Y%m%d-%H%M%S)"

for file in \
  "$HOME/.zshrc" \
  "$HOME/.config/zellij/config.kdl" \
  "$HOME/.config/zellij/layouts/codex-workspace.kdl" \
  "$HOME/.local/bin/cw"
do
  if [ -f "$file" ]; then
    cp -p "$file" "$file.bak.$stamp"
  fi
done

mkdir -p "$HOME/.config/zellij/layouts" "$HOME/.local/bin"
```

本手册示例使用 `~/.config/zellij`。如果你使用自定义配置目录，请相应修改路径；第 8 节脚本可以通过 `CW_LAYOUT` 指定布局文件。Zellij 的配置查找方式见官方说明。[^z-config]

### 3.2 现有仓库不动，新 worktree 统一放置

```text
现有仓库：保持原位置
例如 ~/Desktop/yuncai/IOS-acc/Auxiliary

~/worktrees/
├── ios/
│   ├── auth/
│   └── payment/
└── backend/
    └── api-v2/
```

上面的仓库路径取自前面截图中的终端路径，仅作为配置起点。**先确认它仍然存在，且是你要管理的 Git 工作区根目录。**它可以是原始工作目录，也可以是同一仓库的既有 worktree。

把下面内容加入 `~/.zshrc`，已有同名配置时编辑原项，不重复追加：

```bash
export PATH="$HOME/.local/bin:$PATH"

# 改成你的实际 Git 工作区根目录
export CW_IOS_REPO="$HOME/Desktop/yuncai/IOS-acc/Auxiliary"

# 仅在确实有 backend 项目时设置；否则可以不加这一行
export CW_BACKEND_REPO="$HOME/workspace/backend"

# 只影响以后由 cw 新建的 worktree，不移动现有目录
export CW_WORKTREE_ROOT="$HOME/worktrees"
```

保存后新开一个普通 shell，或执行：

```bash
source "$HOME/.zshrc"

git -C "$CW_IOS_REPO" rev-parse --show-toplevel
git -C "$CW_IOS_REPO" worktree list
```

只有当输出确实对应目标仓库时才继续。不要在 `.zshrc` 中直接写不加条件的 `zellij` 自动启动命令，本手册使用手动进入，避免产生嵌套会话。

## 4. 先理解 Git worktree 的手动操作

这部分用于理解后面的 `cw` 做了什么。已有 worktree 的任务可以跳过创建，直接进行第 6 节的布局验证。

### 4.1 新任务：创建分支和工作目录

先看清楚本项目实际使用的基线；`fetch` 用于获取远端对象与引用，区别于执行合并。[^git-fetch]

```bash
git -C "$CW_IOS_REPO" branch -a

# 需要更新远端引用时再执行；不会替你合并当前分支
git -C "$CW_IOS_REPO" fetch origin
```

下面以 `origin/develop` 为例；项目用 `origin/main`、其他分支或某个提交时，修改 `BASE`。它不是通用默认值。

```bash
REPO="$CW_IOS_REPO"
BASE="origin/develop"  # 必须改成你确认过的基线
TARGET="$HOME/worktrees/ios/payment"

mkdir -p "$HOME/worktrees/ios"

git -C "$REPO" worktree add \
  -b feature/payment \
  "$TARGET" \
  "$BASE"
```

该命令从指定基线创建 `feature/payment`，并把它检出到目标目录。**当前目录里的未提交改动不会因此自动搬到新 worktree。**[^git-worktree]

### 4.2 已有本地分支：不要再加 `-b`

以下是另一种情形，不要紧接上一步对同一目录重复执行：

```bash
git -C "$CW_IOS_REPO" worktree add \
  "$HOME/worktrees/ios/payment" \
  feature/payment
```

如果提示分支已被另一个 worktree 使用，先查：

```bash
git -C "$CW_IOS_REPO" worktree list
```

### 4.3 worktree 的隔离边界

把 worktree 理解为**代码工作目录与检出分支的隔离**，不要把它当成完整的运行环境隔离。由此在工作流上需要额外检查：不同任务是否使用相同服务端口、同一数据库、同一个模拟器或共享构建输出。

依赖安装、本地配置、密钥以及测试环境仍按项目自己的方式准备。不要自动复制 `.env`、签名资料或其他敏感文件到每个任务目录。

## 5. 配置 Zellij：先少改配置

Zellij 使用 KDL 配置文件。第一次配置时，可以在 `~/.config/zellij/config.kdl` 中加入以下内容；**已有配置时只合并对应选项，不要覆盖原有键位和插件配置。**[^z-config][^z-options]

```kdl
// 日常把大多数按键交给 Codex / shell，减少快捷键冲突
// 使用经典默认键位时，Ctrl + g 在 Locked / Normal 间切换
default_mode "locked"

mouse_mode true
pane_frames true

// 允许保存会话布局等信息，便于退出后重建
// 这不是进程内存快照，也不是代码备份
session_serialization true
```

## 6. 创建 Codex 专用三面板布局

默认布局的目标是：

```text
┌───────────────────────────────────────────────┐
│ work                                          │
├───────────────────────────────────────────────┤
│                                               │
│                 Codex                         │
│          可按需要切换为独占显示                │
│                                               │
├───────────────────────┬───────────────────────┤
│ Git / Shell           │ Tests / Logs          │
│ git status / git diff │ 项目测试或日志命令    │
├───────────────────────┴───────────────────────┤
│ Zellij 状态与快捷键提示                        │
└───────────────────────────────────────────────┘
```

### 6.1 保存布局文件

确认第 3 节已经备份同名文件，然后执行：

```bash
cat > "$HOME/.config/zellij/layouts/codex-workspace.kdl" <<'KDL'
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }

    tab name="work" {
        pane name="Codex" size="72%" focus=true
        pane size="28%" split_direction="vertical" {
            pane name="Git / Shell"
            pane name="Tests / Logs"
        }
    }
}
KDL
```

`size` 控制分配比例；下方容器的 `split_direction="vertical"` 让两个面板左右排列；tab-bar 和 status-bar 是官方布局示例使用的内置插件。这里没有写死工作目录，首次创建时沿用启动位置。[^z-layout]

### 6.2 从一个实际 worktree 启动

```bash
cd "$HOME/worktrees/ios/payment"

zellij \
  --layout "$HOME/.config/zellij/layouts/codex-workspace.kdl" \
  attach --create ios--payment
```

`attach --create` 用于连接已有会话或在不存在时创建。**已存在的会话不会因为你换了外层 shell 目录，就被重新定位到另一个 worktree；旧会话的布局也不会被新文件直接替换。**[^z-command][^z-cli]

进入后先在三个面板分别运行 `pwd`，确认都在期望的 worktree。可以用鼠标点击切换面板。

上方面板选择一种操作：

```bash
# 新任务：开始新对话
codex

# 同一个任务：选择已有对话继续
codex resume
```

`codex resume` 用于继续以前的交互会话，不等同于重新连接 Zellij。[^codex]

下方左侧：

```bash
git status --short
git diff
```

下方右侧：先留作普通 shell，再手动执行你已经确认的项目命令。不要直接照搬 `npm run dev` 到 iOS 项目，也不要把不存在的 `logs` 当成日志路径。

### 6.3 可选：新建布局时自动启动 Codex

基础版本故意先打开 shell，让你自己选择 `codex` 或 `codex resume`。这样不容易误开新对话或接错历史任务。

确实希望创建新任务时自动启动 Codex，可以把布局中的这一行：

```kdl
pane name="Codex" size="72%" focus=true
```

改为：

```kdl
pane name="Codex" size="72%" focus=true {
    command "codex"
}
```

这是命令面板，不是智能恢复器：它启动的是 `codex`，不会替你判断应该恢复哪个历史对话；命令退出后，该面板也不等同于一个正常返回提示符的 shell。日常恢复历史任务仍优先使用基础布局。命令面板与布局语法见官方说明。[^z-layout]

## 7. 日常切换与 Ghostty 配置

### 7.1 Zellij 常用操作

下面按**经典默认键位**书写。“`Ctrl + o` → `w`”表示先按组合键，松开后再按 `w`，不是三个键一起按。

启用了 `default_mode "locked"` 后，通常先按 `Ctrl + g` 解锁，再使用表中操作。完成后查看底部模式提示，必要时再按 `Ctrl + g` 返回 Locked。若你使用其他键位预设，以界面提示和本机配置为准。[^z-session][^z-keybinds][^z-options]

| 操作 | 经典默认键位 / 方法 |
| --- | --- |
| 打开会话管理器，查找和切换任务 | Normal 模式下 `Ctrl + o` → `w` |
| detach：离开界面而不主动退出会话 | Normal 模式下 `Ctrl + o` → `d` |
| 当前面板独占显示 / 恢复布局 | Normal 模式下 `Ctrl + p` → `f` |
| 切换当前面板 | 鼠标点击目标面板 |
| 列出会话 | 外层 shell 执行 `zellij list-sessions` |
| 回到指定会话 | 外层 shell 执行 `zellij attach ios--payment` |

**日常“下班离开”优先使用 detach，不是退出整个 Zellij session。**如果电脑仍运行且会话进程仍存活，之后可以重新连接；detach 不保证机器睡眠、断网或重启时任务仍能照常执行。[^z-command][^z-restore]

### 7.2 Ghostty 可以完全不改

本方案的分类与布局在 Zellij 层完成，Ghostty 不需要新增特殊插件。

需要调整时，优先用 Ghostty 菜单中的打开配置功能找到当前实际配置文件，再备份编辑。官方文档目前列出了 `config.ghostty` 和旧名 `config`，以及 XDG 与 macOS 专用路径；不要盲目新建多个互相覆盖的配置文件。[^ghostty-config]

可以保留以下少量选项：

```ini
font-size = 15
shell-integration = detect
```

字体和主题沿用你当前的设置即可，不必为了这套工作流更换。需要核对可用项时：

```bash
ghostty +list-fonts
ghostty +list-themes
ghostty +list-keybinds --default
```

如果 `ghostty` 不在 shell 的 PATH 中，使用应用菜单查看设置即可，不能据此认定 GUI 应用没有安装。字体、主题和 shell integration 的定义见官方参考。[^ghostty-options][^ghostty-keys]

原生分屏快捷键也可以保留：

```ini
keybind = cmd+d=new_split:right
keybind = cmd+shift+d=new_split:down
```

但这两项分割的是 **Ghostty 窗格**，不是 Zellij 面板。进入 Zellij 后，建议主要用 Zellij 管理面板，避免产生两套分屏层级。[^ghostty-actions]

## 8. 安装可选的 `cw` 工作区命令

### 8.1 它做什么、不做什么

本文提供的 `cw` 是本地辅助脚本，不是 Codex、Ghostty 或 Zellij 自带命令。

它按以下规则工作：

```text
cw ios payment origin/develop
    ↓
读取 CW_IOS_REPO
    ↓
创建或检查 ~/worktrees/ios/payment
    ↓
新任务分支使用 feature/payment
    ↓
创建 / 连接 ios--payment 会话，使用三面板布局
```

脚本**不会**自动提交、推送、合并、删除 worktree、重置分支、复制密钥或运行测试。使用基础布局时，Codex 仍由你在面板内选择新建或恢复。

首次创建新分支时要求显式指定基线。已有工作区或本地分支时省略基线，避免误以为“传一个新基线”会安全地更新已有任务。

脚本新增项目的入口是 `case "$project"`，目前示例支持 `ios` 和 `backend`。其他项目可以照样加一项。项目代号不同却指向同一 Git 仓库时，分支名仍会共享；不要指望项目别名提供额外隔离。

### 8.2 保存脚本

确认第 3 节已经备份原有 `~/.local/bin/cw`，然后完整执行下面的代码块：

```bash
cat > "$HOME/.local/bin/cw" <<'CW_SCRIPT'
#!/usr/bin/env bash
# cw: 一个任务一个 Git worktree + 一个 Zellij session。
# 兼容 Bash 3.2+；不提交、不删除、不重置代码，不自动执行项目命令。
set -euo pipefail

fail() { printf 'cw: %s\n' "$*" >&2; exit 1; }
usage() {
  cat <<'HELP'
用法：
  cw ios payment origin/main    首次创建任务（基线必须明确）
  cw ios payment                打开已有任务 / 复用已有本地分支
  cw backend api-v2 origin/main
  cw open ios--legacy /绝对路径/已有worktree
  cw attach ios--payment        重连或尝试恢复已有会话
  cw list                       列出会话

项目路径：CW_IOS_REPO、CW_BACKEND_REPO
新 worktree 根目录：CW_WORKTREE_ROOT（默认 ~/worktrees）
布局：CW_LAYOUT（默认 ~/.config/zellij/layouts/codex-workspace.kdl）
HELP
}
slug_ok() { [[ "$1" =~ ^[a-z0-9][a-z0-9_-]*$ ]]; }
need() { command -v "$1" >/dev/null 2>&1 || fail "找不到命令：$1"; }
outside_zellij() {
  [[ -z "${ZELLIJ:-}" ]] || fail '请先 detach 到外层 shell；会话内切换请用 Zellij 会话管理器。'
}
repo_root() {
  local p top
  [[ -d "$1" ]] || fail "目录不存在：$1"
  p=$(cd "$1" && pwd -P)
  top=$(git -C "$p" rev-parse --show-toplevel 2>/dev/null) || fail "不是普通 Git 工作目录：$p"
  top=$(cd "$top" && pwd -P)
  [[ "$p" == "$top" ]] || fail "请传入工作区根目录，而非子目录：$top"
  printf '%s\n' "$p"
}
common_dir() {
  # --git-common-dir 可能返回相对路径，必须在对应工作区中解析。
  ( cd "$1"; cd "$(git rev-parse --git-common-dir)"; pwd -P )
}
open_workspace() {
  local session="$1" target="$2"
  local layout="${CW_LAYOUT:-$HOME/.config/zellij/layouts/codex-workspace.kdl}"
  slug_ok "$session" || fail '会话名只允许小写字母、数字、下划线和连字符，并须以字母或数字开头。'
  [[ -f "$layout" ]] || fail "请先创建布局文件：$layout"
  target=$(repo_root "$target")
  printf '会话：%s\n目录：%s\n' "$session" "$target"
  printf '进入后在 Codex 面板执行 codex 或 codex resume。\n'
  cd "$target"
  # 创建时使用布局；已存在的会话会被重连，不会重设其目录和布局。
  exec zellij --layout "$layout" attach --create "$session"
}

case "${1:-help}" in
  help|-h|--help) usage; exit 0 ;;
esac
need git
need zellij

case "$1" in
  list)
    [[ $# -eq 1 ]] || fail '用法：cw list'
    exec zellij list-sessions
    ;;
  attach)
    [[ $# -eq 2 ]] || fail '用法：cw attach 会话名'
    outside_zellij
    slug_ok "$2" || fail '会话名格式错误。'
    exec zellij attach "$2"
    ;;
  open)
    [[ $# -eq 3 ]] || fail '用法：cw open 会话名 /绝对路径/已有worktree'
    outside_zellij
    [[ "$3" == /* ]] || fail '请使用绝对路径；也可使用 "$HOME/..."。'
    open_workspace "$2" "$3"
    ;;
esac

[[ $# -eq 2 || $# -eq 3 ]] || { usage; exit 1; }
outside_zellij
project="$1"
task="$2"
base="${3:-}"
slug_ok "$project" && slug_ok "$task" || fail '项目名和任务名必须是小写英文/数字/下划线/连字符。'
[[ "$project" != *--* && "$task" != *--* ]] || fail '项目名和任务名不要包含连续两个连字符。'
case "$project" in
  ios) repo="${CW_IOS_REPO:-$HOME/workspace/ios-app}" ;;
  backend) repo="${CW_BACKEND_REPO:-$HOME/workspace/backend}" ;;
  *) fail "未知项目：$project；请在脚本 case 中新增项目映射。" ;;
esac
repo=$(repo_root "$repo")
root="${CW_WORKTREE_ROOT:-$HOME/worktrees}"
[[ "$root" == /* ]] || fail 'CW_WORKTREE_ROOT 必须是绝对路径。'
target="$root/$project/$task"
branch="feature/$task"
session="$project--$task"
layout="${CW_LAYOUT:-$HOME/.config/zellij/layouts/codex-workspace.kdl}"
[[ -f "$layout" ]] || fail "请先创建布局文件：$layout"

if [[ -e "$target" || -L "$target" ]]; then
  [[ -z "$base" ]] || fail '任务目录已存在；重新打开时请省略基线参数。'
  target=$(repo_root "$target")
  [[ "$(common_dir "$repo")" == "$(common_dir "$target")" ]] || fail '目标目录属于其他 Git 仓库。'
  actual=$(git -C "$target" symbolic-ref --quiet --short HEAD) || fail '目标工作区处于 detached HEAD；请用 cw open 明确打开。'
  [[ "$actual" == "$branch" ]] || fail "目标分支是 $actual，而非 $branch；请用 cw open 明确打开。"
else
  if git -C "$repo" show-ref --verify --quiet "refs/heads/$branch"; then
    [[ -z "$base" ]] || fail "本地分支 $branch 已存在；复用时请省略基线参数。"
    mkdir -p "$root/$project"
    git -C "$repo" worktree add "$target" "$branch"
  else
    [[ -n "$base" ]] || fail "首次创建请指定基线，例如：cw $project $task origin/main（按项目实际分支修改）。"
    [[ "$base" != -* ]] || fail '基线不能以 - 开头。'
    git -C "$repo" rev-parse --verify "${base}^{commit}" >/dev/null 2>&1 || fail "找不到基线提交：$base；请检查分支或先 git fetch。"
    mkdir -p "$root/$project"
    git -C "$repo" worktree add -b "$branch" "$target" "$base"
  fi
fi
open_workspace "$session" "$target"
CW_SCRIPT

chmod +x "$HOME/.local/bin/cw"

# 仅为当前 shell 立即生效；长期配置已在第 3 节写入 ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

cw --help
```

### 8.3 常用示例

下面的 `origin/develop` 和 `origin/main` 都是示例，请选用仓库里真实存在、适合任务的基线。

```bash
# 新任务：目录和分支尚不存在时，明确传入基线
cw ios auth origin/develop

# 同一任务再次进入：先 detach 到外层 shell，再运行
cw ios auth

# 新建另一个项目的任务；需先正确设置 CW_BACKEND_REPO
cw backend api-v2 origin/main

# 列出会话
cw list

# 指定会话：重连或尝试恢复
cw attach ios--auth
```

对于**已经存在、目录不遵循新规则的 worktree**，无需搬动，也无需重新创建分支：

```bash
# 将第二个参数替换成真实的绝对路径
cw open ios--legacy "$HOME/某个已有worktree路径"
```

同一个 session 名始终留给同一个任务。`cw open` 并不维护全局的“名称—目录”注册表：若该名称已被你手工用于别的目录，连接后仍是原会话。首次接入旧任务时用新的、唯一的名称，并在进入后检查 `pwd`。

在 Zellij 内运行 `cw` 的打开命令会被脚本拒绝，以免嵌套；请使用会话管理器切换，或 detach 后再执行。`cw list` 可以直接列出会话。

### 8.4 代码验证范围

本次整理对脚本做了 Bash 语法检查，并在临时 Git 仓库中通过了 12 项逻辑测试，覆盖新建、复用、含空格路径、非法任务名、缺失基线、跨仓库误用和嵌套防护等。

**Zellij 在测试中使用了替身程序验证参数传递，没有在你的 macOS 上实际联调 Ghostty、Zellij 或 Codex。**因此第一次使用请只接入一个测试任务，按第 15 节逐项验收；不要直接批量迁移全部工作区。

## 9. 推荐的日常使用流程

### 开始一个新需求

在外层 shell 中创建或进入任务：

```bash
# 第一次使用时选好实际基线
cw ios payment-v2 origin/develop
```

进入后在上方面板执行 `codex`，给出本任务目标与范围；下方两个面板分别用于检查差异和运行测试。这里采用“一项主要任务一段对话”作为组织约定，不把它当成必须遵守的软件限制。

### 中途切换任务

打开会话管理器，按项目或任务名查找，例如 `ios`、`payment`，然后切换。不要为了切换任务再增加一个长期打开的 Ghostty 标签。会话管理器的操作以其当前界面提示为准。[^z-session]

### 暂时离开

确认没有待处理的交互确认，然后 detach。之后用 `cw attach ios--payment-v2` 回到原会话。

Zellij 可以保留终端会话，但不能替你处理 Codex 的审批提示，也不能保证网络请求永不失败。

### 查看长输出

需要专注阅读 Codex 时把当前面板独占显示，完成后恢复三面板。分屏是减少切换的工具，不必一直固定占用屏幕。

## 10. 会话恢复：把三层状态分开理解

| 需要恢复的东西 | 对应机制 | 不能据此假定什么 |
| --- | --- | --- |
| 仍在运行的终端会话 | Zellij attach | 不保证电脑睡眠或断网时任务继续正常工作 |
| 退出或重启后的布局 | Zellij session resurrection | 不是原进程内存、连接和执行位置的恢复 |
| Codex 的历史对话 | `codex resume` | 不等于重连原终端进程，也不代替代码备份 |

Zellij 的序列化与复活用于重建布局、目录和命令等会话信息，实际恢复还受缓存是否存在和配置影响；Codex 有自己的历史对话恢复入口。[^z-restore][^codex]

### 10.1 只是 detach，原会话还活着

```bash
cw attach ios--payment
```

这时先查看原 Codex 是否仍在运行，不要在另一个面板又启动一个处理相同任务的 Codex。

### 10.2 电脑重启或会话已经退出

先查看可用记录：

```bash
cw list
cw attach ios--payment
```

有可恢复记录时，可以尝试恢复；必要时从会话管理器的已退出会话区域选择。部分命令面板可能需要你按界面提示确认重新运行。恢复后检查当前目录、运行进程和测试服务，不要假定它们全部自动正常。[^z-restore]

随后在正确 worktree 的 shell 中恢复 Codex：

```bash
cd "$HOME/worktrees/ios/payment"

# 更稳妥：先查看候选历史会话
codex resume

# 仅在确认当前目录最近一次对话就是该任务时使用
codex resume --last
```

按核对时的官方 CLI 文档，`--last` 默认限定在当前工作目录，`--all` 会扩大选择范围。多任务环境下不要随手加 `--all`。[^codex]

如果恢复不到 Zellij 会话，但代码目录仍在，可以用一个新会话名重新搭建布局，再执行 `codex resume`。这只是重建工作环境，不是找回原进程运行现场。

## 11. 任务结束与安全清理

**detach 不代表任务完成，关闭一个面板也不代表代码已经提交。**清理前先确认 Codex、测试进程和编辑器不再使用目标目录。

先检查工作目录的改动与被忽略文件。[^git-status]

```bash
TARGET="$HOME/worktrees/ios/payment"

git -C "$TARGET" status --short
git -C "$TARGET" diff

# 额外看看被忽略的本地文件；输出可能较多
git -C "$TARGET" status --short --ignored
```

确认需要的代码已经按你的流程提交或备份，本地配置和重要产物也已另行保存，再正常退出该任务的会话，然后从外层 shell 执行：

```bash
# 这是删除任务工作目录的操作，只在任务确实完成时执行
# 不要添加 --force 绕过未保存文件的检查
git -C "$CW_IOS_REPO" worktree remove "$HOME/worktrees/ios/payment"

git -C "$CW_IOS_REPO" worktree list
```

Git 默认限制对不干净 worktree 的删除，但被忽略文件同样需要你主动检查，不能把“命令可以执行”当成“所有重要内容都已经备份”。分支是否保留或删除，按你的分支管理流程单独处理。[^git-worktree]

不要直接用文件管理器或 `rm -rf` 清理 worktree。已退出的 Zellij 会话记录也应在会话管理器中确认后清理，避免日后误恢复到已删除目录。

## 12. 常见问题与排错

| 现象 | 先检查什么 |
| --- | --- |
| `cw: command not found` | `~/.local/bin/cw` 是否存在且可执行；`echo "$PATH"` 是否包含 `~/.local/bin` 的展开路径 |
| 提示仓库目录不存在 | 核对 `CW_IOS_REPO` / `CW_BACKEND_REPO`；必须是实际 Git 工作区根目录 |
| `origin/main` 或 `origin/develop` 不存在 | `git branch -a` 查看真实分支；必要时 `git fetch origin`，不要猜基线 |
| 分支已经在另一个 worktree 使用 | `git worktree list` 找到旧路径，用 `cw open` 接入，不要强制重复检出 |
| Codex 快捷键被截获 | 查看 Zellij 当前模式；回到 Locked，再测试输入；确认使用的键位预设 |
| 修改 KDL 后旧会话没变化 | 新布局用于创建；使用新的测试 session 名验证，不要误认为旧会话会被自动重建 |
| 三个面板的目录不对 | 分别运行 `pwd`；检查是否重连了旧会话，或 shell 初始化文件中是否有自动 `cd` |
| `cw` 拒绝在当前终端打开任务 | 当前已在 Zellij 内；先 detach，或直接用会话管理器切换 |
| 重新打开却是新 Codex 对话 | `codex` 是启动新对话；应该在对应 worktree 使用 `codex resume` |
| Ghostty 配置不生效 | 从应用菜单打开实际配置；检查 macOS 专用目录是否还有覆盖项 |

优先运行本机帮助，不要把未来版本或另一台机器的选项直接套过来：

```bash
zellij --help
zellij attach --help
zellij setup --help
codex resume --help
```

Zellij 的每个子命令有自己的帮助；Ghostty 也提供本机配置参考与配置重载入口。[^z-command][^ghostty-config]

## 13. 可选替代方案：项目一个 session，任务一个 tab

如果使用一段时间后，发现更需要真正的“项目 → 任务”两层组织，可以改成：

```text
Zellij session：ios
├── tab：auth
│   ├── Codex
│   ├── Git / Shell
│   └── Tests / Logs
└── tab：payment
    ├── Codex
    ├── Git / Shell
    └── Tests / Logs

Zellij session：backend
└── tab：api-v2
```

这仍不是常驻左侧树，但利用了 session → tab 的原生层级，比只靠名称前缀更明确。

**这是另一种管理模型，不是第 8 节 `cw` 脚本的模式。**先选定一种，不要同时维护“Ghostty 项目标签 + 每任务 session + 每任务 tab”三套索引。

手工试用方法：

```bash
# 在外层普通 shell 中，创建或连接项目会话
cd "$CW_IOS_REPO"
zellij attach --create ios
```

进入项目会话后，在一个 shell 面板中执行：

```bash
# 目标 worktree 必须事先存在
zellij action new-tab \
  --name payment \
  --cwd "$HOME/worktrees/ios/payment" \
  --layout "$HOME/.config/zellij/layouts/codex-workspace.kdl"
```

该命令会新建 tab；重复执行会继续新增，不会替你按任务名去重。Zellij 官方 CLI 支持用名称、工作目录和布局创建 tab。[^z-actions]

至于“左侧一直显示可展开的项目树，点击切换右侧任务”，本文没有实现。左侧文件浏览器只显示文件，也不能自动等同于任务会话管理器；不要把两者混为一谈。

## 14. 最常用命令速查

```bash
# 1. 新任务：首次明确基线
cw ios auth origin/develop

# 2. 已有任务：省略基线
cw ios auth

# 3. 接入旧 worktree：使用唯一会话名和实际绝对路径
cw open ios--legacy "$HOME/你的已有worktree路径"

# 4. 查看 / 重连
cw list
cw attach ios--auth

# 5. 在正确 worktree 中恢复 Codex 对话
codex resume

# 6. 查看 Git 工作区关系
git -C "$CW_IOS_REPO" worktree list
```

`cw` 的打开命令在 **Zellij 外层 shell** 使用；`codex` / `codex resume` 在 **目标 worktree 的面板 shell** 使用。

## 15. 实施验收清单

### 第一阶段：先验证一个任务

- [ ] Zellij、Git、Codex 均可运行，版本已记录。
- [ ] 现有配置已备份，选定的仓库路径已核对。
- [ ] 一个测试 session 能打开三面板，三个面板的 `pwd` 正确。
- [ ] Codex 的输入、中文、复制粘贴和常用快捷键正常。
- [ ] 会话管理器能找到测试任务，detach 后能重新 attach。
- [ ] 已亲自验证面板独占显示和恢复分屏。

### 第二阶段：再增加自动化

- [ ] `cw --help` 正常输出。
- [ ] 显式指定基线后，能创建一个新的测试 worktree。
- [ ] 对同一任务执行 `cw 项目 任务`，没有创建第二个分支或重复目录。
- [ ] 能用 `cw open` 接入一个现有 worktree，而不移动原目录。
- [ ] 能在正确目录用 `codex resume` 找到要继续的对话。
- [ ] 已理解重启恢复不是进程原地继续，清理 worktree 前会检查代码和本地文件。

完成后再逐步减少 Ghostty 的旧标签。先迁移一个任务，再迁移一个项目，不要一次关闭所有正在工作的终端。
