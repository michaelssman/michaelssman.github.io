# git clone

从远程拉取代码 

1. 先在本地创建一个文件夹
2. 终端cd进入该文件夹
3. git clone 远程仓库的路径

# git add .

git add . (注意后面有个点)表示添加目录下所有文件到缓存库,如果只添加某个文件,只需把 . 换成你要添加的文件名即可;

 `.`这个点和`add`之间有空格。

# git status

命令的输出十分详细

git status --short或git status -s 格式更为紧凑的输出

# git commit 

应该是本地提交

将缓存中的文件Commit到git库

git commit -m "添加你的注释,一般是一些更改信息"

# git push  

git push origin master

```
git push <远程主机名> <本地分支名>
```

# git pull

拉取/同步远程仓库的代码到本地，更新代码。

# git tag

查看当前tag

git tag 0.1.0。打tag。

git push --tags。提交tag。

