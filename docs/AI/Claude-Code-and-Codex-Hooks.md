# Claude Code 与 Codex CLI Hooks

> 本文依据 Claude Code 与 Codex CLI 官方文档整理，最后核对时间：2026-09-02。Hooks 仍在持续演进，使用新事件或字段前，应先检查 `claude --version`、`codex --version`，再核对对应版本的官方文档。

## 1. Hooks 是什么

Hooks 是编码智能体的生命周期自动化机制。当会话、提示词、工具调用、子智能体或结束状态发生特定事件时，客户端会自动运行预先配置的处理器。

一次 Hook 的处理过程可以简化为：

```text
事件触发 -> matcher 筛选 -> 处理器运行 -> 读取退出码或 JSON -> 继续、阻止或补充上下文
```

Hooks 适合处理需要实时执行的工作，例如：

- 执行前拦截危险命令。
- 执行后运行格式化或静态检查。
- 会话开始时注入分支、环境等动态状态。
- 智能体准备结束时检查验证结果和未完成项。
- 记录审计信息或发送通知。

它与其他机制的职责不同：

| 机制 | 主要用途 | 触发方式 |
| --- | --- | --- |
| `CLAUDE.md` / `AGENTS.md` | 长期稳定的项目规范和背景知识 | 会话加载时读取 |
| Skill | 可复用的专项工作流 | 用户或智能体调用 |
| Agent Hook | 智能体生命周期中的检查、拦截和自动化 | 指定事件自动触发 |
| Git Hook | `commit`、`push` 等 Git 生命周期检查 | Git 操作自动触发 |

Agent Hook 与 `.git/hooks/`、`.githooks/` 中的 Git Hook 不是一回事。提交前必须执行的仓库级校验，仍应优先放在 Git `pre-commit` Hook 或 CI 中。

## 2. 能否写成 Claude Code 和 Codex CLI 通用 Hook

可以共享**设计原则和执行脚本**，但不能把所有配置直接写成一份文件。

| 层次 | 能否共享 | 说明 |
| --- | --- | --- |
| 生命周期模型 | 可以 | 两者都采用事件、Matcher、Handler、JSON 输入输出 |
| `command` 脚本 | 通常可以 | 只读取双方共有字段，并返回双方都支持的结果即可 |
| 项目脚本目录 | 可以 | 建议使用中立目录 `.agent-hooks/` |
| 配置文件 | 不可以直接共享 | Claude 使用 `.claude/settings.json`，Codex 使用 `.codex/hooks.json` 或 `config.toml` |
| 事件 | 部分共享 | Claude Code 当前提供的事件更多 |
| Handler 类型 | 部分共享 | 两者都正式支持 `command`、`mcp_tool`，其他类型存在差异 |
| 通知配置 | 不共享 | Claude 有 `Notification` 事件；Codex 的 `notify` 是独立配置 |

推荐结构：

```text
project/
├── .agent-hooks/               # 两个客户端共用的脚本
│   ├── block-dangerous-rm.sh
│   └── verify-delivery.sh
├── .claude/settings.json       # Claude Code 接入配置
└── .codex/hooks.json           # Codex CLI 接入配置
```

## 3. 核心差异

| 对比项 | Claude Code | Codex CLI |
| --- | --- | --- |
| 用户级配置 | `~/.claude/settings.json` | `~/.codex/hooks.json`、`~/.codex/config.toml` |
| 项目级配置 | `.claude/settings.json`、`.claude/settings.local.json` | `.codex/hooks.json`、`.codex/config.toml` |
| 插件配置 | `hooks/hooks.json` | `hooks/hooks.json` |
| 正式支持的 Handler | `command`、`http`、`mcp_tool`、`prompt`、`agent` | `command`、`mcp_tool`；`prompt`、`agent` 目前会被解析但跳过 |
| 事件范围 | 较完整，包含文件、任务、模型切换、通知、MCP 交互等事件 | 当前集中在会话、提示词、工具、压缩、子智能体和结束事件 |
| `/hooks` | 查看已加载 Hook，主要是只读浏览器 | 查看、信任、禁用或重新启用非托管 Hook |
| 项目信任 | 依赖工作区信任和设置来源 | 非托管 Hook 按配置内容哈希审核，修改后需要重新信任 |
| JSON 之外的配置 | 主要使用 settings JSON | 还支持在 `config.toml` 中内联配置 |

不要因为两者都使用 `hooks`、`matcher`、`command` 等字段，就假设全部事件和返回值完全一致。共享脚本应只依赖明确的交集。

## 4. 共同事件

当前两者都支持以下常用事件：

| 事件 | 触发时机 | 常见用途 |
| --- | --- | --- |
| `SessionStart` | 会话开始或恢复 | 注入分支、环境和任务背景 |
| `UserPromptSubmit` | 用户提示词提交后、模型处理前 | 补充上下文、检查输入 |
| `PreToolUse` | 工具执行前 | 拦截危险命令、检查参数 |
| `PermissionRequest` | 工具需要权限确认时 | 返回允许或拒绝决定 |
| `PostToolUse` | 工具执行成功后 | 格式化、检查、记录结果 |
| `PreCompact` | 上下文压缩前 | 保存状态、执行压缩前检查 |
| `PostCompact` | 上下文压缩后 | 恢复或补充必要上下文 |
| `SubagentStart` | 子智能体启动时 | 注入子任务上下文、记录执行 |
| `SubagentStop` | 子智能体准备结束时 | 检查子任务是否真正完成 |
| `Stop` | 主智能体准备结束本轮时 | 检查验证结果和交付说明 |
| `SessionEnd` | 会话结束时 | 清理临时资源、保存日志 |

需要注意：

- `PreToolUse` 发生在工具执行前，适合阻止操作。
- `PostToolUse` 发生在工具产生副作用后，只能反馈问题，无法撤销操作。
- `PermissionRequest` 应返回事件规定的结构化权限决定。
- `Stop`、`SubagentStop` 可以要求智能体继续工作，但脚本必须避免无限循环。
- `SessionEnd` 适合清理和记录，不应承担必须阻塞的门禁。

### 4.1 Claude Code 的扩展事件

Claude Code 当前还提供更多事件，主要包括：

| 分类 | 事件 |
| --- | --- |
| 初始化与指令 | `Setup`、`InstructionsLoaded` |
| 消息与工具 | `UserPromptExpansion`、`MessageDisplay`、`PermissionDenied`、`PostToolUseFailure`、`PostToolBatch` |
| 任务与协作 | `TaskCreated`、`TaskCompleted`、`TeammateIdle`、`StopFailure` |
| 文件与工作区 | `ConfigChange`、`CwdChanged`、`DirectoryAdded`、`FileChanged`、`WorktreeCreate`、`WorktreeRemove` |
| 模型切换 | `PreModelSwitch`、`PostModelSwitch` |
| MCP 与通知 | `Elicitation`、`ElicitationResult`、`Notification` |

这些事件不要直接复制到 Codex 配置中。先确认 Codex 当前版本的事件支持列表。

## 5. 通用输入与输出

### 5.1 Command Hook 输入

`command` Hook 从 stdin 接收 JSON。下面是工具事件中常见的交集字段：

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "git status"
  }
}
```

不同事件会附加不同字段。编写共享脚本时：

1. 使用 `jq` 或语言自带的 JSON 解析器，不要截取字符串解析 JSON。
2. 对可选字段提供默认值，例如 `.tool_input.command // ""`。
3. 使用输入中的 `cwd` 或 Git 仓库根目录，不依赖某个客户端独有的环境变量。
4. MCP 工具通常使用 `mcp__<server>__<tool>` 命名，可通过工具类事件匹配。

Codex 还会提供 `model`、`turn_id` 等扩展字段，但共享脚本不应把它们设为必需字段。

### 5.2 退出码

| 退出码 | 常见含义 |
| --- | --- |
| `0` | Hook 成功；stdout 可按事件要求返回结构化 JSON |
| `2` | 在支持阻塞的事件中阻止当前动作，原因写入 stderr |
| 其他 | 通常视为 Hook 执行错误，不一定阻止原动作 |

超时和普通失败通常不等于拒绝，不能把“脚本崩溃”设计成安全门禁。

### 5.3 共同使用的结构化结果

`PreToolUse` 拒绝工具执行：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "检测到危险命令"
  }
}
```

`Stop` 或 `SubagentStop` 要求智能体继续：

```json
{
  "decision": "block",
  "reason": "测试尚未运行，请完成验证后再结束"
}
```

不同事件的上下文注入和权限决定结构并不完全相同，应按各自官方 Schema 编写。stdout 只输出一个有效 JSON 对象，普通日志写入 stderr。

## 6. 编写可共享脚本

### 6.1 执行前拦截递归删除

创建 `.agent-hooks/block-dangerous-rm.sh`：

```bash
#!/bin/bash
set -eu

input=$(cat)
command=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

if printf '%s\n' "$command" \
  | grep -Eq '(^|[;&|[:space:]])rm[[:space:]]+[^;&|]*(-[^[:space:]]*r|--recursive)([[:space:]]|$)'; then
  echo "已阻止递归删除，请确认范围后由用户显式执行。" >&2
  exit 2
fi

exit 0
```

添加执行权限：

```bash
chmod +x .agent-hooks/block-dangerous-rm.sh
```

这个正则示例只提供一层辅助保护，不能完整解析所有 Shell 语法，也不能替代客户端权限控制、操作系统权限、Git 和备份。

### 6.2 结束前检查交付说明

创建 `.agent-hooks/verify-delivery.sh`：

```bash
#!/bin/bash
set -eu

input=$(cat)
stop_hook_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
message=$(printf '%s' "$input" | jq -r '.last_assistant_message // ""')

# 已经由 Stop Hook 要求继续过一次时放行，避免无限循环。
if [ "$stop_hook_active" = "true" ]; then
  exit 0
fi

if printf '%s\n' "$message" \
  | grep -Eqi '测试|验证|构建|未验证|无法验证|test|lint|typecheck|build'; then
  exit 0
fi

jq -nc '{
  decision: "block",
  reason: "结束前请说明测试、lint、构建或其他验证结果；无法验证时请明确原因。"
}'
```

添加执行权限：

```bash
chmod +x .agent-hooks/verify-delivery.sh
```

这个脚本只检查最终说明中是否出现验证信息，不会证明测试真的执行过。严格门禁应直接运行具体测试，或交给 Git Hook 和 CI。

## 7. 分别接入两个客户端

### 7.1 Claude Code 配置

在项目的 `.claude/settings.json` 中配置：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -lc 'root=$(git rev-parse --show-toplevel 2>/dev/null || pwd); exec \"$root/.agent-hooks/block-dangerous-rm.sh\"'",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -lc 'root=$(git rev-parse --show-toplevel 2>/dev/null || pwd); exec \"$root/.agent-hooks/verify-delivery.sh\"'",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Claude Code 还支持 `if` 条件，可以使用权限规则语法进一步筛选工具参数。为了让示例容易移植到 Codex，这里把具体判断放进共享脚本。

### 7.2 Codex CLI 配置

在项目的 `.codex/hooks.json` 中配置：

```json
{
  "description": "项目共享安全与交付检查",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -lc 'root=$(git rev-parse --show-toplevel 2>/dev/null || pwd); exec \"$root/.agent-hooks/block-dangerous-rm.sh\"'",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -lc 'root=$(git rev-parse --show-toplevel 2>/dev/null || pwd); exec \"$root/.agent-hooks/verify-delivery.sh\"'",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Codex 会合并用户、项目和插件中的匹配 Hook。非托管 Hook 首次加载或配置内容变化后，需要在 `/hooks` 中检查并信任。

Codex 工具匹配还需要注意：

- Shell 与统一命令执行工具会规范为 `Bash`。
- `apply_patch` 的规范名称是 `apply_patch`，同时兼容 `Edit`、`Write` 别名。
- MCP 工具使用 `mcp__server__tool` 形式。
- 部分托管工具或专用工具可能不会触发 Hook，因此 Hook 不是完整的安全边界。

Codex 也支持在 `.codex/config.toml` 中内联 Hook。项目已经使用 `hooks.json` 时，不必再维护一份等价 TOML，避免重复执行。

## 8. 客户端专属能力

### 8.1 Claude Code

Claude Code 还可以按场景使用以下 Handler：

| 类型 | 用途 |
| --- | --- |
| `http` | 将事件 JSON 发送到审批或审计服务 |
| `prompt` | 使用模型进行一次结构化语义判断 |
| `agent` | 启动可读取和搜索代码的子智能体进行复杂检查 |

例如，只有 Claude Code 可以把 `Stop` 配置为 `prompt` Handler，让模型判断任务是否完整。此类检查会增加延迟和用量，不应复制到 Codex；Codex 当前会解析但跳过 `prompt`、`agent` Handler。

Claude Code 还有 `Notification` 生命周期事件，可通过 `osascript` 等命令发送桌面通知。相关事件、Matcher 和通知类型应以 Claude Code 文档为准。

### 8.2 Codex CLI

Codex 的项目 Hook 具有显式信任流程：

1. Codex 根据 Hook 配置内容计算哈希。
2. 用户在 `/hooks` 中检查并信任非托管 Hook。
3. 配置变化后哈希变化，需要重新审核。
4. 非托管 Hook 可以在 `/hooks` 中禁用或重新启用，托管 Hook 不能由普通用户关闭。

Codex Handler 还支持 `additionalContextLimit`、`async`、`commandWindows` 等字段。异步 Hook 不能阻止、批准或改写当前操作，不适合作为关键门禁。

Codex 的 `notify` 是 `config.toml` 中独立的外部通知命令，不是 Claude Code `Notification` 事件的同名实现。不要把两者写成一份共享 Hook 配置。

## 9. 调试与验证

### 9.1 查看已加载 Hook

在对应客户端会话中输入：

```text
/hooks
```

- Claude Code：查看事件、Matcher、处理器和配置来源；修改配置仍需编辑文件。
- Codex CLI：查看配置来源，并完成信任、禁用或重新启用操作。

Claude Code 可以开启 Hook 调试日志：

```bash
claude --debug hooks
claude --debug hooks --debug-file ./claude-hooks-debug.log
```

Codex 当前的 Hooks 功能已经稳定启用，可检查状态：

```bash
codex features list
```

### 9.2 手工测试共享脚本

测试危险命令拦截：

```bash
printf '%s\n' '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf ./build"}}' \
  | .agent-hooks/block-dangerous-rm.sh
```

预期退出码为 `2`，并在 stderr 中显示阻止原因。允许的命令应返回 `0`。

测试结束前验收：

```bash
printf '%s\n' '{"hook_event_name":"Stop","stop_hook_active":false,"last_assistant_message":"修改已经完成。"}' \
  | .agent-hooks/verify-delivery.sh
```

预期 stdout 返回 `decision: block` 的 JSON。之后再分别在非重要项目中触发真实事件，确认客户端行为。

### 9.3 常见问题

| 现象 | 常见原因 | 处理方式 |
| --- | --- | --- |
| Hook 不触发 | 事件、Matcher、版本或信任状态不匹配 | 使用 `/hooks` 检查来源和状态 |
| JSON 解析失败 | stdout 混入日志或返回结构错误 | stdout 只输出一个 JSON；日志写 stderr |
| 找不到脚本 | 相对路径以会话 `cwd` 解析 | 先用 `git rev-parse --show-toplevel` 获取仓库根目录 |
| 脚本失败但操作继续 | 返回普通错误码或事件不支持阻塞 | 使用事件规定的结构化决定或 `exit 2` |
| Hook 超时但操作继续 | 超时通常按非阻塞错误处理 | 缩短检查并设置合理 `timeout` |
| Hook 重复执行 | 多个配置来源同时匹配 | 用 `/hooks` 检查来源，脚本保持幂等 |
| Stop Hook 循环 | 每次结束都返回阻塞 | 检查 `stop_hook_active`，只反馈可完成的问题 |
| Claude 配置复制到 Codex 后无效 | 使用了 Codex 不支持的事件或 Handler | 按交集拆分共享脚本和专属配置 |

## 10. 安全与维护原则

1. `command` Hook 以当前用户权限执行，启用第三方 Hook 前必须审查源码。
2. 不在配置、脚本或日志中硬编码 Token、密码、私钥和 Cookie。
3. 对工具输入、路径和命令进行校验，Shell 变量使用双引号。
4. 项目应提交 Hook 脚本，并注明 `jq`、Node.js 或格式化工具等依赖。
5. 多个匹配 Hook 可能并行执行，脚本应幂等，不依赖固定顺序。
6. 不把超时、异常或异步执行当成拒绝结果。
7. Agent Hook 不能替代操作系统权限、客户端沙箱、Git Hook、代码评审和 CI。
8. 不受信任的仓库可能携带恶意 Hook；加载项目前先检查 `.claude/`、`.codex/` 和脚本目录。
9. 事件、字段和 Handler 支持范围可能随版本变化，升级后应重新验证关键门禁。

## 11. 参考资料

- [Claude Code 官方文档：Hooks reference](https://code.claude.com/docs/en/hooks)
- [Claude Code 官方文档：Automate workflows with hooks](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code 官方文档：Settings](https://code.claude.com/docs/en/settings)
- [Codex 官方文档：Hooks](https://learn.chatgpt.com/docs/hooks)
- [Codex 官方文档：Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [MCP](MCP.md)
