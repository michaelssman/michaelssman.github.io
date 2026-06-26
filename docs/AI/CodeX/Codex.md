# Codex

官方入口：[Codex docs](https://developers.openai.com/codex/)

---

## 目录

1. [Codex 是什么](#1-codex-是什么)
2. [模型选择](#2-模型选择)
3. [CLI 常用工作流](#3-cli-常用工作流)
4. [斜杠命令速查](#4-斜杠命令速查)
5. [权限、沙箱与安全边界](#5-权限沙箱与安全边界)
6. [AGENTS.md 项目指令](#6-agentsmd-项目指令)
7. [Skills、MCP、Plugins、Subagents](#7-skillsmcppluginssubagents)
8. [Codex App 重点能力](#8-codex-app-重点能力)
9. [实践建议与避坑](#9-实践建议与避坑)
10. [官方资料索引](#10-官方资料索引)

---

## 1. Codex 是什么

- **它可以被定制**：通过 `AGENTS.md`、`config.toml`、Skills、MCP、插件、子智能体和自动化任务，让 Codex 更贴近个人或团队工作流。

---

## 2. 模型选择

### CLI

### 模型选择

临时指定模型：

```bash
codex -m gpt-5.5
codex --model gpt-5.5
```

配置默认模型可写入 `~/.codex/config.toml`：

```toml
model = "gpt-5.5"
```

---

## 3. CLI 常用工作流

### 3.1 交互模式

在项目目录启动：

```bash
cd /path/to/project
codex
```

也可以直接带初始提示：

```bash
codex "Explain this codebase to me"
```

常见能力：

- 粘贴截图或通过 `--image` 附加图片。

### 3.2 恢复会话

Codex 会在本地保存 transcript，可用 `resume` 恢复：

```bash
codex resume
codex resume --all
codex resume --last
codex resume <SESSION_ID>
```

非交互模式也可以恢复：

```bash
codex exec resume --last "继续修复刚才发现的问题"
codex exec resume <SESSION_ID> "实现刚才的计划"
```

### 3.3 非交互模式

适合脚本、CI、流水线、定时任务：

```bash
codex exec "summarize the repository structure and list the top 5 risky areas"
```

管道输出：

```bash
codex exec "generate release notes for the last 10 commits" | tee release-notes.md
```

JSONL 输出：

```bash
codex exec --json "summarize the repo structure" | jq
```

权限示例：

```bash
codex exec --sandbox workspace-write "update docs and run tests"
codex exec --sandbox danger-full-access "run this in an isolated CI runner"
```

**注意**：官方说明 `codex exec` 默认运行在 read-only sandbox 中。

### 3.4 远程 TUI / App Server

Codex CLI 支持连接远程 app server：

```bash
codex app-server --listen ws://127.0.0.1:4500
codex --remote ws://127.0.0.1:4500
```

如果要从另一台机器访问，需要配置 WebSocket 鉴权，并优先放在 TLS 后面。不要把未鉴权的远程端点暴露到公网。

### 3.5 Web Search

Codex CLI 官方内置 first-party web search。默认本地任务使用 OpenAI 维护的搜索缓存，而不是每次实时抓取网页。这样可以降低任意网页内容带来的 prompt injection 风险，但搜索结果仍应视为不可信外部输入。

需要最新结果时：

```bash
codex --search "查找某个库的最新官方迁移说明"
```

或在配置里设置：

```toml
web_search = "live"
```

也可以关闭：

```toml
web_search = "disabled"
```

如果要限制搜索工具范围，可使用 `tools.web_search` 配置允许域名、上下文大小和近似位置。

---

## 4. 斜杠命令速查

### 4.1 CLI 常用斜杠命令

| 命令 | 用途 |
| --- | --- |
| `/permissions` | 调整 Codex 无需询问即可执行的权限范围 |
| `/model` | 选择活动模型和可用 reasoning effort |
| `/fast` | 在支持的模型上切换 Fast service tier |
| `/plan` | 切换到计划模式，让 Codex 先做方案设计 |
| `/goal` | 设置、查看、暂停、恢复或清除持续目标 |
| `/review` | 审查当前工作树、未提交改动、commit 或分支 diff |
| `/status` | 查看线程配置、模型、审批策略、可写目录和 token 使用 |
| `/statusline` | 配置 TUI 底部状态栏字段 |
| `/title` | 配置终端窗口或 tab 标题字段 |
| `/raw` | 查看最近一次 assistant 消息的原始 markdown |
| `/compact` | 压缩/总结长对话，释放上下文 |
| `/copy` | 复制最近一次完成的 Codex 输出，快捷键 `Ctrl+O` |
| `/diff` | 查看 Git diff，包括未跟踪文件 |
| `/approve` | 对最近一次 auto review 拒绝的动作允许重试一次 |
| `/init` | 为当前目录生成 `AGENTS.md` scaffold |
| `/mcp` | 查看 MCP 工具和服务器状态 |
| `/skills` | 浏览和使用本地 Skills |
| `/plugins` | 浏览、安装、启用或管理插件 |
| `/apps` | 浏览 app/connectors，并把 `$app-slug` 插入提示 |
| `/hooks` | 查看和管理 lifecycle hooks |
| `/agent` | 切换/查看子智能体线程 |
| `/side` 或 `/btw` | 开启临时侧边对话，不打断主线 |
| `/fork` | 从当前会话派生新线程 |
| `/new` | 在同一 CLI 会话里开启新对话 |
| `/resume` | 从会话列表恢复历史对话 |
| `/clear` | 清屏并开启新的对话；不同于 `Ctrl+L` 只清屏 |
| `/ide` | 拉取 IDE 打开的文件、选择区等上下文 |
| `/keymap` | 查看和保存 TUI 快捷键映射 |
| `/sandbox-add-read-dir` | Windows 上给 sandbox 额外增加只读目录 |
| `/debug-config` | 调试配置层级和生效策略 |
| `/theme` | 选择并保存终端语法高亮主题 |
| `/vim` | 切换 composer 的 Vim 模式 |
| `/memories` | 配置 memory 注入或生成 |
| `/experimental` | 切换实验功能，必要时重启 Codex |
| `/feedback` | 向 Codex 维护者发送反馈和日志 |
| `/exit` 或 `/quit` | 退出 CLI |

### 4.2 App 斜杠命令

Codex App 也支持在 composer 中输入 `/` 使用命令。官方列出的常见命令包括：

| 命令 | 用途 |
| --- | --- |
| `/feedback` | 打开反馈对话框 |
| `/goal` | 设置持续目标 |
| `/init` | 为当前项目生成 `AGENTS.md` |
| `/mcp` | 查看 MCP 连接状态 |
| `/plan` | 切换计划模式 |
| `/review` | 审查未提交改动或对比 base branch |
| `/status` | 查看 thread ID、上下文使用量和 rate limits |

---

## 5. 权限、沙箱与安全边界

Codex 的安全模型由两层共同组成：

- **Sandbox**：技术边界，决定 Codex 运行命令时能读写哪些文件、是否能联网、是否能越过工作区。
- **Approval policy**：审批策略，决定 Codex 何时必须停下来询问用户或自动审查者。

### 5.1 常见 sandbox mode

| 模式 | 含义 |
| --- | --- |
| `read-only` | Codex 可以查看文件，但不能不经审批编辑文件或运行命令 |
| `workspace-write` | Codex 可以读取文件、在 workspace 内编辑，并在边界内运行常规本地命令 |
| `danger-full-access` | 取消沙箱限制，拥有更广泛的文件系统和网络访问能力，只应在隔离环境中使用 |

### 5.2 常见 approval policy

| 策略 | 含义 |
| --- | --- |
| `untrusted` | 不在 trusted set 中的命令需要询问 |
| `on-request` | 在沙箱内自动运行，越界时请求审批 |
| `never` | 不弹出审批请求 |

默认本地工作通常是 `workspace-write` + `on-request`。官方称 Full access 对应 `sandbox_mode = "danger-full-access"` 和 `approval_policy = "never"`，不要在真实项目里随手开启。

### 5.3 平台差异

- macOS 使用系统内置 Seatbelt 沙箱，通常开箱即用。
- Windows 原生 PowerShell 使用 Windows sandbox；WSL2 使用 Linux 沙箱实现。
- Linux / WSL2 建议安装 `bubblewrap`，如 Ubuntu/Debian 使用 `sudo apt install bubblewrap`。

---

## 6. AGENTS.md 项目指令

`AGENTS.md` 是 Codex 的持久项目指导文件。它适合放“每次进入这个仓库都要遵守”的规则，例如：

- 构建和测试命令。
- Review 关注点。
- 仓库特定编码约定。
- 目录级说明和路由。

### 6.1 官方发现顺序

Codex 每次启动或每个 TUI 会话开始时构建 instruction chain：

1. **全局层**：默认读取 `~/.codex/AGENTS.override.md`，如果不存在则读取 `~/.codex/AGENTS.md`。这一层只取第一个非空文件。
2. **项目层**：从项目根目录向当前工作目录逐层查找，每层按 `AGENTS.override.md`、`AGENTS.md`、`project_doc_fallback_filenames` 中的文件名顺序加载，且每个目录最多取一个。
3. **合并顺序**：从上层到更靠近当前目录的文件拼接。越靠近当前目录的文件越晚出现，因此优先级更高。

默认合并上限是 `project_doc_max_bytes = 32768` 字节。文件过大可能被截断，应拆到更靠近业务目录的 `AGENTS.md` 中。

### 6.2 推荐写法

```markdown
# AGENTS.md

## Repository expectations

- 修改 JavaScript 文件后运行 `npm test`。
- 提交 PR 前运行 `npm run lint`。
- 公共工具函数行为变化时同步更新 `docs/`。

## Review expectations

- 代码审查优先关注正确性、安全、行为回归和缺失测试。
- 不把纯风格问题作为高优先级发现，除非它掩盖真实风险。
```

---

## 7. Skills、MCP、Plugins、Subagents

### 7.1 Skills

Skills 用来给 Codex 增加任务专用能力、领域知识和可复用流程。一个 Skill 是一个目录，至少包含 `SKILL.md`：

```text
my-skill/
  SKILL.md       # 必需：metadata + instructions
  scripts/       # 可选：可执行脚本
  references/    # 可选：参考文档
  assets/        # 可选：模板、图片、资源
  agents/
    openai.yaml  # 可选：UI metadata、依赖、触发策略
```

`SKILL.md` 必须包含：

```markdown
---
name: skill-name
description: Explain exactly when this skill should and should not trigger.
---

Skill instructions for Codex to follow.
```

触发方式：

- 显式触发：在 CLI / IDE 中使用 `/skills` 或输入 `$skill-name`。
- 隐式触发：任务匹配 `description` 时由 Codex 自动选择。

Skill 存放位置：

| Scope | 位置 | 用途 |
| --- | --- | --- |
| Repo | `$CWD/.agents/skills` 到 `$REPO_ROOT/.agents/skills` | 仓库或子目录专用技能 |
| User | `$HOME/.agents/skills` | 个人通用技能 |
| Admin | `/etc/codex/skills` | 机器或容器内共享技能 |
| System | Codex 内置 | OpenAI 随 Codex 提供的技能，如 skill creator |

### 7.2 MCP

MCP 用于把 Codex 连接到第三方工具和上下文，例如文档系统、浏览器、Figma、Sentry、GitHub 等。

配置方式：

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

或写入 `~/.codex/config.toml` / 受信任项目的 `.codex/config.toml`：

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
env_vars = ["LOCAL_TOKEN"]
```

CLI 和 IDE Extension 共享 MCP 配置。TUI 中可用 `/mcp` 查看当前 MCP 服务器状态。

### 7.3 Plugins

插件是 Codex 的可安装分发单元，可以打包：

- Skills
- App integrations
- MCP servers
- 生命周期 hooks
- 展示资产和 marketplace metadata

使用上：

- App 里从 Plugins 页面浏览和安装。
- CLI 里输入 `/plugins` 打开插件浏览器。
- 安装后可以让 Codex 自行选择，也可以用 `@plugin` 明确指定。

自己构建插件时，官方建议优先使用 `@plugin-creator`。最小插件需要 `.codex-plugin/plugin.json` manifest。

### 7.4 Subagents

子智能体用于并行处理复杂任务，尤其适合：

- 大型代码库探索。
- 多角度代码审查。
- 多步骤功能实现中的独立子任务。

官方要点：

- 当前 Codex 版本默认启用 subagent workflow。
- Codex 只会在你明确要求时生成子智能体。
- 子智能体会消耗额外 token，因为每个子智能体都会做自己的模型和工具工作。
- 子智能体继承当前 sandbox policy；也可以为自定义 agent 单独覆盖沙箱配置。

自定义 agent 文件位置：

```text
~/.codex/agents/       # 个人 agent
.codex/agents/         # 项目 agent
```

每个自定义 agent TOML 至少需要：

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
"""
```

---

## 8. Codex App 重点能力

### 8.1 线程与项目

Codex App 是面向并行线程的桌面体验。一个项目类似在特定目录启动一个 Codex 会话。多个项目或多个包建议拆成独立项目，让 sandbox 边界更清晰。

### 8.2 Local / Worktree / Cloud

App 新线程可选择：

| 模式 | 含义 |
| --- | --- |
| Local | 直接在当前项目目录工作 |
| Worktree | 创建 Git worktree 隔离改动 |
| Cloud | 在配置好的云环境远程运行 |

Worktree 依赖 Git 仓库。它是 Git worktree 机制下的独立 checkout，不会干扰你的本地 checkout，适合并行探索或后台任务。

Git worktree 允许多个 checkout 并行，通常会涉及不同 branch 或 detached HEAD；重点是隔离工作区。

### 8.3 Review pane

Review pane 展示 Git 仓库中的改动，不只展示 Codex 改的内容，还包括用户自己改的和其他未提交改动。

可切换 scope：

- Uncommitted changes
- All branch changes
- Last turn changes

可做的事：

- 查看 diff。
- 给具体行添加 inline comments。
- stage 或 revert change。
- 让 Codex 根据 inline comments 修复。

CLI 中 `/review` 的结果也可以在 App review pane 中以内联评论形式显示。

### 8.4 Automations

Automations 用于定期运行后台任务。适合：

- 定期检查 telemetry 错误并建议修复。
- 定期总结代码库变化。
- 结合 Skills 执行复杂例行流程。

项目级 automation 要求运行本地 Codex App 的机器开机、Codex 正在运行、项目目录仍然存在。Git 仓库中 automation 可以运行在本地项目或新的 background worktree；非 Git 项目会直接在项目目录运行。

### 8.5 In-app browser 与 Browser Use

In-app browser 给你和 Codex 一个共享页面视图，适合本地开发服务器、文件预览、无需登录的公开页面。

限制：

- 不支持登录流程。
- 不使用你的浏览器 profile、cookies、扩展或已打开 tab。
- 需要登录态或浏览器扩展时，应使用普通浏览器或 Codex Chrome extension。

Browser Use 让 Codex 操作 in-app browser，例如点击、输入、截图、检查渲染状态和验证修复。使用前需要安装并启用 Browser plugin。

### 8.6 Computer Use

Computer Use 让 Codex 操作 macOS 或 Windows 的图形界面。适合命令行或结构化工具无法覆盖的任务，例如：

- 测试桌面应用。
- 复现 GUI 中才出现的问题。
- 操作需要点击的设置界面。
- 跨多个应用执行流程。

macOS 需要授予 Screen Recording 和 Accessibility 权限。由于它会影响项目之外的 app 或系统状态，应尽量给出明确边界并审查权限提示。

---

## 9. 实践建议与避坑

### 9.1 推荐工作流

1. **从小任务开始**：先让 Codex 解释项目、定位文件、列出风险，再让它修改。
2. **先 Plan 再做大改动**：复杂任务用 `/plan`，确认路线后再执行。
3. **用 Git 保护自己**：重要任务前后创建 Git checkpoint；App 中可用 diff、stage、commit、push 和 PR。
4. **用 Review 做第二视角**：开发完成后跑 `/review`，重点看正确性、安全、回归和测试缺口。
5. **把重复反馈写进 AGENTS.md**：不要每次口头重复团队约定。
6. **用最小权限跑任务**：默认使用 sandbox；只有隔离环境或明确需要时才用 `danger-full-access`。
7. **需要外部知识时配置 MCP 或 Web Search**：不要让模型凭记忆猜 API、版本或产品行为。

### 9.2 常见误区

- ❌ 把 Codex 当一次性代码生成器。
  ✅ 更好的方式是“计划 → 修改 → 验证 → review → 反馈 → 迭代”。

- ❌ 一上来开 Full Access。
  ✅ 大多数本地工作用 `workspace-write` + `on-request` 已足够。

- ❌ 把所有规则塞到全局 `AGENTS.md`。
  ✅ 个人偏好放全局，团队/项目/目录规则放最近的仓库 `AGENTS.md`。

- ❌ 使用过时模型名或网上教程里的私有命令。
  ✅ 以 `/model`、`codex -m` 和官方 Models 页面为准。

- ❌ 让 Codex 联网查“最新资料”但不说明来源要求。
  ✅ 明确要求使用官方文档、指定 MCP 或指定可信来源。

---

## 10. 官方资料索引

- [Codex Quickstart](https://developers.openai.com/codex/quickstart)
- [Codex CLI](https://developers.openai.com/codex/cli)
- [Slash commands in Codex CLI](https://developers.openai.com/codex/cli/slash-commands)
- [Non-interactive mode](https://developers.openai.com/codex/noninteractive)
- [Codex Models](https://developers.openai.com/codex/models)
- [Sandbox](https://developers.openai.com/codex/concepts/sandboxing)
- [Customization](https://developers.openai.com/codex/concepts/customization)
- [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Configuration Reference](https://developers.openai.com/codex/config-reference)
- [Model Context Protocol](https://developers.openai.com/codex/mcp)
- [Agent Skills](https://developers.openai.com/codex/skills)
- [Plugins](https://developers.openai.com/codex/plugins)
- [Build plugins](https://developers.openai.com/codex/plugins/build)
- [Subagents](https://developers.openai.com/codex/subagents)
- [Codex app features](https://developers.openai.com/codex/app/features)
- [Codex app review](https://developers.openai.com/codex/app/review)
- [Codex app automations](https://developers.openai.com/codex/app/automations)
- [Codex app worktrees](https://developers.openai.com/codex/app/worktrees)
- [Codex app in-app browser](https://developers.openai.com/codex/app/browser)
- [Codex app computer use](https://developers.openai.com/codex/app/computer-use)
- [Codex app commands](https://developers.openai.com/codex/app/commands)

---
