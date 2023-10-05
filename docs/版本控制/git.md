# Git命令

## git clone

从远程拉取代码 

1. 先在本地创建一个文件夹
2. 终端cd进入该文件夹
3. git clone 远程仓库的路径

## git add .

添加到缓存。

`.`表示添加目录下所有文件到缓存库。 `.`和`add`之间有空格。

如果只添加某个文件，只需把 `.` 换成要添加的文件名即可。

## git status

命令的输出十分详细

git status --short或git status -s 格式更为紧凑的输出

## git commit -m "注释"

本地提交。将缓存中的文件Commit到git库

git commit -m "添加你的注释,一般是一些更改信息"

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

## 冲突解决

选中冲突的文件，点击右键选择'冲突解决'菜单中的选项解决问题。





`git config pull.rebase false`
