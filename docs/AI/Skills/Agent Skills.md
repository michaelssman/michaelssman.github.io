# Agent Skills

Agent Skills 用于把专业知识、可重复工作流、脚本和资源封装成可按需加载的能力。一个 Skill 本质上是一个目录，其中必须包含 `SKILL.md`。

## 1. 核心概念

### 渐进式披露

智能体通常分三步加载 Skill：

1. **发现**：启动时只读取 `name` 和 `description`，用于判断 Skill 的用途和触发时机。
2. **激活**：任务匹配后加载完整的 `SKILL.md`。
3. **执行**：根据指令按需读取 `references/`、使用 `assets/` 或运行 `scripts/`。

这种机制可以同时提供多个 Skills，而不必一开始就把全部内容放入上下文窗口。

### Skill 的价值

- 封装团队规范、领域知识和操作步骤。
- 将重复提示转成可复用、可版本控制的工作流。
- 通过明确的步骤、边界和输出格式提高结果一致性。
- 将详细资料和模板放到外部文件中，减少不必要的上下文占用。

Skill 不会凭空增加系统权限。它只能使用当前智能体已经具备的工具；纯指令型 Skill 不一定需要 Bash 或文件写入权限，执行脚本或修改文件时才需要相应工具。

## 2. 目录与规范

典型目录结构：

```text
my-skill/
├── SKILL.md          # 必需：元数据和主要指令
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：详细参考资料
└── assets/           # 可选：模板、图片、数据等资源
```

### `SKILL.md`

`SKILL.md` 由 YAML frontmatter 和 Markdown 正文组成：

```yaml
---
name: code-review
description: Reviews code for quality, security, and project conventions. Use when the user asks for a code review or risk assessment.
---

# Code Review

1. Read the project conventions.
2. Inspect the relevant changes.
3. Report findings by severity with file references.
```

开放规范中的主要字段：

| 字段 | 必需 | 约束或用途 |
| --- | --- | --- |
| `name` | 是 | 1～64 个字符；使用小写字母、数字和连字符；与父目录同名 |
| `description` | 是 | 1～1024 个字符；同时说明“做什么”和“何时使用” |
| `license` | 否 | 许可证名称或许可证文件路径 |
| `compatibility` | 否 | 最多 500 个字符；说明系统、依赖或网络要求 |
| `metadata` | 否 | 额外的字符串键值信息 |
| `allowed-tools` | 否 | 预批准工具列表；属于实验字段，客户端支持可能不同 |

为了提高跨客户端兼容性，应遵循开放规范显式填写 `name` 和 `description`，不要依赖特定客户端自动推断字段。

### 可选目录

- `scripts/`：放置 Python、Bash、JavaScript 等脚本。脚本应说明依赖，提供清晰错误信息并处理边界情况。
- `references/`：放置详细规范、技术资料和领域知识，仅在需要时读取。
- `assets/`：放置输出模板、图片、数据文件和 Schema 等静态资源。

建议让 `SKILL.md` 只保留决策入口和主要流程，将长篇资料移到引用文件。主文件最好不超过 500 行，文件引用尽量只深入一层。

## 3. Skill 与其他能力的区别

| 能力 | 主要作用 | 上下文与执行方式 |
| --- | --- | --- |
| Skill | 可复用的知识、规范和工作流 | 匹配任务后按需加载 |
| 工具 | 读取文件、执行命令、调用 API 等实际能力 | 由运行环境提供并受权限控制 |
| `CLAUDE.md` | 项目长期规则和每次会话都需要的背景 | 会话启动时加载 |
| 子智能体 | 在独立上下文中完成委派任务 | 只将任务结果返回主智能体 |
| MCP | 连接外部服务、数据源和工具 | 通过 MCP Server 暴露结构化能力 |

外部系统和数据连接统一记录在 [MCP](../MCP.md) 中。

这些能力可以组合使用。例如，主智能体加载代码审查 Skill，再把审查任务委派给只具有读取权限的子智能体；子智能体根据 Skill 中的标准检查代码，并把结果返回主智能体。

## 4. 创建自定义 Skill

### 创建步骤

1. 明确 Skill 要解决的重复问题和不负责的范围。
2. 创建与 `name` 同名的目录和 `SKILL.md`。
3. 在 `description` 中写清能力、触发场景和关键词。
4. 在正文中提供顺序步骤、判断条件、边界情况和输出要求。
5. 将详细资料、模板和可重复执行逻辑分别放入 `references/`、`assets/` 和 `scripts/`。
6. 使用真实任务测试触发、执行和失败处理，再根据结果迭代。

### 编写原则

- 使用明确、可执行的指令，避免只写宽泛目标。
- 说明什么时候必须**停止**、**请求确认**或**跳过某一步**。
- 输出格式要求较复杂时引用模板，不要把所有示例堆进 `SKILL.md`。
- 一个 Skill 聚焦一个稳定职责；复杂工作流可以组合多个 Skills。
- 脚本适合确定性操作，Markdown 指令适合需要智能体判断的步骤。
- 涉及写入、网络、凭据或危险命令时，遵循最小权限原则。

## 5. 验证与测试

可以使用官方参考工具检查目录和 frontmatter：

```bash
skills-ref validate ./my-skill
```

行为测试至少覆盖：

- 应当触发 Skill 的典型请求。
- 不应触发 Skill 的相邻请求。
- 缺少文件、依赖或权限时的处理。
- 正常输入、边界输入和失败输入。
- 输出是否符合模板和项目约定。
- 脚本是否可重复执行，是否会产生意外副作用。

Anthropic 的 [`skills`](https://github.com/anthropics/skills) 仓库提供示例、模板和 `skill-creator`。`skill-creator` 可以辅助初始化、验证和评估 Skill，但生成结果仍需要结合真实任务检查。

## 6. 在 Claude Code 中使用

常见存放位置：

| 范围 | 路径 |
| --- | --- |
| 个人 | `~/.claude/skills/<skill-name>/SKILL.md` |
| 项目 | `.claude/skills/<skill-name>/SKILL.md` |
| 插件 | `<plugin>/skills/<skill-name>/SKILL.md` |

Claude Code 可以根据 `description` 自动选择 Skill，也可以通过 `/skill-name` 显式调用。

项目结构可以这样组织：

```text
.claude/
├── CLAUDE.md
├── skills/
│   └── code-review/
│       └── SKILL.md
└── agents/
    └── code-reviewer.md
```

- 每次会话都需要遵守的项目事实和规则放入 `CLAUDE.md`。
- 只在特定任务中需要的知识和流程放入 `.claude/skills/`。
- 自定义子智能体定义在 `.claude/agents/`。
- 子智能体使用独立上下文，可以通过 frontmatter 的 `skills` 字段预加载指定 Skills。

## 7. 在 Claude API 中使用

Claude API 支持 Anthropic 预建 Skills 和通过 Skills API 上传的自定义 Skills。调用 Messages API 时，在容器配置中指定需要使用的 Skill，并启用代码执行工具。

Files API 主要负责上传输入文件和下载生成文件，不是注册自定义 Skill 的替代方案。不同产品有各自的安装和加载机制，不应假设 Claude.ai、Claude Code、Claude API 之间会自动同步自定义 Skills。

## 8. 在 Claude Agent SDK 中使用

Agent SDK 可以把 Skills、子智能体和工具组合成可编程工作流：

1. 通过项目设置来源加载 `.claude/skills/`。
2. 允许主智能体使用 `Skill` 工具加载 Skills。
3. 通过 `agents` 参数定义子智能体，并允许主智能体使用 `Agent` 工具进行委派。
4. 为每个子智能体配置完成任务所需的最小工具集。
5. 汇总各子智能体结果，由主智能体生成最终输出。

例如，研究型智能体可以加载 `learning-a-tool` Skill 制定研究计划，再并行委派：

- Docs Researcher：阅读官方文档。
- Repo Analyzer：分析源码和项目结构。
- Web Researcher：补充教程和外部资料。

生产环境中应对 Bash、写入、网络访问和外部系统操作设置权限边界；高风险操作应暂停并请求人工确认。Claude Agent SDK 与 Notion 的外部写入示例见 [MCP：Claude Agent SDK 与 Notion](../MCP.md#claude-agent-sdk-notion-mcp)。

## 9. 总结

- Skill 用于封装按需加载的专业知识和可重复工作流。
- `description` 决定 Skill 能否在正确场景被发现，应同时写清“做什么”和“何时使用”。
- `SKILL.md` 保持精简，详细资料、脚本和模板按需拆分。
- Skill 提供方法，工具提供执行能力，子智能体提供上下文隔离，MCP 提供外部连接。
- 使用真实任务验证触发准确性、输出质量、权限边界和失败处理。

## 官方资料

- [Agent Skills 开放规范](https://agentskills.io/specification)
- [Anthropic Skills 示例仓库](https://github.com/anthropics/skills)
- [Claude Code：Skills](https://code.claude.com/docs/en/skills)
- [Claude Code：子智能体](https://code.claude.com/docs/en/sub-agents)
- [Claude API：Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Claude Agent SDK：Skills](https://code.claude.com/docs/en/agent-sdk/skills)
- [Claude Agent SDK：子智能体](https://code.claude.com/docs/en/agent-sdk/subagents)
