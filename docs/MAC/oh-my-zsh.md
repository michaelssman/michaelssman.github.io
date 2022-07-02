##### 查看系统当前使用的shell

` echo $SHELL`

##### 查看shell列表，系统是否安装zsh

`cat /etc/shells`

##### 切换shell为zsh

`chsh -s /bin/zsh`

##### 安装oh-my-zsh

`sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

##### 配置文件.zshrc

文件位置：`~/.zshrc`，`vim ~/.zshrc`去编辑，`.zshrc`中可以修改主题。

## 退出vim

强制退出 不保存修改：先按`esc`然后`:q!`。

##### ZSH_DISABLE_COMPFIX 异常

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

## 更新配置

修改了`~/.zshrc`文件需要更新

`source ~/.zshrc`

##### 更新oh-my-zsh

`omz update`
