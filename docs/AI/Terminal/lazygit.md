# Lazygit + Delta

在 Ghostty 中运行 Lazygit，可以用左侧文件树选择修改文件，在右侧查看差异，并执行暂存、提交、拉取和推送。Lazygit 提供交互界面与 Git 操作，Delta 负责差异高亮。

Lazygit 是独立终端程序，也可以在 [Herdr](Herdr.md) 中以分屏或浮动窗口使用；它不是 Herdr 内置的 Git 功能。Delta 单独使用时见 [Delta 文档](delta.md)。

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

   本机 macOS 使用 `~/Library/Application Support/lazygit/config.yml`；在其他机器上以命令输出为准。

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

## 4. 在 Herdr 中查看项目差异

这一部分整理自 Dave Ebbelaar 的 [Herdr 完整指南视频（21:09）](https://www.youtube.com/watch?v=Shqtk_2Jd3c&t=1269s)和[作者 Lazygit 配套指南](https://learn.datalumina.com/docs/herdr/lazygit)。配置核对日期为 **2026-11-14，Herdr TUI 0.9.5、Lazygit 0.66.2**。

纯 Agent 对话不容易直观看到当前分支、目录结构和未提交修改。视频用 Neovim 浏览代码，用 Lazygit 审核 Git 差异；当前项目中的 Lazygit 弹窗可以随时打开，查看完再返回 Agent。

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

- 按键无效：先试 `Ctrl+b → d`；若前缀按键有效而 `Cmd+Shift+G` 无效，检查 Ghostty 是否已让出快捷键并重载。
- 两种按键都无效：执行 `herdr config check`，再用 `Ctrl+b → Shift+r` 重载当前客户端配置，按 `Ctrl+b → ?` 检查生效的绑定。
- 弹窗显示的目录不是 Git 项目：在打开弹窗的空闲 Shell 面板运行 `pwd`，进入实际仓库后再打开；不要把 Shell 命令输入正在运行的 Agent 对话中。

## 6. 官方资料

- [Homebrew Lazygit](https://formulae.brew.sh/formula/lazygit)
- [Lazygit v0.66.2 配置](https://github.com/jesseduffield/lazygit/blob/v0.66.2/docs/Config.md)
- [Lazygit v0.66.2 差异渲染器与 Delta](https://github.com/jesseduffield/lazygit/blob/v0.66.2/docs/Custom_DiffRenderers.md)
- [Lazygit v0.66.2 快捷键](https://github.com/jesseduffield/lazygit/blob/v0.66.2/docs/keybindings/Keybindings_en.md)

## 15 个实用功能

未核对视频画面中的快捷键及其与当前版本的差异，实际操作时请按 `?` 查看当前上下文的按键。

### 第 2 章：快速暂存文件

假设我打开 Lazygit，想把这些文件暂存，只需要用方向键逐个选中文件，再按空格键。现在它们就都已经暂存了，可以提交。

另一种方法是直接按 `a`，一次性切换所有文件的暂存状态。

### 第 3 章：逐行暂存

第二个功能是暂存单独的代码行。

选中一个文件后，不按空格，而是按回车，就能进入文件的差异内容。接下来可以向下移动，每按一次空格，就会把选中的那一行加入暂存区。

比如，我可能只想先提交这一块内容。写个提交说明，提交。看，这个提交就出现了。接着，我可以再提交剩下的内容。

还可以按 `v` 开始选择一个范围，然后按空格，将这个范围里的内容一起暂存。

按 Tab 切换到另一侧后，可以按 `d` 取消暂存。

也可以回到这里按 `d`，直接丢弃这一行的修改。

好，再提交一次。现在我们有两个提交了。

接下来，我要展示第三个功能：挑选提交。

### 第 4 章：挑选提交

选中其中一个提交，按 `c`，再选中另一个提交按 `c`，就可以把它们选为要挑选的提交。

现在切换到另一个分支。如果想把这些提交粘贴过来，只需要按 `b`，然后确认要把它们移过来。

这样就完成了。

### 第 5 章：清空工作区改动

接下来，假设我们还没有提交这些改动，先让它们回到工作区。

如果想丢弃所有这些内容，其实很简单。

首先，可以选中一个文件，按 `d`，然后选择“丢弃所有修改”。这不会删除文件，只会丢弃工作区中对这个文件所做的修改。

按 `Shift+D` 则会出现更多选项，比如硬重置、软重置等。

其中一个我经常使用的功能，是彻底清空工作区改动。因为有时候 `git status` 会列出一大堆文件，而你完全不在乎这些修改，只想把它们全部清掉。

这个命令就能帮你做到。看，现在都没了。

### 第 6 章：交互式变基

接下来是交互式变基。

有时，你想修改几个提交之前的内容。通常，你可能会到命令行里执行交互式变基。

不过，在这里，我会直接进入提交面板。可以用左右方向键切换这些面板，然后按 `e`，就开始了一次交互式变基。

这些提交目前的操作都是 `pick`，也就是保留提交。你可以修改每个提交对应的操作：要编辑就按 `e`，要合并就按 `s`，要执行 `fixup` 就按 `f`。还可以选择保留或丢弃提交。

这里暂时不能执行 `reword`，也就是修改提交说明。你可以在没有进行交互式变基时修改，但我们还没有把这个功能加到这里。

假设我们保留这些提交……或者，把其中几个合并起来。将这个提交合并到前一个提交中，然后按 `m` 打开变基操作菜单，选择继续。

看，合并完成了。挺方便的。

还可以做什么呢？你也可以调整提交顺序。

在这个状态下，按 `Ctrl+J` 或 `Ctrl+K`，就能上下移动提交、交换它们的位置。这在需要重新排列提交时很有用。

现在先中止这次变基。以上就是交互式变基。

另一个很实用的功能是修订提交。

假设这部分改动还没有放进提交，而我想把它加到这个较早的提交里，因为它更适合属于那个提交，而不是最新的提交，也不适合单独创建一个新提交。

我可以选中目标提交，按 `Shift+A`，然后确认要修订它。

好了，现在这部分改动就在那个提交里了。

顺便说一下，按回车就可以查看某个提交实际包含的文件。

这个功能很方便。你还可以创建 `fixup` 提交。

比如，我不想直接修订这个提交，而是想先创建一个用于修正它的提交，因为我不想现在就强制推送。假设我正在处理一个 Pull Request，其他人还在评审。

这里可以创建一个针对所选提交的 `fixup` 提交。按 `Shift+F`，然后回车。

现在，这个新提交就是用来修正那个提交的。

接着，选中这里的提交……有一个选项，可以把上面的这些 `fixup` 提交都合并进去。

按 `Shift+F`……抱歉，是 `Shift+S`。它会询问：“确定要合并上面的所有 `fixup` 提交吗？”

确认，完成。

现在，刚才那一点修改就进入了它原本要修正的提交中。

### 第 7 章：打开 Pull Request

还有一个很方便的功能：只按一个键，就能打开 Pull Request 页面。

在这里按 `o`……不过，要先推送。

按 `Shift+P` 推送，按小写的 `p` 则是拉取。

然后打开 Pull Request，它就会在浏览器中打开相应页面。

我把浏览器窗口拖过来。看，这里已经选中了对应的分支，直接填写 Pull Request 就行。

### 第 8 章：撤销提交

还有什么呢？修订提交、创建 `fixup` 提交都介绍过了。我们也可以很方便地撤销一个提交。

假设我后悔加入了这些内容，但这个提交可能已经在 `master` 分支上了，那么最合适的做法就是通过 `revert` 撤销它。

按 `t`，好了，已经撤销了。

这些操作都可以在菜单里找到。按 `x`……我以为问号也可以？不行，还是按 `x`。向下滚动，就能看到具体有哪些选项。

接下来还有一个很实用的功能。

有时，你只想储藏一部分修改，而不是全部修改。假设这些修改还在，我只想储藏这个 GoReleaser 相关文件的改动，不想储藏另外两个文件。

先按空格把这个文件暂存，然后按 `Shift+S`。

顺便说一下，普通的储藏操作只需要按 `s`。而按 `Shift+S`，就可以选择只储藏已暂存的修改。

选中这个选项，按回车，随便起个名字。

看，下面只储藏了那一个文件。如果你想储藏某些修改，同时保留其他修改，这个功能就很有用。

接下来，我们看看怎样处理旧提交里的内容。

我切换到一个小型测试仓库来演示，先确认配置正确。好的。

这里有一份购物清单。我把垃圾食品放在一个提交里，把乳制品放在另一个提交里。

这只是一个示例：每个提交都应该在逻辑上相对独立。但是，垃圾食品那个提交的末尾出现了牛奶。

牛奶显然不应该放在那里，它应该属于乳制品那个提交。

我可以先按回车查看提交中的文件，再按一次回车查看具体内容。然后用方向键向下移动，选中牛奶这一行，把它加入右侧的自定义补丁。

按几次 Esc 返回，再选中乳制品那个提交。

接着按 `Ctrl+P`，选择“将补丁移动到所选提交”。

完成了。很方便吧？

另一个例子是，从旧提交里删除某些内容。比如，你不小心提交了 `binding.pry` 或 `console.log` 之类的调试代码，现在想把它们去掉。

这里有一个较新的提交，把可乐替换成了柠檬汽水。

如果我们回到前面的提交，删除可乐这一行，再选择“从原提交中移除补丁”，Lazygit 就会在后台执行一次交互式变基。

当它处理到那个把可乐替换成柠檬汽水的较新提交时，就会发现问题：前面已经把可乐删掉了，而后面的提交又想把可乐替换成柠檬汽水。现在应该怎么办？

这就会产生合并冲突。

### 第 9 章：解决合并冲突

我选择继续处理这些冲突，然后打开购物清单。

我喜欢柠檬汽水，所以选择保留柠檬汽水。完成。

现在回头看看，购物清单里有柠檬汽水，而垃圾食品那个提交里已经没有可乐了。

这个功能很不错。

### 第 10 章：轻松变基到 origin/master

接下来，看看怎样轻松地把当前分支变基到 `origin/master`。

先回到 Lazygit 的仓库。我先清掉这两个东西。我知道这样操作没问题，不过在你自己的仓库里，不一定也是如此。

接下来获取 `master` 的最新内容，让它与 `origin/master` 保持同步。

然后按 `r`，把当前分支变基到它上面。

出现冲突了，没关系，因为我确实做过一些修改。这里就选择同时保留两边的内容。按 `b`，保留冲突双方的内容，然后继续。

完成。

所以，要变基到最新的 `origin/master`，操作很简单：先按 `f` 获取最新内容，再按 `r` 进行变基。

### 第 11 章：带着未提交的修改切换分支

接下来还有几个功能。比如，带着未提交的修改切换分支。不过，我不确定现在这个仓库能不能演示出来。

假设我做了一些修改……先重置一下这个提交，再试着切换到另一个分支。

有时候，切换分支会报错，说现有修改可能与目标分支产生冲突。

但在 Lazygit 里，你不需要自己先储藏修改、切换分支，再恢复修改。它会直接询问：“要我帮你处理这些步骤吗？”

这里我选择是，先把修改临时保存起来。

好了，这次很幸运，甚至没有出现合并冲突。

这就是那种会让人觉得“真方便”的功能。很多时候，工具只会给你一条错误信息，然后你还得手动储藏和恢复修改，尽管最终可能根本不会产生冲突。

即使真的出现了冲突，也没关系，直接在工作区里处理就行。

还有什么呢？应该还有一两个功能。
