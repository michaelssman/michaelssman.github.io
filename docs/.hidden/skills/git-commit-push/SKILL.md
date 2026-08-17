---
name: git-commit-push
description: Use when the user explicitly asks Codex to complete a git workflow that may stage changes, generate a Conventional Commit message, create a commit, pull/rebase from the remote branch, and push. Trigger on requests such as commit and push, submit code, pull then push, or finish the git commit workflow. Do not use when the user only wants commit message text; use git-commit-message instead.
---

# Git Commit Push

## Overview

完成完整 git 提交流程：检查仓库状态，生成提交信息，提交本地改动，拉取远端更新并推送。这个 skill 会执行改变本地仓库和远端仓库的命令，因此只在用户明确要求提交、拉取或推送时使用。

提交信息规则见 `references/commit-message-rules.md`。生成提交信息前先读取该文件。

## Trigger

以下语义应触发：
- `提交并推送`
- `帮我提交代码`
- `拉取代码后推送`
- `生成提交信息并 commit`
- `commit and push`
- `把当前改动提交到远端`

以下语义不要触发本 skill，改用 `git-commit-message`：
- `生成 commit 信息`
- `帮我写提交信息`
- `润色 commit message`
- `只要提交文案`

## Workflow

1. 定位仓库根目录：运行 `git rev-parse --show-toplevel`。如果当前目录不是 git 仓库，停止。
2. 检查仓库状态：运行 `git status --short --branch`，确认当前分支、upstream、ahead/behind、staged、unstaged 和 untracked 状态。
3. 检查阻塞状态：
   - 处于 merge、rebase、cherry-pick、bisect 中时停止，说明当前 git 状态需要先处理。
   - detached HEAD 时停止，除非用户明确指定目标分支。
   - 没有 worktree 改动且没有待推送 commit 时停止，说明没有可提交或可推送内容。
4. 确定提交范围：
   - 已有 staged 改动时，默认只提交 staged 范围，并说明 unstaged/untracked 会保留。
   - 没有 staged 改动时，检查当前 worktree 改动；通过安全检查后使用 `git add -A` stage 当前改动。
   - 用户明确要求只提交部分文件时，只 stage 用户指定范围。
5. 安全检查：
   - 查看 `git diff --stat`、`git diff --cached --stat` 和必要的 diff 内容。
   - 检查 untracked 文件名、明显大文件、构建产物、日志、临时文件、密钥、证书、token、`.env`、私钥和凭据文件。
   - 发现疑似敏感信息、明显无关改动、超大文件或多个无关主题时，停止并让用户确认。
6. 生成提交信息：
   - 读取 `references/commit-message-rules.md`。
   - 基于 staged diff 生成 1 条 Conventional Commit 信息。
   - 不要编造 diff 中不存在的行为、对象或修复结论。
7. 执行提交：
   - 若还没有 staged 改动，先按第 4 步 stage。
   - 运行 `git diff --cached --check` 做基础空白检查；除非项目规则要求，不要顺手修复无关 whitespace。
   - 运行项目已有且范围合适的最小校验；如果没有明确命令或成本过高，可以跳过但最终说明未验证。
   - 运行 `git commit -m "<subject>"`；有 body 时使用多个 `-m` 参数。
8. 同步远端：
   - 先确认 upstream；已有 upstream 时运行 `git pull --rebase`。
   - 没有 upstream 且只有一个明确 remote 时，先运行 `git fetch <remote>`。
   - fetch 后如果 `<remote>/<current-branch>` 存在，运行 `git rebase <remote>/<current-branch>`，推送时再设置 upstream。
   - fetch 后如果远端同名分支不存在，跳过 rebase，推送时创建远端分支并设置 upstream。
   - 多个 remote、没有 remote 或目标分支不清楚时停止确认。
   - pull/rebase 冲突时停止，报告冲突文件和当前状态，不要自动 abort 或强行解决。
9. 推送：
   - 运行 `git push`。
   - 没有 upstream 但目标已按第 8 步明确时，运行 `git push -u <remote> HEAD`。
10. 汇报结果：
   - 说明提交范围、commit hash、提交信息、pull/rebase 结果、push 目标和执行过的验证。
   - 若某一步停止，说明停止原因、当前 git 状态和建议下一步。

## Command Policy

- 遵循当前环境的权限和审批规则；需要写 git index、创建 commit、访问远端或推送时，按工具要求申请权限。
- 不执行 `git push --force`、`git push --force-with-lease`、`git reset --hard`、`git clean`、`git checkout --` 或删除文件，除非用户明确要求并确认影响。
- 不自动 stash 用户改动；如 pull 需要干净工作区，优先先提交目标范围，其他未提交改动存在时停止说明。
- 不把“提交并推送”变成代码评审；只做提交前必要的状态、范围和敏感信息检查。
- 不修改与本次提交无关的文件、格式、依赖或配置。
- 不因为没有自动测试命令就阻塞提交；但最终必须明确说明未验证内容。

## Edge Cases

- **只有待推送 commit，没有新改动**：跳过生成提交信息和 commit，直接执行 pull/rebase 与 push。
- **staged 与 unstaged 同时存在**：默认只提交 staged；如果 unstaged 会影响验证或 pull/rebase，停止说明。
- **多个独立主题**：建议拆分提交；用户坚持一条时按主要用户价值生成提交信息。
- **远端落后且 rebase 成功**：继续 push，并在最终结果中说明已 rebase。
- **远端冲突或认证失败**：停止，保留现场，说明失败命令和关键错误。

## Output

成功时按以下顺序简洁汇报：

1. 提交范围
2. Commit hash 与提交信息
3. Pull/rebase 结果
4. Push 目标
5. 已运行验证和未验证项

停止时按以下顺序汇报：

1. 停止原因
2. 当前仓库状态
3. 已执行到哪一步
4. 建议用户下一步怎么处理
