# Lazygit + Delta

在 Ghostty 中运行 Lazygit，可以用左侧文件树选择修改文件，在右侧查看差异，并执行暂存、提交、拉取和推送。Lazygit 提供交互界面与 Git 操作，Delta 负责差异高亮；不需要 Ghostty 插件。

## 1. 安装

以下操作在 macOS 的 Ghostty 终端中执行，需已安装 [Homebrew](https://brew.sh/) 和 Git。

```bash
brew install lazygit git-delta
lazygit --version
delta --version
```

两条版本命令都应输出版本号。本文配置依据 Lazygit `v0.66.2` 的官方文档；更新时运行 `brew update`，再运行 `brew upgrade lazygit git-delta`。

## 2. 配置左侧文件树与右侧差异

1. 找到 Lazygit 实际使用的配置目录：

   ```bash
   lazygit --print-config-dir
   ```

   macOS 默认目录是 `~/Library/Application Support/lazygit`，环境变量可能改变它，以命令输出为准。

2. 创建或打开该目录中的 `config.yml`：

   ```bash
   lazygit_config_dir="$(lazygit --print-config-dir)"
   mkdir -p "$lazygit_config_dir"
   touch "$lazygit_config_dir/config.yml"
   open -t "$lazygit_config_dir/config.yml"
   ```

3. 写入以下配置。如果文件已有内容，把这些字段合并到现有的 `gui`、`git` 节点中，保留其他设置；不要重复添加顶层节点。若已有 `diffRenderers` 列表，将 Delta 条目放到首项，保留仍需使用的其他条目。

   ```yaml
   gui:
     language: zh-CN
     screenMode: half
     enlargedSideViewLocation: left
     showFileTree: true
     mouseEvents: true
     showCommandLog: false

   git:
     diffRenderers:
       - command: delta --{{colorScheme}} --paging=never
   ```

   - `screenMode: half` 使用等宽双栏，只展开当前面板及其内容；`left` 让文件面板在左、差异在右。
   - `showFileTree` 启用目录树，`mouseEvents` 启用鼠标操作，`showCommandLog: false` 隐藏命令日志区域。
   - `language: zh-CN` 使用简体中文；`{{colorScheme}}` 让 Delta 跟随终端深浅主题。
   - `--paging=never` 关闭 Delta 自身分页，由 Lazygit 管理滚动与按键。Lazygit 内不使用 Delta 的 `n`、`N` 区块导航。

此配置只接入 Lazygit；普通 `git diff` 的全局配置见 [Delta](delta.md)。

## 3. 打开仓库并验证

先进入需要查看的 Git 仓库，例如：

```bash
cd "/Users/michael/Documents/java_demo"
git rev-parse --show-toplevel
lazygit
```

将示例目录替换为自己的仓库路径。第二条命令应输出仓库根目录；若提示不是 Git 仓库，先确认进入了正确目录。

关闭首次提示后按 `2` 聚焦“文件 / Files”。配置已设为 `half`，无需再按 `+`；此时应看到左侧修改文件树与右侧所选文件的差异。上下移动选择文件，检查差异是否有 Delta 高亮。没有本地修改时，文件面板为空属于正常情况。

## 4. 常用操作

下表中的文件操作以“文件 / Files”面板为上下文；同一按键在其他面板可能有不同作用。

| 按键 | 作用 |
| --- | --- |
| `2` | 回到文件面板 |
| `↑` / `↓` 或 `k` / `j` | 选择文件，右侧自动更新差异 |
| `Enter` | 对目录展开或折叠；对文件进入全屏逐行操作视图 |
| `Esc` | 退出差异视图或关闭当前弹窗 |
| 反引号（`` ` ``） | 切换文件树与平铺列表 |
| `K` / `J` 或 `Ctrl+U` / `Ctrl+D` | 向上 / 向下滚动右侧差异 |
| 空格 | 暂存或取消暂存选中的文件 |
| `c` | 打开提交窗口，提交已暂存修改 |
| `p` | 拉取当前分支的远程更新 |
| `P` | 推送当前分支；尚未配置上游时按提示设置 |
| `+` / `_` | 向后 / 向前切换 normal、half、full 布局 |
| `?` | 查看当前上下文的快捷键 |
| `q` | 退出 Lazygit |

仅查看差异时，选择文件即可，不需要按空格。按 `Enter` 进入逐行操作时，使用 Lazygit 原生差异显示，便于选择和暂存代码；按 `Esc` 返回文件树与 Delta 预览。提交前先检查暂存内容；`p`、`P` 分别会更新本地仓库和远程仓库。

## 5. 常见问题

### 命令不存在或配置键不识别

```bash
command -v lazygit
command -v delta
lazygit --version
delta --version
```

命令应能找到安装路径。如果新装后找不到，重新打开 Ghostty，并检查 Homebrew 的 shell 环境设置。配置键不识别时，核对已安装版本对应的官方文档；本文使用 `v0.66.2` 的 `git.diffRenderers` 配置。

### 配置没有生效

重新运行 `lazygit --print-config-dir`，确认编辑的是该目录中的 `config.yml`，保存后退出并重新启动 Lazygit。检查 `LG_CONFIG_FILE` 是否指定了其他文件，以及仓库的 `.git/lazygit.yml` 或父目录的 `.lazygit.yml` 是否覆盖了全局设置。

### 布局或快捷键与预期不同

按 `2` 回到 Files；若全屏只剩一个区域，按 `_` 从 full 返回 half。`+` 会继续切换到下一个布局，而不是固定进入 half。确保 Ghostty 窗口足够宽，并在普通 shell 中运行 Lazygit；若外层终端复用器或其他终端界面拦截按键，先退出该界面或检查其快捷键，再按 `?` 核对 Lazygit 当前按键。

### 差异没有高亮

先确认 `delta --version` 成功，再检查配置缩进、`git.diffRenderers` 中的命令及可执行文件路径。存在多个渲染器时，按 `|` 切换到 Delta；不要把 Delta 自身分页器的快捷键当作 Lazygit 快捷键。

## 6. 官方资料

- [Homebrew Lazygit](https://formulae.brew.sh/formula/lazygit)
- [Lazygit v0.66.2 配置](https://github.com/jesseduffield/lazygit/blob/v0.66.2/docs/Config.md)
- [Lazygit v0.66.2 差异渲染器与 Delta](https://github.com/jesseduffield/lazygit/blob/v0.66.2/docs/Custom_DiffRenderers.md)
- [Lazygit v0.66.2 快捷键](https://github.com/jesseduffield/lazygit/blob/v0.66.2/docs/keybindings/Keybindings_en.md)
