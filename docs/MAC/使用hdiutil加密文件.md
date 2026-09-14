# 使用 hdiutil 加密文件

在 macOS 上，可以把文件夹制作成加密磁盘映像（`.dmg`）。解锁后，映像会像一个磁盘一样显示在访达中。

## 创建加密磁盘映像

下面的命令把 `pmw` 文件夹中的内容装进 `pmw.dmg`，使用 AES-256 加密，并允许以后修改映像中的文件。

在 Mac 本机终端中复制命令并执行：

命令可以分成多行书写。除最后一行外，每行末尾需要加反斜杠 `\`，表示下一行仍属于这条命令：

```bash
hdiutil create \
  -srcfolder "/Users/michael/Documents/pmw" \
  -volname pmw \
  -format UDRW \
  -encryption AES-256 \
  "/Users/michael/Documents/pmw.dmg"
```

反斜杠必须紧接换行，后面不要再加空格或注释。路径用双引号包裹，可以正确处理路径中的空格。

这里的路径是示例，使用时替换为实际目录。

### 参数含义

| 参数 | 含义 |
| --- | --- |
| `hdiutil` | macOS 自带的磁盘映像管理工具，无需额外安装。 |
| `create` | 创建一个新的磁盘映像。 |
| `-srcfolder "…"` | 指定要装进映像的源文件夹，包含其中的文件和子文件夹。 |
| `-volname pmw` | 指定解锁后在访达中显示的磁盘名称为 `pmw`。 |
| `-format UDRW` | 使用可读写的磁盘映像格式，允许读取和修改里面的文件。 |
| `-encryption AES-256` | 使用 AES（高级加密标准）的 256 位密钥加密映像，通过密码解锁。 |
| 最后的 `"…/pmw.dmg"` | 指定加密磁盘映像的保存位置。 |

## 参考资料

- [Apple：在 Mac 上使用“磁盘工具”创建磁盘映像](https://support.apple.com/zh-cn/guide/disk-utility/dskutl11888/mac)
- 本机完整命令手册：在终端执行 `man hdiutil`，查看 `create`、`-srcfolder`、`-format` 和 `-encryption` 的说明。
