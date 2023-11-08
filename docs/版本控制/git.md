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

### 切换分支

git checkout (branch) 切换到我们要修改的分支。

### 合并分支

本地合并，解决冲突，提交，推送。

`git merge --no-ff '3.3.0'`。

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



`git config pull.rebase false`
