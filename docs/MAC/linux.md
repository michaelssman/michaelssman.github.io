# Mac终端命令

#### 在finder中打开当前终端进入的文件夹       open .

只要是打开文件的都是open命令，打开文件夹、打开文件都是。

#### 回到根目录 文件目录

首先要清楚几个文件目录：

```
" / "  ：根目录

" ~ " ：用户主目录的缩写。例如当前用户为hello，那么" ~ "展开来就是：/Users/hello

" . "  ：当前目录

".."   ：父目录
```
命令
然后说一下最基本的几个命令。

#### cd 跳转到某个目录

例如：
`$ cd /Users/apple/Desktop/  `
在这里有个小技巧，就是在输入目录如Desktop时，只要输入Des并按tab键，该目录名便自动补全了。
其中

- cd /   表示跳转到根目录。
- cd ~   表示跳转到用户主目录。
- cd ~apple   表示跳转到用户apple的主目录。
- cd ..   表示跳转到上级目录。（cd和..之间的空格不能漏）
#### clear 清空当前输入

如果Terminal窗口中的内容太多了，可以用clear命令将其清空。

#### ls 列出当前目录下的子目录和文件

例如：

```
$ ls  
Desktop     Downloads   Movies      Pictures    build  
Documents   Library     Music       Public      log.txt  
```

#### 文件权限

##### chmod 777 文件或目录 

示例：`chmod 777 /etc/squid` 运行命令后，squid文件夹（目录）的权限就被修改为777（可读可写可执行）。

如果是Ubuntu系统，可能需要加上sudo来执行：

`sudo chmod 777 /etc/squid`

`sudo chmod -R 777 /Library/Ruby/Gems/2.6.0/`其中`-R`会递归下面的所有文件和文件夹 并修改权限。

## 终端标识符

每个终端都有一个唯一的标识符，使用tty查看。

```
Last login: Wed Jul  6 21:07:59 on ttys001
michael@MichaeldeMacBook-Pro ~ % tty
/dev/ttys001
michael@MichaeldeMacBook-Pro ~ % 
```

