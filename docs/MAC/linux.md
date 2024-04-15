# Mac终端命令

## 文件目录

- `/`：根目录
- `~`：用户主目录的缩写。例如当前用户为hello，那么" ~ "展开来就是：/Users/hello
- `.`：当前目录
- `..`：父目录

### open

在finder中打开当前终端进入的文件夹`open .`

open命令：打开文件夹、打开文件。

### cd 

跳转到某个目录

例如：
`$ cd /Users/apple/Desktop/  `
在这里有个小技巧，就是在输入目录如Desktop时，只要输入Des并按tab键，该目录名便自动补全了。

- cd /   表示跳转到根目录。
- cd ~   表示跳转到用户主目录。
- cd ~apple   表示跳转到用户apple的主目录。
- cd ..   表示跳转到上级目录。

### mkdir

创建文件夹

### clear

清空当前输入，如果Terminal窗口中的内容太多，可以用clear命令将其清空。

### ls 

列出当前目录下的子目录和文件

### chmod

文件权限：chmod 777 文件或目录 

示例：`chmod 777 /etc/squid` 运行命令后，squid文件夹（目录）的权限就被修改为777（可读可写可执行）。

如果是Ubuntu系统，可能需要加上sudo来执行：

`sudo chmod 777 /etc/squid`

`sudo chmod -R 777 /Library/Ruby/Gems/2.6.0/`其中`-R`会递归下面的所有文件和文件夹 并修改权限。

### man

在Unix-like系统中，`man`命令是用来查看用户手册的命令，它的名字来自于“manual”的缩写。当你在终端或命令行界面输入`man`后跟着一个命令或程序的名称时，它会显示那个命令或程序的手册页（man page）。手册页通常包含了如何使用命令、它的选项、以及一些例子和详细的描述。

## 终端标识符

每个终端都有一个唯一的标识符，使用tty查看。

```
Last login: Wed Jul  6 21:07:59 on ttys001
michael@MichaeldeMacBook-Pro ~ % tty
/dev/ttys001
michael@MichaeldeMacBook-Pro ~ % 
```

## shell

### 查看系统当前使用的shell

` echo $SHELL`

### 查看shell列表，系统是否安装zsh

`cat /etc/shells`

### 切换shell为zsh

`chsh -s /bin/zsh`

## 配置文件.zshrc

文件位置：`~/.zshrc`，`vim ~/.zshrc`去编辑，`.zshrc`中可以修改主题。

### 退出vim

强制退出 不保存修改：先按`esc`然后`:q!`。

### 更新配置

修改了`~/.zshrc`文件需要更新

`source ~/.zshrc`

## 安装oh-my-zsh

`sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

### ZSH_DISABLE_COMPFIX 异常

```
[oh-my-zsh] Insecure completion-dependent directories detected:
drwxrwxr-x  3 fn-116  admin  96 11  1 17:41 /usr/local/share/zsh
drwxrwxr-x  2 fn-116  admin  64 11  1 17:41 /usr/local/share/zsh/site-functions

[oh-my-zsh] For safety, we will not load completions from these directories until
[oh-my-zsh] you fix their permissions and ownership and restart zsh.
[oh-my-zsh] See the above list for directories with group or other writability.

[oh-my-zsh] To fix your permissions you can do so by disabling
[oh-my-zsh] the write permission of "group" and "others" and making sure that the
[oh-my-zsh] owner of these directories is either root or your current user.
[oh-my-zsh] The following command may help:
[oh-my-zsh]     compaudit | xargs chmod g-w,o-w

[oh-my-zsh] If the above didn't help or you want to skip the verification of
[oh-my-zsh] insecure directories you can set the variable ZSH_DISABLE_COMPFIX to
[oh-my-zsh] "true" before oh-my-zsh is sourced in your zshrc file.
```

处理方法

`vim .zshrc`点击`i`进入编辑，在顶部加上`ZSH_DISABLE_COMPFIX=true`。

### 更新oh-my-zsh

`omz update`

## 环境变量

家目录下创建一个文件夹，可以是隐藏的。里面放自己的脚本和工具。

用的时候需要配置环境变量。

打开.zshrc文件`open ~/.zshrc`

如果不存在则创建.zshrc文件`touch ~/.zshrc`

`vi ~/.zshrc`

```shell
# Flutter镜像配置
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
# Flutter 配置
export FLUTTER=/opt/flutter/bin

# 写入环境变量，多个环境变量配置中间使用:隔开
export PATH=$FLUTTER:$PATH
```

## git配置

家目录下有一个隐藏的.ssh目录，里面创建公钥.pub和私钥。

known_hosts里面记录了公钥和私钥。

1. Settings
2. Developer settings，创建access token
3. 保存环境变量里，终端使用的时候直接使用环境变量里的。

