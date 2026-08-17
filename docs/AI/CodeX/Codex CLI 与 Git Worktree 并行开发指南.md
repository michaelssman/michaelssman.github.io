# Codex CLI 与 Git Worktree 并行开发指南

> 适用范围：任意使用 Git 的项目
> 适用场景：使用多个独立需求分支并行开发和维护。
> 更新时间：2026-08-12

## 1. 核心结论

Git Worktree 可以让同一个 Git 仓库在多个目录中同时检出不同分支。每个目录拥有独立的工作区和暂存区，但共享提交、分支、远端等 Git 数据。

Codex CLI 与 Worktree 的推荐配合方式是：

1. 用 `git worktree` 为每个需求创建独立目录。
2. 在每个 Worktree 目录中分别启动一个 Codex CLI 会话。
3. 一个目录只开发一个需求，一个本地分支只被一个 Worktree 检出。
4. 每个需求独立提交、推送，并按团队规范分别合入 `develop`、`release` 和 `main`。

需要区分：Codex 桌面端可以自动创建和管理 Codex Worktree；Codex CLI 的常规用法是先由 Git 创建 Worktree，再从对应目录运行 `codex`。不要把桌面端的 Handoff、自动清理等能力当成 CLI 命令。

## 2. 通用示例约定

本文使用以下通用名称，不代表任何真实业务分支。实际操作前，请按自己的项目替换变量值：

```bash
REPO_DIR="/path/to/project"
WORKTREE_B_DIR="/path/to/project-requirement-b"
BRANCH_A="feature/requirement-a"
BRANCH_B="feature/requirement-b"
```

| 目录 | 本地分支 | 用途 |
| --- | --- | --- |
| `$REPO_DIR` | `$BRANCH_A` | 开发或维护需求 A |
| `$WORKTREE_B_DIR` | `$BRANCH_B` | 开发或维护需求 B |

示例场景：

- 需求 A 的分支已经在主目录检出。
- 需求 B 的本地分支已经存在，需要创建第二个 Worktree。
- 如果需求分支尚未设置上游，第一次推送时使用 `git push -u` 建立跟踪关系。

## 3. 首次创建第二个 Worktree

先在当前主目录确认没有未处理的改动，并刷新远端信息：

```bash
cd "$REPO_DIR"
git status --short --branch
git fetch origin --prune
```

为已有的需求 B 分支创建独立目录：

```bash
git worktree add "$WORKTREE_B_DIR" "$BRANCH_B"
```

验证结果：

```bash
git worktree list

git -C "$REPO_DIR" status --short --branch
git -C "$WORKTREE_B_DIR" status --short --branch
```

预期对应关系：

```text
项目主目录          -> 需求分支 A
需求 B Worktree     -> 需求分支 B
```

### 本地分支不存在时

如果以后需要从一个已有远端分支创建 Worktree，可先创建本地跟踪分支：

```bash
git fetch origin --prune
git branch --track "$BRANCH_B" "origin/$BRANCH_B"
git worktree add "$WORKTREE_B_DIR" "$BRANCH_B"
```

## 4. 创建一个全新的需求分支

新需求通常从团队指定的开发基线创建。以下示例以 `origin/develop` 为基线：

```bash
cd "$REPO_DIR"
git fetch origin --prune

NEW_BRANCH="feature/requirement-c"
NEW_WORKTREE_DIR="/path/to/project-requirement-c"

git worktree add -b "$NEW_BRANCH" "$NEW_WORKTREE_DIR" origin/develop
```

进入新目录，确认分支并创建远端上游：

```bash
cd "$NEW_WORKTREE_DIR"
git status --short --branch
git push -u origin "$NEW_BRANCH"
```

如果本地需求分支已经存在，不要再次使用 `-b` 创建同名分支。需要设置远端上游时，应在对应 Worktree 确认状态后执行：

```bash
cd "$REPO_DIR"
git status --short --branch
git push -u origin "$BRANCH_A"
```

## 5. 在两个 Worktree 中分别运行 Codex CLI

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

每个终端对应一个独立 Codex 会话。启动后可输入 `/status`，确认 Codex 当前使用的目录、模型和权限配置。

建议每个新会话的第一条任务都写清范围，例如：

```text
当前目录应为需求 B 的 Worktree，当前分支应为需求分支 B。
请先检查分支和工作区状态，只修改本需求相关文件，不要操作其他 Worktree。
```

## 6. 每天开始开发前

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

## 7. 日常提交与推送

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

## 8. 按当前团队规范流转分支

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

## 9. iOS 项目的额外注意事项

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

## 10. 查看和管理 Worktree

查看所有 Worktree：

```bash
git worktree list
git worktree list --porcelain
```

查看指定 Worktree 的状态：

```bash
git -C "$WORKTREE_B_DIR" status --short --branch
```

如果某个 Worktree 被手动移动，可修复记录：

```bash
git worktree repair
```

如果 Worktree 被锁定且确认不再被其他进程使用：

```bash
git worktree unlock "$WORKTREE_B_DIR"
```

## 11. 需求结束后的安全清理

只有在以下条件全部满足后才清理：

- 需求已按团队流程合入 `main`。
- 本地没有未提交改动。
- 本地提交已全部推送。
- 不再有 Codex、Xcode 或终端进程使用该目录。

先检查：

```bash
git -C "$WORKTREE_B_DIR" status --short --branch
git worktree list
```

再从其他 Worktree 中安全移除：

```bash
cd "$REPO_DIR"
git worktree remove "$WORKTREE_B_DIR"
git worktree prune
git worktree list
```

不要直接使用 `rm -rf` 删除 Worktree 目录，否则容易残留 Git Worktree 记录。

确认团队不再需要需求分支后，才考虑删除本地和远端分支：

```bash
git branch -d "$BRANCH_B"
git push origin --delete "$BRANCH_B"
```

## 12. 常见问题

### 提示分支已经被另一个 Worktree 使用

错误示例：

```text
fatal: 'feature/example' is already used by worktree at '<路径>'
```

Git 不允许同一个本地分支同时被两个 Worktree 检出。先执行：

```bash
git worktree list
```

然后进入已经检出该分支的目录继续工作，或先让原 Worktree 切换到其他分支，再进行后续操作。

### 提示目标目录已经存在

`git worktree add` 的目标路径应不存在或为空。不要覆盖已有项目目录；换一个明确的新目录名，并再次核对路径。

### 新 Worktree 缺少本地配置或依赖

这是正常现象：Git Worktree 不会复制未跟踪或被忽略的文件。按照项目启动文档重新生成依赖和配置；涉及密钥时不要随意复制或提交。

### 删除目录后 `git worktree list` 仍显示旧记录

先确认目录确实不再需要，然后运行：

```bash
git worktree prune
```

## 13. 最短操作清单

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

牢记三条规则：

1. 一个需求一个本地分支、一个 Worktree、一个 Codex 会话。
2. 提交前始终执行 `pwd` 和 `git status --short --branch`。
3. 两个需求分支互不合并，分别向 `develop`、`release`、`main` 提交合并请求。

## 参考资料

- [OpenAI 官方 Codex CLI 文档](https://learn.chatgpt.com/docs/codex/cli)
- [OpenAI 官方 Codex Worktree 文档](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Git 官方 Worktree 文档](https://git-scm.com/docs/git-worktree)
