# 将已有 Skills 目录关联到 GitHub 仓库

## 1. 关联现有目录与远程仓库

在本机终端依次执行，每一步成功后再执行下一步：

```bash
cd "~/.codex/skills"

git init -b main
git remote add origin git@github.com:michaelssman/PWAgent.git
git fetch origin
git switch --no-overwrite-ignore -c main --track origin/main

git status --short
```

| 命令或参数 | 作用 |
| --- | --- |
| `cd "…"` | 进入已有 Skills 目录。 |
| `git init -b main` | 创建本地 `.git` 目录，设置初始分支名为 `main`，不会自动提交现有文件。 |
| `git remote add origin …` | 将 GitHub 仓库地址登记为名叫 `origin` 的远程仓库。 |
| `git fetch origin` | 下载远程提交历史并更新远程跟踪分支，不会直接改写工作目录中的技能文件。 |
| `git switch … -c main --track origin/main` | 基于 `origin/main` 的历史建立并切换到本地 `main`，同时设置上游分支。远程已有的文件会检出到本地。 |
| `--no-overwrite-ignore` | 即使已有文件被忽略规则匹配，也不允许切换分支时覆盖发生冲突的文件。 |
| `git status --short` | 查看哪些文件尚未跟踪或存在修改。 |

`git init -b main` 之后尚未产生提交，所以这里可以通过 `git switch -c main` 基于远程历史建立同名分支。不要在这两个步骤之间先创建本地提交，否则就不再符合本流程的初始条件。

现有、不与远程文件冲突的 Skills 会保留。若提示文件将被覆盖，命令会停止；先备份并核对冲突文件，再决定如何合并，不要通过添加 `-f` 强行覆盖。

## 2. 忽略内置技能和临时文件

编辑 `.gitignore`；若文件不存在则新建，若已经存在则保留原有规则并追加：

```gitignore
/.system/
/codex-primary-runtime/
.DS_Store
```

- `/.system/`：忽略目录根部的内置系统技能。
- `/codex-primary-runtime/`：忽略目录根部的运行时目录。
- `.DS_Store`：忽略 macOS 生成的目录显示信息文件。

## 3. 检查是否接入成功

在 Skills 目录中执行：

```bash
git remote -v
git branch -vv
git status --short
```

检查结果应符合以下条件：

1. `origin` 指向自己的 GitHub 仓库地址。
2. 当前分支是 `main`，上游分支是 `origin/main`。
3. 内置技能和 `.DS_Store` 不再出现在待添加列表中；尚未被远程仓库收录的自定义技能通常显示为 `??`，表示未跟踪。
