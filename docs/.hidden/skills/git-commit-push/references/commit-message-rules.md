# Commit Message Rules

## Rules

- 统一使用 Conventional Commits，默认格式为 `type(scope): summary`。
- `type` 只从固定集合中选择：`feat` 新功能、`fix` 修复问题、`refactor` 重构、`docs` 文档、`style` 格式、`test` 测试、`chore` 构建/依赖/配置、`perf` 性能、`ci` CI/CD、`build` 构建系统或外部依赖、`revert` 回滚。
- Commit Message 必须基于实际 git diff、staged diff 或用户提供的提交草稿生成，不要编造 diff 中不存在的行为、对象或修复结论。
- 提交内容需聚焦单一功能或单一问题；混入多个不相关目标时先提醒最好拆分，若用户坚持只要一条 message，则按主要用户价值选择 `type`。
- `scope` 表达本次改动影响的模块、页面、业务对象、配置域或包名，优先来自用户草稿、目录/文件名、模块名、页面名或 diff 中明确出现的业务对象。
- `scope` 要短且稳定；已有英文目录或模块标识时优先使用英文/kebab-case，只有中文对象本身更稳定时才保留中文 scope，不要为了看起来规范而硬翻译。
- 无法从草稿或 diff 稳定判断 scope 时，可以退回 `type: summary`，并简短说明 scope 依据不足；不要编造 diff 中不存在的模块名。
- 统一不用 `[]`。正确写法是 `fix(goods): ...`，不是 `[fix]: ...`。
- 若用户给的是 `[fix]: ...` 草稿，默认规范化为当前推荐格式；若用户给的是 `feat(scope): ...` 草稿，保留其 scope 或按实际 diff 修正不准确的 scope。
- `summary` 默认使用中文，直接写“对象 + 动作/结果”，不写 `update`、`调整代码`、`杂项优化` 这类空话。
- 只有在标题不足以表达关键背景时才补 body，body 放在标题下一行空行之后，使用扁平 bullet：`- xxx`。
- body 只列标题无法承载的关键细节，例如多个相关改动点、兼容行为、数据迁移点、配置变化或用户明确要求补充的详情。
- body 不重复标题，不写审核结论，不写“测试通过”“风险较低”这类提交事实外的信息。

## Examples

- `feat(goods): 支持商品列表快捷筛选`
- `fix(product-edit): 修复商品编辑页金额回写异常`
- `refactor(order-detail): 抽离订单详情状态映射逻辑`
- `docs(readme): 更新项目启动说明`
- `chore(deps): 升级第三方依赖`

```gitcommit
fix(product-edit): 修复商品编辑页金额回写异常

- 补齐商品选择后的金额刷新逻辑
- 避免手动改价状态被默认价格覆盖
```
