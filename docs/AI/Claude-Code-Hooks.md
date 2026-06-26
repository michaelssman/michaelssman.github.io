# Claude Code Hooks 完整指南

> 最后更新：2026-06-25

## 一、什么是 Hooks

Hooks（钩子）是 Claude Code 中的**事件驱动脚本/程序**，在 Claude 执行生命周期的特定节点自动运行。与 `CLAUDE.md` 中的提示词不同，hooks 是**确定性的强制执行机制**——它们通过退出码强制执行规则（退出码 2 可以完全阻止操作），而 AI 无法绕过。

**核心原则：Prompts 提供建议，Hooks 提供保证。**

---

## 二、Hook 事件类型（26+ 种）

事件按生命周期分类：

### 2.1 会话生命周期

| 事件 | 触发时机 | Matcher 过滤依据 |
|------|---------|-----------------|
| `SessionStart` | 会话开始或恢复时 | 启动方式: `startup`, `resume`, `clear`, `compact` |
| `Setup` | `--init-only`, `--init -p`, `--maintenance -p` | CLI flag: `init`, `maintenance` |
| `SessionEnd` | 会话终止时 | 结束原因 |

### 2.2 用户交互

| 事件 | 触发时机 | Matcher 过滤依据 |
|------|---------|-----------------|
| `UserPromptSubmit` | 用户提交提示词后，Claude 处理前 | 不支持 matcher（始终触发） |
| `UserPromptExpansion` | 用户输入命令被扩展为提示词时 | 命令名称 |
| `MessageDisplay` | 助手消息文本即将显示时 | 不支持 matcher |

### 2.3 工具执行

| 事件 | 触发时机 | Matcher 过滤依据 |
|------|---------|-----------------|
| `PreToolUse` | 工具调用执行**前** | 工具名称（如 `Bash`, `Edit\|Write`, `mcp__.*`） |
| `PermissionRequest` | 权限对话框出现时 | 工具名称 |
| `PermissionDenied` | 自动模式拒绝工具调用时 | 工具名称 |
| `PostToolUse` | 工具调用**成功后** | 工具名称 |
| `PostToolUseFailure` | 工具调用**失败后** | 工具名称 |
| `PostToolBatch` | 并行工具调用批次全部完成后 | 不支持 matcher |

### 2.4 AI 生命周期

| 事件 | 触发时机 |
|------|---------|
| `Stop` | Claude 完成回复时 |
| `StopFailure` | 回合因 API 错误结束时 |

### 2.5 子代理

| 事件 | 触发时机 |
|------|---------|
| `SubagentStart` | 子代理生成时 |
| `SubagentStop` | 子代理完成时 |

### 2.6 任务系统

| 事件 | 触发时机 |
|------|---------|
| `TaskCreated` | 通过 TaskCreate 创建任务时 |
| `TaskCompleted` | 任务标记为完成时 |

### 2.7 协作

| 事件 | 触发时机 |
|------|---------|
| `TeammateIdle` | 代理团队成员即将进入空闲状态时 |

### 2.8 配置与工作区

| 事件 | 触发时机 |
|------|---------|
| `InstructionsLoaded` | CLAUDE.md 或 `.claude/rules/*.md` 加载时 |
| `ConfigChange` | 会话中配置文件变更时 |
| `CwdChanged` | 工作目录变更时 |
| `FileChanged` | 监听的文件在磁盘上变更时 |

### 2.9 工作树

| 事件 | 触发时机 |
|------|---------|
| `WorktreeCreate` | 创建 worktree 时 |
| `WorktreeRemove` | 移除 worktree 时 |

### 2.10 上下文管理

| 事件 | 触发时机 |
|------|---------|
| `PreCompact` | 上下文压缩前 |
| `PostCompact` | 上下文压缩完成后 |

### 2.11 MCP 交互

| 事件 | 触发时机 |
|------|---------|
| `Elicitation` | MCP 服务器请求用户输入时 |
| `ElicitationResult` | 用户响应 MCP 请求时 |

### 2.12 通知

| 事件 | 触发时机 |
|------|---------|
| `Notification` | Claude Code 发送通知时 |

---

## 三、Hook 类型（5 种）

| 类型 | 描述 | 适用场景 |
|------|------|---------|
| `command` | 运行 shell 命令；通过 stdin 接收 JSON，通过退出码和 stdout 通信 | 本地脚本、格式化、安全检查 |
| `http` | 将 JSON 作为 HTTP POST 发送到远端；从响应体获取结果 | 远程服务调用、企业审批 |
| `mcp_tool` | 调用已连接的 MCP 服务器上的工具 | MCP 生态集成 |
| `prompt` | 发送提示词给 Claude 模型进行单轮是/否评估 | AI 辅助决策 |
| `agent` | 生成可调用工具（Read, Grep, Glob）的子代理来验证条件（实验性） | 复杂的代码审查逻辑 |

---

## 四、配置位置（5 级层次结构）

| 位置 | 范围 | 可共享 | 文件路径 |
|------|------|--------|---------|
| 全局用户设置 | 所有项目 | 否 | `~/.claude/settings.json` |
| 项目设置 | 单个项目 | 是 | `.claude/settings.json` |
| 项目本地设置 | 单个项目 | 否（gitignored） | `.claude/settings.local.json` |
| 托管策略设置 | 组织范围 | 是（管理员控制） | N/A（企业功能） |
| 插件 hooks | 启用插件时 | 是（已打包） | 插件 `hooks/hooks.json` |

**优先级（从低到高）**：全局 -> 项目 -> 本地 -> 托管策略

---

## 五、配置 Schema

### 5.1 基本结构

```json
{
  "hooks": {
    "<事件名称>": [
      {
        "matcher": "匹配模式",
        "hooks": [
          {
            "type": "command|http|mcp_tool|prompt|agent",
            // ... 类型特定字段
          }
        ]
      }
    ]
  }
}
```

### 5.2 通用字段（所有 hook 类型）

| 字段 | 必须 | 描述 |
|------|------|------|
| `type` | **是** | `command`, `http`, `mcp_tool`, `prompt`, `agent` |
| `if` | 否 | 权限规则语法过滤，如 `Bash(git *)`, `Edit(*.ts)`。仅在工具事件上评估 |
| `timeout` | 否 | 取消前的秒数。默认: command/http/mcp_tool 600秒; prompt 30秒; agent 60秒 |
| `statusMessage` | 否 | hook 运行时自定义的 spinner 消息 |
| `once` | 否 | 如果为 `true`，每个会话只运行一次然后被移除（仅用于 skill frontmatter） |

### 5.3 Command Hook 字段

| 字段 | 必须 | 描述 |
|------|------|------|
| `command` | **是** | 要执行的 shell 命令。Shell 形式（无 `args`）通过 `sh -c` 执行 |
| `args` | 否 | 参数列表。存在时采用 exec 形式，不涉及 shell |
| `async` | 否 | 如果为 `true`，在后台运行而不阻塞 |
| `asyncRewake` | 否 | 如果为 `true`，后台运行并在退出码为 2 时唤醒 Claude |
| `shell` | 否 | `bash`（默认）或 `powershell` |

```json
{
  "type": "command",
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/my-check.sh",
  "timeout": 30,
  "statusMessage": "正在检查安全性..."
}
```

### 5.4 HTTP Hook 字段

| 字段 | 必须 | 描述 |
|------|------|------|
| `url` | **是** | 发送 POST 请求的 URL |
| `headers` | 否 | 键值对。值支持 `$VAR_NAME` / `${VAR_NAME}` 插值 |
| `allowedEnvVars` | 否 | 可以插值到 header 值中的环境变量名列表 |

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "timeout": 30,
  "headers": { "Authorization": "Bearer $MY_TOKEN" },
  "allowedEnvVars": ["MY_TOKEN"]
}
```

**注意**：HTTP hooks 需在 settings 中配置 `allowedHttpHookUrls` 白名单才能使用。

### 5.5 MCP Tool Hook 字段

| 字段 | 必须 | 描述 |
|------|------|------|
| `server` | **是** | 已配置的 MCP 服务器名称 |
| `tool` | **是** | 要在该服务器上调用的工具名称 |
| `input` | 否 | 传递给工具的参数。支持 `${path}` 替换 |

### 5.6 Prompt & Agent Hook 字段

| 字段 | 必须 | 描述 |
|------|------|------|
| `prompt` | **是** | 提示词文本。使用 `$ARGUMENTS` 作为 hook 输入 JSON 的占位符 |
| `model` | 否 | 使用的模型。默认为快速模型 |

```json
{
  "type": "prompt",
  "prompt": "检查以下代码是否安全：$ARGUMENTS。如果安全回复 OK，否则回复 BLOCK。",
  "timeout": 30
}
```

---

## 六、Matcher 匹配模式

| Matcher 值 | 行为 | 示例 |
|-----------|------|------|
| `*`, `""`, 或省略 | 匹配所有事件 | 每次触发都执行 |
| 仅字母、数字、`_`、`\|` | 精确字符串或 `\|` 分隔的列表 | `Bash` 只匹配 Bash；`Edit\|Write` 匹配两者 |
| 包含其他字符 | JavaScript 正则表达式 | `^Notebook`, `mcp__memory__.*` |

**MCP 工具命名规则**：`mcp__<服务器名>__<工具名>`，例如 `mcp__memory__create_entities`。

---

## 七、退出码行为

这是 hooks 强制执行的核心机制：

| 退出码 | 含义 | 说明 |
|--------|------|------|
| **0** | 成功 | stdout 解析为 JSON 输出字段，继续执行 |
| **2** | 阻塞错误 | stderr 反馈给 Claude 作为错误消息，**阻止操作** |
| **其他**（1, 3-255） | 非阻塞错误 | 继续执行，stderr 显示为通知 |

### 可以被退出码 2 阻塞的事件

`PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `ConfigChange`, `PostToolBatch`, `PreCompact`, `Elicitation`, `ElicitationResult`, `WorktreeCreate`（任何非零退出码）, `PostToolUse`, `PostToolUseFailure`

### 忽略退出码 2 的事件

`StopFailure`, `PermissionDenied`, `Notification`, `SubagentStart`, `SessionStart`, `Setup`, `SessionEnd`, `CwdChanged`, `FileChanged`, `PostCompact`, `WorktreeRemove`, `InstructionsLoaded`, `MessageDisplay`

---

## 八、stdout JSON 输出字段

退出码为 0 时，hook 可以通过 stdout 输出 JSON 来控制行为：

| 字段 | 描述 |
|------|------|
| `continue` | 如果为 `false`，Claude 完全停止处理 |
| `stopReason` | 当 `continue` 为 `false` 时显示给用户的消息 |
| `suppressOutput` | 如果为 `true`，从记录中隐藏 hook 的 stdout |
| `systemMessage` | 显示给用户的警告消息 |
| `terminalSequence` | 要发出的终端转义序列 |
| `hookSpecificOutput` | 包含 `hookEventName` + 事件特定字段的嵌套对象 |
| `decision` | 顶层字段，带 `reason` 的 `block` 决策 |

**注意**：输出字符串上限 10,000 个字符，超出部分会被保存到文件。

### 常用输出示例

```json
// 阻塞操作
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "检测到危险命令，已被 hook 阻止"
  }
}

// 注入附加上下文（SessionStart）
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "当前分支: feat/auth-refactor\n未提交文件: src/auth.ts",
    "sessionTitle": "auth-refactor"
  }
}
```

---

## 九、stdin JSON 输入

Hook 通过 stdin 接收 JSON，包含当前事件的上下文信息。

### 所有事件共享的基础字段

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "effort": { "level": "medium" },
  "hook_event_name": "PreToolUse",
  "agent_id": "subagent-uuid",
  "agent_type": "Explore"
}
```

### 工具事件额外字段

```json
{
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "old_string": "...",
    "new_string": "..."
  }
}
```

---

## 十、环境变量

### 内置变量

| 变量 | 描述 |
|------|------|
| `$CLAUDE_PROJECT_DIR` | 项目根目录 |
| `$CLAUDE_PLUGIN_ROOT` | 插件的安装目录 |
| `$CLAUDE_PLUGIN_DATA` | 插件的持久化数据目录 |
| `$CLAUDE_ENV_FILE` | 持久化环境变量的文件（在 SessionStart, Setup, CwdChanged, FileChanged 中可用） |
| `$CLAUDE_TOOL_INPUT_FILE_PATH` | 在 PostToolUse 中，Claude 刚写入/编辑的文件路径 |

### 自定义环境变量

在 settings 顶层设置全局 `env`，对所有 hooks 及其子进程可用：

```json
{
  "env": {
    "MY_TOKEN": "secret-value",
    "NODE_ENV": "development"
  }
}
```

---

## 十一、Shell 形式 vs Exec 形式

| 形式 | 配置方式 | 特点 |
|------|---------|------|
| **Shell** | 无 `args`，整个 `command` 传给 `sh -c` | 支持管道、`&&`、重定向、变量展开 |
| **Exec** | 有 `args`，`command` 是可执行文件 | 不涉及 shell，更安全，参数逐字传递 |

```json
// Shell 形式
{
  "type": "command",
  "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\""
}

// Exec 形式
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

---

## 十二、条件过滤 `if` 语法

`if` 字段用于在工具事件中基于工具输入进行条件匹配。

| 模式 | 命令 | 匹配？ | 原因 |
|------|------|--------|------|
| `Bash(git *)` | `FOO=bar git push` | 是 | 前置环境变量赋值被剥离 |
| `Bash(git *)` | `npm test && git push` | 是 | 子命令被检查 |
| `Bash(rm *)` | `echo $(rm -rf /)` | 是 | `$()` 内的内容被检查 |
| `Bash(rm *)` | `echo $(date)` | 否 | 没有匹配的子命令 |
| `Bash(git push *)` | `echo $(date)` | 是 | 多 token 模式也在 `$()`/反引号上运行 |

---

## 十三、实用示例

### 示例 1：阻止危险的 rm 命令

**settings.json：**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "if": "Bash(rm *)",
          "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
          "statusMessage": "检查命令安全性..."
        }]
      }
    ]
  }
}
```

**`.claude/hooks/block-rm.sh`：**

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+/'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "危险命令已阻止: rm -rf /"
    }
  }'
  exit 0
fi
exit 0
```

### 示例 2：PostToolUse 自动格式化代码

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\"",
          "timeout": 30,
          "statusMessage": "正在格式化代码..."
        }]
      }
    ]
  }
}
```

### 示例 3：SessionStart 注入项目上下文

**settings.json：**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{
          "type": "command",
          "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/session-start.sh"
        }]
      }
    ]
  }
}
```

**`.claude/hooks/session-start.sh`：**

```bash
#!/bin/bash
BRANCH=$(git branch --show-current 2>/dev/null || echo "N/A")
CHANGES=$(git status --short 2>/dev/null | wc -l | tr -d ' ')

jq -n --arg branch "$BRANCH" --arg changes "$CHANGES" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("当前 Git 分支: \($branch)\n未提交文件数: \($changes)"),
    sessionTitle: $branch
  }
}'
```

### 示例 4：桌面通知

**macOS：**

```json
{
  "hooks": {
    "Notification": [{
      "hooks": [{
        "type": "command",
        "command": "osascript -e 'display notification \"Claude Code 需要你的关注\" with title \"Claude Code\"'"
      }]
    }]
  }
}
```

**Linux：**

```json
{
  "hooks": {
    "Notification": [{
      "hooks": [{
        "type": "command",
        "command": "notify-send 'Claude Code' '等待你的输入'"
      }]
    }]
  }
}
```

### 示例 5：Stop 事件自动 LGTM 检查（Homebrew 实际案例）

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./bin/brew lgtm",
            "timeout": 360
          }
        ]
      }
    ]
  }
}
```

### 示例 6：UserPromptSubmit 内容审查

**settings.json：**

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-prompt.sh"
      }]
    }]
  }
}
```

**`.claude/hooks/check-prompt.sh`：**

```bash
#!/bin/bash
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt')

# 阻止包含特定关键词的提示词
if echo "$PROMPT" | grep -qi "password\|secret\|token"; then
  echo '{"continue": false, "stopReason": "提示词包含敏感关键词，已被阻止"}'
  exit 0
fi
exit 0
```

---

## 十四、调试 Hooks

### 调试命令

```bash
# 启动时开启 hooks 调试日志
claude --debug hooks

# 将调试日志写入文件
claude --debug hooks --debug-file ./debug.log
```

### 在会话中查看 hooks

在 Claude Code 会话中输入 `/hooks`，会打开一个只读浏览器，显示所有已配置的 hooks 及其来源标签：

- `User` - 用户级全局设置
- `Project` - 项目级设置
- `Local` - 项目本地设置
- `Plugin` - 插件 hooks
- `Session` - 会话级临时 hooks
- `Built-in` - 内置 hooks

### 临时禁用 hooks

在 settings 中添加：

```json
{
  "disableAllHooks": true
}
```

### 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Hook 不触发 | 事件名、matcher 或 `if` 条件不匹配 | 检查配置拼写和匹配规则 |
| JSON 解析失败 | stdout 包含非 JSON 内容（如 shell profile 输出） | 确保脚本只输出 JSON |
| Hook 超时 | 脚本执行时间超过 `timeout` 限制 | 增加 `timeout` 或使用 `async: true` |
| 权限被拒 | HTTP hook URL 不在白名单中 | 在 settings 中添加 `allowedHttpHookUrls` |
| stderr 显示为通知 | 不带 `--debug` 时，stderr 输出显示为 hook 错误通知 | 使用 `--debug hooks` 查看完整 stderr |

---

## 十五、Hook 安全管理

### 重要提醒

1. **Hooks 以用户权限运行**：恶意仓库中的 `.claude/settings.json` 可能被用来进行初始访问或持久化攻击
2. **审计不受信任的仓库**：始终在使用前检查不受信任仓库中的 `.claude/` 目录
3. **环境变量安全**：不要在 settings.json 中硬编码密钥，使用环境变量或密钥管理工具
4. **脚本权限**：确保 hook 脚本有正确的执行权限（`chmod +x`）

### 推荐做法

```bash
# 设置脚本权限
chmod +x .claude/hooks/*.sh

# 添加 .claude/settings.local.json 到 .gitignore
echo ".claude/settings.local.json" >> .gitignore
```

---

## 十六、快速参考卡片

```
┌──────────────────────────────────────────────────────────┐
│  Hook 生命周期速查                                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  SessionStart ──→ UserPromptSubmit ──→ PreToolUse        │
│       │                                    │              │
│       │                              ┌─────┴──────┐      │
│       │                              │  工具执行   │      │
│       │                              └─────┬──────┘      │
│       │                         ┌──────────┴─────────┐   │
│       │                         │ PostToolUse/        │   │
│       │                         │ PostToolUseFailure  │   │
│       │                         └──────────┬─────────┘   │
│       │                                    │              │
│       └────────────────────────────────────┘              │
│                       ↓                                   │
│                    Stop ──→ SessionEnd                    │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  退出码：0=成功  2=阻塞  其他=非阻塞警告                    │
│  配置：~/.claude/settings.json                           │
│        .claude/settings.json                             │
│        .claude/settings.local.json                       │
├──────────────────────────────────────────────────────────┤
│  调试：claude --debug hooks                              │
│  查看：/hooks（在会话中）                                  │
│  禁用：disableAllHooks: true                             │
└──────────────────────────────────────────────────────────┘
```

---

## 参考来源

- [Claude Code 官方文档 - Settings](https://code.claude.com/docs/en/settings)
- [Claude Code 官方文档 - Hooks](https://code.claude.com/docs/en/hooks)
- [claude-awesome-stack - Hook 精选示例](https://github.com/giacomogaglione/claude-awesome-stack)
- [GUVI - Claude Code Hooks 配置指南](https://www.guvi.in/blog/claude-code-hooks-how-to-configure-them/)
- [Skywork - Claude CLI Hooks 终极指南](https://skywork.ai/blog/slide-template/the-ultimate-guide-to-claude-cli-hooks-in-2026/)



> 请帮我创建一个 Claude Code Stop hook。
>
> 作用：Claude 准备结束前做交付验收。
>
> 规则：如果本轮改了代码、配置或文档，但没有说明测试、lint、typecheck、功能验证或TODO检查结果，就不允许结束，继续工作，并让 Claude 继续完成验证。
>
> 如果已经验证，允许结束。
>
> 创建完成后，告诉我怎么用/hooks 检查
