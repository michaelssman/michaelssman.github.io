# Commit Message Pressure Scenarios

## RED: Baseline failures without this skill

这些是未使用本 skill 时最容易出现的失败模式：

1. **回退到旧格式**
   - 压力：用户给了 `[fix]: ...` 或 `feat(scope): ...` 草稿
   - 常见错误：原样沿用旧格式，而不是规范化到统一规则

2. **scope 缺失或臆造**
   - 压力：diff 涉及明确模块，或只出现模糊的跨模块改动
   - 常见错误：明确模块下仍输出 `fix: ...`；或 scope 不稳定时编造 `fix(goods): ...`

3. **提交标题空泛**
   - 压力：diff 变更多、时间紧
   - 常见错误：给出 `chore: update`、`refactor: 调整代码` 这类看不出对象的标题

4. **正文详情缺失**
   - 压力：同一提交下有多个相关改动点，单行标题只能概括其中一个点
   - 常见错误：只输出一行标题，漏掉会影响理解的关键细节

5. **越界做审核结论**
   - 压力：发现明显风险
   - 常见错误：开始输出“建议先修复”“有 Major 风险”，越过本 skill 边界

## GREEN: Required passing scenarios with this skill

### Scenario 1: Plain message from diff
- User: `根据改动写个提交信息`
- Context: diff 是商品模块的普通 bug 修复
- Expected:
  - 输出 `fix(goods): ...`
  - 不加 `[]`
  - scope 来自 diff 中明确的模块、目录或业务对象

### Scenario 2: Normalize legacy draft
- User: `把这条 [fix]: 修复商品价格问题 润色一下`
- Expected:
  - 保留原意
  - 默认补充可稳定判断的 scope，例如 `fix(商品): 修复商品价格问题`

### Scenario 3: Mixed diff
- User: `给我一个 commit message`
- Context: diff 同时有功能调整和 CI 配置修改
- Expected:
  - 先提醒最好拆分提交
  - 若仍只要一条 message，按主要价值选择前缀
  - 标题不空泛

### Scenario 4: Message with body details
- User: `提交信息写详细一点`
- Context: diff 在同一模块内同时补齐列表筛选、默认值和空状态处理
- Expected:
  - 标题使用 `type(scope): summary`
  - 标题下方空一行，用扁平 bullet 罗列关键详情
  - body 不重复标题，不写审核或验证结论

### Scenario 5: No diff
- User: `帮我写提交信息`
- Context: git 工作区无任何改动
- Expected:
  - 直接停止
  - 说明没有可用于生成提交信息的改动

## Success Criteria

每个场景都必须满足：
- 只生成提交文案，不做审核结论
- 默认标题优先使用 `type(scope): summary`
- 不使用 `[]`
- scope 必须来自草稿或 diff，可稳定判断时必须补充
- 前缀只能来自固定词表
- 标题不能是空泛描述
- 标题不足以覆盖关键改动时，使用 body bullet 补充详情
