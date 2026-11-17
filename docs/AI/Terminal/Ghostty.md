# Ghostty：终端配置与快捷键

Ghostty 是 macOS 上用来运行 Shell 和终端程序的应用。本文介绍安装、备份、配置和重载步骤。工作区和 Agent 管理见 [Herdr](Herdr.md)。

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

修改前，运行以下命令，将现有配置复制到以时间命名的备份目录。如果配置路径与上文不同，先修改 `ghostty_config`：

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

<a id="herdr-keybindings"></a>

## 3. 快捷键与外观配置

在配置文件中，`super` 表示 Mac 的 Command 键，`unbind` 取消 Ghostty 对该组合键的绑定。

```ini
# 让终端内的程序接收这些快捷键。
keybind = super+t=unbind
keybind = super+w=unbind
keybind = super+k=unbind
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

## 4. 校验与重载

保存配置后，在普通 Shell 中执行：

```bash
ghostty +validate-config
```

校验通过后，在 Ghostty 中按 **`Cmd+Shift+,`**（Command、Shift 和逗号）重载配置。

如果修改没有生效，按 `Cmd+,` 确认打开的是刚才编辑的文件。

## 5. 可选：全局唤起快速终端

如果想在其他应用中也能呼出 Ghostty 快速终端，可添加以下配置并重载：

```ini
keybind = global:ctrl+grave_accent=toggle_quick_terminal
```

按 Control 和反引号键（`grave_accent`）即可显示或隐藏快速终端。此全局快捷键可能需要系统授权，**本机未启用**。[Ghostty 全局快捷键说明](https://ghostty.org/docs/config/keybind)
