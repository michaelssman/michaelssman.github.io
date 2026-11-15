# Neovim：阅读代码与搜索文件

Neovim 是独立的终端编辑器。本页将它配置为方便查看代码的工具：左侧文件树、语法高亮、文件搜索和项目内容搜索。

## 1. 安装与备份

```bash
brew install neovim ripgrep fd tree-sitter-cli
nvim --version
```

`fd` 用于查找文件，`ripgrep` 搜索文件内容，`tree-sitter-cli` 用于安装语法解析器。编译解析器需要 macOS Command Line Tools；缺少时运行 `xcode-select --install`，完成系统安装后再继续。[LazyVim 官方要求](https://www.lazyvim.org/)

已有 `~/.config/nvim` 时，先备份整个目录，再决定合并或替换，不能直接覆盖：

```bash
nvim_backup="$HOME/.local/state/nvim-setup/$(date +%Y%m%d-%H%M%S)"
if [ -d "$HOME/.config/nvim" ]; then
  mkdir -p "$nvim_backup"
  chmod 700 "$nvim_backup"
  cp -Rp "$HOME/.config/nvim" "$nvim_backup/nvim"
fi
```

## 2. 配置 LazyVim

以下克隆命令仅用于尚未有 `~/.config/nvim` 的情况；已有配置时按上一节先备份，再合并需要的设置：

```bash
# 仅在尚未有 ~/.config/nvim 时执行
git clone https://github.com/LazyVim/starter "$HOME/.config/nvim"
```

LazyVim 会在首次启动安装插件；之后生成的 `lazy-lock.json` 记录插件版本，迁移机器时一起保留。结构如下：

```text
~/.config/nvim/
├─ init.lua                 加载入口
├─ lua/config/lazy.lua      插件管理与 LazyVim extras
├─ lua/config/options.lua   阅读选项
├─ lua/config/keymaps.lua   快捷键
└─ lua/plugins/             文件树、语法与主题覆盖
```

在 `lua/config/lazy.lua` 的 `spec` 中，保留官方 LazyVim 导入，在本地插件导入前添加 neo-tree：

```lua
{ "LazyVim/LazyVim", import = "lazyvim.plugins" },
{ import = "lazyvim.plugins.extras.editor.neo-tree" },
{ import = "plugins" },
```

`lua/config/options.lua`：

```lua
vim.opt.number = true
vim.opt.relativenumber = false
vim.opt.mouse = "a"
vim.opt.confirm = true
vim.opt.wrap = true
vim.opt.linebreak = true
vim.opt.breakindent = true
vim.opt.showtabline = 2
-- 浏览代码时保存只保留手动修改，不自动格式化整份文件。
vim.g.autoformat = false
```

`lua/config/keymaps.lua`：

```lua
vim.keymap.set("n", "<C-p>", function()
  LazyVim.pick("files")()
end, { desc = "Find Files" })
```

`lua/plugins/viewer.lua`：

```lua
return {
  {
    "nvim-neo-tree/neo-tree.nvim",
    opts = {
      filesystem = {
        filtered_items = { hide_dotfiles = false, never_show = { ".git", ".DS_Store" } },
      },
      window = {
        width = 34,
        mappings = {
          ["<LeftRelease>"] = {
            function(state)
              local node = state.tree:get_node()
              if not node then
                return
              end
              if node.type == "directory" then
                state.commands.open(state)
              elseif node.type == "file" then
                state.commands.preview(state)
              end
            end,
            config = { use_float = false },
          },
        },
      },
    },
  },
  {
    "nvim-treesitter/nvim-treesitter",
    opts = { ensure_installed = { "java", "dart" } },
  },
  {
    "akinsho/bufferline.nvim",
    opts = { options = { always_show_bufferline = true } },
  },
}
```

`lua/plugins/theme.lua`：

```lua
return {
  {
    "folke/tokyonight.nvim",
    opts = {
      style = "night",
      on_colors = function(colors)
        colors.bg = "#1D1E27"
        colors.bg_dark = "#1D1E27"
        colors.bg_sidebar = "#1D1E27"
      end,
    },
  },
}
```

这里使用 LazyVim 自带的 TokyoNight 并匹配 Ghostty 背景。Java、Dart 增加的是语法解析器，**不是语言服务器**；本次未安装 Java/Dart LSP，因此不承诺点击定义跳转。保留 Vim 的 `/` 文件内搜索。

## 3. 初始化与使用

```bash
cd "/Users/michael/Documents/java_demo"
nvim .
```

用 `:Lazy` 查看插件状态，`:Mason` 查看工具状态，`:checkhealth` 检查依赖。单独执行 headless 的 `Lazy! sync` 只保证插件同步，随即退出可能中止仍在安装的工具；本次已等待它们完成后再验证。

| 操作 | 本机用法 |
| --- | --- |
| 显示文件树 | `Space → e` |
| 预览文件 | 文件树单击文件；使用 neo-tree 原生预览 |
| 打开文件 | 双击或 Enter，使用 neo-tree 原生打开 |
| 搜索文件名 | `Ctrl+P` |
| 搜索项目内容 | `Space → /` |
| 当前文件内搜索 | `/` 后输入内容，Enter；`n` 下一个 |
| 回到普通模式 | `Esc` |
| 保存文件 | `:w`，Enter |
| 关闭当前窗口 | `:q`，Enter |
| 退出全部窗口 | `:qa`，Enter；有未保存修改会提示 |
| 查看可用快捷键 | `Space` 后等待提示 |

Neovim 默认仍是编辑器，本机关闭了自动格式化，不代表所有文件都是只读。只想查看某个文件时可用 `nvim -R "文件路径"`。

作者配套指南的单击复用预览标签、双击固定标签和 Cmd/Ctrl+单击定义跳转需要额外定制及 LSP；本机采用原生预览/打开行为，不宣称与 VS Code 完全一致。[neo-tree 官方说明](https://github.com/nvim-neo-tree/neo-tree.nvim)

## 4. 如何退出 Neovim

运行 `nvim .` 后，要退出整个 Neovim（包括左侧文件树），在 Neovim 内依次操作：

1. 按 **`Esc`**，回到普通模式。
2. 输入 **`:qa`**。
3. 按 **回车**，退出全部窗口。

如果提示有未保存修改，可以按需要选择，输入命令后按回车：

- `:wqa`：保存全部修改并退出。
- `:qa!`：丢弃全部未保存修改，强制退出。

`:q` 只关闭当前窗口；存在文件树或分屏时，用 `:qa` 才能一次退出整个 Neovim。

## 5. 配置记录与排查

2026-11-14 的配置与运行检查结果：

- Java/Dart 实际解析与高亮、目录树预览/打开、Ctrl+P 文件搜索和项目内容搜索通过运行检查。

首次启动下载失败时，检查网络，使用 `:Lazy`、`:Mason` 和 `:checkhealth` 查看安装状态。若使用 Herdr，先确认在空闲 Shell 中运行 `nvim .`，不要把 Shell 命令输入运行中的 Agent 对话。

视频中的“代码查看”标签将 Neovim、Lazygit 和普通 Shell 组合在一起；布局操作见 [Lazygit 的 Herdr 集成说明](lazygit.md)。各工具是独立程序，Herdr 负责组织面板与保存会话布局。

查看本机配置目录：

```bash
open "$HOME/.config/nvim"
```
