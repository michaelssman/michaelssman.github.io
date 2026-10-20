# Codex CLI 与 Git Worktree 并行开发指南

## 1. 核心结论

Git Worktree 可以让同一个 Git 仓库在多个目录中同时检出不同分支。每个目录拥有独立的工作区和暂存区，但共享提交、分支、远端等 Git 数据。

## 2. 远端已存在需求分支

**本地分支不存在时，先创建本地跟踪分支：**

```bash
git branch --track "$BRANCH_B" "origin/$BRANCH_B"
```

为已有的需求 B 分支创建独立目录：

```bash
git worktree add "$WORKTREE_B_DIR" "$BRANCH_B"
```

验证结果：

```bash
git worktree list
```

## 3. 创建全新的需求分支

新需求通常从团队指定的开发基线创建。以下示例以 `origin/develop` 为基线：

```bash
git worktree add -b "$NEW_BRANCH" "$NEW_WORKTREE_DIR" origin/develop
```

## 4. 在两个 Worktree 中分别运行 Codex CLI

### 方式一：进入目录后启动

终端 A，开发需求 A：

```bash
cd "$REPO_DIR"
codex
```

终端 B，开发或维护需求 B：

```bash
cd "$WORKTREE_B_DIR"
codex
```

### 方式二：使用 `-C` 指定工作目录

```bash
codex -C "$REPO_DIR"
```

```bash
codex -C "$WORKTREE_B_DIR"
```

每个终端对应一个独立 Codex 会话。

建议每个新会话的第一条任务都写清范围，例如：

```text
当前目录应为需求 B 的 Worktree，当前分支应为需求分支 B。
请先检查分支和工作区状态，只修改本需求相关文件，不要操作其他 Worktree。
```

## 5. 每天开始开发前

在各自 Worktree 中分别检查：

```bash
pwd
git status --short --branch
git branch --show-current
git log -1 --oneline --decorate
```

刷新远端信息只需在任意一个 Worktree 中执行一次，因为同一仓库的 Worktree 共享 Git 元数据：

```bash
git fetch origin --prune
```

如果当前分支已经设置上游，并且工作区干净，可按团队习惯同步当前远端需求分支：

```bash
git pull --rebase
```

不要在未确认影响范围时，把一个需求分支合并到另一个需求分支。是否把最新 `develop` 同步进需求分支，也应先确认团队约定和最终合入 `release`、`main` 时是否会携带无关提交。

## 6. 日常提交与推送

所有命令都必须在对应需求的 Worktree 中执行：

```bash
git status --short --branch
git diff
git add <本需求相关文件>
git diff --cached --check
git commit -m "feat(<模块>): <中文描述>"
git pull --rebase
git push
```

注意事项：

- 提交前先看目录和分支，避免在错误的 Worktree 中提交。
- 两个 Worktree 的未提交改动和暂存区彼此独立。
- 分支、提交、标签和远端信息由所有 Worktree 共享。
- `git stash` 也由同一仓库共享；如果必须使用，应写清名称，例如 `git stash push -m "需求 B 临时修改"`。
- 不要让两个 Codex 会话同时修改同一个分支。
- 不要把与需求无关的 Xcode 用户配置或本地环境文件加入提交。

## 7. 按当前团队规范流转分支

两个需求分别执行同一套流程，互不合并：

```text
需求开发完成：feature/<需求> -> develop
准备上线：    feature/<需求> -> release
上线完成：    feature/<需求> -> main
```

建议通过合并请求分别操作，并在每次合并前确认差异范围：

```bash
git fetch origin --prune
git log --oneline origin/develop..feature/<需求>
git diff --stat origin/develop...feature/<需求>
```

切换比较目标时，把 `origin/develop` 替换为 `origin/release` 或 `origin/main`。

需求分支在合入 `main` 之前应继续保留。某个需求后续需要修复时，直接进入对应 Worktree 继续提交；不要在另一个需求的 Worktree 中修改。

## 8. iOS 项目的额外注意事项

新 Worktree 只会检出 Git 跟踪的文件。被 `.gitignore` 忽略的本地配置、依赖或生成文件不会自动出现在新目录，需要按项目既有方式重新生成或谨慎复制。

如果两个 Worktree 同时执行 Xcode 构建或测试，建议给它们使用不同的 Derived Data 路径，避免构建缓存互相影响：

```bash
xcodebuild <其他参数> \
  -derivedDataPath /tmp/project-requirement-a-derived-data
```

```bash
xcodebuild <其他参数> \
  -derivedDataPath /tmp/project-requirement-b-derived-data
```

同一时刻只在一个 Worktree 中执行 CocoaPods、工程文件生成或其他会改写共享外部状态的命令；执行后检查实际变更范围。

## 9. 查看和管理 Worktree

查看所有 Worktree：

```bash
git worktree list
git worktree list --porcelain
```

如果某个 Worktree 被手动移动，可修复记录：

```bash
git worktree repair
```

如果 Worktree 被锁定且确认不再被其他进程使用：

```bash
git worktree unlock "$WORKTREE_B_DIR"
```

## 10. 需求结束后的安全清理

从其他 Worktree 中安全移除：

```bash
git worktree remove "$WORKTREE_B_DIR"
git worktree prune
git worktree list
```

确认团队不再需要需求分支后，才考虑删除本地和远端分支：

```bash
git branch -d "$BRANCH_B"
git push origin --delete "$BRANCH_B"
```

## 11. 最短操作清单

首次为已有的需求 B 分支创建 Worktree：

```bash
REPO_DIR="/path/to/project"
WORKTREE_B_DIR="/path/to/project-requirement-b"
BRANCH_B="feature/requirement-b"

cd "$REPO_DIR"
git fetch origin --prune
git worktree add "$WORKTREE_B_DIR" "$BRANCH_B"
git worktree list
```

分别启动 Codex CLI：

```bash
codex -C "$REPO_DIR"
codex -C "$WORKTREE_B_DIR"
```

牢记规则：

提交前始终执行 `pwd` 和 `git status --short --branch`。
