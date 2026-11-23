# Orca

Orca 把 Git worktree、Agent 会话、代码差异和浏览器放在同一工作区，方便多个 Agent 并行开发。每个独立写代码的任务使用自己的 worktree，最后再审查、测试和合并成果。

本文的并行开发用法整理自大书大的[《【实测】Orca：多个 Coding Agent 并行开发》](https://www.douyin.com/video/7688607402861612315)，操作入口按 2026-11-19 的官方文档核对。

## 安装与准备

从[官网](https://orca.dev)下载对应系统版本。macOS 已安装 Homebrew 时，也可以执行：

```bash
brew install --cask stablyai/orca/orca
```

## 项目和工作区

**“添加项目”是把代码仓库或文件夹接入 Orca；“新工作区”是在某个项目下，开一个用来完成具体任务的工作环境。一个项目可以有多个工作区。**

|                      | 「添加项目」                                      | 「新工作区」                                           |
| -------------------- | ------------------------------------------------- | ------------------------------------------------------ |
| **主要作用**         | 告诉 Orca：我要处理这个仓库或文件夹               | 告诉 Orca：我要在某个项目里开展一项工作                |
| **操作对象**         | 整个项目，例如 `my-app`                           | 项目下的工作区，例如“修复登录”“开发搜索”               |
| **通常什么时候用**   | 第一次把某个项目加入 Orca，或者开始处理另一个项目 | 为已有项目开一个新任务，或并行尝试另一种方案           |
| **创建时主要选什么** | 要加入的目录或仓库                                | 所属项目、工作区名称、Agent，以及 Git 项目的起始分支等 |

### 举个例子

假设你有一个网站项目 `my-app`，想同时修复登录问题、开发搜索功能：

1. 点 **“添加项目”**，选择 `my-app` 的代码目录。
2. 点 **“新工作区”**，选择 `my-app`，创建“修复登录”，让 Claude Code 处理。
3. 再点 **“新工作区”**，仍然选择 `my-app`，创建“开发搜索”，让 Codex 处理。

### 一个容易混淆的细节

**“新工作区”是否有独立的文件，要看项目类型：**

- **Git 项目**：常规的新工作区使用独立的 worktree，分别修改各自目录里的代码。[Orca Docs](https://www.onorca.dev/docs/model/worktrees?utm_source=chatgpt.com)
- **普通文件夹项目**：也能有多个工作区，但它们可以指向**同一个文件夹**，分别管理工作会话。因此，不能仅凭创建了多个工作区，就认为文件也被复制并隔离了。[GitHub](https://github.com/stablyai/orca/issues/22712?utm_source=chatgpt.com)

**你现在如果是要打开电脑上的某个代码项目，先点左边“添加项目”；之后想在这个项目里开新的任务，再点右边“新工作区”。**

## 多 Agent 并行开发

### 同一个问题，比较多个方案

按上面的流程创建三个 Git 工作区，选择**相同的起始提交、不同的新分支**，分别启动 Claude Code、Codex、Cursor CLI，也可以换成自己已配置的 Agent。三个终端输入相同任务，例如：

```text
登录接口在高并发下偶发 500，请定位并修复竞态问题。
补充能复现问题的回归测试，保持对外接口不变。
完成后说明根因、修改范围、测试命令和实际结果。
本轮只完成本地修改与验证。
```

在仓库终端用 `git worktree list` 检查各工作区的路径和分支。新建 worktree 从选定提交开始，主目录尚未提交的改动不会自动带过去；各工作区按项目要求准备依赖，多个开发服务使用不同端口。

比较各方案的正确性、改动范围和测试证据，选择合适的一份再集成。**独立目录能避免互相覆盖文件，后续合并仍可能冲突。**需要把需求拆给多个 Agent 协作时，参见[编排](编排.md)。

### 分屏查看进度

- 把工作区标签拖到面板右侧或下侧边缘，建立左右或上下分屏；终端、差异和浏览器可以并排显示。
- macOS 按 `Cmd+J` 找到工作区，选中后按 `Shift+Enter` 也可分屏打开。
- 根据“运行中、等待输入、空闲或结束、失败”等状态，优先处理需要确认或报错的会话。

分屏不会创建独立代码副本；Agent 空闲或结束也不代表测试通过，需要检查终端结果和代码差异。[工作区导航](https://orca.dev/docs/model/quick-open)

### 审查差异，把意见集中发回 Agent

1. 打开工作区的 **Diff**，确认比较基准，检查已暂存、未暂存和未跟踪文件。
2. 在问题行旁点击 `+`，或选中多行添加批注，写清触发条件、问题和预期。例如：“先查询再加锁仍可能产生并发竞争，请检查临界区并补回归测试。”
3. 收集好本轮意见，点击 **Send to agent**，选择对应会话，一次发送。
4. 修改完成后重新检查差异和测试结果，确认问题已解决，再按行或代码块暂存需要提交的内容。
5. 按项目流程执行提交、推送和 PR 评审。**暂存、发送批注、提交、推送、合并是不同操作。**

Diff 面板常用键如下；快捷键作用于当前聚焦的差异视图。[差异视图](https://orca.dev/docs/review/diff-viewer) · [代码批注](https://orca.dev/docs/review/annotate-ai-diff)

| 按键 | 操作 |
| --- | --- |
| `j` / `k` | 下一个 / 上一个变更文件 |
| `n` / `p` | 下一个 / 上一个代码块 |
| `s` | 暂存光标所在的整个代码块 |
| `c` | 开始写批注 |

### 用 Design Mode 修改页面

1. 在工作区启动项目的开发服务，用该工作区的浏览器打开页面。
2. 点击浏览器工具栏的 **Annotate**，选中需要调整的元素。
3. 描述具体效果，例如：“按钮与输入框间距改为 16px，小屏幕下保持对齐”，发送给对应 Agent。
4. 等待热更新或刷新，核验页面效果及交互，再检查代码差异。

元素信息可包含 HTML、CSS 和截图；源文件行号依赖可用的 source map。批量发送页面批注时默认发送简短摘要，需要完整页面信息时勾选 **Include page details**。[Design Mode 用法](https://orca.dev/docs/browser/design-mode)

## 日常操作与扩展

| 功能 | 使用方法 |
| --- | --- |
| 快速找文件或评审 | `Cmd+P` 搜当前工作区的文件。`Cmd+J` 跨工作区查找标签和会话。已有评审缓存时，还能输入 GitHub PR 编号（如 `#123`）或 GitLab MR 编号（如 `!123`）找到对应工作区。[跳转面板](https://orca.dev/docs/model/quick-open) |
| 通知与用量 | 开启需要的完成或待处理通知，点击通知回到工作区；状态栏查看受支持账号的用量和重置时间。 |
| Codex 账号切换 | 在 **Settings → Agents → Codex Accounts** 管理账号，从状态栏选择。选择作用于之后启动的会话，已有进程重启前仍使用原账号。[说明](https://orca.dev/docs/agents/codex-hot-swap) |
| Task 子代理 | 主 Agent 派出的子任务可在支持的会话界面展开查看；子代理不等于独立 worktree，需要文件隔离和任务交接时使用[Orca 编排](编排.md)。 |
| 新会话继续 | 先让原 Agent 总结目标、改动、验证和待办，再把摘要交给新会话。需要近期终端记录时，右键终端选择 **Copy Context**；新会话先核对分支和改动。[说明](https://orca.dev/docs/terminal#copy-terminal-context) |
| 会话恢复 | 后台守护进程仍存活时，重新打开 Orca 可以接回原终端；电脑重启或守护进程退出后，需要重新启动 Agent。[说明](https://orca.dev/docs/model/session-restore) |
| 空闲会话休眠 | 后台工作区多、想释放内存时，可在 **Settings → Experimental → Agent hibernation** 开启。此功能默认关闭。开启后，支持恢复的 Agent 完成本轮任务并在后台空闲满设定时长（默认 30 分钟），满足条件时会休眠。重新打开工作区会恢复会话。[休眠条件](https://orca.dev/docs/agents/hibernation) |
| SSH 开发 | **Settings → SSH → Add Target** 添加并测试主机，创建工作区时在 **Run on** 选择它；代码和 Agent 在远端运行。[说明](https://orca.dev/docs/ssh) |
| 手机查看 | 在桌面端生成配对码，用移动端 **Pair** 连接；手机查看进度或回复，执行仍依赖主机及连接可用。[说明](https://orca.dev/docs/mobile) |

### CLI 与定时任务

需要让 Agent 创建工作树、分派任务和收集结果时，先按[编排](编排.md)安装 Orca CLI、`orca-cli` 和 `orchestration` 技能，命令以本机版本的指南为准。

视频中还用命令行查看工作区状态。已安装 Orca CLI、且桌面端已选中目标工作区时，在终端运行 `orca snapshot --worktree active --json`，可以读取当前工作区的快照，供脚本判断下一步。[CLI 命令参考](https://orca.dev/docs/cli/reference)

要让 Agent 操作桌面应用，可以按需使用 Orca 的 `computer-use` 技能。要让支持 MCP 的 Agent 调用外部工具，在 **Settings → Integrations → MCP** 登记对应的服务端点。[技能与 MCP](https://orca.dev/docs/cli/skills)

定期巡检可在 **Automations** 中配置：

1. 选择运行主机、项目或已有工作区，以及 Agent。
2. 填写任务提示词，例如：“运行本项目已有测试，汇总失败项、命令和日志位置，只输出报告。”
3. 设置每天、工作日、每周等周期或 cron，并核对时区；先保存为禁用状态。
4. 手动运行一次，检查运行记录、目标目录和输出，确认符合预期后启用计划。

可用前置检查命令跳过不满足条件的轮次。连接多台主机后，**Automations** 会汇总各主机的计划，排查漏跑时先核对任务所属主机和最近一次运行记录。[定时任务说明](https://orca.dev/docs/cli/automations)

定时任务按计划投递提示词。如果要求开发完成后立即测试，把测试写进开发任务的验收条件，或安排为依赖开发任务的下一步。[终端工作流](../Agent/智能体开发新需求.md)

## 工作区重命名

### 显示名称、Git 分支与目录名

这三个名称分别管理，不需要保持一致：

| 名称 | 含义 | 示例 |
| --- | --- | --- |
| 显示名称 | Orca 左侧工作区卡片上的名称 | `InvoiceVoucher` 或“凭证与发票” |
| Git 分支名 | 当前 worktree 检出的分支 | `dungeness` |
| 目录名 | 工作区在磁盘上的文件夹名称 | `/Users/michael/orca/workspaces/ios-cbc/dungeness` |

**手动设置显示名称可以通过 Orca 的 `worktree set --display-name` 完成，不会同时重命名 Git 分支或磁盘目录。** [Orca CLI 官方指南](https://github.com/stablyai/orca/blob/main/skill-guides/orca-cli.md)

### “重命名失败”如何判断

出现红色“重命名失败”标记时，可以在目标工作区目录的终端执行：

```bash
orca worktree current --json
```

查看返回结果中 `result.worktree.firstAgentMessageRenameError` 的具体错误。例如：

```text
Generation timed out after 60s.
```

这表示根据首次 Agent 消息自动生成名称的任务在 60 秒后超时。这条错误本身不能证明 Git 分支重命名冲突；显示名称也可能已经成功设置，只是自动命名错误记录仍然保留。

同时查看 `displayName`（显示名称）、`displayNameMode`（命名模式）和 `branch`（Git 分支），区分实际名称与失败记录。`displayNameMode` 为 `fixed` 表示固定显示名称。

### 手动设置显示名称

确保 Orca 正在运行，并且终端可以执行 `orca`。以下以本机工作区为例，将其显示名称设置为“凭证与发票”；用于其他工作区时，替换路径与目标名称，保留 `path:` 前缀：

```bash
orca worktree set \
  --worktree "path:/Users/michael/orca/workspaces/ios-cbc/dungeness" \
  --display-name "凭证与发票" \
  --json
```

`--worktree` 指定要修改的工作区，`--display-name` 指定新的显示名称。该命令只更新 Orca 元数据；如果要修改 `dungeness` 分支名，需要另行处理 Git 分支重命名。

### 修改后核验

使用同一个工作区路径读取状态，避免检查到其他工作区：

```bash
orca worktree show \
  --worktree "path:/Users/michael/orca/workspaces/ios-cbc/dungeness" \
  --json
```

核对 `result.worktree` 中的以下字段：

- `displayName` 是否为目标名称，`displayNameMode` 是否为 `fixed`。
- `branch` 是否仍为原分支，例如 `refs/heads/dungeness`。
- `pendingFirstAgentMessageRename` 是否为 `false`，`firstAgentMessageRenameError` 是否已为 `null`。

本次现场复查确认：显示名称已是“凭证与发票”，Git 分支仍是 `dungeness`，自动命名任务不再等待且错误字段为 `null`。这确认的是 Orca 返回的元数据状态；红色标记是否已在界面消失，需要另外查看界面。不能仅凭设置名称的命令成功，就假定所有版本都会清除错误标记。
