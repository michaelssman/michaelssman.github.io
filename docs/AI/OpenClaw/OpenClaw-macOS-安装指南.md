# OpenClaw macOS 安装指南

## 1. 系统环境检查

安装前建议先确认系统、Node.js、npm、Git 和 Homebrew 都可用。

可用下面的命令检查环境：

```bash
node --version
npm --version
sw_vers
uname -m
git --version
brew --version
```

---

## 2. 安装 OpenClaw

### 推荐方式：官方一键安装脚本

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

安装脚本会自动检测 macOS 环境，并通过 npm 安装 OpenClaw。记录中的成功安装版本为：

| 项目 | 详情 |
|------|------|
| 安装方式 | npm 全局安装 |
| 安装版本 | OpenClaw 2026.5.27 (commit: 27ae826) |
| 可执行文件 | `/opt/homebrew/bin/openclaw` |
| npm 包位置 | `/opt/homebrew/lib/node_modules/openclaw` |
| 安装大小 | 约 784 MB |
| 安装状态 | 成功 |

### 备用方式：npm 直接安装

如果不使用官方脚本，也可以直接通过 npm 安装：

```bash
npm install -g openclaw@latest
```

---

## 3. 安装后验证

```bash
openclaw --version
which openclaw
npm list -g openclaw
```

示例输出：

```text
OpenClaw 2026.5.27 (27ae826)
/opt/homebrew/bin/openclaw
/opt/homebrew/lib
└── openclaw@2026.5.27
```

如果 `openclaw` 可以直接执行，说明 Homebrew Node.js 的全局 bin 目录 `/opt/homebrew/bin` 已在 `PATH` 中。

---

## 4. 初始化配置

使用 DeepSeek API Key 完成非交互式初始化，并安装 Gateway 后台服务：

```bash
openclaw onboard \
  --accept-risk \
  --non-interactive \
  --auth-choice deepseek-api-key \
  --deepseek-api-key "sk-***" \
  --install-daemon \
  --flow quickstart \
  --gateway-bind loopback
```

如果想跳过渠道和 UI 初始化，也可以使用记录中的另一组参数：

```bash
openclaw onboard \
  --accept-risk \
  --non-interactive \
  --auth-choice deepseek-api-key \
  --deepseek-api-key "sk-***" \
  --install-daemon \
  --skip-channels \
  --skip-ui
```

初始化完成后会生成或更新：

| 项目 | 路径或值 |
|------|----------|
| AI 提供商 | DeepSeek |
| 默认模型 | `deepseek-v4-flash` |
| 主配置文件 | `~/.openclaw/openclaw.json` |
| 工作区 | `~/.openclaw/workspace` |
| 会话目录 | `~/.openclaw/agents/main/sessions` |
| Gateway 服务 | `~/Library/LaunchAgents/ai.openclaw.gateway.plist` |
| Gateway 日志 | `~/Library/Logs/openclaw/gateway.log` |

---

## 5. Gateway 和运行状态验证

查看整体状态：

```bash
openclaw status
```

记录中的状态示例：

```text
OS:        macos 26.5 (arm64) · node 25.6.1
Dashboard: http://127.0.0.1:18789/
Gateway:   local · ws://127.0.0.1:18789 (loopback) · reachable · auth token
Service:   LaunchAgent installed · loaded · running
Agent:     1 · main · default
Model:     deepseek-v4-flash (1000k ctx)
Sessions:  0 active
Channels:  No channels configured
```

也可以进一步检查 Gateway 和健康状态：

```bash
openclaw gateway status
openclaw health
```

Gateway 默认配置：

| 配置项 | 值 |
|--------|-----|
| 端口 | 18789 |
| 模式 | local |
| 绑定 | loopback (127.0.0.1) |
| 认证 | token |
| Tailscale | off |
| Dashboard | `http://127.0.0.1:18789/` |

---

## 6. 目录结构

```text
~/.openclaw/
├── openclaw.json
├── workspace/
├── plugins/
├── credentials/
└── agents/
    └── main/
        └── sessions/
```

常见路径说明：

| 路径 | 说明 |
|------|------|
| `/opt/homebrew/bin/openclaw` | OpenClaw 可执行文件 |
| `/opt/homebrew/lib/node_modules/openclaw` | npm 全局包目录 |
| `~/.openclaw/openclaw.json` | 主配置文件 |
| `~/.openclaw/workspace/` | Agent 工作区 |
| `~/.openclaw/plugins/` | 技能插件 |
| `~/.openclaw/credentials/` | API Key 等凭证，加密存储 |
| `~/.openclaw/agents/main/sessions/` | main agent 会话存储 |
| `~/Library/LaunchAgents/ai.openclaw.gateway.plist` | macOS LaunchAgent 服务文件 |
| `~/Library/Logs/openclaw/gateway.log` | Gateway 日志 |

---

## 7. 常用命令速查

| 命令 | 说明 |
|------|------|
| `openclaw dashboard` | 打开 Web 控制台：`http://127.0.0.1:18789/` |
| `openclaw status` | 查看运行状态 |
| `openclaw status --deep` | 深度状态检查 |
| `openclaw gateway status` | 查看 Gateway 状态 |
| `openclaw gateway start` | 启动 Gateway |
| `openclaw gateway stop` | 停止 Gateway |
| `openclaw gateway restart` | 重启 Gateway |
| `openclaw health` | 健康检查 |
| `openclaw doctor` | 诊断配置和环境问题 |
| `openclaw doctor --fix` | 自动修复可修复的问题 |
| `openclaw configure` | 交互式配置管理 |
| `openclaw config get <path>` | 读取配置项 |
| `openclaw config set <path> <value>` | 设置配置项 |
| `openclaw chat` | 打开终端聊天界面 |
| `openclaw tui` | 打开终端交互界面 |
| `openclaw logs --follow` | 实时查看日志 |
| `openclaw security audit --deep` | 深度安全审计 |
| `openclaw skills list` | 列出可用技能 |
| `openclaw --help` | 查看所有可用命令 |

---

## 8. 后续建议

1. 打开 Web 控制台：`http://127.0.0.1:18789/`
2. 在终端运行 `openclaw chat` 或 `openclaw tui` 开始使用。
3. 使用 `openclaw configure --section web` 配置 Web 搜索能力，例如 Brave Search API Key。
4. 使用 `openclaw channels` 配置 Telegram、WhatsApp、Discord 等消息渠道。
5. 使用 `openclaw doctor --fix` 安装或修复缺失依赖。
6. 按需配置 command owner，以获得完整命令权限。

---

## 9. 参考链接

- 官网: https://openclaw.ai
- 官方文档: https://docs.openclaw.ai
- GitHub: https://github.com/openclaw/openclaw
- DeepSeek 控制台: https://platform.deepseek.com
- 国内镜像: https://open-claw.org.cn

