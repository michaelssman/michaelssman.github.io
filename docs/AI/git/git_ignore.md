# Git 忽略规则

## 本地忽略规则

`.git/info/exclude` 用于忽略当前仓库中不需要纳入版本管理的个人文件。规则只在本地当前仓库生效，不随提交或推送共享。

在仓库根目录编辑 `.git/info/exclude`，按 `.gitignore` 的语法每行写一条规则，例如：

```gitignore
/local-notes/
/debug.log
```

上面分别忽略仓库根目录的 `local-notes` 文件夹和 `debug.log` 文件。保存后自动生效，无需额外配置。可在仓库根目录检查匹配的规则及来源：

```bash
git check-ignore -v debug.log
```

## 全局忽略规则

文件路径：`~/.gitignore_global`。
