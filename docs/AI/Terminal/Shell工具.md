# Shell 辅助工具：fzf、fd、bat 与 eza

这些工具用于终端中的搜索、文件阅读和目录展示，可用于普通 Shell 或 Herdr 面板。快速进入常用目录的 zoxide 独立记录在 [zoxide 文档](zoxide.md)。

| 工具 | 用途 |
| --- | --- |
| fzf | 交互搜索与选择列表，例如 zoxide 的 `zi` |
| fd | 查找文件，为本文的 fzf 默认列表提供文件路径 |
| bat | 带语法高亮地阅读文件 |
| eza | 显示目录详情和目录树 |

## 1. 安装

在本机终端的空闲 Shell 中执行：

```bash
brew install fzf fd bat eza
```

已安装的工具不必重装。

## 2. 配置前备份

下面的初始化写入 `~/.zshrc`。先备份现有文件，保留 PATH、Java、Flutter、`VISUAL` 和其他已有设置：

```bash
shell_backup="$HOME/.local/state/shell-setup/$(date +%Y%m%d-%H%M%S)"
if [ -f "$HOME/.zshrc" ]; then
  mkdir -p "$shell_backup"
  chmod 700 "$shell_backup"
  cp -p "$HOME/.zshrc" "$shell_backup/.zshrc"
  chmod 600 "$shell_backup/.zshrc"
fi
```

这是 Shell 命令：`$(date ...)` 在目录名中加入时间；`cp -p` 保留文件属性；`700`、`600` 将备份限制为当前用户访问。备份只保存在本机，不将配置中的凭据复制到知识库。

原 2026-11-14 配置时，`.zshrc` 随整套终端设置备份在 `~/.local/state/herdr-setup/20261114-010133/`。今后单独调整 Shell 工具，可使用上面的独立备份目录。恢复前先比较文件，避免覆盖后续修改。

## 3. 配置与生效

在 `~/.zshrc` 末尾合并以下内容；已有同类设置时不重复添加：

```zsh
export BAT_THEME="TwoDark"
export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border --cycle'
if [[ -t 0 && -t 1 ]] && command -v fzf >/dev/null; then
  source <(fzf --zsh)
fi
alias ll='eza -la'
alias tree='eza --tree'
```

- `BAT_THEME` 选择 bat 的显示主题。
- `FZF_DEFAULT_COMMAND` 用 fd 列出文件，包含隐藏文件并排除 `.git`。
- `FZF_DEFAULT_OPTS` 设置 fzf 列表高度、布局、边框和循环选择。
- 条件判断只在输入、输出连接终端且 fzf 已安装时，加载 fzf 的 zsh 集成。[fzf 官方初始化说明](https://github.com/junegunn/fzf#setting-up-shell-integration)
- `ll` 和 `tree` 是 eza 的快捷命令；没有将系统 `ls`、`cat` 全局替换。

zoxide 的初始化行单独见 [zoxide 文档](zoxide.md)，与这些设置可共同保留在 `.zshrc` 中。

保存后新开一个 Shell，或在当前空闲 Shell 中运行：

```bash
source "$HOME/.zshrc"
```

## 4. 使用与验证

| 命令 | 用途 |
| --- | --- |
| `fzf` | 打开文件选择列表；方向键选择、Enter 确认、Esc 取消 |
| `fd --type f --hidden --exclude .git` | 列出当前目录下匹配的文件 |
| `bat "文件路径"` | 带语法高亮阅读指定文件 |
| `ll` | 显示当前目录详情，包含隐藏条目 |
| `tree` | 显示当前目录树 |

`fzf` 选择文件后输出路径；需要阅读内容时再运行 `bat`。用以下命令检查安装是否能被当前 Shell 找到：

```bash
fzf --version
fd --version
bat --version
eza --version
```

如果提示找不到命令，检查 Homebrew 的 Shell 环境与 PATH；如果工具存在但 `ll`、`tree` 不可用，检查当前 Shell 是否加载了 `.zshrc`。本页从原终端配置中拆出，未在本次文档整理中重新安装或运行工具验证。
