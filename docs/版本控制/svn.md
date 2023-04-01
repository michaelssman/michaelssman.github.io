# SVN

## import项目，把项目提交到svn

1. 进入到桌面文件夹

   ```
   cd Desktop/
   ```

2. import项目

   ```
   svn import ExcellentArtProject/ svn://123.57.53.21/yyt/ios -m ""
   ```

3. Authentication

   身份验证，验证电脑密码，然后验证SVN远程用户名和密码。

## Mac批量删除 .svn 文件

如果项目是非export导出的，那么项目中会有很多的.svn文件。

打开terminal终端，cd进入到.svn所在的文件夹。

输入：`find . -type d -name ".svn"|xargs rm -rf`

回车，这个命令会递归的删除目录下所有.svn的文件夹。

.svn 直接删除也可以

#### svn is already under version control问题解决

svn ci 时出现 xx is already under version control，然后无法提交，出现这个问题的原因是你所提交的文件或目录是其他SVN的东西，即下面有.svn的目录，需要先把它们删除才能提交。
