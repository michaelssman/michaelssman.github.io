# MCP（Model Context Protocol）

MCP 用于把智能体或 AI 应用连接到外部工具、数据源和系统。模型需要访问文档系统、数据库、浏览器、Figma、Sentry、GitHub、Notion 等外部上下文时，可以通过 MCP 服务器获得对应的工具和数据。

## 1. 一句话理解

MCP 负责提供连接能力：

```text
智能体或 AI 应用
    ↓
MCP 客户端
    ↓
MCP 服务器
    ↓
外部工具、数据源或业务系统
```

MCP 本身不规定智能体应该怎样完成业务流程，它主要解决“如何连接并调用外部能力”的问题。

## 2. MCP、工具、Skills 和子智能体 { #mcp-skills-subagents }

| 能力 | 主要作用 |
| --- | --- |
| 工具 | 提供读取文件、执行命令、搜索或调用接口等底层操作能力 |
| MCP | 将外部系统提供的工具和数据接入智能体 |
| Skill | 提供可复用流程、领域知识和操作规范 |
| 子智能体 | 拆分任务、隔离上下文并并行处理 |
| Plugin | 将 Skills、MCP 服务器、Hooks 等能力打包分发 |

可以把工具理解为锤子、锯子和钉子，把 Skill 理解为“如何建造书架”的操作方法。MCP 将外部系统中的工具和数据带进来，Skill 再告诉智能体如何组合这些能力，形成稳定且可重复的工作流。

工具定义通常会持续占用上下文；Skill 则通过渐进式披露按需加载。MCP 提供的工具与内置工具、自定义工具一样，最终都由智能体根据任务调用。

组合示例：

```text
主智能体负责整体需求。
子智能体 A 使用 code-review Skill 审查代码。
子智能体 B 通过 MCP 查询线上错误日志。
子智能体 C 使用 docs Skill 整理变更说明。
最后由主智能体汇总结果并给出修改方案。
```

## 3. Codex 中的 MCP { #codex-mcp }

### 3.1 添加服务器

可以通过 Codex CLI 添加 MCP 服务器：

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

也可以写入用户级 `~/.codex/config.toml`，或受信任项目中的 `.codex/config.toml`：

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
env_vars = ["LOCAL_TOKEN"]
```

CLI 和 IDE Extension 共享 MCP 配置。

### 3.2 查看连接状态

| 使用位置 | 命令 | 用途 |
| --- | --- | --- |
| Codex CLI | `/mcp` | 查看 MCP 工具和服务器状态 |
| Codex App | `/mcp` | 查看 MCP 连接状态 |

### 3.3 与 Plugin 的关系

Codex Plugin 是可安装的分发单元，可以把 Skills、App integrations、MCP servers、生命周期 Hooks 和展示资产打包在一起。MCP 定义外部连接，Plugin 负责分发一整套可安装能力。

### 3.4 使用建议

- 模型需要外部知识、实时数据或私有系统内容时，再配置 MCP。
- 明确指定可信服务器和数据来源，不要让模型根据记忆猜测 API、版本或产品行为。
- MCP 工具仍然受 Sandbox、审批策略和项目权限边界约束。

## 4. Codex 连接 Reqable { #codex-reqable-mcp }

将 Reqable MCP Server 接入 Codex 后，Codex 可以直接筛选实时抓包记录，读取请求头、请求体、响应状态、响应头和响应体，不再需要手动复制接口数据。

### 4.1 前提条件

- 读取抓包数据时，Reqable 应保持运行。

### 4.2 添加 Reqable MCP Server

Reqable macOS 应用内置了 MCP Server，可以直接使用，不依赖 Node.js 或 `npx`：

```bash
codex mcp add reqable -- \
  /Applications/Reqable.app/Contents/Helpers/mcp-server \
  --scope minimal
```

`minimal` 仍会注册部分可写工具。如果只需要 Codex 分析接口，建议在 `~/.codex/config.toml` 中收紧为只读工具：

```toml
[mcp_servers.reqable]
command = "/Applications/Reqable.app/Contents/Helpers/mcp-server"
args = ["--scope", "minimal"]
enabled_tools = [
  "capture_live_filter",
  "capture_live_get_by_id",
  "capture_live_generate_curl",
]
default_tools_approval_mode = "prompt"
```

| 工具 | 作用 |
| --- | --- |
| `capture_live_filter` | 按 URL、域名等条件筛选抓包记录 |
| `capture_live_get_by_id` | 根据数字 ID 读取完整请求和响应 |
| `capture_live_generate_curl` | 将抓包请求生成 cURL |

这个白名单不允许 Codex 删除抓包数据，也不允许创建重写、断点或脚本规则。

### 4.3 检查配置

```bash
codex mcp get reqable
codex mcp list
```

应能看到 `reqable` 的状态为 `enabled`，并且 `enabled_tools` 只包含上述三个工具。然后重启 Codex，可以使用类似以下的请求：

```text
查看 Reqable 中最近的接口请求。
分析 Reqable 中 URL 包含 /login 的请求和响应。
查找 Reqable 中响应状态异常的接口。
```

### 4.4 Reqable 与其他代理冲突

Reqable 默认可以自动接管 macOS 系统代理。如果同时使用 FlClash、Clash 或其他代理软件，打开 Reqable 后可能出现浏览器或终端无法联网。

查看当前系统代理、终端代理环境变量和端口占用：

```bash
scutil --proxy
env | rg -i '^(http|https|all|no)_proxy='
lsof -nP -iTCP -sTCP:LISTEN | rg ':7892|:9000|Reqable|adb'
```

在本机的一次实际排查中：

- FlClash 相关进程监听 `127.0.0.1:7892`。
- 终端的 `http_proxy`、`https_proxy` 和 `all_proxy` 均指向 `127.0.0.1:7892`。
- `adb` 占用了 `9000`，而 `9000` 又是 Reqable 的默认代理端口。

这些端口只是当时环境的实例，应以自己电脑的实际输出为准。

#### 解决端口冲突

如果 `9000` 已被占用，可以在 Reqable 中将代理端口改为 `9001`、`9080` 或其他未占用端口。Reqable MCP Server 会优先读取 Reqable 的实际 `proxyPort`，不需要在 MCP 配置中重复写死端口。

#### 串联 FlClash

需要同时使用 Reqable 和 FlClash 时，在 Reqable 中选择“代理 -> 二级代理 -> 新建”，例如：

```text
地址：127.0.0.1
端口：7892
模式：Include
规则：*
```

网络链路为：

```text
应用 -> Reqable:9080 -> FlClash:7892 -> 互联网
```

如果只使用 Reqable 抓取 iPhone 协同流量，可以关闭 Reqable 的“自动设置系统代理”，避免它接管 Mac 浏览器和终端的网络。

### 4.5 安全注意事项

- 抓包内容可能包含 `Authorization`、Cookie、Token、密码和个人数据。
- MCP 工具读取的内容会进入当前模型上下文，应只在必要时抓取和分析。
- 优先按域名或 URL 筛选所需请求，避免一次性读取无关流量。

## 5. Claude Code Hooks 与 MCP { #claude-hooks-mcp }

Claude Code Hooks 可以监听 MCP 交互，也可以直接调用已连接 MCP 服务器上的工具。

### 5.1 MCP 交互事件

| 事件 | 触发时机 |
| --- | --- |
| `Elicitation` | MCP 服务器请求用户输入时 |
| `ElicitationResult` | 用户响应 MCP 请求时 |

工具执行类事件也可以通过 Matcher 匹配 MCP 工具，例如 `mcp__.*`。

### 5.2 MCP Tool Hook

`mcp_tool` 类型用于调用已连接的 MCP 服务器工具，适合把 Claude Code Hooks 接入外部系统。

| 字段 | 必须 | 描述 |
| --- | --- | --- |
| `server` | 是 | 已配置的 MCP 服务器名称 |
| `tool` | 是 | 要在该服务器上调用的工具名称 |
| `input` | 否 | 传递给工具的参数，支持 `${path}` 替换 |

MCP 工具命名规则：

```text
mcp__<服务器名>__<工具名>
```

例如：

```text
mcp__memory__create_entities
```

该名称可以用于 `PreToolUse`、`PostToolUse` 等工具事件的 Matcher，例如 `mcp__memory__.*`。

## 6. Claude Agent SDK 与 Notion MCP { #claude-agent-sdk-notion-mcp }

一个研究智能体可以组合 Skill、子智能体和 MCP：

1. 主智能体加载 `learning-a-tool` Skill 并制定研究计划。
2. Docs Researcher、Repo Analyzer 和 Web Researcher 等子智能体并行收集资料。
3. 主智能体综合结果，生成学习指南、资源列表和代码示例。
4. Notion MCP 服务器把最终结果写入 Notion 页面。

配置时需要定义 Notion MCP 服务器，并使用通配符模式将对应 MCP 工具加入主智能体的允许工具列表。子智能体继续使用各自更受限的工具集，以符合最小权限原则。

当用户要求写入 Notion 时，主智能体读取本地 `resources.md`，转换为 Notion 富文本块，再通过 MCP 工具提交。各部分职责如下：

| 组成 | 职责 |
| --- | --- |
| Skill | 提供结构化、可重复的研究流程 |
| 子智能体 | 并行执行专注的研究任务 |
| MCP 服务器 | 提供 Notion 等外部系统连接 |
| Agent SDK | 以可编程方式编排完整工作流 |

## 7. 什么时候使用 MCP

- 需要访问模型上下文之外的实时或私有数据。
- 需要调用第三方系统提供的工具。
- 希望不同智能体客户端复用统一的外部能力。
- 希望把 MCP 与 Skills、子智能体或 Plugin 组合成完整工作流。

如果任务只需要固定说明和可重复步骤，优先考虑 Skill；如果只是拆分任务或隔离上下文，使用子智能体；只有需要连接外部系统时，才需要 MCP。

## 8. 相关文档

- [Agent Skills](Skills/Agent%20Skills.md)
- [Subagents 子智能体](Agent/Subagents.md)
- [Claude Code Hooks](Claude-Code-Hooks.md)
- [Codex](CodeX/Codex.md)
- [Codex MCP 官方文档](https://developers.openai.com/codex/mcp)
- [Reqable MCP Server](https://github.com/reqable/reqable-mcp-server)
- [Reqable 代理配置](https://github.com/reqable/reqable-docs/blob/master/en-US/capture/11_proxy.md)
