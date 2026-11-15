# zoxide：快速进入常用目录

zoxide 会记录访问过的目录，让你用目录关键词快速跳转，可以理解为“会记住常用目录的 `cd`”。它是 Shell 工具，在普通终端或 Herdr 面板中都能使用。

本文整理自 [Herdr 完整指南视频的 24:39 章节](https://www.youtube.com/watch?v=Shqtk_2Jd3c&t=1479s)及原本机配置记录。`24:39` 是视频时间点；安装与初始化依据 [zoxide 官方说明](https://github.com/ajeetdsouza/zoxide#installation)。

## 1. 安装与准备

在本机终端的空闲 Shell 中执行：

```bash
brew install zoxide fzf
```

zoxide 负责记住和匹配目录，fzf 为 `zi` 提供交互搜索列表。已安装的工具不必重装；fzf 的通用配置见 [Shell 工具](Shell工具.md)。

初始化需要修改 `~/.zshrc`，先按 [Shell 工具](Shell工具.md)中的“配置前备份”步骤备份该文件。保留原有 PATH、Java、Flutter、`VISUAL` 等设置。

## 2. 初始化 zsh

在 `~/.zshrc` 末尾加入下面一行；如果已有相同初始化，保留一份即可：

```zsh
command -v zoxide >/dev/null && eval "$(zoxide init zsh)"
```

`command -v` 检查命令是否存在，`zoxide init zsh` 生成 zsh 初始化内容，`eval` 将它加载到当前 Shell，使 `z`、`zi` 可用。

保存后新开一个终端或 Shell 面板，也可以在空闲 Shell 中执行：

```bash
source "$HOME/.zshrc"
```

不要把 Shell 命令输入正在运行的 Agent 对话。

## 3. 记录目录与日常使用

首次使用完整路径进入项目，让 zoxide 记录它：

```bash
cd "/Users/michael/Documents/java_demo"
cd "/Users/michael/Documents/flutter_demo"
```

之后可以用目录关键词跳转：

```bash
z java_demo
pwd
```

`z java_demo` 根据访问记录进入最匹配的目录；`pwd` 显示实际进入的路径。目录记录可以供同一用户后续新开的 Shell 使用。

| 命令 | 作用 |
| --- | --- |
| `z java_demo` | 进入匹配的 Java 项目目录 |
| `z flutter_demo` | 进入匹配的 Flutter 项目目录 |
| `zi` | 打开已记录目录的交互搜索列表 |
| `zoxide query java_demo` | 查看匹配路径，不切换当前目录 |
| `pwd` | 查看当前目录 |

**`zi` 的第二个字符是小写字母 i，不是 `zy`。** 进入列表后输入关键词，用方向键选择，按 Enter 进入目录，按 Esc 取消。视频还演示输入 `z 目录关键字` 后按 Tab 补全；它依赖 zsh 补全初始化，原本机配置已有 `compinit`。

也可以主动添加常用项目，不必先逐个进入：

```bash
zoxide add "/Users/michael/Documents/java_demo"
zoxide add "/Users/michael/Documents/flutter_demo"
zoxide add "/Users/michael/Documents/michaelssman.github.io"
```

在 Herdr 中可按“新建标签 → `z flutter_demo` → `pwd` 确认目录 → `codex` 或 `omp`”使用。`z` 和 `cd` 只改变当前 Shell 的目录，不会自动切换左侧工作区；工作区管理见 [Herdr](Herdr.md)。

## 4. 验证与排查

新开 Shell 后执行：

```bash
zoxide --version
fzf --version
zoxide query java_demo
z java_demo
pwd
```

最后两个路径应对应你要进入的项目。

| 现象 | 检查方法 |
| --- | --- |
| 找不到 `z` 或 `zi` | 检查是否已安装 zoxide，以及当前 Shell 是否加载了 `.zshrc`；新开面板或执行 `source "$HOME/.zshrc"` |
| `zi` 不能打开列表 | 检查 `fzf --version` 是否成功 |
| 找不到目标目录 | 先用完整路径 `cd` 进入，或用 `zoxide add` 添加记录 |
| 跳到了其他同名目录 | 使用 `zi` 选择，并用 `pwd` 确认实际路径 |

**历史验证记录（2026-11-14）：** 本机 zoxide 0.10.0、fzf 0.75.0 已初始化，上述三个项目已加入记录；在新的登录式 zsh 中验证过 `z java_demo`、`z flutter_demo` 返回正确路径。这是原配置时的结果，本次文档拆分未重新运行验证。
