# Claude

```sh
claude --version
```

## 首次启动配置

```sh
claude
```

- 文字显示风格：内置 6 种色彩方案，首次启动需选择

- 连接后端模型方式：
  - Claude account with subscription：Claude.Al 账号 + 订阅（固定月费），选择后跳转官网登录
  - Anthropic console account：按使用量计费，适用于高用量团队 / 企业，成本较高
  - Third party platform：通过第三方平台，需手动设置环境变量 API KEY 和 base URL

新建终端窗口

```sh
nano ~/.zshrc
```

配置环境变量，在文件末尾添加：

```sh
export ANTHROPIC_API_KEY="sh-ant-你的真实key在这里"
export ANTHROPIC_BASE_URL="url"
```

执行source命令，让终端生效

```sh
source ~/.zshrc
```

验证环境变量是否设置成功

```sh
echo $ANTHROPIC_API_KEY
```

在Claude code中运行`whoami`，如果输出账号信息，则配置成功。

## 使用

进入本地项目目录

运行

```sh
claude /init
```

Claude code会互动式的提问，从而自动生成配置文件，这会产生一个claude.md文件。

### claude.md

claude.md是Claude code最核心的记忆文件，作用是让Claude code记住并严格遵守你的项目个人规则，相当于给AI一个**持久的个人偏好级**，每次启动Claude的会话时，它会自动把相关的claude.md文件加载到上下文里，它的优先级比你临时输入的提示词要高很多，这样Claude就能更好的理解你的代码库，遵守规范，减少反复说明，大幅提升输出质量和一致性。

### 偏好级文件

#### claude.md

位于项目根目录以及子目录下，用于指定项目架构代码规范、常用命令、团规约定工作流等等。它是最常用的PL级配置文件，是团队协作的首选。在每个目录下都可以存在claude.md文件。

当前子目录下的claude.md文件优先级最高，项目根目录下的claude.md文件中指定的规则会被子目录的规则所覆盖或者强化。

这就是monorepo或模块化项目设计的目的：根目录放通用规则，子目录放专属规范。

#### claude.local.md

用于指定自己机器特有的设置偏好、临时实验、敏感信息等。它是为了不污染仓库而指定的个人定制。这个文件仅在本地个人使用，不会提交到git仓库。

#### ~/.claude/claude.md

**全局个人偏好配置文件**，用于全项目的通用习惯、默认工具、个人安全、身份信息等等，它适合于跨项目统一个人风格，这个文件会在所有项目中都生效。

#### 优先级

`claude.local.md > 项目claude.md > 全局claude.md`。

## Claude code

Claude code本质是一个终端里面的智能开发工具，自己不产生智能，必须接一个大模型的服务。官方默认的是Anthropic Claude模型（海外服务），网络、支付、账号、稳定、服务等限制问题。所以接国内的大模型接口，价格、稳定等更好一点。例如：智谱的GLM、MiniMax、Kimi等。

### 注意

claude code会发送代码片段到anthropic服务器处理，需要注意隐私与安全。可以在项目全局的`settings.json`文件中设置，用permissons中的deny来防止Claude读取密钥。

## CC-Switch接口管理工具

购买多个服务商的不同的模型，CC-Switch帮助管理这些模型，点一下启动按钮就可以切换模型。

1. 大模型的官方网站购买Coding Plan。
2. 在API Key的管理页面创建新的API Key，把API Key复制出来。
3. 打开CC-Switch，添加服务商，选择品牌，粘贴API Key，重启Claude code。

## plan mode

为了防止改错，越改越乱的问题。