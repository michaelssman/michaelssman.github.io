# Delta

Delta（Homebrew 包名为 `git-delta`）是 Git 输出分页器。它不会替换 Git 的差异计算逻辑，而是为 `git diff`、`git show`、`git log -p`、`git blame` 等输出增加语法高亮、行号、行内差异和导航能力。

## 1. 当前环境

本机安装信息：

| 项目 | 当前值 |
| --- | --- |
| 终端 | Ghostty |
| 安装方式 | Homebrew |
| Homebrew 包 | `git-delta` |
| Delta 版本 | `0.19.2` |
| 可执行文件 | `/opt/homebrew/bin/delta` |

Ghostty 可以直接显示 Delta 的颜色和交互式分页输出，不需要额外的 Ghostty 配置。

## 2. 安装与更新

### 安装

```bash
brew install git-delta
```

检查是否安装成功：

```bash
delta --version
command -v delta
```

正常情况下会输出版本号以及 Delta 的可执行文件路径。

### 更新

```bash
brew update
brew upgrade git-delta
```

### 卸载

```bash
brew uninstall git-delta
```

卸载 Delta 前应先删除或修改 Git 中引用 `delta` 的配置，避免 Git 找不到分页器。

## 3. 配置 Git

当前采用以下全局配置：

```bash
git config --global core.pager delta
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.navigate true
git config --global delta.line-numbers true
git config --global delta.dark true
git config --global merge.conflictStyle zdiff3
```

对应的 `~/.gitconfig` 内容：

```gitconfig
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true
    line-numbers = true
    dark = true

[merge]
    conflictStyle = zdiff3
```

配置作用：

- `core.pager`：让 Git 默认使用 Delta 显示分页输出。
- `interactive.diffFilter`：让 `git add -p` 等交互式命令保留 Delta 高亮。
- `delta.navigate`：使用 `n`、`N` 在差异区块之间移动。
- `delta.line-numbers`：显示新旧文件行号。
- `delta.dark`：使用适合深色 Ghostty 主题的颜色。
- `merge.conflictStyle = zdiff3`：解决冲突时同时显示共同祖先内容，方便理解两侧修改。

查看当前配置：

```bash
git config --global --get core.pager
git config --global --get interactive.diffFilter
git config --global --get-regexp '^(delta\.|merge\.conflictStyle)'
```

## 4. 日常使用

配置完成后Git原有命令会自动使用 Delta。

### 查看未暂存修改

```bash
git diff
```

### 查看已暂存修改

```bash
git diff --staged
```

### 查看提交

```bash
git show
git show <commit>
```

### 查看提交历史及差异

```bash
git log -p
git log --stat -p
```

### 比较分支或提交范围

```bash
git diff main...HEAD
git diff <commit-a>..<commit-b>
```

### 查看暂存区并交互式选择修改

```bash
git add -p
```

Delta 只负责高亮差异，`y`、`n`、`s`、`e`、`q` 等 Git 交互选项仍然保持不变。

### 查看其他 Git 输出

```bash
git stash show -p
git reflog -p
git blame <file>
```

## 5. 分页与导航

Delta 默认借助分页器显示长内容，常用按键如下：

| 按键 | 作用 |
| --- | --- |
| `q` | 退出 |
| `n` | 跳到下一个差异区块 |
| `N` | 跳到上一个差异区块 |
| `Space` | 向下翻页 |
| `b` | 向上翻页 |
| `g` | 跳到开头 |
| `G` | 跳到结尾 |

## 6. 可选设置

### 临时使用并排视图

当前默认使用统一差异视图。Ghostty 窗口足够宽时，可以仅为本次命令启用并排显示：

```bash
git -c delta.side-by-side=true diff
```

需要长期启用时：

```bash
git config --global delta.side-by-side true
```

恢复统一视图：

```bash
git config --global --unset delta.side-by-side
```

### 临时绕过 Delta

需要查看 Git 原始输出时：

```bash
git --no-pager diff
git --no-pager show <commit>
```

### 使用浅色主题

如果 Ghostty 改为浅色主题：

```bash
git config --global --unset delta.dark
git config --global delta.light true
```

恢复深色主题：

```bash
git config --global --unset delta.light
git config --global delta.dark true
```

## 7. 常见问题

### Git 没有使用 Delta

先检查：

```bash
delta --version
git config --global --get core.pager
echo "$GIT_PAGER"
```

如果环境变量 `GIT_PAGER` 被设置为其他分页器，它可能覆盖 `core.pager`。可以在当前终端临时取消：

```bash
unset GIT_PAGER
```

如果该变量写在 `~/.zshrc` 中，还需要删除或修改对应的 `export GIT_PAGER=...`。

### 输出颜色不适合当前主题

深色主题使用：

```bash
git config --global delta.dark true
git config --global --unset delta.light
```

浅色主题使用：

```bash
git config --global delta.light true
git config --global --unset delta.dark
```

### 卸载后 Git 报找不到 `delta`

清理相关配置：

```bash
git config --global --unset core.pager
git config --global --unset interactive.diffFilter
git config --global --remove-section delta
```

## 8. 官方资料

- [Delta GitHub 仓库](https://github.com/dandavison/delta)
- [Delta 官方文档](https://dandavison.github.io/delta/)
- [Delta 配置说明](https://dandavison.github.io/delta/configuration.html)
- [Delta 使用说明](https://dandavison.github.io/delta/usage.html)
