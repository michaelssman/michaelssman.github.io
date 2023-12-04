# Git命令

## git clone

从远程拉取代码 

1. 先在本地创建一个文件夹
2. 终端cd进入该文件夹
3. git clone 远程仓库的路径

### clone某一次commit

克隆Git仓库的特定提交，需要先克隆整个仓库，然后使用`checkout`命令切换到特定的提交。以下是步骤：

1. 克隆整个仓库：

```bash
git clone <repository-url>
```

2. 切换到你的目标仓库：

```bash
cd <repository-name>
```

3. 使用`checkout`命令切换到特定的提交。你需要知道你想要切换的提交的哈希值：

```bash
git checkout <commit-hash>
```

注意，当切换到一个特定的提交时，你会处于一个"DETACHED HEAD"状态。这意味着任何你做的改变都不会影响任何分支。如果你想要保存你的改变，你可以创建一个新的分支。

如果你想要创建一个新的分支来保存你所做的提交，你可以使用`git switch -c <new-branch-name>`命令来创建。你也可以随时使用这个命令。

如果你想撤销这个操作，你可以使用 `git switch -` 命令来回到你之前的状态。

如果你不想再看到这个提示，你可以通过设置配置变量`advice.detachedHead`为`false`来关闭它。例如，运行 `git config --global advice.detachedHead false`。

## git add .

添加到缓存。

`.`表示添加目录下所有文件到缓存库。 `.`和`add`之间有空格。

如果只添加某个文件，只需把 `.` 换成要添加的文件名即可。

## git status

命令的输出十分详细

git status --short或git status -s 格式更为紧凑的输出

## git commit -m "注释"

本地提交，将缓存中的文件Commit到git库。

## git push  

git push origin master。提交到远程的master分支。

```
git push <远程主机名> <分支名>
```

## git pull

拉取/同步远程仓库的代码到本地，更新代码。

## git tag

`git tag`：查看当前tag

`git tag 0.1.0`：打tag。

`git push --tags`：提交tag到远程。

## 分支

列出分支基本命令：`git branch`。

没有参数时，**git branch** 会列出你在本地的分支。

```
$ git branch
* master
```

此例的意思就是，我们有一个叫做 **master** 的分支，并且该分支是当前分支。

### 创建分支

执行 **git branch (branchname)** 即可。

```
$ git branch testing
$ git branch
* master
  testing
```

现在我们可以看到，有了一个新分支 **testing**。

### 切换分支checkout

git checkout (branch) 切换到我们要修改的分支。

### 合并分支merge

本地合并，解决冲突，提交，推送。

`git merge --no-ff '3.3.0'`：将3.3.0分支合并到当前分支。

#### 在本地检出、审核和合并

**第 1 步.** 获取并检出这个合并请求的功能分支：

```
git fetch origin
git checkout -b '3.3.2费用改造' 'origin/3.3.2费用改造'
```

**第 2 步.** 在本地查看更改。

**第 3 步.** 将功能分支合并到目标分支并修复任何冲突。 [我该如何修复它们？](http://192.168.1.66/help/user/project/merge_requests/conflicts#resolve-conflicts-from-the-command-line)

```
git fetch origin
git checkout 'main'
git merge --no-ff '3.3.2费用改造'
```

**第 4 步.** 将目标分支推送到 GitLab。

```
git push origin 'main'
```

**提示：** 您也可以在本地检出合并请求。[了解更多。](http://192.168.1.66/help/user/project/merge_requests/reviews/index.md#checkout-merge-requests-locally-through-the-head-ref)

## 冲突解决

选中冲突的文件，点击右键选择'冲突解决'菜单中的选项解决问题。

## 拉取代码报错

```sh
From git.nmy.cn:app/003Code/ios-scm

 \* branch      main    -> FETCH_HEAD

hint: You have divergent branches and need to specify how to reconcile them.

hint: You can do so by running one of the following commands sometime before

hint: your next pull:

hint: 

hint:  git config pull.rebase false # merge

hint:  git config pull.rebase true  # rebase

hint:  git config pull.ff only    # fast-forward only

hint: 

hint: You can replace "git config" with "git config --global" to set a default

hint: preference for all repositories. You can also pass --rebase, --no-rebase,

hint: or --ff-only on the command line to override the configured default per

hint: invocation.

fatal: Need to specify how to reconcile divergent branches.
```

这个错误信息表明你的本地分支和远程分支已经发散，它们拥有不同的提交历史，Git 需要知道如何合并这些更改。这通常发生在其他人已经推送了一些提交到远程仓库的 `main` 分支，而你的本地 `main` 分支也有一些不同的提交。Git 不确定应该如何合并这些更改，所以它需要你提供一个策略来解决这个问题。

Git 提供了几种策略来解决这个问题：

1. **合并（Merge）**：这会创建一个新的合并提交，它结合了两个分支的更改。这是最直观的方法，因为它保留了完整的历史记录，但可能会导致历史变得复杂。

   执行以下命令来设置合并为默认的拉取策略：

   ```sh
   git config pull.rebase false
   ```

2. **变基（Rebase）**：这会将你的本地更改重新应用在远程分支的最新提交之上。这会创建一个更干净的项目历史，但它会改变已经存在的提交的历史。

   执行以下命令来设置变基为默认的拉取策略：
   ```sh
   git config pull.rebase true
   ```

3. **快进（Fast-forward only）**：如果你的本地分支落后于远程分支，Git 只会更新你的本地分支以匹配远程分支。如果你的本地分支包含了远程没有的提交，Git 会拒绝操作。

   执行以下命令来设置快进为默认的拉取策略：
   ```sh
   git config pull.ff only
   ```

你可以选择一个适合你工作流程的策略，并使用上面的命令来配置它。如果你想为所有仓库设置默认策略，可以使用 `--global` 标志。例如，如果你想全局设置合并策略，可以使用：

```sh
git config --global pull.rebase false
```

如果你只想为当前操作解决这个问题，而不改变全局设置，你可以在执行 `git pull` 命令时添加相应的标志，例如：

- 对于合并：
  ```sh
  git pull --no-rebase
  ```
- 对于变基：
  ```sh
  git pull --rebase
  ```
- 对于快进：
  ```sh
  git pull --ff-only
  ```

选择一个策略后，运行相应的命令，然后你应该能够成功地拉取和合并远程分支的更改。
