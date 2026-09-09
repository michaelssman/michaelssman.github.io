# Maven 的 pom.xml

POM 是 Project Object Model，用来描述项目坐标、依赖、模块与构建规则。本文以 hhjava 的多模块工程解释常用标签；片段需要放进对应 POM 位置，不是互相独立的完整工程。

## 入门：为什么不手工下载所有 Jar

Maven 是构建与依赖管理工具。“构建”包括把 `.java` 编译为 `.class`、复制资源、运行测试、生成 Jar；“依赖”是代码所使用的其他库。一个库还可能依赖其他库，Maven 按依赖关系解析它们，称为传递依赖。

| 名称 | 含义 |
| --- | --- |
| 构件（artifact） | 可以发布和引用的构建产物及其元数据，常见为 Jar 与 POM |
| 仓库（repository） | 存放构件的位置；本地仓库通常在 `~/.m2/repository`，远端仓库通过网络访问 |
| 插件（plugin） | 执行构建工作的工具，如编译、测试插件；不是 IDEA 插件，也不是业务运行库 |
| 目标（goal） | 插件提供的一个具体动作，如 `dependency:tree`；生命周期阶段可绑定多个目标 |
| Reactor | Maven 多模块构建机制，根据聚合模块及依赖关系组织构建 |
| BOM（Bill of Materials，物料清单） | Maven 中常指集中管理一组兼容依赖版本的 POM，不会自动把所有依赖加入模块 |

Maven 不负责自动安装 MySQL、MinIO 服务端，也不替代 Java：`mvn -v` 会显示 Maven 正在使用哪个 JDK。

### XML 最外层是什么样

POM 是 XML（Extensible Markup Language，可扩展标记语言）文件，标签要正确嵌套。下面是结构示意，不是要求在现有 POM 再包一层 project：

```text
project                         唯一根元素
├── modelVersion                POM 模型版本
├── parent                      可选的唯一直接父 POM
├── groupId / artifactId / version
├── packaging                   不写时通常是 jar
├── properties                  可复用属性
├── modules                     可选，聚合哪些子模块
├── dependencyManagement        可选，管理依赖默认元数据
├── dependencies                实际需要的依赖
├── build
│   ├── pluginManagement        插件默认规则
│   └── plugins                 插件声明与配置
└── repositories                按需声明受信任仓库
```

`xmlns` 声明 XML 命名空间，`xsi:schemaLocation` 提供结构规范位置，都不是 Maven 镜像下载地址。完整可复制 POM 放在 [Spring Boot 第一个接口](../SpringBoot.md) 第 9.2 节；使用同一份工程逐步添加依赖，避免把几段互不关联的 XML 当成完整项目。

## 1. 项目坐标与打包类型

```xml
<modelVersion>4.0.0</modelVersion>
<groupId>com.hhjava.www</groupId>
<artifactId>hhjava</artifactId>
<version>1.0-SNAPSHOT</version>
<packaging>pom</packaging>
```

- `modelVersion` 是 POM 模型版本，不是 Java 或项目版本。
- `groupId` 是项目所属组织标识，`artifactId` 是模块标识，两者与 `version` 一起定位构件。
- `SNAPSHOT` 表示开发中的快照版本，不等于固定的发布版本。
- `packaging=pom` 常用于聚合/父模块；普通代码组件通常为 `jar`。
- `war` 是另一种 Web 部署打包形式，不是 hhjava 当前微服务的打包方式。

## 2. parent：继承父配置

hhjava 根 POM 继承 Spring Boot 父 POM，当前源码使用 Java 17、Spring Boot 3.3.7。这里描述项目基线，不表示它们是官方最新版本；升级应统一验证版本兼容性。

user 的直接父级是 `hhjava-service`，继承链为：

```text
Spring Boot parent → hhjava → hhjava-service → hhjava-user
```

```xml
<parent>
    <groupId>com.hhjava.www</groupId>
    <artifactId>hhjava-service</artifactId>
    <version>1.0-SNAPSHOT</version>
</parent>
```

每个 POM 只能有一个直接父 POM，但可以通过多级继承获得祖先配置。属性、依赖及管理配置、可继承插件配置等可能沿父链传递；最终生效内容以 effective POM 为准。

## 3. modules：聚合构建

例如 `hhjava-service/pom.xml`：

```xml
<packaging>pom</packaging>
<modules>
    <module>hhjava-user</module>
    <module>hhjava-backup-file</module>
</modules>
```

`modules` 告诉 Maven Reactor 哪些子工程一起构建，不代表这些模块自动互相依赖。构建顺序由依赖关系等因素决定，不应靠调整目录顺序解决缺少依赖的问题。

## 4. properties：集中可复用属性

根 POM 中的实际属性节选：

```xml
<properties>
    <java.version>17</java.version>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <minio.version>8.5.17</minio.version>
</properties>
```

后续通过 `${minio.version}` 引用版本。集中管理是为了各模块保持一致，不要在子 POM 又写一份不同的 SDK 版本。Spring Boot 管理的依赖优先沿用其版本管理，不逐个任意升级 Spring 组件。

## 5. dependencyManagement 与 dependencies

最容易混淆的区别：

| 位置 | 作用 |
| --- | --- |
| `dependencyManagement/dependencies` | 管理版本、范围等默认元数据，本身不把依赖加入所有模块 |
| 当前 POM 的 `dependencies` | 实际声明依赖；父 POM 的这类依赖也可能被子模块继承 |

根 POM 统一管理 MinIO：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.minio</groupId>
            <artifactId>minio</artifactId>
            <version>${minio.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

文件 Starter 按需引入，不重复版本：

```xml
<dependencies>
    <dependency>
        <groupId>io.minio</groupId>
        <artifactId>minio</artifactId>
    </dependency>
</dependencies>
```

Spring Cloud 等 BOM 使用 `type=pom`、`scope=import` 放在 `dependencyManagement` 中导入版本管理。这与 `parent` 继承、`modules` 聚合是不同机制。[Maven 依赖机制说明](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)

当前 `hhjava-service` 已声明公共 Web、common 等依赖，user/backup-file 继承后不需要机械重复。只有单个模块需要的业务依赖，应留在那个模块。

## 6. scope 与 exclusions

常见 scope：`compile` 为默认，`runtime` 供运行时使用，`test` 仅供测试，`provided` 表示编译需要、运行时通常由环境等提供。不要把测试工具放进生产依赖范围。

| scope | 主代码编译 | 应用通常运行时 | 测试时 | 典型例子 |
| --- | --- | --- | --- | --- |
| compile | 有 | 有 | 有 | 主代码直接使用的类库 |
| runtime | 无 | 有 | 有 | 仅通过接口/配置加载的 JDBC 驱动 |
| test | 无 | 无 | 有 | JUnit、测试断言 |
| provided | 有 | 通常由容器等提供 | 有 | 需要运行环境提供的 API；最终打包还需看插件规则 |

`import` 只用于 dependencyManagement 中导入 POM 类型 BOM，不能当作上表的普通运行依赖范围。也不推荐用 `systemPath` 绑定本机某个 Jar 绝对路径，否则换电脑很容易无法构建。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

`exclusions` 排除某条依赖路径带来的传递依赖，不是“同一个 Jar 出现两次就必须排除”。即使在一条路径排除，其他路径仍可能引入它；检查 `mvn dependency:tree` 后再决定。

若同一库出现多个版本，Maven 会按依赖管理和依赖调解规则选择版本，通常不是把它们全部带进来。`exclusion` 的 groupId/artifactId 必须来自实际依赖树，不能凭教程随意排除安全、日志或 JSON 库后期待框架自行补齐。

日志实现等冲突需要检查完整依赖树，不能仅凭某个 POM 的注释认定运行时已经只有一种实现。

## 7. build、plugins 与 pluginManagement

`build` 管理资源、编译、测试、打包等规则。`pluginManagement` 主要提供插件默认配置；是否执行某个目标，还要结合生命周期绑定和实际插件声明判断。

可启动服务按需使用 Spring Boot 插件生成可执行 Jar。普通 common、unify、Starter 不需要启动入口，也不应被当成可启动服务执行 repackage；但它们仍可能需要资源、编译或测试配置，不能直接删除整个 `build`。

演示代码放进 `src/test/java`。启动类不承担无关 `CommandLineRunner` 打印，`ResponseResult` 等 DTO 不放 `main` 演示序列化。

## 8. repositories 与本机镜像

Maven 区分依赖仓库与插件仓库。公共仓库元数据集中放在根 POM，子模块不重复复制；本机下载镜像、凭据等由 Maven `settings.xml` 等外部配置管理。

不在 POM 保存仓库密码，也不为下载某个库随意加入未经核实的仓库。下载失败先检查坐标、有效仓库/镜像、网络和认证配置。

## 9. 当前项目的 JSON 依赖原则

业务 JSON 使用框架集成的 Jackson。common/unify 不需要为响应 DTO 的演示代码直接引入 Fastjson；gateway 使用注入的 `ObjectMapper` 创建可复用 writer。

删除直接依赖不保证第三方 SDK 的传递依赖完全不含该库，依赖树才是事实来源。也不要因为采用 Jackson 就把 OAuth2 协议错误强行包装成业务响应。详见 [序列化](../序列化.md)。

## 10. 常用验证命令

从 hhjava 根目录执行，项目没有 Maven Wrapper：

```sh
# 选择 user，并同时构建所需的 Reactor 依赖模块。
mvn -pl hhjava-service/hhjava-user -am test

# 父 POM、公共模块或跨模块变更后完整回归。
mvn clean test

# 测试完成后按需检查打包；此命令本身不执行测试。
mvn -DskipTests package

# 定位依赖来源。
mvn dependency:tree
```

更改版本或模块结构时，同时检查父子 POM、依赖树和完整 Reactor 构建。不要只确认 IDEA 不再显示红色，就认为命令行和其他电脑也能构建成功。

## 11. 动手理解编译、测试、打包、安装

前置：先完成 [Spring Boot 独立练习](../SpringBoot.md)，准备 JDK 17 和 Maven 3。以下都在 Mac 的 `hhjava-learning-basics` 根目录，不是在服务器，也不是在其 src 子目录。

### 11.1 先观察生命周期

```text
validate → compile → test → package → verify → install → deploy
检查      编译      测试   打包       验证      本地安装  发布仓库
```

这是常用阶段的简图，中间还包含资源处理、测试编译等阶段。执行后面的阶段会经过之前绑定的动作。例如 `mvn package` 通常先编译并测试。`clean` 属于另一条生命周期，清理构建目录后可重新执行默认生命周期。[Maven 生命周期说明](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)

### 11.2 按顺序执行并检查

```sh
cd /Users/michael/Documents/java_demo/hhjava-learning-basics
mvn validate
mvn compile
mvn test
mvn package
```

每一步预期：

1. validate：POM 可解析、项目基本模型有效；不是所有配置在此阶段都会被实际连接验证。
2. compile：`target/classes/com/example/learning` 下出现 class 文件；resources 中的配置复制到 target/classes。
3. test：测试执行成功；`target/surefire-reports` 中可查看结果。
4. package：出现 `target/hhjava-learning-basics-1.0-SNAPSHOT.jar`；Boot 插件把应用和运行依赖组织成可执行归档。

检查归档内容可执行：

```sh
jar tf target/hhjava-learning-basics-1.0-SNAPSHOT.jar
```

预期能找到 `BOOT-INF/classes` 的应用内容与 `BOOT-INF/lib` 的依赖。普通组件 Jar 不采用同样的可执行结构，不能据此要求 common 也必须出现 BOOT-INF。

`mvn install` 是把构件装进**本地 Maven 仓库**，供其他本地 Maven 工程解析，不是安装到 ECS。`mvn deploy` 会发布到配置的远端构件仓库，有外部影响，本练习不执行。运行网站是 `java -jar` 或对应启动命令，与 Maven install 是不同事情。

### 11.3 看最终配置，不只看当前文件

在学习工程根目录执行：

```sh
mvn help:effective-pom
mvn dependency:tree
```

effective POM 是继承、属性等合并后的生效模型，可查插件及依赖管理版本；依赖树可查库从哪条路径引入。只有自己确认无秘密的练习配置才适合直接展示；实际项目的 effective settings、环境变量、带认证的仓库 URL 不能原样贴到公开聊天或文章。

### 11.4 回到 hhjava 的多模块命令

```sh
cd /Users/michael/Documents/java_demo/hhjava
mvn -pl hhjava-service/hhjava-user -am test
```

`-pl` 选择模块，`-am` 同时构建该模块需要的 Reactor 模块。不是把路径切到 user 子目录就一定能解析尚未安装的兄弟组件。根 `<modules>` 聚合关系与子 `<parent>` 继承关系各自配置，目录嵌套本身不自动建立两种关系。

## 12. 初学者常见问题

| 现象 | 排查步骤 |
| --- | --- |
| 红色依赖 / 无法下载 | 先检查坐标和版本是否存在，再检查 Maven 选用的 settings、镜像、网络与认证；不要引入来源不明镜像 |
| `Non-resolvable parent POM` | 检查父坐标、relativePath 是否指向正确父 POM、远端是否可达，以及是否从正确聚合根构建 |
| 找不到兄弟模块 SNAPSHOT | 从 hhjava 根用 `-pl ... -am` 构建；若确需给另一个独立工程使用，再按需 install |
| IDEA 能编译，终端失败 | 对比 JDK、Maven、profile 和配置文件；不要只依赖 IDEA 手动添加的库 |
| XML 未进入产物 | 优先放 `src/main/resources`；检查资源配置，详情见 [Mapper](../Java分层/Mapper数据库连接层.md) |
| 找不到主类 / repackage 失败 | 确认可启动服务有 main；普通 Starter 不需要 repackage，但仍需要正常编译和资源处理 |
| 想“清缓存”解决一切 | 先用依赖树定位具体构件，不删除整个 `.m2`；`mvn clean` 清理本工程构建目录，不负责删除全局依赖缓存 |

`-DskipTests` 通常跳过测试执行但仍可能编译测试；`-Dmaven.test.skip=true` 还会影响测试编译。两者都不能作为“测试通过”的证据。
