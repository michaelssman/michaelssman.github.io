# OpenClaw

## 自动记忆保存Pre-Compaction

当 Session 接近 token 限制时（默认阈值约 4000 tokens），OpenClaw 触发一个 silent agentic turn：

1. 检测阈值

   Session token 用量接近上限，触发 Pre-Compaction 流程

2. 静默保存

   Agent 在后台执行一个隐藏 turn，将重要记忆写入MEMORY.md和 Daily Log

3. 压缩上下文

   旧消息被压缩或截断，释放 token 空间。用户看不到这个过程（返回NO_REPLY）

> 为什么这很重要？这个机制保证了即使对话极长，关键信息也不会随着上下文窗口的滑动而丢失。ClaudeCode 等工具的会话结束后上下文就消失了，而 OpenClaw 通过文件系统实现了真正的持久记忆。