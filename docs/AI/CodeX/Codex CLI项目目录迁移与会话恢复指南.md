# Codex CLI 项目目录迁移与会话恢复指南

## 结论

移动项目文件夹不会删除 Codex CLI 会话。会话保存在：

```text
/Users/michael/.codex/sessions
```

移动后看不到旧会话，是因为 `codex resume` 默认按当前工作目录过滤。使用 `codex resume --all` 即可查找旧目录下的会话，再通过 `-C/--cd` 指定新的项目目录。

适用环境：`codex-cli 0.149.1`。

## 目标目录

将以下两个项目：

```text
/Users/michael/Desktop/yuncai/ios-cbc
/Users/michael/Desktop/yuncai/bill-basic-fields
```

移动到：

```text
/Users/michael/Desktop/yuncai/cbc
```

移动后的路径为：

```text
/Users/michael/Desktop/yuncai/cbc/ios-cbc
/Users/michael/Desktop/yuncai/cbc/bill-basic-fields
```

## 操作步骤

### 1. 退出正在运行的 Codex CLI

移动前先退出以上两个项目中正在运行的 Codex CLI，避免当前进程继续持有旧工作目录。

### 2. 可选：备份 Codex 会话

```bash
cp -a '/Users/michael/.codex/sessions' \
      '/Users/michael/Desktop/codex-sessions-backup-20260902'
```

项目移动本身不会修改会话目录，这一步仅用于额外保险。

### 3. 移动项目文件夹

```bash
mv '/Users/michael/Desktop/yuncai/ios-cbc' \
   '/Users/michael/Desktop/yuncai/cbc/'

mv '/Users/michael/Desktop/yuncai/bill-basic-fields' \
   '/Users/michael/Desktop/yuncai/cbc/'
```

### 4. 在新目录恢复旧会话

恢复 `ios-cbc` 会话：

```bash
codex resume --all \
  -C '/Users/michael/Desktop/yuncai/cbc/ios-cbc'
```

恢复 `bill-basic-fields` 会话：

```bash
codex resume --all \
  -C '/Users/michael/Desktop/yuncai/cbc/bill-basic-fields'
```

参数说明：

- `--all`：取消当前目录过滤，显示其他工作目录中的历史会话，并展示 CWD 列。
- `-C <目录>`：强制恢复后的 Codex 会话使用指定的新项目目录。

也可以先进入新目录，再打开全部会话：

```bash
cd '/Users/michael/Desktop/yuncai/cbc/ios-cbc'
codex resume --all
```

选择旧会话后，如果 Codex 询问使用“当前目录”还是“会话原目录”，应选择当前目录。

## 永久配置

在 `/Users/michael/.codex/config.toml` 已有的 `[tui]` 配置段中增加：

```toml
[tui]
terminal_title = ["activity", "thread-title", "git-branch"]
resume_cwd = "current"
```

这样恢复旧会话时，如果当前目录与会话保存的原目录不同，Codex 会默认使用当前目录。

注意：`resume_cwd = "current"` 只控制恢复后使用哪个目录，不会取消会话列表的工作目录过滤。旧会话首次查找仍应使用：

```bash
codex resume --all
```

## 注意事项

- 不要删除 `/Users/michael/.codex/sessions`。
- 不要批量替换会话 JSONL 文件中的旧目录路径，会话还包含索引和上下文元数据，直接修改可能破坏记录。
- 不建议使用 `codex resume --last --all` 查找指定项目，因为它可能恢复其他项目的全局最新会话。
- 如已知会话 UUID，可直接指定会话并绑定新目录：

```bash
codex resume -C '/新的项目目录' '<SESSION_ID>'
```

## 官方说明

OpenAI 官方文档说明：`codex resume --all` 可以显示当前目录之外的会话；当当前目录与会话保存目录不一致时，可以选择使用当前目录或原会话目录，显式指定的 `-C/--cd` 优先级最高。

- [Codex CLI `resume` 官方说明](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
