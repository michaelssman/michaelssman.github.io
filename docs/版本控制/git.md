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

3. 使用`checkout`命令切换到特定的提交。你需要知道想要切换的提交的哈希值：

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

可以查看哪些文件修改了或者冲突了。

命令的输出十分详细

git status --short或git status -s 格式更为紧凑的输出。

## git commit -m "注释"

本地提交，将缓存中的文件Commit到git库。

## git push  

git push origin master。提交到远程的master分支。

```
git push <远程主机名> <分支名>
```

## git pull

拉取/同步远程仓库的代码到本地，更新代码。

## tag

`git tag`：查看所有tag。

`git tag 0.1.0`：打tag。

`git push --tags`：提交tag到远程。

## branch

列出分支基本命令：`git branch`。

没有参数时，**git branch** 会列出你在本地的分支。

```
$ git branch
* master
```

此例的意思就是，有一个 **master** 分支，并且该分支是当前分支。

### 创建分支

执行 **git branch (branchname)** 即可。

```
$ git branch testing
$ git branch
* master
  testing
```

### checkout

git checkout (BranchName) 切换到要修改的分支。

### merge

本地合并，解决冲突，提交，推送。

`git merge --no-ff '3.3.0'`：将3.3.0分支合并到当前分支。

```
git fetch origin
//先切换到主分支
git checkout 'main'
//将3.3.2分支合并到main分支，并且会创建一个新的合并提交，即使可以进行快速前进合并。
git merge --no-ff '3.3.2'
//将目标分支推送到 GitLab。
git push origin 'main'
```

`--no-ff` 选项的作用是强制执行非快速前进（non-fast-forward）合并。

**详细解释**

- **快速前进合并（Fast-Forward Merge）**：
  - 如果目标分支（例如 `main`）直接位于源分支（例如 `feature`）的历史之前，Git 默认会执行快速前进合并。这种合并方式不会创建新的合并提交，只是简单地将目标分支的指针移动到源分支的最新提交。
- **非快速前进合并（Non-Fast-Forward Merge）**：
  - 使用 `--no-ff` 选项时，Git 会创建一个新的合并提交。这种方式会保留分支的合并历史，明确显示合并点。

**示例**

假设你有以下分支结构：

```
A---B---C (main)
     \
      D---E (feature)
```

如果你在 `main` 分支上执行 `git merge feature`：

- **默认（快速前进）**：
  
  - 结果是 `main` 分支直接移动到 `E`，提交历史变为：
    ```
    A---B---C---D---E (main)
    ```
  
- **使用 `--no-ff`**：
  
  - 结果是创建一个新的合并提交 `M`，提交历史变为：
    ```
    A---B---C---M (main)
             / \
            D---E
    ```

使用 `--no-ff` 可以更清晰地记录分支合并的历史，可以帮助更好地理解代码的演变过程。

### 当前修改创建分支

需求：将当前的修改创建一个新的分支，不在当前分支上commit和push。

通过 Git 的分支操作解决。以下是分步解决方案：

1. **暂存当前修改**：
   使用 `git stash` 将当前的修改暂存（适用于未提交的修改）。

   ```bash
   git stash  # 将未提交的修改暂存起来
   ```

2. **创建并切换到新分支**：
   创建一个新的分支并切换到该分支。

   ```bash
   git checkout -b new-feature-branch
   ```

3. **恢复暂存的修改**（如果执行了 stash）：

   ```bash
   git stash pop  # 将暂存的修改应用到新分支
   ```

4. **提交修改**：
   在新分支上提交你的修改。

   ```bash
   git add .
   git commit -m "Your commit message"
   ```

5. **推送到远程仓库**：
   将新分支推送到远程仓库。

   ```bash
   git push origin new-feature-branch
   ```

这样，你就可以在新的分支上进行提交和推送，而不会影响到 `develop` 分支。

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

## git reset

`git reset --hard efa965834671bd20a19c049b572b647fc07613c4`会回退到`efa965834671bd20a19c049b572b647fc07613c4`这次提交，后面的提交在本地没有了，但是可以拉取。

![image-20240709155256180](assets/image-20240709155256180.png)

## iOS合并代码

只处理project.pbxproj。

### 不需要解决的文件

1. pod
   - pod的冲突会很多，不处理`ProjectName/Pods/Pods.xcodeproj`，删除pod冲突的文件，重新pod解决。s
2. **用户状态文件**：
   - `AccCollege/AccCollege.xcworkspace/xcuserdata/michael.xcuserdatad/UserInterfaceState.xcuserstate`：这个文件与用户的个人设置相关，通常不需要合并。
3. **Xcode Schemes**：
   - `AccCollege/Pods/xcuserdata/michael.xcuserdatad/xcschememanagement.plist`：这个文件包含用户特定的Scheme设置，通常可以忽略。
4. **sTarget Support Files**：
   - `AccCollege/Pods/Target Support Files/Pods-AccCollege/Pods-AccCollege.debug.xcconfig`
   - `AccCollege/Pods/Target Support Files/Pods-AccCollege/Pods-AccCollege.release.xcconfig`：这些是配置文件，通常不需要解决。
