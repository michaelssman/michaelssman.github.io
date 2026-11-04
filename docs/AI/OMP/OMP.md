# OMP

OMP（Oh My Pi）是运行在终端中的 AI 编程工具，支持模型登录、文件操作、命令执行和子 Agent 调度。

## 1. 本机安装范围

| 内容 | 路径或用途 |
| --- | --- |
| OMP 程序 | `~/.local/bin/omp` |
| 全局配置 | `~/.omp/agent/config.yml` |
| 全局行为规范入口 | `~/.omp/agent/RULES.md` |
| 协作目录 | `/Users/michael/Documents/app-management` |
| 协作项目配置与规则 | 协作目录的 `.omp/config.yml`、`.omp/RULES.md` |
| 五角色入口 | 协作目录的 `.omp/agents/*.md` |

## 2. 安装官方稳定版

### 2.1 核对版本与现有安装

```sh
uname -m
command -v omp
```

Apple Silicon 输出 `arm64`。已有 `omp` 时先执行 `omp --version` 并确认其安装方式，避免同时使用 Homebrew、Bun 和手动二进制管理同一命令。

### 2.2 下载并检查官方安装脚本

```sh
OMP_VERSION="v18.15.0"
OMP_INSTALL_SCRIPT="$(mktemp -t omp-install)"
curl --fail --location \
  "https://raw.githubusercontent.com/can1357/oh-my-pi/${OMP_VERSION}/scripts/install.sh" \
  --output "$OMP_INSTALL_SCRIPT"
sh -n "$OMP_INSTALL_SCRIPT"
less "$OMP_INSTALL_SCRIPT"
```

在 `less` 中按 `q` 退出。确认脚本来自官方仓库后安装：

```sh
PI_INSTALL_DIR="$HOME/.local/bin" \
  sh "$OMP_INSTALL_SCRIPT" --binary --ref "$OMP_VERSION"
"$HOME/.local/bin/omp" --version
```

- `--binary` 使用预编译程序，不需要额外安装 Bun 或 Rust 工具链。
- `--ref` 固定安装版本；必须与 `--binary` 一起使用，否则安装器可能选择源码安装。
- `PI_INSTALL_DIR` 指定安装目录，安装器没有 `--prefix` 参数。
- 安装器从官方构建服务获取二进制及 SHA-256，校验一致后替换程序，并执行版本检查。

### 2.3 确认终端可以找到命令

```sh
command -v omp
omp --version
```

本机 `~/.local/bin` 已在 PATH 中，不需要修改终端配置。如果其他机器只能通过完整路径运行，则在 `~/.zprofile` 中加入一次：

```sh
export PATH="$HOME/.local/bin:$PATH"
```

重新打开终端再检查。不要重复追加已有配置。

### 2.4 直接安装官方 Release 二进制

安装器下载不顺畅时，可以从同一官方 Release 下载文件并校验后安装。

以下示例仅适用于 **v18.15.0、macOS arm64**。更新版本或更换架构时，必须重新从[官方构建元数据](https://build.stencil.so/api/products/omp/versions/18.15.0/macos-arm64)获取对应 `file.sha256`，不能沿用旧值。

```sh
OMP_BINARY="$(mktemp -t omp-binary)"
curl --fail --location \
  "https://github.com/can1357/oh-my-pi/releases/download/v18.15.0/omp-darwin-arm64" \
  --output "$OMP_BINARY"
printf '%s  %s\n' \
  "d36dfabf0ee52d6f08efadb59c46f0349545c6f6975522417adae29646e73e34" \
  "$OMP_BINARY" | shasum -a 256 -c -
```

只有看到 `OK` 才继续；已有程序时先退出 OMP 并备份旧程序：

```sh
mkdir -p "$HOME/.local/bin"
install -m 755 "$OMP_BINARY" "$HOME/.local/bin/omp"
"$HOME/.local/bin/omp" --version
```

## 3. 配置全局行为

下方是本机配置内容，不要直接覆盖其他机器已有的模型或工具设置。

创建目录：

```sh
mkdir -p "$HOME/.omp/agent"
```

编辑 `~/.omp/agent/config.yml`：

```yaml
tools:
  approvalMode: write
skills:
  enableCodexUser: true
```

- `write`：主会话自动批准读写类工具，执行命令、派工等执行类工具需要审批；显式工具策略可能进一步改变结果。
- `enableCodexUser`：发现已有 `~/.codex/skills`，复用 Git 等工作流指令。它不会直接导入整套 Codex 插件、登录态和权限配置，也不保证每个依赖专属工具的 skill 都能运行。

创建 `~/.omp/agent/RULES.md`，引用现有个人规则：

```markdown
# 个人协作规范

默认使用简体中文。开始任务前读取并遵循 `/Users/michael/.codex/AGENTS.md`；涉及代码、脚本、配置或文档时，按该文件的适用条件读取工程规范与文档维护规范。
保留用户已有改动。不要读取或输出无关凭据；安装、登录、配置内容不得包含明文密钥。任务涉及的 Git、发布、真实数据修改和收费操作以用户明确授权为准。
这些是行为规范；OMP 的工具审批、额外工作目录和角色工具列表不构成操作系统沙箱。
```

`RULES.md` 是持续提供给 Agent 的行为规则。它复用个人规范，不复制工程和文档规范全文。

## 4. 接入 Java／Flutter 协作目录

### 4.1 配置目录与并发

```sh
mkdir -p "/Users/michael/Documents/app-management/.omp/agents"
```

编辑 `/Users/michael/Documents/app-management/.omp/config.yml`：

```yaml
task:
  maxConcurrency: 3
  maxRecursionDepth: 1
  isolation:
    enabled: false
workspace:
  additionalDirectories:
    - /Users/michael/Documents/java_demo
    - /Users/michael/Documents/flutter_demo
```

- 最多同时运行 3 个子 Agent，子 Agent 不再派工。
- 额外目录让会话发现两个项目的上下文；它不是文件访问白名单。
- `omp config set` 默认修改全局配置；项目配置应直接编辑本文件。

### 4.2 创建 OMP 的协作规则

编辑协作目录的 `.omp/RULES.md`：

```markdown
# OMP 协作入口

本会话运行在 OMP。先读取 `/Users/michael/Documents/app-management/AGENTS.md` 与 `docs/current-iteration.md`，沿用其中的产品、原型、交付审核节点及文件写入分工。用户已有批准继续有效。
AGENTS.md 中的 `agent_type` 是 Codex 调用方式；在 OMP 中使用 `task` 工具的 `agent` 字段，按需选择 `.omp/agents/` 中的 product、designer、backend、flutter、reviewer。主 Agent 是用户唯一日常入口，简单任务不必派工。
角色入口引用 `.codex/agents/<角色>.toml` 中的职责说明；这是复用指令内容，不代表 OMP 执行 Codex 的配置或权限模型。每个子 Agent 必须先读取对应职责文件、个人规范、协作规范、当前迭代以及目标项目的适用规范，再开展任务。不要依赖父会话的 AGENTS.md 自动继承。
派工写清目标、已批准范围、实际工作目录、可修改文件、依赖、验收条件和回报格式。子 Agent 不再派工；不修改共享迭代记录，不提交、推送或发布。
本协调目录不属于 Git 仓库，当前未启用 OMP 自动任务隔离。Java 和 Flutter 仍使用各自仓库；命令明确进入 hhjava、flutter_01 或 flutter_package。额外工作目录不限制其他路径的访问；同一文件同时只能有一个写入者。
如果用户明确安排独立 worktree，使用其实际路径并保留审核节点；不要自行把两个仓库合并，也不要假定从协调目录派工会自动创建隔离工作树。
designer 先确认当前可用设计工具与文件权限；Figma 不可用时按原职责交付本地 HTML 原型，不能把 Codex 已授权等同于 OMP 已接通。reviewer 核对可复现证据，未经实际执行不得声称验证通过。
```

OMP 子 Agent 不自动继承名为 `AGENTS.md` 的上下文文件，所以这里及各角色入口显式要求读取。[任务上下文限制](https://github.com/can1357/oh-my-pi/blob/v18.15.0/docs/tools/task.md#gotchas)。

### 4.3 创建五个角色入口

OMP 不直接加载 `.codex/agents/*.toml`。本配置新增 Markdown 入口，要求 Agent 读取原 TOML 的 `developer_instructions`，让职责继续只有一个维护位置。

| 角色 | 内置工具 | 职责来源 |
| --- | --- | --- |
| product | read、grep、glob | `.codex/agents/product.toml` |
| designer | 上述工具及 write、edit、bash | `.codex/agents/designer.toml` |
| backend | 上述工具及 write、edit、bash | `.codex/agents/backend.toml` |
| flutter | 上述工具及 write、edit、bash | `.codex/agents/flutter.toml` |
| reviewer | read、grep、glob、bash | `.codex/agents/reviewer.toml` |

例如 `.omp/agents/product.md`：

```markdown
---
name: product
description: 小木记账产品经理：梳理现有逻辑、范围和验收条件。
tools: [read, grep, glob]
spawns: []
---

你担任 product。执行任务前必须读取 `/Users/michael/Documents/app-management/.codex/agents/product.toml`，以其中的 `developer_instructions` 为职责和工作约束。
同时读取 `/Users/michael/.codex/AGENTS.md`、`/Users/michael/Documents/app-management/AGENTS.md`、`/Users/michael/Documents/app-management/docs/current-iteration.md`，并按任务读取目标项目规范。
仅执行主 Agent 本次分配的范围，返回成果和验证证据；不再派工，不修改共享迭代记录，不执行 Git 提交、推送或发布。
```

在另一台机器重建时，可用以下 Python 3 脚本生成全部五个入口。执行目录不限；目标角色文件已经存在时会停止，不覆盖已有内容：

```sh
python3 - <<'PY'
from pathlib import Path
import json

root = Path('/Users/michael/Documents/app-management')
roles = {
    'product': ('产品流程、范围和验收条件', ['read', 'grep', 'glob']),
    'designer': ('UI、交互规范和可点击原型', ['read', 'grep', 'glob', 'write', 'edit', 'bash']),
    'backend': ('Java 后端开发和测试', ['read', 'grep', 'glob', 'write', 'edit', 'bash']),
    'flutter': ('Flutter 移动端开发和测试', ['read', 'grep', 'glob', 'write', 'edit', 'bash']),
    'reviewer': ('独立审查与验收', ['read', 'grep', 'glob', 'bash']),
}
for role in roles:
    assert (root / f'.codex/agents/{role}.toml').is_file(), f'缺少职责文件：{role}'
    assert not (root / f'.omp/agents/{role}.md').exists(), f'角色已存在：{role}'
(root / '.omp/agents').mkdir(parents=True, exist_ok=True)
for role, (description, tools) in roles.items():
    text = (
        f'---\nname: {role}\ndescription: {description}\n'
        f'tools: {json.dumps(tools)}\nspawns: []\n---\n\n'
        f'你担任 {role}。先读取 `{root}/.codex/agents/{role}.toml`，'
        '遵循其中的 developer_instructions。\n'
        f'再读取 `/Users/michael/.codex/AGENTS.md`、`{root}/AGENTS.md`、'
        f'`{root}/docs/current-iteration.md` 及目标项目适用规范。\n'
        '仅执行本次分配范围，返回成果和验证证据；不再派工，不修改共享迭代记录，'
        '不提交、推送或发布。\n'
    )
    (root / f'.omp/agents/{role}.md').write_text(text, encoding='utf-8')
print('已创建五个 OMP 角色入口')
PY
```

以后修改职责时维护原 TOML；角色名称、描述或工具列表变化时同步 Markdown 入口。`spawns: []` 禁止角色继续委派。工具列表仅限制内置工具，后续接入的 MCP／扩展工具可能追加；reviewer 的 bash 可运行测试，也具有执行命令的能力。[官方角色契约](https://github.com/can1357/oh-my-pi/blob/v18.15.0/docs/task-agent-discovery.md)。

## 5. 登录模型与首次启动

1. **连接模型服务。** 使用 ChatGPT 订阅时：

   ```sh
   omp login openai-codex
   ```

   使用其他服务时运行 `omp login`，选择对应服务并按提示操作。

2. **进入协作目录启动：**

   ```sh
   cd "/Users/michael/Documents/app-management"
   omp
   ```

3. **在 OMP 会话输入 `/model`。** 选择已经登录且有权限的模型；若希望下次沿用，在模型角色设置中配置 `default`。五个角色未固定独立模型，初次使用不必配置多供应商路由。
4. **输入 `/agents`。** 确认有 `product`、`designer`、`backend`、`flutter`、`reviewer`；它们是角色定义列表。`Alt+A` 打开的是运行中的 Agent Hub，两者用途不同。
5. **先做只读检查：**

   ```text
   先读取协作规范和当前迭代，仅核对两个 Git 仓库状态。
   告诉我当前迭代、下一步及可用的五个角色。
   不修改业务文件，不执行提交、推送或发布，不派发开发任务。
   ```

## 6. 日常使用

### 发起一个新需求

```text
按现有协作规范推进本轮需求：改善【具体页面或流程】。
先让 product 调查现有实现，给我一个推荐方案、范围和验收条件。
产品方案批准后交 designer 做可点击原型；原型批准后再开发。
前后端有接口依赖时先明确契约，再安排 backend 和 flutter。
完成后由 reviewer 独立验收，给我可运行入口与实际验证证据。
当前先停在产品审核节点，不提前改业务代码。
```

### 恢复已有工作

```text
读取 docs/current-iteration.md，核对实际 Git 状态。
沿用已有批准范围，从记录的下一步继续；不要重复启动已完成的迭代。
本轮只处理【具体范围】，交付后更新迭代记录。
```

### 常用入口

| 操作 | 命令或快捷键 |
| --- | --- |
| 模型选择 | `/model` |
| 角色定义与设置 | `/agents` |
| 运行中子 Agent 的状态、对话和干预 | `Alt+A` |
| 配置设置 | `/settings` |
| 历史会话选择 | `/resume` |
| 显式使用已有 skill | `/skill:git-commit-pull-push` 等；以实际发现的名称为准 |
| 查看当前快捷键 | `/hotkeys` |

## 7. 审批与能力边界

- **主会话与子 Agent 的审批不同。** 主会话采用 `write`；子 Agent 因没有交互审批界面，会使用 `yolo`。显式拒绝策略仍生效，需要交互确认的策略在无界面时会阻止执行。批准父任务前先检查其范围，不能假定子任务每条命令都会再次询问。
- **行为规范不等于沙箱。** OMP 进程使用当前账户权限，额外目录、角色职责和工具审批都不提供与 Codex `workspace-write` 等价的操作系统隔离。
- **本次未配置自动 worktree 合并。** 单仓库后续要使用隔离时，需要从该 Git 仓库启动，配置隔离能力，并给任务显式设置 `isolated: true`；不能从本协调目录自动隔离两个外部仓库。
- **Figma 尚未接入 OMP。** 现有 Codex 插件授权不自动迁移。将来接入时使用官方远程 MCP，并分别核对授权、工具、设计 skills、文件权限和额度；当前 designer 可沿用本地 HTML 原型方案。
- **未安装 Java 语言服务器或额外调试器。** 本配置通过现有 Maven／Flutter 命令开展验证，没有承诺后台 Agent 已获得 LSP 语义分析。需要时再按 [LSP 官方配置](https://github.com/can1357/oh-my-pi/blob/v18.15.0/docs/lsp-config.md) 配置真实模块目录及语言服务器，并核对 `task.enableLsp`。

来源：[审批模式](https://github.com/can1357/oh-my-pi/blob/v18.15.0/docs/approval-mode.md)、[任务隔离](https://github.com/can1357/oh-my-pi/blob/v18.15.0/docs/tools/task.md)、[MCP 配置](https://github.com/can1357/oh-my-pi/blob/v18.15.0/docs/mcp-config.md)。

## 8. 检查配置

### 检查实际生效值

在协作目录执行：

```sh
cd "/Users/michael/Documents/app-management"
omp --version
omp config path
omp config get tools.approvalMode --json
omp config get skills.enableCodexUser --json
omp config get task.maxConcurrency --json
omp config get task.maxRecursionDepth --json
omp config get task.isolation.enabled --json
omp config get workspace.additionalDirectories --json
```

预期分别为已安装版本、全局配置目录、`write`、`true`、`3`、`1`、`false`、两个项目目录。配置命令不需要先发起模型对话。

如果角色没有出现，检查启动目录、`.omp/agents/*.md` 的 frontmatter，以及被引用的职责文件是否存在。`omp agents` 没有 `list` 子命令；不要运行 `omp agents unpack` 来检查，它会写出内置角色文件。

## 9. 本次操作与验证记录

本节记录本机实际操作，通用步骤见前文。

- 已实际启动未登录的交互终端，打开 `/agents`，确认五个角色均显示为 `project` 来源；主会话显示 `no-model`。五角色配置与职责引用还通过独立静态核对。
- OMP 凭据库中的模型凭据数量为 0；未完成模型登录，未发送模型任务。非交互 RPC 检查需要先选定可用模型，因此本次改用本地交互角色列表验证。
- 文档中的五角色生成脚本已在临时目录验证：能生成五个入口，再次执行会拒绝覆盖。MkDocs 严格构建通过；其他既有文档的链接提示不属于本次变更。
- 未验证真实模型对话、子 Agent 实际派工、Figma、Java／Flutter 业务测试和真机操作。登录后按第 5 节完成首次只读验收。
