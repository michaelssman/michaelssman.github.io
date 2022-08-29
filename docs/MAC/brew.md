安装[Homebrew](https://brew.sh/)

在gitee上搜索brew

`/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"`

## brew update  

##### 简单使用

- brew list 本地软件库列表
- brew search google 查找软件（google替换为要查找的关键字）
- brew -v 查看brew版本
- brew update更新brew版本

1. 安装软件：brew install 软件名，例：brew install node
3. 卸载软件：brew uninstall 软件名，例：brew uninstall wget
3. 更新具体软件：brew upgrade 软件名 ，例：brew upgrade git
4. 查看软件信息：brew info／home 软件名 ，例：brew info git ／ brew home git
    PS：brew home指令是用浏览器打开官方网页查看软件信息
8. 查看哪些已安装的程序需要更新： brew outdated
9. 显示包依赖：brew reps
10. 显示帮助：brew help

使用`brew help`命令，可以看到所有的使用：
![image.png](https://upload-images.jianshu.io/upload_images/1892989-d52d0427144dde5d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

