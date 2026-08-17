---
name: git-commit-message
description: Use when the user asks to generate, suggest, draft, or refine git commit messages from current code changes, and only commit text is needed without code review or executing git commit.
---

# Git Commit Message

## Overview

只根据实际改动生成 commit 信息，遵循 Conventional Commits，并优先输出 `type(scope): summary`。

这个 skill 只负责提炼提交主题和输出提交文案，不做代码审核，不给风险评级，也不执行 `git commit`、`git pull` 或 `git push`。如果用户明确要求提交、拉取或推送，改用 `git-commit-push`。

## Trigger

以下语义都应触发：
- `生成 commit 信息`
- `帮我写提交信息`
- `根据改动写个 commit message`
- `给我一个 feat(scope): summary`
- `把这条 [fix]: ... 改一下`
- `润色一下这条 commit message`

如果用户明确只要提交文案，而不是要审核代码或直接提交，就使用本 skill。

如果用户要求 `提交并推送`、`帮我提交代码`、`拉取后推送` 或类似完整 git 流程，不要使用本 skill，改用 `git-commit-push`。

## Workflow

1. 先检查 `git status --short`，确认当前是否存在 staged、unstaged 或 untracked 改动。
2. 确定生成范围：
   - 有 staged 改动时，优先基于 staged 改动生成，并明确说明本次文案对应 staged 范围。
   - 没有 staged 但有 unstaged / untracked 改动时，基于当前工作区改动生成。
   - 没有任何改动时，直接停止，说明当前没有可用于生成提交信息的改动。
3. 读取必要的 diff 或用户提供的提交草稿，只提炼“做了什么”“影响了什么对象”和“可稳定作为 scope 的范围”。
4. 如果用户要求润色现有 commit message，保留原意，优先把旧格式规范化到当前规则。
5. 如果单行标题不足以覆盖关键改动，在推荐提交信息下方补充 body 细节。
6. 输出 1 条推荐提交信息，最多再给 2 条备选。

## Commit Rules

- 统一使用 Conventional Commits，默认格式为 `type(scope): summary`
- `type` 只从固定集合中选择：`feat` 新功能、`fix` 修复问题、`refactor` 重构、`docs` 文档、`style` 格式、`test` 测试、`chore` 构建/依赖/配置、`perf` 性能、`ci` CI/CD、`build` 构建系统或外部依赖、`revert` 回滚
- Commit Message 必须基于实际 git diff、staged diff 或用户提供的提交草稿生成，不要编造 diff 中不存在的行为、对象或修复结论
- 提交内容需聚焦单一功能或单一问题；混入多个不相关目标时先提醒最好拆分，若用户坚持只要一条 message，则按主要用户价值选择 `type`
- `scope` 表达本次改动影响的模块、页面、业务对象、配置域或包名，优先来自用户草稿、目录/文件名、模块名、页面名或 diff 中明确出现的业务对象
- `scope` 要短且稳定；已有英文目录或模块标识时优先使用英文/kebab-case，只有中文对象本身更稳定时才保留中文 scope，不要为了看起来规范而硬翻译
- 无法从草稿或 diff 稳定判断 scope 时，可以退回 `type: summary`，并简短说明 scope 依据不足；不要编造 diff 中不存在的模块名
- 统一不用 `[]`。正确写法是 `fix(goods): ...`，不是 `[fix]: ...`
- 若用户给的是 `[fix]: ...` 草稿，默认规范化为当前推荐格式；若用户给的是 `feat(scope): ...` 草稿，保留其 scope 或按实际 diff 修正不准确的 scope
- `summary` 默认使用中文，直接写“对象 + 动作/结果”，不写 `update`、`调整代码`、`杂项优化` 这类空话
- 只有在标题不足以表达关键背景时才补 body，body 放在标题下一行空行之后，使用扁平 bullet：`- xxx`
- body 只列标题无法承载的关键细节，例如多个相关改动点、兼容行为、数据迁移点、配置变化或用户明确要求补充的详情
- body 不重复标题，不写审核结论，不写“测试通过”“风险较低”这类提交事实外的信息

## Output Rules

- 默认输出顺序：
  1. 标明提交信息对应的改动范围
  2. 给出 1 条推荐提交信息，必要时包含 body 细节
  3. 最多补充 2 条备选
- 推荐项优先满足“最贴近实际改动、格式最稳定、对象最清楚”
- 如果 diff 同时包含多个独立主题，优先提醒“当前改动混杂多个主题，commit message 只能概括主要改动”

## Hard Gates

- 不要做代码审核
- 不要输出严重性、评分、风险等级或“建议先修复”
- 不要执行 `git commit`
- 不要执行 `git pull`
- 不要执行 `git push`
- 不要把“生成提交信息”偷换成“帮用户决定是否可以提交”
- 不要编造 diff 中不存在的行为、对象或修复结论
- 不要输出 `[fix]: ...`
- 不要为了满足 scope 形式而编造没有依据的 scope；scope 不稳时宁可说明并退回 `type: summary`
- 不要给出 `chore: update`、`fix: 调整代码` 这类空泛标题

## Examples

推荐格式示例：

- `feat(goods): 支持商品列表快捷筛选`
- `fix(product-edit): 修复商品编辑页金额回写异常`
- `refactor(order-detail): 抽离订单详情状态映射逻辑`
- `docs(readme): 更新项目启动说明`
- `chore(deps): 升级第三方依赖`

带详情的提交信息示例：

```gitcommit
fix(product-edit): 修复商品编辑页金额回写异常

- 补齐商品选择后的金额刷新逻辑
- 避免手动改价状态被默认价格覆盖
```

旧格式规范化示例：

- `[fix]: 修复商品选择后的价格回填问题` -> `fix(商品): 修复商品选择后的价格回填问题`
- `feat(goods): 商品模块` -> `feat(goods): 支持商品模块基础资料维护`

如需压力场景，查看 `references/pressure-scenarios.md`。
