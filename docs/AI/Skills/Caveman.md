# Caveman：精简 Agent 回复

Caveman 用技能约束聊天表达：先给答案、减少套话，同时保留技术事实、否定条件和必要步骤。代码、命令、路径和错误信息保持原样，写入文件的文档与提交说明仍使用正常文风。[官方项目](https://github.com/JuliusBrussee/caveman)

以下使用 **Codex 技能版**，按需启用。完整版另外提供本地代理、工具输出压缩和模型路由，属于不同的安装范围。

## 1. 安装

在已安装 Node.js 和 npm 的终端中执行：

```bash
npx skills add JuliusBrussee/caveman -a codex -g \
  --skill caveman ultracave megacave
```

- `-a codex`：安装给 Codex。
- `-g`：用户级安装，供不同项目使用。
- `--skill`：只选择这三个回复风格技能。

上面的命令安装默认分支上的版本。需要固定版本时，也可以在 Codex 中让内置安装技能完成：

```text
$skill-installer 安装 JuliusBrussee/caveman 的 v4.1.0 版本，
选择 skills/caveman、skills/ultracave、skills/megacave，使用默认技能目录。
```

两种方式任选一种；已有同名技能时先核对来源，避免重复安装。安装后从下一轮对话开始使用；若技能列表未刷新，再打开新会话。[Codex 安装说明](https://github.com/JuliusBrussee/caveman/blob/v4.1.0/INSTALL.md#codex)

## 2. 使用

下面的指令输入在 **Codex 对话框**中，不是在 Shell 中执行：

| 指令 | 作用 |
| --- | --- |
| `$caveman` | 标准模式，精简表达，适合日常使用 |
| `$ultracave` | 更强压缩，更多短句和片段 |
| `$megacave` | 使用文言文，技术标识保留原文 |
| `$caveman status` | 查看当前会话模式，不切换模式 |
| `stop caveman` | 关闭 Caveman，恢复正常表达 |

可以与任务一起发送，例如：

```text
$caveman
用简体中文解释这段错误。给出原因、修复步骤和验证方法。
```

模式持续到当前会话中明确关闭。纯技能版没有安装自动启动钩子，新会话按需再次调用；状态显示 `not tracked by this host` 时，表示宿主没有通过钩子跟踪状态。[标准模式规则](https://github.com/JuliusBrussee/caveman/blob/v4.1.0/skills/caveman/SKILL.md)

`$megacave` 适合希望尝试文言表达时使用，字数更少不代表 token 或费用一定更少。[文言模式规则](https://github.com/JuliusBrussee/caveman/blob/v4.1.0/skills/megacave/SKILL.md)

## 3. 使用边界

- **主要减少聊天输出。** 仅安装技能，不会自动压缩历史上下文、工具输出或模型推理；实际节省取决于模型、任务和计费方式。
- **简洁服从清晰。** 有歧义、关键操作顺序或必要风险说明时，应使用完整句子，不能为了短而遗漏信息。
- **知识正文仍按知识库规范编写。** 不把文言或碎片化表达自动用于教程、代码注释、提交说明等持久内容。
- **与 Ponytail 分工不同。** Caveman 管理回复措辞，Ponytail 管理实现范围、复用和工程取舍；需要时可分别启用。
