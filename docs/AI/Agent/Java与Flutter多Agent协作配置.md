# Java 与 Flutter 多 Agent 协作配置

Java 后端和 Flutter App 保留独立 Git 仓库，由一个主 Agent 统一协调产品、设计、开发和验收，用户审核产品方案、交互原型和最终交付。

## 1. 目录与角色

协作目录只保存团队配置和跨项目资料，不移动源码，也不合并两个 Git 仓库。启动后只与主 Agent 沟通，由它派工并汇总结果。

| 角色 | 实现方式 | 职责与产物 |
| --- | --- | --- |
| 项目负责人 | 主会话读取 `AGENTS.md` | 拆任务、管理依赖、记录审核、集成与交付 |
| 产品经理 | `product` | 问题依据、用户流程、范围与验收条件 |
| UI / 交互设计 | `designer` | 设计规范、可点击原型和页面状态 |
| Java 开发 | `backend` | `hhjava` 的接口、业务、鉴权与测试 |
| Flutter 开发 | `flutter` | 主 App、必要公共组件与交互验证 |
| 独立验收 | `reviewer` | 对照批准需求验收，返回问题及证据 |

五种子角色按任务启动，最多同时运行三个；不是五个一直运行的后台进程。模型与推理等级继承主 Agent，当前配置不指定模型。

## 2. 准备与安装

### 2.1 创建协作目录

可下载本次配置的完整初始模板：[app-management.zip](Java与Flutter多Agent协作配置.assets/app-management.zip)。压缩包包含下列九个文件：

```text
app-management/
├── AGENTS.md
├── README.md
├── .codex/
│   ├── config.toml
│   └── agents/
│       ├── product.toml
│       ├── designer.toml
│       ├── backend.toml
│       ├── flutter.toml
│       └── reviewer.toml
└── docs/
    └── current-iteration.md
```

全新安装时，将压缩包解压到 `/Users/michael/Documents`。

### 2.2 配置并发与项目范围

`app-management/.codex/config.toml`：

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/Users/michael/Documents/java_demo",
  "/Users/michael/Documents/flutter_demo",
]

[agents]
enabled = true
max_concurrent_threads_per_session = 3
```

- 当前协作目录是主工作区；`writable_roots` 补充两个代码仓库的写入范围。
- 并发值 `3` 只计算子 Agent，不包括主 Agent。
- `workspace-write` 保留沙盒限制；需要超出权限的操作仍按当前客户端和管理策略处理。
- 自定义角色继承主会话权限。角色中的“只读代码”“只改后端”是协作约定，不是独立安全沙盒；不要在角色 TOML 中设置 `sandbox_mode` 来冒充权限隔离。

配置依据：[官方 Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)、[沙盒与可写目录](https://learn.chatgpt.com/docs/sandboxing#configure-defaults)。

### 2.3 定义专业角色

每个角色使用一个 TOML 文件，必须有 `name`、`description`、`developer_instructions`。例如 `.codex/agents/product.toml`：

```toml
name = "product"
description = "小木记账产品经理：梳理现有产品逻辑，提出核心流程、迭代范围和验收条件。"
developer_instructions = """
你是产品经理，向主 Agent 汇报，不代替用户批准方案。
先阅读协作目录 AGENTS.md、docs/current-iteration.md，以及目标项目的适用规范和相关业务实现。
结合小木记账现有普通、礼金/借贷、基金账本及账号/备份能力分析任务；不要自动把所有模块纳入本轮。
区分源码已确认事实、用户反馈和待验证假设，不编造访谈、指标或市场结论。
每轮围绕一个核心流程，说明目标用户、问题依据、建议流程、范围、暂不包含的事项和验收条件。
按用户实际操作描述成功与失败路径；涉及真实账本数据时明确数据影响。
返回一份主 Agent 可以直接提交用户审核的简洁方案，附必要源码或文档依据。
只读业务仓库；不修改代码、共享迭代记录或 Git 状态，不启动子 Agent。
"""
```

其余四个文件已在模板中提供完整指令。修改角色时优先明确允许的工作范围、输入、产物与验证要求，避免只写一个职位名称。

设计角色默认复用可用工具；没有设计工具时，在 `design/<迭代标识>/` 制作不需要构建的 HTML/CSS/JS 原型，使用虚构数据。此目录在实际设计任务中再创建。原型用于审核流程和视觉，Flutter 的键盘、手势和设备适配仍需实际验收。

### 2.4 设置总控规则和状态记录

主 Agent 从协作目录 `AGENTS.md` 读取团队规则；完整内容已在模板中提供。其关键约定为：

1. 派工指定自定义 `agent_type`、目标、批准材料、工作目录、修改范围、依赖和验收条件。
2. 操作 Java 前显式读取 `hhjava/AGENTS.md`；操作 Flutter 前显式读取根 `AGENTS.md`、`AGENTS.flutter.md` 和目标目录更近的规则。额外可写目录不意味着其规则已自动加载。
3. 主 Agent 独占 `docs/current-iteration.md`；designer 独占获分配的原型文件；同一文件同时只有一个修改者。
4. 前后端并行前先确定接口字段、鉴权、错误与示例；接口详细说明沿用两端现有权威文档，迭代记录保存增量和链接。
5. 子 Agent 不执行 Git 提交、推送或切换分支，由主 Agent 按用户授权统一处理。
6. 同仓库需要 worktree 隔离时显式创建并分配路径、权限，不能假定子 Agent 自动拥有独立工作树。

`docs/current-iteration.md` 保存目标、阶段、产品方案、原型版本、任务表、用户审核记录和验证结果。只有主 Agent 更新。开始新迭代前，将上一轮记录归档至 `docs/iterations/<迭代标识>.md`。采用项目已有 OpenSpec 流程时，链接其权威文件，不另抄一份需求和任务。

规则加载依据：[官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

### 2.5 信任项目并启动

Codex 只加载受信任项目的 `.codex/` 配置。在本机终端执行：

```sh
codex -C "/Users/michael/Documents/app-management"
```

首次启动若提示目录信任，阅读配置后选择信任。已安装的本机配置只为这个协作目录增加了信任项；复现时也可以在 `~/.codex/config.toml` 中添加以下独立表，若已存在则修改现有项，不能重复添加：

```toml
[projects."/Users/michael/Documents/app-management"]
trust_level = "trusted"
```

主 Agent 应从 **app-management** 开始新会话。如果从 Java 或 Flutter 目录单独启动，不会自动使用旁边协作目录的角色与总控规则。修改角色配置后，重新开始会话加载。

进入会话后用 `/status` 检查工作目录与权限，用 `/subagents` 查看实际启动的子任务。桌面客户端可以打开该协作目录作为工作目录；本次验证的是本机 CLI，桌面端实际权限以会话显示为准。

官方依据：[配置加载与信任](https://learn.chatgpt.com/docs/config-file/config-basic)、[CLI 命令](https://learn.chatgpt.com/docs/developer-commands)。

## 3. 日常使用与审核

### 第一轮：先检查一个核心流程

向主 Agent 发送：

```text
你担任项目负责人，按 AGENTS.md 调度专业 Agent。
本轮先分析「普通账本的新增记账流程」。
读取两个项目中相关的实现、现有规范和 docs/current-iteration.md。
请 product 提出问题依据、推荐流程、范围和验收条件，汇总后交我审核。
现在停在产品审核节点；批准后再做原型，原型批准后才实施业务代码。
每个阶段向我提供具体成果，已批准范围内的常规工作自行推进。
```

将示例流程替换为本轮目标。这只是提示词示例，当前配置没有启动或批准该产品改造。

### 三个审核节点

| 节点 | AI 先完成什么 | 用户审核什么 | 明确回复示例 |
| --- | --- | --- | --- |
| 产品 | 问题依据、范围、流程和验收条件 | 是否解决正确的问题 | “批准这版产品范围和验收条件，进入原型阶段” |
| 原型 | 可点击页面及必要交互状态 | 操作和视觉是否满意 | “批准当前原型版本，按此方案开发” |
| 交付 | 实现、联调、独立验收及运行证据 | 可运行成果和剩余限制 | “接受这次交付；暂不发布”，或明确发布目标及范围 |

已批准范围内的常规开发、测试和修复自主执行。产品方向、范围或已批准交互发生实质变化时才回到相应节点；不把“用户没回复”或 AI 自评当作批准。纯后端或无 UI 变化的任务可说明原型节点不适用。

### 中断后继续

重新从协作目录启动，发送：

```text
读取 docs/current-iteration.md，并核对两个代码仓库的实际状态。
说明当前阶段、已经批准的范围和下一步，然后继续已获批准的工作。
不要根据之前的聊天标题推断审核结果。
```

配置文件定义角色，迭代文件保存工作状态；它们不让 Agent 在会话关闭后持续工作。

## 4. 开发与验收边界

- Java 按 `hhjava/AGENTS.md` 选择 Maven 模块测试，命令在 `hhjava` 执行。
- Flutter 按项目规则在受影响模块执行格式化、分析和测试；公共组件变化检查调用方。
- reviewer 对照批准材料和真实证据检查，问题交回开发者，修复后复验。
- 文本配置检查不证明业务测试通过；静态原型不证明 App 真机交互通过。
- 本地代码变化不会自动部署到服务器；部署、真实短信、数据库变更和上传发布包按明确授权处理。
- 用户已有修改与真实账本数据必须保留；共享资料、原型和日志不保存真实凭据或个人数据。

## 5. 检查与排障

启动后可先发送这条轻量检查：

```text
只做团队配置检查，不修改两个业务仓库。
确认当前工作目录、两个项目路径和可用的五个自定义角色。
调用 product，只让它汇报当前职责与产品审核节点，不开展产品调研。
等待结果后汇总，停止在检查完成处。
```

| 现象 | 检查方法 |
| --- | --- |
| 没有五个角色 | 确认从 app-management 启动；检查项目是否受信任、角色 TOML 三个必填字段，修改后新开会话 |
| Java / Flutter 无法写入 | 用 `/status` 检查权限，核对 `writable_roots` 和实际路径；管理策略可能继续限制权限 |
| Agent 忽略项目规范 | 主 Agent 在派工时明确提供目标仓库规范路径，并要求先读取 |
| 多个 Agent 同时改同一文件 | 主 Agent 重新分配写入范围，保留已有变更；共享迭代文件保持主 Agent 单写 |
| 每次恢复都丢失阶段 | 检查主 Agent 是否更新了 current-iteration 的审核依据、产物版本和下一步 |

## 6. 本次配置记录

2026-10-27 使用本机 Codex CLI `0.164.0` 完成配置：

- 新建 `/Users/michael/Documents/app-management`，安装九个团队配置与状态文件。
- 在 `~/.codex/config.toml` 中只新增协作目录信任项，原配置备份为 `/Users/michael/.codex/config.toml.before-app-management-20261027-114051.bak`；其余配置保持原样。
- TOML 解析、角色集合、路径检查通过；安装后的文件与下载模板逐文件一致。
- Codex 严格配置读取确认项目配置已加载、两个额外可写目录及子 Agent 并发上限生效；原生提示输入检查确认总控规则和五个自定义角色已注册。

本次只验证配置加载，未运行完整角色派工迭代、Java/Flutter 业务测试或桌面客户端验收，也未启动业务改造或发布。

相关基础概念参见 [Subagents 子智能体](Subagents.md)。
