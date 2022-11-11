# Mac终端命令

### 文件目录

```
" / "  ：根目录

" ~ " ：用户主目录的缩写。例如当前用户为hello，那么" ~ "展开来就是：/Users/hello

" . "  ：当前目录

".."   ：父目录
```

### open

在finder中打开当前终端进入的文件夹`open .`

open命令：打开文件夹、打开文件。

### cd 

跳转到某个目录

例如：
`$ cd /Users/apple/Desktop/  `
在这里有个小技巧，就是在输入目录如Desktop时，只要输入Des并按tab键，该目录名便自动补全了。
其中

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

### 终端标识符

每个终端都有一个唯一的标识符，使用tty查看。

```
Last login: Wed Jul  6 21:07:59 on ttys001
michael@MichaeldeMacBook-Pro ~ % tty
/dev/ttys001
michael@MichaeldeMacBook-Pro ~ % 
```

