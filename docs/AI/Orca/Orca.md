# Orca

## 项目和工作区

**“添加项目”是把代码仓库或文件夹接入 Orca；“新工作区”是在某个项目下，开一个用来完成具体任务的工作环境。一个项目可以有多个工作区。**

|                      | 「添加项目」                                      | 「新工作区」                                           |
| -------------------- | ------------------------------------------------- | ------------------------------------------------------ |
| **主要作用**         | 告诉 Orca：我要处理这个仓库或文件夹               | 告诉 Orca：我要在某个项目里开展一项工作                |
| **操作对象**         | 整个项目，例如 `my-app`                           | 项目下的工作区，例如“修复登录”“开发搜索”               |
| **通常什么时候用**   | 第一次把某个项目加入 Orca，或者开始处理另一个项目 | 为已有项目开一个新任务，或并行尝试另一种方案           |
| **创建时主要选什么** | 要加入的目录或仓库                                | 所属项目、工作区名称、Agent，以及 Git 项目的起始分支等 |

官方入门流程也是：先添加仓库，再创建工作区，然后选择在其中运行的 Agent。普通的非 Git 文件夹也可以通过界面加入。[Orca Docs](https://www.onorca.dev/docs/first-session?utm_source=chatgpt.com)

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
