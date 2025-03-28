# Mac终端命令

## 文件目录

- `.`：当前目录
- `..`：父目录

Linux 的文件系统采用单一的树形结构，从根目录（/）开始，所有文件和目录都在其下。

### 根目录（/）

根目录（/）是 Linux 文件系统的顶层目录。所有的文件和目录都从这里开始，形成一个树形结构。根目录下的每个子目录都有其特定的功能和用途。

- **/bin**：存放基本用户命令。
- **/boot**：存放启动加载程序和内核文件。
- **/dev**：存放设备文件。
- **/etc**：存放系统配置文件。
- **/lib**：存放系统库文件和内核模块。
- **/media**：用于自动挂载的可移动设备。
- **/mnt**：用于临时挂载文件系统。
- **/sbin**：存放系统管理命令。

- **/tmp**：存放临时文件。
- **/home**：存放用户主目录。
- **/var**：存放可变数据文件。
- **/usr**：存放用户级应用程序和文件。
- **/opt**：存放附加软件包。
- **/proc**：存放系统内核和进程信息。
- **/sys**：存放系统设备和内核信息。
- **/root**：超级用户的主目录。

### /bin 目录

/bin（binary）目录包含系统启动和单用户模式下使用的基本命令。这些命令是系统正常运行所必需的，并且在单用户模式或系统紧急修复时也可以使用。

常见的命令包括：

- **ls**：列出目录内容。
- **cp**：复制文件或目录。
- **mv**：移动或重命名文件或目录。
- **rm**：删除文件或目录。
- **cat**：连接文件并显示输出。
- **echo**：显示消息。

这些命令通常是静态链接的，确保在系统启动时不依赖于其他库文件。

### /sbin 目录

/sbin（system binary）目录包含系统管理命令，这些命令通常需要超级用户权限执行。它们用于系统启动、维护和修复。

常见的命令包括：

- **ifconfig**：配置网络接口。
- **reboot**：重启系统。
- **shutdown**：关闭系统。
- **fdisk**：磁盘分区工具。
- **mkfs**：创建文件系统。

这些命令对于系统管理员来说是至关重要的，因为它们涉及到系统的核心功能和配置。

### /etc 目录

/etc 目录包含所有的系统全局配置文件。这些文件定义了系统的各种设置和参数。

常见的配置文件和目录包括：

- **/etc/passwd**：用户账号信息文件。
- **/etc/fstab**：文件系统挂载表。
- **/etc/hosts**：主机名和 IP 地址对应表。
- **/etc/hostname**：定义系统的主机名。
- **/etc/network/interfaces**：网络接口配置文件（在基于 Debian 的系统中）。

在 /etc 目录中，每个服务和应用程序通常都有自己的子目录或配置文件，例如 Apache 的配置文件在 `/etc/apache2/` 下。

### /dev 目录

/dev 目录包含设备文件，这些文件表示系统中的各种硬件设备。Linux 中的一切皆文件，包括硬件设备。

常见的设备文件包括：

- **/dev/sda**：第一个 SCSI 硬盘。
- **/dev/tty**：终端设备。
- **/dev/null**：空设备，丢弃所有写入其中的数据。
- **/dev/random**：随机数生成器。

这些设备文件允许用户和应用程序以文件的方式访问硬件设备。

### /tmp 目录

/tmp 目录用于存放临时文件。系统和应用程序在运行过程中可能会在此目录下创建临时文件。通常，系统会在每次启动时清理 /tmp 目录，以防止磁盘空间被临时文件占用过多。

/tmp 目录中的文件通常对所有用户可读写，但应注意临时文件的权限和安全性。

### /home 目录

/home 目录是用户的主目录，每个用户在 /home 目录下都有一个以其用户名命名的子目录。用户的所有个人文件和配置文件都存放在这个子目录中。例如，用户 `john` 的主目录为 `/home/john`。

常见的文件和子目录包括：

- **~/Documents**：用户的文档目录。
- **~/Downloads**：用户的下载目录。
- **~/Pictures**：用户的图片目录。
- **~/.bashrc**：Bash Shell 配置文件。
- **~/.profile**：用户的环境设置文件。

用户目录的权限设置通常是这样的，只有该用户和超级用户（root）可以访问和修改其内容。这可以保护用户的隐私和数据安全。

`~`：用户主目录的缩写。例如当前用户为hello，那么" ~ "展开来就是：/Users/hello

### /var 目录

/var 目录用于存放系统运行时产生的可变数据。不同于 /etc 目录中的配置文件，/var 中的数据是动态变化的。

常见的子目录和文件包括：

- **/var/log**：系统日志文件目录。常见的日志文件有 `/var/log/syslog`（系统日志）、`/var/log/auth.log`（认证日志）、`/var/log/kern.log`（内核日志）等。
- **/var/mail**：用户邮件存放目录。
- **/var/spool**：队列目录，用于存放打印任务、邮件队列等。
- **/var/cache**：应用程序缓存文件。
- **/var/www**：Web 服务器的根目录，存放网站文件。

/var 目录中的数据可能会迅速增长，因此需要定期清理和维护，以防止磁盘空间不足。

### /usr 目录

Unix系统资源（unix  system  resources）的简写。

/usr 目录用于存放用户级应用程序和文件。这是一个非常重要的目录，包含了大量的二进制文件、库文件、文档和其他资源。

常见的子目录包括：

- **/usr/bin**：用户级命令的二进制文件。常见的命令有 `gcc`（GNU 编译器）、`perl`（Perl 解释器）等。
- **/usr/sbin**：系统管理命令的二进制文件。与 /sbin 类似，但这些命令不是启动时必须的。
- **/usr/lib**：库文件目录，存放应用程序和系统所需的共享库。
- **/usr/share**：共享数据目录，存放不特定于某个用户或系统的共享数据，如文档、图标、声音等。
- **/usr/local**：本地安装的软件和文件。用户可以在不影响系统其他部分的情况下安装和管理软件。

/usr 目录中的内容通常由系统包管理器管理，如 apt、yum、Homebrew等。

### /opt 目录

/opt 目录用于安装附加软件包。通常，第三方软件或自定义应用程序会安装在此目录下。每个软件通常会在 /opt 下有一个独立的子目录，例如 `/opt/software`。这种方式可以避免与系统的其他部分产生冲突，并便于管理和卸载。

### /mnt 目录

/mnt 目录用于临时挂载文件系统。系统管理员可以将外部存储设备（如 USB 驱动器、网络文件系统等）挂载到 /mnt 下的某个子目录中。例如，可以使用 `mount /dev/sdb1 /mnt/usb` 将一个 USB 驱动器挂载到 `/mnt/usb`。

### /media 目录

/media 目录用于自动挂载的可移动设备，如光盘、U 盘等。当这些设备插入时，系统会自动将其挂载到 /media 下的一个子目录中。例如，插入一个 U 盘后，系统可能会在 `/media/user/USB` 下自动创建一个目录并挂载该设备。

### /boot 目录

/boot 目录包含启动加载程序和内核文件。系统启动时，启动加载程序（如 GRUB）会从这里加载内核和其他必要文件。

常见文件包括：

- **vmlinuz**：压缩的 Linux 内核镜像文件。
- **initrd.img**：初始 RAM 盘，用于启动时加载必要的驱动程序和文件系统。
- **grub**：GRUB 启动加载程序的配置文件和模块。

/boot 目录中的文件对于系统启动至关重要，因此应谨慎修改。

### /lib 目录

/lib 目录包含系统库文件和内核模块。系统启动时，许多关键程序依赖于这些库文件。常见的库文件包括 C 标准库（libc.so）、动态链接器（ld-linux.so）等。内核模块（如文件系统驱动、硬件驱动）通常位于 `/lib/modules` 目录中。

### /proc 目录

/proc 目录是一个虚拟文件系统，包含系统内核和进程信息。这个目录中的内容并不实际存在于磁盘上，而是由内核在运行时动态生成的。/proc 目录提供了一种方便的方式来访问系统信息和进程数据。

常见的文件和目录包括：

- **/proc/cpuinfo**：显示 CPU 的信息，包括型号、速度和核心数。
- **/proc/meminfo**：显示内存使用情况，包括总内存、可用内存和缓存。
- **/proc/uptime**：显示系统的运行时间和空闲时间。
- **/proc/[pid]/**：每个运行中的进程都有一个以其 PID（进程标识符）命名的子目录，包含该进程的详细信息，如状态、内存映射、打开的文件等。

/proc 目录中的信息对于系统管理员和开发者来说非常重要，因为它提供了对系统运行状态的实时监控和调试工具。

### /sys 目录

/sys 目录是另一个虚拟文件系统，提供系统设备和内核信息。与 /proc 类似，/sys 目录中的内容也是由内核在运行时动态生成的。/sys 目录主要用于提供内核与用户空间之间的接口，允许用户查看和配置硬件设备。

常见的文件和目录包括：

- **/sys/class/**：分类显示不同类型的设备，如网络设备（/sys/class/net）、块设备（/sys/class/block）等。
- **/sys/devices/**：显示系统中的所有设备，以设备树的形式组织。
- **/sys/module/**：显示已加载的内核模块及其参数。

通过 /sys 目录，用户和管理员可以方便地管理和配置系统硬件，进行性能调优和故障排除。

### /root 目录

/root 目录是超级用户（root）的主目录。与普通用户的主目录位于 /home 下不同，root 用户的主目录直接位于根目录下。这是因为 root 用户需要在单用户模式下进行系统维护和修复，/root 目录可以在没有挂载其他文件系统的情况下访问。常见的文件和目录包括：

- **/root/.bashrc**：root 用户的 Bash Shell 配置文件。
- **/root/.profile**：root 用户的环境设置文件。

root 用户拥有系统的最高权限，因此 /root 目录中的文件和配置通常只有 root 用户本身可以访问和修改。

### 符号链接（Symbolic Link）

符号链接是一种特殊的文件，它指向另一个文件或目录。符号链接可以简化文件路径访问和管理。创建符号链接的命令是 `ln -s`，例如：

```
ln -s /path/to/target /path/to/link
```

符号链接在文件目录结构中具有重要作用，尤其是在需要在多个位置访问同一文件或目录时。符号链接可以跨文件系统边界，并且可以指向目录或文件。

### /run 目录

/run 目录是一个临时文件系统，用于存放系统运行时的状态文件和进程信息。它是在系统启动时动态创建的，并且其内容在每次启动时都会被清空。常见的文件和目录包括：

- **/run/lock**：用于锁文件，防止多个进程同时访问同一个资源。
- **/run/user/**：用于用户相关的运行时数据，每个用户都有一个以其 UID 命名的子目录。

/run 目录中的文件和目录通常由系统服务和守护进程使用，提供了一种轻量级的进程间通信方式。

### /srv 目录

/srv 目录用于存放服务相关的数据。srv 是 "service" 的缩写，表示该目录用于存放系统提供的各种服务的数据。例如，Web 服务器的文件可以存放在 /srv/www 下，FTP 服务器的文件可以存放在 /srv/ftp 下。/srv 目录结构可以根据具体服务的需求进行自定义。

### /lost+found 目录

/lost+found 目录存在于每个使用 ext 文件系统（如 ext2、ext3、ext4）的文件系统根目录下。它用于存放文件系统在崩溃或损坏后恢复的文件碎片。当文件系统进行 fsck（文件系统一致性检查）时，找回的孤立文件会被放置在 /lost+found 目录中。系统管理员可以在检查后决定如何处理这些文件。

## 终端命令

### open

在finder中打开当前终端进入的文件夹`open .`

open命令：打开文件夹、打开文件。

### cd 

跳转到某个目录

例如：
`$ cd /Users/apple/Desktop/  `
在这里有个小技巧，就是在输入目录如Desktop时，只要输入Des并按tab键，该目录名便自动补全了。

- `cd /`   表示跳转到根目录。
- `cd ~`   表示跳转到用户主目录。
- `cd ~apple`   表示跳转到用户apple的主目录。
- `cd ..`   表示跳转到上级目录。

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

`sudo chmod -R 777 /Library/Ruby/Gems/2.6.0/`其中`-R`会递归下面的所有文件和文件夹并修改权限。

#### 执行权限

```sh
chmod +x create_xcframework.sh
```

### man

`man`（manual）是用来查看用户手册的命令。

在终端或命令行界面输入`man`后跟着一个命令或程序的名称时，它会显示那个命令或程序的手册页（man page）。手册页通常包含了如何使用命令、它的选项、以及一些例子和详细的描述。

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

打开.zshrc文件`open ~/.zshrc`，如果不存在则创建.zshrc文件`touch ~/.zshrc`，`vim ~/.zshrc`去编辑，`.zshrc`中可以修改主题。

### 退出vim

强制退出 不保存修改：先按`esc`然后`:q!`。

### 更新配置

修改了`~/.zshrc`文件需要更新

```shell
source ~/.zshrc
```

```sh
source ~/.zprofile
```

## 环境变量

家目录下创建一个文件夹，可以是隐藏的。里面放自己的脚本和工具。

用的时候需要配置环境变量。

`vi ~/.zshrc`

```shell
# gem
#export GEM_HOME="$HOME/.gem"
#export PATH="$GEM_HOME/bin:$PATH"

# Flutter镜像配置
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
# Flutter 配置
export FLUTTER=/opt/flutter/bin
# 写入环境变量，多个环境变量配置中间使用:隔开
export PATH=$FLUTTER:$PATH

# 配置Maven
export M2_HOME=/usr/local/apache-maven-3.8.8
export PATH=$PATH:$M2_HOME/bin

# 配置JDK
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
```

## git配置

家目录下有一个隐藏的.ssh目录，里面创建公钥.pub和私钥。

known_hosts里面记录了公钥和私钥。

1. Settings
2. Developer settings，创建access token
3. 保存环境变量里，终端使用的时候直接使用环境变量里的。

ip addr：查看ip地址
