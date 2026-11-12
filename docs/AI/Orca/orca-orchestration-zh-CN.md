# Orca CLI 多智能体编排（Orchestration）中文译文

- 原文：[Orchestration — Orca Docs](https://www.onorca.dev/docs/cli/orchestration)
- 翻译日期：2026-11-10

通过 Run、任务、受监督的执行智能体、消息和决策关卡，协调多个智能体。

Orchestration 是 Orca 中用于多智能体协作的结构化管理层，包含以下组成部分：**Run（命名空间＋协调者收件箱）、Task（任务）、Dispatch（派发记录）、受监督的 worker（执行智能体）、消息，以及决策关卡。**

当你需要明确任务归属、跟踪完成情况，或者构建 DAG（有向无环图）时，可以使用它。如果只是向智能体发送一次性提示，使用 `orca terminal send` 即可。如果希望完全移交任务负责权，且不再进行监督，则使用 `orca-cli` 技能中的 worktree／terminal 命令。

> **实验性功能**
>
> 使用这些命令之前，需要在 **Settings → Experimental（设置 → 实验性功能）** 中启用编排功能。实验性的 Orchestration 面板及其开关目前暂不可用。
>
> CLI 会与正在运行的 Orca 运行时通信，因此应先确保 `orca status --json` 能够成功执行。

worker 可以继续启动辅助 worker，嵌套层数受设置中的 **Nested worker depth（worker 嵌套深度）** 限制。默认值为 **4**；之前设为 **1** 的配置会自动调整为 **4** 一次，之后用户自行选择的值会被保留。停止一个 worker 时，也会停止它启动的辅助 worker。

## 核心模型

| 概念 | 含义 |
|---|---|
| **Run（运行实例）** | 持久化的命名空间和主收件箱。它本身不负责调度 worker，也不决定 worker 的运行位置。 |
| **Task（任务）** | 一个工作项，包含任务说明、依赖关系和状态。状态包括：`pending`（待处理）、`ready`（就绪）、`dispatched`（已派发）、`completed`（已完成）、`failed`（失败）、`blocked`（阻塞）。 |
| **Dispatch（派发记录）** | 某项任务在某个终端上的一次执行尝试。`worker_done` 和 heartbeat（心跳）消息对应的生命周期以它为准。 |
| **Message（消息）** | 收件箱中的消息，例如 `status`、`dispatch`、`worker_done`、`escalation`、`question`、`heartbeat` 等。 |
| **Decision gate（决策关卡）** | 由协调者负责处理的问题。在问题得到解决之前，相关任务会保持阻塞。 |

是否有权报告任务完成，由当前有效的 Dispatch 上下文决定。worker 的完成消息和心跳消息都应同时包含 `taskId` 和 `dispatchId`。

终端中显示的任务 ID，例如 `task_...`，是可点击的链接。点击后，Orca 会向运行时查询该任务当前的 Dispatch，并切换焦点到分配给它的终端。即使任务位于远程运行时或 SSH 运行时中，也支持这一行为。

## 推荐的受监督执行流程

```bash
orca orchestration run-create --objective "Split checkout QA and summarize blockers" --json
orca orchestration task-create --spec "Audit billing settings for mobile layout" --task-title "Billing audit" --json
orca orchestration worker-start --task <taskId> --worktree current --agent codex --json

# 或者使用新的 worktree：
orca orchestration worker-start --task <taskId> --worktree new-child --name billing-audit --agent codex --setup run --json

# 可选：为单个 worker 指定模型和推理强度。
# 适用于 Claude、Codex、Muse、Cursor、Antigravity、OpenCode；
# 不能与 --terminal 同时使用：
orca orchestration worker-start --task <taskId> --worktree current --agent claude --model <opaque-model-id> --effort high --json

# 在本地子 worktree 中，将 Antigravity 作为受监督的 worker 启动：
orca orchestration worker-start --task <taskId> --worktree new-child --name research --agent antigravity --setup run --json
```

`--model` 接受 Claude、Codex、Muse、Cursor、Antigravity 和 OpenCode 的供应商模型 ID，直接按原样传入。

- 对于 **Muse**，传入你安装的 Muse 所支持的模型 ID，例如 `muse-spark-1.3`。
- 对于 **Antigravity**，使用 `agy models` 列出的模型标识。
- 对于 **OpenCode**，指定的模型会在执行主机上进行验证，而且仅对当前 worker 生效，不会改变其他启动操作使用的默认模型。

`--effort` 必须与 `--model` 一起使用，并且只有对应智能体／模型支持指定的推理强度时才会生效。这两个参数都不能与 `--terminal` 同时使用，因为 `--terminal` 表示复用现有窗格。

对于比 Orca 内置列表更新的 Codex 模型，例如 `gpt-6.x`，只要安装的 Codex 支持，`--effort` 就可以接受所有已知的强度名称，包括 `max` 和 `ultra`；未知的强度名称仍会被拒绝。

这些覆盖设置仅对本次启动生效，并会显示在启动返回结果的 `launch.requested`／`launch.effective` 字段中。跨主机启动时，worker 所在主机需要声明支持启动偏好设置。

创建新的 worktree 时，可以省略 `--name`，让 Orca 自动生成名称。

在 **Settings → Agent Orchestration（设置 → 智能体编排）** 中，可以关闭 worker 心跳，或者将心跳间隔设为 **1～60 分钟**。默认间隔为 **5 分钟**。修改只会影响之后新派发的 worker；现有 worker 继续遵循原先收到的任务说明，旧版主机也会继续使用默认的 5 分钟间隔。

开启 **Chat UI（聊天界面）** 后，`worker-start` 启动受支持智能体的方式与新建智能体标签页相同：如果智能体和主机都支持，则使用结构化聊天界面；否则使用终端。`--terminal` 仍然表示复用现有窗格。

在启动 Antigravity worker 之前，Orca 会先为其本地子 worktree 准备信任配置。这套信任配置不支持通过 SSH 对 Antigravity 进行监督。关于 Antigravity 的常规智能体功能，请参阅原站的 **Supported agents（支持的智能体）** 文档。

### 等待任务完成

先处理一次 **Delivery（消息投递批次）** 中的所有消息，再进行确认（ack）：

```bash
orca orchestration check --wait --types worker_done,escalation,question --timeout-ms 900000 --json
orca orchestration check --ack <deliveryId> --wait --types worker_done,escalation,question --timeout-ms 900000 --json
```

### worker 报告完成

在 worker 所在窗格中执行，并携带系统注入的 ID：

```bash
orca orchestration send \
  --type worker_done \
  --subject "Completed mobile audit" \
  --body "Fixed footer overlap; no follow-ups." \
  --task-id <taskId> \
  --dispatch-id <dispatchId> \
  --outcome succeeded \
  --files-modified "src/app/settings/Billing.tsx" \
  --json
```

`worker_done` 必须指定 `--outcome succeeded|failed`，也就是明确说明执行成功还是失败。

### 检查与恢复

```bash
orca orchestration worker-show --dispatch <dispatchId> --json
orca orchestration worker-read --dispatch <dispatchId> --limit 50 --json
orca orchestration worker-stop --dispatch <dispatchId> --json

# worker_done 被接受后：
# 可以复用同一个终端执行后续 Dispatch，也可以释放它。
# 释放时会先归档可供查看的输出，
# 然后仅关闭由该协调者拥有的智能体终端：
orca orchestration worker-release --dispatch <dispatchId> --json

# 如果用户要求保留已结束的 worker 以便调试，
# 则让它继续保持运行：
orca orchestration worker-retain --dispatch <dispatchId> --json

# 重试时必须明确指定执行位置；
# --retry-of 不会继承原来的 --on 或 worktree 设置：
orca orchestration worker-start --task <taskId> --retry-of <dispatchId> --worktree current --agent codex --json
```

不要仅仅为了重新查看输出，就让已经完成的 worker 终端一直保持打开。可以先执行 `worker-release`，之后再通过 `worker-read` 查看输出。

如果释放操作返回 `release_pending` 或 `release_unknown`，不要改用作用范围更大的 `terminal close` 命令。应按照返回结果中的恢复指引操作。

## 跨主机 worker（可选）

```bash
orca orchestration worker-start \
  --task <taskId> \
  --on windows \
  --worktree new-top-level \
  --repo <exact_remote_repo_selector> \
  --name remote-worker \
  --agent codex \
  --setup run \
  --json

orca orchestration send --to dispatch:<dispatchId> --subject "Follow-up" --body "…" --json
```

后续命令会根据 Dispatch ID 路由到对应位置，不要再次传入 `--on`。

## 底层派发方式（自定义拓扑）

```bash
orca worktree create --name billing-audit --agent codex --json
orca terminal wait --terminal <workerHandle> --for tui-idle --timeout-ms 60000 --json
orca orchestration dispatch --task <taskId> --to <workerHandle> --inject --json
```

## 消息机制说明

- 默认情况下，`check` 会返回当前绑定 Run 中最早尚未确认的 Delivery，遵循 **先进先出（FIFO）** 顺序。在使用 `--ack` 确认之前，同一批消息会被重复返回。
- `--peek`／`--all` 不会消费消息。
- 支持的群组地址包括：`@all`、`@idle`、`@claude`、`@codex`、`@opencode`、`@gemini`、`@droid`、`@grok`、`@cursor`、`@worktree:<id>`。**不要使用群组地址发送 `worker_done` 或心跳消息。**
- 在 PowerShell 中，群组地址需要加引号，例如 `--to "@all"`。

```bash
orca orchestration send --to @all --subject "Heads up" --body "Pausing dispatches for a review." --json
orca orchestration send --to @idle --subject "Anyone free?" --json
orca orchestration send --to @codex --subject "Codex agents only" --json
```

等待期间，CLI 每隔 **15 秒**会向标准错误流 `stderr` 输出一行简短的 JSON 心跳信息。标准输出流 `stdout` 仍用于输出最终的命令结果。

## worker 执行约定

被派发任务的 worker 会收到一段前置说明，告知它应如何与协调者通信：

- **恰好发送一次 `worker_done`**，即使执行失败也必须发送，并携带 `--outcome`。
- 在 `--body` 中提供简短总结：做了什么、发现了什么，以及还有什么尚未完成。
- 同时携带任务 ID 和 Dispatch ID，防止旧的重试执行错误地将其他 Dispatch 标记为完成。
- 如果派发任务时收到的说明要求发送心跳，则在长时间执行任务期间发送 `heartbeat` 消息。
- 遇到会阻塞任务的问题时，使用 `orca orchestration ask` 提问，而不是通过本地 TUI（终端用户界面）提示进行交互。

```bash
orca orchestration ask \
  --to <coordinatorHandle> \
  --question "Should I update the shared component or only this page?" \
  --options "shared,page-only" \
  --timeout-ms 600000 \
  --json
```

指定 `--json` 后，`ask` 会输出单个 JSON 对象，worker 可以将其通过管道传给 `jq -r .answer` 来提取回答。

## 决策关卡

worker 向协调者提问时，使用 `ask`。

如果协调者已经创建了任务 DAG，并希望在某项决策被记录之前阻塞一个任务，则使用显式的决策关卡：

```bash
orca orchestration gate-create \
  --task <taskId> \
  --question "Merge the shared button change into the task branch?" \
  --options '["yes","no"]' \
  --json

orca orchestration gate-resolve --id <gateId> --resolution "yes" --json
```

## 恢复

```bash
orca orchestration dispatch-show --task <taskId> --json
orca orchestration dispatch-show --task <taskId> --preamble --json
orca orchestration task-list --json
orca orchestration task-update --id <taskId> --status blocked --result '{"reason":"waiting on credentials"}' --json
```

只有在你明确打算放弃现有编排状态时，才执行重置：

```bash
orca orchestration reset --tasks --json
orca orchestration reset --messages --json
orca orchestration reset --all --json
```

`reset` 会影响**整个运行时的全局编排状态**。当另一个协调者仍在运行时，不要执行它，除非这正是你希望进行的清理操作。

## 如何选择合适的命令

| 使用场景 | 应使用的命令 |
|---|---|
| 向你正在关注的智能体发送一个轻量提示 | `orca terminal send` |
| 要求 worker 报告 `worker_done`、通过协调者提问，并通过任务 ID 跟踪执行情况 | `orca orchestration worker-start`，或 `dispatch --inject` |
| 需要持久化的 Run 命名空间，以及受监督的多智能体执行流程 | `orca orchestration run-create`＋任务＋worker |

最后一种场景应使用上述 Run 流程，不要使用已经停用的 `orchestration run` 命令。

## 完整指南

命令参数会随着应用更新而变化。安装后，智能体应执行以下命令，获取完整指南：

```bash
orca skills get orchestration --full
```
