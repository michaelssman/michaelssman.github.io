# Lazygit + Delta

在 Ghostty 中运行 Lazygit，可以用左侧文件树选择修改文件，在右侧查看差异，并执行暂存、提交、拉取和推送。Lazygit 提供交互界面与 Git 操作，Delta 负责差异高亮。

## 1. 安装

以下操作在 macOS 的 Ghostty 终端中执行，需已安装 [Homebrew](https://brew.sh/) 和 Git。

```bash
brew install lazygit git-delta
lazygit --version
delta --version
```

更新时运行 `brew update`，再运行 `brew upgrade lazygit git-delta`。

## 2. 配置左侧文件树与右侧差异

1. 找到 Lazygit 实际使用的配置目录：

   ```bash
   lazygit --print-config-dir
   ```

   本机 macOS 使用 `~/Library/Application Support/lazygit/config.yml`。

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
     screenMode: normal
     sidePanelWidth: 0.25
     enlargedSideViewLocation: left
     showFileTree: true
     mouseEvents: true
     showCommandLog: false

   git:
     diffRenderers:
       - command: delta --{{colorScheme}} --paging=never
   ```

   - `screenMode: normal` 使用常规布局，左侧保留状态、文件、分支、提交等面板，右侧显示差异；`sidePanelWidth: 0.25` 将左侧默认宽度设为约 25%，右侧约 75%。
   - `showFileTree` 启用目录树。
   - `mouseEvents` 启用鼠标操作。
   - `showCommandLog: false` 隐藏命令日志区域。
   - `language: zh-CN` 使用简体中文；`{{colorScheme}}` 让 Delta 跟随终端深浅主题。
   - `--paging=never` 关闭 Delta 自身分页，由 Lazygit 管理滚动与按键。Lazygit 内不使用 Delta 的 `n`、`N` 区块导航。

### 调整左右宽度（不等宽）

- 保持 `screenMode: normal`。切换到 `half` 且 `enlargedSideViewLocation: left` 时，只显示当前侧面板及其内容，并强制左右等宽，`sidePanelWidth` 不生效。
- `+` / `_` 只切换 `normal`、`half`、`full` 布局，不能连续调整宽度。
- 当右侧并排显示已暂存和未暂存两个差异面板时，Lazygit 会自动调整比例，左侧可能小于设定宽度。

宽度行为依据 [v0.66.2 布局实现](https://github.com/jesseduffield/lazygit/blob/v0.66.2/pkg/gui/controllers/helpers/window_arrangement_helper.go#L241-L268)及[鼠标处理实现](https://github.com/jesseduffield/lazygit/blob/v0.66.2/pkg/gocui/gui.go#L1654-L1789)。

## 3. 常用操作

下表中的文件操作以“文件 / Files”面板为上下文；同一按键在其他面板可能有不同作用。

| 按键 | 作用 |
| --- | --- |
| `2` | 回到文件面板 |
| `↑` / `↓` 或 `k` / `j` | 选择文件，右侧自动更新差异 |
| `Enter` | 对目录展开或折叠；对文件聚焦差异，按块或逐行操作 |
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

仅查看差异时，选择文件即可，不需要按空格。按 `Enter` 聚焦差异时，使用 Lazygit 原生显示，默认选择整个差异块，可按 `a` 切换到逐行选择；按 `Esc` 返回文件树与 Delta 预览。提交前先检查暂存内容；`p`、`P` 分别会更新本地仓库和远程仓库。

## 4. 在 Herdr 中查看项目差异

### 4.1 配置弹窗快捷键

弹窗绑定写在 **Herdr 配置** `~/.config/herdr/config.toml` 中，不是 Lazygit 的 `config.yml`。把以下命令块合并到现有配置；如果已经有相同绑定，保留一份即可，不覆盖其他配置：

```toml
[[keys.command]]
key = ["cmd+shift+g", "prefix+d"]
type = "popup"
command = "cd \"${HERDR_ACTIVE_PANE_CWD:-.}\" && exec lazygit"
description = "Git status"
width = "90%"
height = "85%"
```

`HERDR_ACTIVE_PANE_CWD` 是当前面板的目录，因此从哪个项目打开，就查看哪个项目。

本机 Herdr 前缀为 `Ctrl+b`，所以 `prefix+d` 表示先按 `Ctrl+b`、松开，再按 `d`。若使用 `Cmd+Shift+G`，还需要在 Ghostty 的配置中让出该按键：

```ini
keybind = super+shift+g=unbind
```

本机 Ghostty 配置文件为 `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty`。保存后按 `Cmd+Shift+,` 重载 Ghostty，再检查并重载 Herdr：

```bash
herdr config check
herdr server reload-config
```

然后在当前 Herdr 客户端按 `Ctrl+b → Shift+r`，重载客户端快捷键。

### 4.2 打开、验证与退出

1. 按 `Cmd+Shift+G` 或 `Ctrl+b → d`，打开 Lazygit 浮动窗口。
2. 左侧选择修改文件，右侧查看 Delta 高亮差异。
3. 按 `?` 查看当前面板的操作键；按 `q` 退出 Lazygit，浮动窗口随之关闭，返回原面板。

### 4.3 组成代码查看标签

作者配套指南还调整了 panel 分组、分支颜色和多个 diff renderer：分支颜色按名称前缀匹配，不会识别真正作者；配置多个 renderer 后可用 `|` 切换；自动 fetch 会访问远程。这些是作者的额外个人配置，本机沿用第 2 节已有布局，没有改成等宽。

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

按 `2` 回到 Files；若处于 full，按两次 `_` 经 half 返回 normal；若处于 half，按一次 `_` 返回 normal，恢复自定义宽度比例。确保 Ghostty 窗口足够宽，并在普通 shell 中运行 Lazygit；若外层终端复用器或其他终端界面拦截按键，先退出该界面或检查其快捷键，再按 `?` 核对 Lazygit 当前按键。

### 差异没有高亮

先确认 `delta --version` 成功，再检查配置缩进、`git.diffRenderers` 中的命令及可执行文件路径。存在多个渲染器时，按 `|` 切换到 Delta；不要把 Delta 自身分页器的快捷键当作 Lazygit 快捷键。

### Herdr 弹窗没有打开或不是目标项目

- 两种按键都无效：执行 `herdr config check`，再用 `Ctrl+b → Shift+r` 重载当前客户端配置，按 `Ctrl+b → ?` 检查生效的绑定。

## 6. Git 操作指南

以下操作适用于 **Lazygit 0.66.2** 默认快捷键，参考 [Jesse Duffield 的功能演示](https://www.youtube.com/watch?v=CPLdltN7wgE)整理。

在项目目录运行 `lazygit`。按 `2` 到 Files、`3` 到 Branches、`4` 到 Commits、`5` 到 Stash；先选面板再操作，按 `?` 查看当前快捷键。大写字母表示按住 Shift。

**整理历史前注意：** amend、rebase、squash 和移动补丁会重写提交。已推送且被他人依赖的历史，先协调再操作。

### 6.1 整文件暂存

1. 在 Files 选择文件，检查右侧差异。
2. 空格切换该文件的暂存状态；`a` 切换全部文件的暂存状态。
3. 按 `c` 填写说明并提交已暂存内容。无关修改留待下一次提交。

### 6.2 逐行与范围暂存

1. 在 Files 选中文件，按 `Enter` 聚焦差异；默认选择整块，按 `a` 切换逐行选择。
2. 用方向键移动，空格暂存选中行；按 `v` 开始范围选择，扩展选区后按空格。
3. `Tab` 切换已暂存 / 未暂存侧，空格切换暂存状态；`Esc` 返回 Files，再按 `c` 提交。

`d` 在已暂存侧是取消暂存，在未暂存侧是丢弃修改。先确认当前面板。

### 6.3 挑选提交（Cherry-pick）

1. 在来源分支的 Commits 中选中提交，按 `C` 标记；可逐个标记多个提交。
2. 到 Branches 选中目标分支，按空格检出。
3. 回到 Commits，按 `V` 应用提交；有冲突则解决后继续。

来源提交仍保留，目标分支通常生成新的提交 ID。

### 6.4 丢弃修改

- 整文件：Files 选中文件，按 `d` 选择丢弃范围。
- 部分代码：聚焦差异，在未暂存侧选中行或块，按 `d`。
- 整个工作区：Files 按 `D` 打开重置菜单，核对范围后执行。

这些操作可能永久丢失未提交内容，尤其是未跟踪文件。不确定是否还要时，先 stash 或备份。

### 6.5 交互式变基与提交排序

在 Commits 选中提交后操作：

| 按键 | 作用 |
| --- | --- |
| `e` | 开始交互式变基，在选中提交处停下以便编辑 |
| `s` | Squash 到父提交，合并提交说明 |
| `f` | Fixup 到父提交，保留父提交说明 |
| `d` | 丢弃选中提交 |
| `r` / `R` | 在界面 / 编辑器中修改提交说明 |
| `Ctrl+j` / `Ctrl+k` | 向下 / 向上移动提交 |
| `m` | 打开 Continue、Abort 等变基操作 |

变基中只能修改当前 HEAD 的说明，不能直接对待执行的 TODO 提交 reword。完成后检查提交顺序与最终代码。

### 6.6 把修改补入旧提交

1. 在 Files 中只暂存要补入的修改。
2. 到 Commits 选中应接收修改的旧提交，按 `A` 确认修订。
3. 解决可能出现的冲突，检查修改已进入正确提交。

### 6.7 Fixup 与自动合并

1. 暂存修正内容，在 Commits 选中原提交，按 `F`，选择创建 `fixup!` 提交。
2. 评审期间可保留这些修正提交，便于查看每轮变更。
3. 整理时选中功能分支最早的提交，按 `S`，选择合并上方或当前分支的 fixup 提交，核对范围后确认。

`F` 创建修正提交，`f` 直接把选中提交并入父提交。后续自动合并会重写历史。

### 6.8 打开 Pull Request

1. 按 `P` 推送分支，首次推送按提示设置上游；小写 `p` 是拉取。
2. 在 Branches 选中该分支，按 `o` 打开 PR 创建页面。
3. 在浏览器核对来源与目标分支、填写说明，再完成创建。

### 6.9 Revert 撤销提交

在 Commits 选中要撤销的提交，按 `t` 并确认；有冲突则解决后继续。检查新增 revert 提交的差异，再验证和推送。

Revert 用新提交抵消原提交，保留原有历史，适合撤销共享分支上的修改。撤销合并提交时需确认主线选择。

### 6.10 只储藏部分修改

1. 在 Files 中暂存要收起的文件或代码行。
2. 按 `S` 打开菜单，再按 `s` 选择“仅储藏已暂存修改”，填写说明。
3. 检查剩余修改与 Stash 条目。恢复时在 Stash 选中条目，空格为 Apply（保留条目），`g` 为 Pop（成功恢复后移除条目）。

Files 中直接按 `s` 是储藏全部修改。注意区分“只储藏已暂存”与“保留暂存、储藏其余修改”；未跟踪文件是否包含在内，以选项和结果为准。

### 6.11 在旧提交间移动或移除代码

1. 在 Commits 选中来源提交，按 `Enter` 查看文件，再选中文件按 `Enter` 查看差异。
2. 按 `a` 切换逐行选择，空格把所需内容加入自定义补丁，检查右侧结果。
3. 逐级按 `Esc` 返回 Commits；若要移动代码，选中接收补丁的目标提交。
4. 按 `Ctrl+p` 打开补丁菜单：`m` 将补丁移动到所选提交，`d` 从原提交移除补丁。

操作要求当前没有进行中的 merge / rebase，且相关历史允许变基。若后续提交依赖这些代码，可能产生冲突；完成后检查来源、目标提交与最终文件。

### 6.12 解决合并冲突

1. 在 Files 选中冲突文件，按 `Enter`。
2. 方向键选择冲突内容，空格接受所选内容，`b` 保留双方；需改写时用编辑器处理。
3. 检查冲突标记已清除、内容正确，并确认解决结果已暂存。
4. 若正在合并、变基或 cherry-pick，按 `m` 选择 Continue 继续，或 Abort 放弃；完成后执行项目所需的构建或测试。

根据代码含义选择结果，不要仅凭 rebase 中的 ours / theirs 判断哪边是自己的修改。

### 6.13 变基到最新远程主线

1. 提交或储藏未完成修改，保持当前为自己的功能分支。
2. 在 Files 按 `f` 执行 fetch。
3. 按 `3`，用 `[` / `]` 切到 Remotes；在远程上按 `Enter` 展开，选中 `origin/main` 等实际目标，再按 `r`。
4. 解决冲突并继续，完成后检查历史、差异和测试结果。

`r` 将**当前分支**变基到所选分支之上，不要先检出主线。本地 Branches 的 `f` 是 Fast-forward，Files 的 `f` 才是 fetch；推送被拒绝时先核对历史，不要直接强推。

### 6.14 带着未提交修改切分支

1. 在 Branches 选中目标分支，按空格检出。
2. 若本地修改阻止切换，按提示确认 Autostash；Lazygit 会储藏、切换分支，再恢复修改。
3. 检查当前分支、Files 和 Stash；恢复时有冲突则先解决。

不要改用 `F` 强制检出，它会丢弃本地修改。

### 6.15 自定义主题

用 `lazygit --print-config-dir` 找到配置目录，把以下字段合并到 `config.yml` 已有的 `gui` 节点：

```yaml
gui:
  theme:
    activeBorderColor: [yellow, bold]
    inactiveBorderColor: [red]
```

活动面板边框为黄色加粗，其他面板为红色。保存后重新打开 Lazygit 检查效果。
