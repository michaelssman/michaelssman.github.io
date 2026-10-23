# Ponytail + Codex CLI

Ponytail 是面向编码 Agent 的提示词与技能插件，帮助 Codex 优先复用现有代码，以最少的必要改动完成任务。

`SessionStart`、`UserPromptSubmit`、`SubagentStart` 三个 hooks 均为 `Trusted`；默认使用 `full`。

## 1. 安装与启用

在普通 Shell 或 Herdr 的 Shell 面板中检查环境：

```bash
codex --version
node --version
command -v node
```

Codex 需支持 `plugin` 子命令。Ponytail 的生命周期 hooks 使用 Node.js，`node` 必须位于非交互 Shell 的 `PATH` 中；使用 nvm 等环境管理器时尤其需要检查。[安装要求](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md)

在 **Shell 中**依次执行：

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
codex
```

进入 Codex 后，在 **Codex 输入框中**输入：

```text
/hooks
```

审阅并信任 Ponytail 的 hooks，以 `/hooks` 实际列表为准，然后创建新会话。

## 2. 日常使用

启用后，直接向 Codex 描述编码任务。需要主动调用功能时，在 **Codex 输入框中**使用插件命名空间：

- `ponytail-help`：查看命令说明。
- `ponytail-review`：评审当前改动；可指定 `uncommitted`、`staged`、`branch` 或 PR 链接。
- `ponytail-audit`：检查整个仓库，并按重要程度排列问题。

### 切换强度

在 Codex 输入框中选择一项：

```text
$ponytail:ponytail lite
$ponytail:ponytail full
$ponytail:ponytail ultra
$ponytail:ponytail off
```

| 模式 | 用途 |
|---|---|
| `lite` | 按要求实现，同时提出更小的方案供选择 |
| `full` | 默认且推荐，完整应用最小必要改动与优先复用规则 |
| `ultra` | 实现前还会质疑缺乏必要性的需求部分 |
| `off` | 关闭 Ponytail |

切换后观察回复确认。普通的 `lite/full/ultra/off` 切换不修改新会话默认值。[模式定义](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md#levels)、[切换实现](https://github.com/DietrichGebert/ponytail/blob/main/hooks/ponytail-mode-tracker.js)

## 3. 代码逻辑评审

`ponytail-review` 把代码逻辑正确性放在评审首位，会读取变更及相关调用方、被调用函数和测试，追踪数据流。重点检查：

- 条件分支、空值、边界值、金额舍入等错误。
- 修改是否破坏调用方，数据在调用链中是否正确传递。
- 并发竞争、重复操作、事务和数据丢失风险。
- 关键逻辑是否缺少能够发现错误的有效测试。

每个问题需要有具体触发场景、代码位置、影响和修复建议。默认只输出报告，不修改代码。[官方评审规则](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md)

按评审范围选择技能：

| 技能 | 适用范围 |
|---|---|
| `ponytail-review` | 指定变更，例如未提交内容、暂存内容、需求分支或 PR；未指定时检查未提交变更，没有未提交变更则检查最近一次提交 |
| `ponytail-audit` | 指定目录或整个仓库；大仓库优先深入高风险区域，并说明未检查的部分 |

`ponytail-audit` 同样检查逻辑正确性，默认只报告问题，不修改代码。[官方仓库审查规则](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-audit/SKILL.md)

### 提供业务判断依据

业务逻辑需要结合需求文档、接口约定和预期行为评审。评审前提供对应资料的实际路径，并明确比较基准分支。

在 **Codex 输入框中**使用下面的提示词；将 `develop` 替换为实际基准分支，并补充需求文档和接口约定的路径：

```text
$ponytail:ponytail-review

审核当前需求分支相对于 develop 的变更。
结合需求文档和接口约定，重点检查业务逻辑、数据流、
边界条件、并发及异常处理，并追踪相关调用链。

只报告有明确证据的问题，给出文件行号、触发条件、
实际结果、预期结果和修复建议。不要修改代码，用中文输出。
```

## 4. 默认配置与 Herdr 多标签

不创建配置文件也能使用，默认模式为 `full`。需要明确设置新会话默认模式时，在 **Codex 输入框中**执行：

```text
$ponytail:ponytail default full
```

该命令只写默认配置，新会话采用，不切换当前模式。[默认模式设置实现](https://github.com/DietrichGebert/ponytail/blob/main/hooks/ponytail-mode-tracker.js)

也可用 `PONYTAIL_DEFAULT_MODE` 环境变量，例如在 Shell 中为这次启动指定：

```bash
PONYTAIL_DEFAULT_MODE=full codex
```

也可在 `~/.config/ponytail/config.json` 中配置新会话的默认模式：

```json
{
  "defaultMode": "full"
}
```

使用默认的 `full` 时无需创建该文件。环境变量优先于配置文件；如果设置了 `XDG_CONFIG_HOME`，配置文件位于该目录的 `ponytail/config.json`。[默认配置说明](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#settings)

Herdr 的多个标签和面板只要使用同一用户、同一个 `CODEX_HOME`，就共用该用户的 Codex 插件配置，无需在每个标签重复安装。安装和信任完成后，在各项目的新 Codex 会话中使用。每个项目继续保留自己的 `AGENTS.md`。

多标签并行建议保持统一模式，当前插件的模式状态并非按会话完全隔离。[状态存储实现](https://github.com/DietrichGebert/ponytail/blob/main/hooks/ponytail-runtime.js)

## 5. 排查

| 现象 | 检查或处理 |
|---|---|
| 安装后没有自动启用 | 在 Codex 中检查 `/hooks` 的信任状态，再创建新会话 |
| 输入 `/ponytail-review` 无效 | 改用 Codex 的 `$ponytail:ponytail-review` 技能调用 |
| 找不到费用统计 band / board | 这是 Claude Code 的配套界面，不是 Codex CLI 功能 |

## 6. 停用与卸载

临时关闭 Ponytail，在 Codex 输入框执行 `$ponytail:ponytail off`。需要禁用插件时，在 Codex 中打开 `/plugins`，选中 Ponytail 后按空格切换启用状态。

卸载插件，在 **Shell 中**执行：

```bash
codex plugin remove ponytail@ponytail
```

不再需要该插件市场时，再移除市场：

```bash
codex plugin marketplace remove ponytail
```

卸载后创建新 Codex 会话，避免沿用已加载的技能上下文。插件管理命令可用 `codex plugin --help` 查看。

项目来源：[Ponytail 官方仓库](https://github.com/DietrichGebert/ponytail)。
