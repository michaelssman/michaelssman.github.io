# Ghostty：终端配置与快捷键

Ghostty 是显示 Shell 和终端程序的应用。本文记录它的安装、配色、按键让渡与配置重载；工作区和 Agent 管理由 [Herdr](Herdr.md)负责，代码阅读见 [Neovim](Neovim.md)，Git 差异查看见 [Lazygit](lazygit.md)。

相关视频演示位于 [Herdr 完整指南的 04:03](https://www.youtube.com/watch?v=Shqtk_2Jd3c&t=243s)。

## 1. 安装与配置文件

在普通 Shell 中安装：

```bash
brew install --cask ghostty
```

在 Ghostty 按 `Cmd+,` 打开当前配置文件：

```text
~/Library/Application Support/com.mitchellh.ghostty/config.ghostty
```

## 2. 修改前备份

下面是 Shell 命令，只备份已有配置，不覆盖原文件。若实际配置路径不同，先修改 `ghostty_config`：

```bash
ghostty_config="$HOME/Library/Application Support/com.mitchellh.ghostty/config.ghostty"
ghostty_backup="$HOME/.local/state/ghostty-setup/$(date +%Y%m%d-%H%M%S)"
if [ -f "$ghostty_config" ]; then
  mkdir -p "$ghostty_backup"
  chmod 700 "$ghostty_backup"
  cp -p "$ghostty_config" "$ghostty_backup/config.ghostty"
  chmod 600 "$ghostty_backup/config.ghostty"
fi
```

## 3. 配置内容

下方包含会改变 `Cmd+T`、`Cmd+W` 行为的按键让渡，含义见[下一节](#herdr-keybindings)。

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

`macos-option-as-alt` 使 Option 作为 Alt 传入终端程序；`scrollback-limit` 单位是**字节**，不是“保留多少行”。[Ghostty 配置参考](https://ghostty.org/docs/config/reference)

<a id="herdr-keybindings"></a>

## 4. 快捷键让渡与 Herdr 配合

Ghostty 在外层接收按键，Herdr 等程序运行在里面。`super` 在 macOS 对应 Command；`unbind` 取消 Ghostty 对该组合键的绑定，使内部程序有机会处理它。[Ghostty 快捷键说明](https://ghostty.org/docs/config/keybind)

配合本文档中的 [Herdr 配置](Herdr.md)后：

| 按键 | Ghostty 默认动作 | 让渡后在 Herdr 内的动作 |
| --- | --- | --- |
| `Cmd+T` | 新建 Ghostty 标签 | 在当前 Herdr 工作区新建标签 |
| `Cmd+W` | 关闭当前 Ghostty 终端面板 | 关闭当前 Herdr 标签及其中面板 |

这些 Ghostty 设置影响其终端中的按键处理，不限于某个 Herdr 项目。没有进入 Herdr 时，`Cmd+T` 也不再执行 Ghostty 原来的新建标签动作。需要外层新窗口或标签时，可使用 Ghostty 菜单。

`Cmd+K`、`Cmd+Shift+G` 等键也需要内部程序有对应绑定才会执行动作。Lazygit 弹窗的 Herdr 绑定见 [Lazygit 集成说明](lazygit.md)，Ghostty 的 `unbind` 本身不会创建弹窗。

## 5. 校验与重载

保存配置后，在普通 Shell 中执行：

```bash
ghostty +validate-config
```

无输出、退出码为 0 表示校验通过。随后在 Ghostty 按 **`Cmd+Shift+,`** 重载配置。若同时修改了 Herdr 配置，还要按 [Herdr 的重载步骤](Herdr.md)操作；只重载 Ghostty 不会更新 Herdr 的按键绑定。

如果 `Cmd+T` 仍创建 Ghostty 标签，先确认已重载、编辑的是当前使用的配置文件。其他按键无效时，按“系统是否截获 → Ghostty 是否截获 → 内部程序是否重载”的顺序检查。

## 6. 可选：全局唤起快速终端

视频提到全局唤起终端，但未展示配置。Ghostty 官方可使用以下设置：

```ini
keybind = global:ctrl+grave_accent=toggle_quick_terminal
```

这是另一项全局快捷键，可能需要系统授权，**本机记录中未启用**。也可以先用 Spotlight 打开 Ghostty，再运行需要的终端程序。[Ghostty 全局快捷键说明](https://ghostty.org/docs/config/keybind)
