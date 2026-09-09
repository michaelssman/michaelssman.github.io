# Spring Boot

## 入门词语：先知道这些代码在做什么

| 词语 | 基础含义与作用 |
| --- | --- |
| JDK（Java Development Kit，Java 开发工具包） | 提供编译和运行 Java 所需的工具；`javac` 编译源码，`java` 启动程序 |
| JVM（Java Virtual Machine，Java 虚拟机） | 执行编译后的 Java 字节码；不同操作系统安装各自的 Java 运行环境 |
| Spring Bean | 由 Spring 创建、管理并提供给其他对象使用的 Java 对象，不是一种特殊 Java 语法 |
| IoC（Inversion of Control，控制反转） | 对象的创建与装配交由容器管理；DI（Dependency Injection，依赖注入）是把所需对象传入的一种实现方式 |
| 注解（Annotation） | 以 `@` 开头的元数据；框架读取它们来决定扫描、路由等行为，不是加上任意注解代码就会生效 |
| Spring MVC（Model-View-Controller） | Spring 的 Servlet Web 框架，把请求分派给 Controller；本练习返回 JSON，不使用服务端页面模板 |
| SSM | Spring、Spring MVC、MyBatis 的组合；Boot 帮助装配这些组件，MyBatis 负责数据库访问 |
| classpath（类路径） | 运行时寻找类和资源的位置；源码目录不会原封不动成为可执行文件，需要先构建 |

## 1. Spring Boot 帮你做什么

Spring Framework 提供依赖注入、事务、Web 等基础设施。Spring Boot 在其上提供自动配置、依赖管理和应用启动支持，让常见应用少写重复装配代码。

“约定优于配置”不是不需要配置：数据库连接、外部服务地址、凭据和安全规则仍需明确提供。

## 2. 启动类和 Starter 不是一回事

- 启动类：应用运行入口，`main` 中调用 `SpringApplication.run(...)`。
- Starter：一组协同依赖的入口，可配合自动配置提供默认 Bean；不是独立微服务。
- 自动配置：根据 classpath、属性、应用类型和已有 Bean 等条件决定如何装配组件。

启动类的最小形式如下：

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

`@SpringBootApplication` 组合了配置、自动配置和组件扫描能力。默认扫描以启动类所在包为基础，但第三方 Starter 不应依赖消费方扩大包扫描。

不清楚“配置类”“Bean”和“自动配置”的区别时，可先看第 10 节：它从 `@Configuration` 讲到 `@Bean` 的对象创建，再对应到 `@AutoConfiguration`。

启动时会准备环境、创建应用上下文并装配 Bean，根据应用类型启动 Web 服务器。不是所有 Boot 应用都启动 Tomcat：hhjava 的 Servlet 业务服务与 WebFlux 网关使用不同的 Web 技术栈。

## 3. 常见 Starter 怎么选

| 依赖 | 主要用途 |
| --- | --- |
| `spring-boot-starter` | Boot 基础能力与默认基础依赖 |
| `spring-boot-starter-web` | Spring MVC、默认嵌入式 Tomcat、JSON 支持 |
| `spring-boot-starter-webflux` | 响应式 Web 应用 |
| `spring-boot-starter-validation` | Bean Validation 校验实现 |
| `spring-boot-starter-test` | 测试工具，使用 test 范围 |

Boot 3 的 Web Starter 不自动等同于完整参数验证依赖，需要 Bean Validation 时应检查 validation 依赖是否实际存在。[Spring Boot Validation 文档](https://docs.spring.io/spring-boot/3.3/reference/io/validation.html)

引入某个 Jar 不意味着其所有自动配置无条件生效。缺少配置、已有替代 Bean 或不满足应用类型，都可能让自动配置不创建默认对象。

## 4. 配置文件基础

Boot 默认识别 `application.properties` 和 `application.yml` / `application.yaml`。properties 用点分键，YAML 用层级缩进表达结构；缩进使用空格，不使用 Tab。

下面两种写法含义相同，只是说明格式：

```properties
spring.application.name=demo-service
server.port=8080
```

```yaml
spring:
  application:
    name: demo-service
server:
  port: 8080
```

实际配置文件名、位置、profile 和导入来源可以调整，不是只能硬编码一种路径。多来源配置存在优先级，避免把同一个键散落多处后凭印象判断生效值。[Spring Boot 外部配置说明](https://docs.spring.io/spring-boot/3.3/reference/features/external-config.html)

Profile 是一组有名字的环境配置，例如 dev 表示开发环境；它不是自动替你创建一台服务器。Nacos 是项目采用的外部配置与服务发现系统；Data ID 标识配置文件，Namespace 和 Group 参与隔离、分组。具体导入哪份配置，由每个应用的导入规则和环境参数共同决定。

## 5. 从 Web 到数据库的开发顺序

1. 在根 POM 统一版本；业务模块只引入实际需要的依赖，避免同时加入不同版本的整套 Spring/MyBatis。
2. 配置数据源和 Mapper 资源加载，建立与数据库表对应的实体。
3. 使用 Mapper 完成参数化查询，复杂 JOIN 放在清晰的 SQL 映射中。
4. 在 Service 中编排事务与业务规则。
5. Controller 接收参数并调用 Service，异常交给对应 HTTP 边界处理。
6. 加测试，再验证真实数据库及外部配置。

当前 user 使用 MyBatis-Plus：常规 CRUD 复用 `BaseMapper`，角色关联查询用自定义 XML。并不是每个 Mapper 都必须写 XML，也不是加入 Starter 后就无需检查扫描与资源路径。详见 [Mapper 数据库访问层](Java分层/Mapper数据库连接层.md)、[Service 业务层](Java分层/Service业务层.md) 和 [Controller 控制层](Java分层/Controller控制层.md)。

## 6. 自定义自动配置的实现步骤

### 第一步：明确边界

公共组件只提供共性能力。例如文件 Starter 提供存储接口和默认 SDK 实现，不替业务服务决定文件属于哪个用户。

### 第二步：定义自动配置和条件

使用 `@AutoConfiguration`；用条件限定什么时候创建 Bean，并允许使用方提供自己的实现。hhjava 的两个例子：

| 自动配置 | 类级条件 | 默认 Bean 的退让条件 |
| --- | --- | --- |
| `ServletExceptionAutoConfiguration` | Servlet Web 应用 | 已有 `GlobalExceptionHandler` 时不重复创建 |
| `MinIOConfig` | 存在 `MinioClient` 类且匹配 `minio.endpoint` 属性条件 | `MinioClient` 和 `FileStorageService` 分别按类型退让 |

例如公共异常自动配置：

```java
@AutoConfiguration
@ConditionalOnWebApplication(type = ConditionalOnWebApplication.Type.SERVLET)
public class ServletExceptionAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean(GlobalExceptionHandler.class)
    public GlobalExceptionHandler globalExceptionHandler() {
        return new GlobalExceptionHandler();
    }
}
```

这段代码的职责是**注册异常处理器**，不是由配置类本身捕获业务异常。

按顺序理解：

- `@AutoConfiguration` 声明自动配置；
- `@ConditionalOnWebApplication` 限定 Servlet Web 应用；
- `@Bean` 声明处理器的创建方法；
- `@ConditionalOnMissingBean` 让已有同类型 Bean 优先。这里“退让”就是不再注册这份默认 Bean，不是覆盖或删除使用方的实现。

user、backup-file 属于 Servlet 应用，能匹配此应用类型条件；gateway 使用响应式 WebFlux，不匹配该条件。是否注册默认处理器还要继续检查已有 Bean，不能仅看到依赖了 common 就判断一定创建了一个新处理器。

### 第三步：声明自动配置入口

在组件 Jar 的资源目录创建：

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

每行填写一个全限定类名。例如 common 中包含：

```text
com.hh.common.exception.ServletExceptionAutoConfiguration
```

文件 Starter 中则包含 `com.hhjava.www.config.MinIOConfig`。Boot 通过 imports 发现候选，再判断条件；自动配置类不依赖组件扫描，其默认实现应通过明确的 Bean 或 Import 装配。[Spring Boot 自定义自动配置文档](https://docs.spring.io/spring-boot/3.3/reference/features/developing-auto-configuration.html)

**只在一个类上加 `@AutoConfiguration`，不等于 Boot 会扫描所有依赖并自动找到它。** 应用需要启用自动配置（通常由启动类的 `@SpringBootApplication` 包含的 `@EnableAutoConfiguration` 完成），组件还需要在上述清单中登记候选类。候选不等于必然生效，排除规则和条件仍会影响加载。

### 第四步：构造器注入与按需退让

`MinIOFileStorageService` 通过构造器接收客户端和配置，由自动配置的 `@Bean` 方法创建，不用 `@Service` 等待外部包扫描。这也让测试可以直接传入替身对象，无需反射注入字段。

自动配置不满足条件时不创建默认 Bean，但如果业务 Controller 必须依赖该 Bean，应用仍可能启动失败。不能把“不启用 MinIO 自动配置”理解成“文件服务获得了一套可用的空实现”。

### 第五步：检查普通 Jar 的构建

common 和 Starter 不需要应用启动类或可执行 Jar 的 repackage；必要的编译、资源、测试配置仍保留。不要为了去掉启动入口而删除整个 `<build>`。

### 第六步：验证装配矩阵

使用轻量应用上下文测试检查：默认配置、缺失配置、自定义替代 Bean、Servlet/Reactive 应用类型，以及没有扩大组件扫描时能否发现默认能力。

“类写对了”与“Jar 中的自动配置清单能被消费方发现”是两个检查点，都需要覆盖。Mock 客户端能验证调用和失败传播，但不能代替连接真实存储服务。

## 7. 当前服务如何使用 common

`hhjava-service/pom.xml` 已声明 `hhjava-common`，user 和 backup-file 通过继承获得依赖，无需重复填写版本。common 中各项能力仍按自己的自动配置条件生效。

`ServletExceptionAutoConfiguration` 不依赖消费方扫描 `com.hh.common`。网关采用 WebFlux，使用自己的响应式认证错误处理器，不为复用 Servlet Advice 而引入 MVC 组件。

项目目录见 [工程结构](工程结构.md)，异常行为见 [异常处理](异常处理.md)，MinIO 配置与存储边界见 [MinIO 文件 Starter](分布式文件系统MinIO.md)。

## 8. 验证命令

从 hhjava 根目录执行 `mvn clean test` 检查公共组件及跨模块契约；需要产物时，在测试完成后执行 `mvn -DskipTests package`。

真实 Nacos、MySQL、MinIO 以及浏览器登录都属于外部集成验证。依赖不可用时明确记录未验证，不通过跳过测试把它描述为启动成功。

## 9. 动手：从空目录写出第一个 JSON 接口

目标：访问 `http://127.0.0.1:18080/hello?name=Java`，收到问候 JSON。所有操作都在 **Mac 本机**，不需要服务器、Nacos、MySQL 或 MinIO。

这是独立学习工程，不是给 hhjava 增加微服务。后续 [Mapper](Java分层/Mapper数据库连接层.md)、[异常](异常处理.md)、[序列化](序列化.md) 的练习使用同一个工程，不要把练习类复制进 hhjava。

### 9.1 准备 Java、Maven 和目录

1. 在 Mac 终端运行 `java -version` 与 `mvn -v`。本练习使用 JDK 17、Maven 3.6.3 或以上的 Maven 3；`mvn -v` 显示的 Java 也应是 17。
2. 在 IDEA 选择新建项目，语言选 Java，构建系统选 Maven，JDK 选 17，目录用 `/Users/michael/Documents/java_demo/hhjava-learning-basics`。若目录已有内容，不覆盖，换一个空的同级目录，并相应替换后续 `cd` 路径。
3. 本练习固定 Boot 3.3.7 以便对照当前 hhjava 源码，不表示这是最新版本或新生产系统的推荐基线。升级版本要另行检查兼容性和安全公告，不混用 Boot 4 的包名及示例。

下文所有“文件”路径均相对于这个学习工程。缺少目录时，在 IDEA 对上级目录右键，新建 Directory 或 Package。完成后结构如下：

```text
hhjava-learning-basics/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/example/learning/
    │   │   ├── LearningApplication.java
    │   │   ├── ApiResponse.java
    │   │   └── HelloController.java
    │   └── resources/application.yml
    └── test/java/com/example/learning/HelloControllerTest.java
```

### 9.2 声明完整依赖

文件：`pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.7</version>
        <relativePath/>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>hhjava-learning-basics</artifactId>
    <version>1.0-SNAPSHOT</version>
    <properties>
        <java.version>17</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

父 POM 统一管理版本，所以这些依赖不用各写一个版本。`relativePath` 为空表示不从相邻目录寻找父 POM。

在 IDEA 的 Maven 工具窗口点击重新加载，等待下载结束。检查 External Libraries 中出现 Spring 库；下载失败先按 [Maven 排障](Maven/pom.xml.md) 检查，不手工复制 Jar。

### 9.3 创建启动类和响应模型

文件：`src/main/java/com/example/learning/LearningApplication.java`

```java
package com.example.learning;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class LearningApplication {
    public static void main(String[] args) {
        SpringApplication.run(LearningApplication.class, args);
    }
}
```

启动类放在 `com.example.learning`，后续组件放在此包或子包，才能被默认组件扫描发现。

文件：`src/main/java/com/example/learning/ApiResponse.java`

```java
package com.example.learning;

// record 是 Java 的数据载体语法，自动提供构造器和 code()/message()/data() 等访问方法。
// T 是泛型参数：让同一种响应外壳可以装字符串、书籍列表或其他类型的数据。
public record ApiResponse<T>(int code, String message, T data) {
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "成功", data);
    }
}
```

这个教学类独立于 hhjava 的 `ResponseResult`，不需要引用 hhjava 模块。`record` 的组件不能重新赋值，但若组件本身是可变集合，也不会自动深度不可变；这里先使用字符串。

### 9.4 创建 Controller 和配置

文件：`src/main/java/com/example/learning/HelloController.java`

```java
package com.example.learning;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    @GetMapping("/hello")
    public ApiResponse<String> hello(
            @RequestParam(name = "name", defaultValue = "Java") String name) {
        return ApiResponse.success("你好，" + name);
    }
}
```

- `@RestController`：让 Spring 管理此类，并把方法返回值交给消息转换器写进响应体。
- `@GetMapping`：GET 请求路径匹配 `/hello` 时调用此方法。
- `@RequestParam`：从 URL 的查询参数取 `name`；`?name=Java` 不是 JSON 请求体。
- 返回 Java 对象后，Jackson 把它转成 JSON，不需要手工拼接带引号的 JSON 字符串。

文件：`src/main/resources/application.yml`

```yaml
spring:
  application:
    name: hhjava-learning-basics
server:
  address: 127.0.0.1
  port: 18080
```

只监听本机回环地址，练习不对公网开放。YAML 冒号后有空格，层级用空格缩进。

### 9.5 启动并发请求

在 Mac 终端执行：

```sh
cd /Users/michael/Documents/java_demo/hhjava-learning-basics
mvn spring-boot:run
```

看到 `Started LearningApplication` 后，保留此终端运行，另开终端：

```sh
curl -i 'http://127.0.0.1:18080/hello?name=Java'
```

预期 HTTP 200，响应体如下，空格和字段展示顺序可能不同：

```json
{"code":200,"message":"成功","data":"你好，Java"}
```

### 9.6 加一个自动化测试

文件：`src/test/java/com/example/learning/HelloControllerTest.java`

```java
package com.example.learning;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class HelloControllerTest {
    @Autowired
    private MockMvc mvc;

    @Test
    void shouldReturnGreeting() throws Exception {
        mvc.perform(get("/hello").param("name", "Java"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").value("你好，Java"));
    }
}
```

`@Test` 标识测试方法；MockMvc 在测试进程内模拟 MVC 请求，不占用真实 HTTP 端口；`$.data` 表示 JSON 根对象的 data 属性。`andExpect` 是断言，不符合预期就让测试失败。

在学习工程根目录执行 `mvn test`，预期 `BUILD SUCCESS`。再执行 `mvn package`，检查生成 `target/hhjava-learning-basics-1.0-SNAPSHOT.jar`。需要验证打包运行时，先停止原学习进程，再执行：

```sh
java -jar target/hhjava-learning-basics-1.0-SNAPSHOT.jar
```

重新访问 `/hello` 应得到同样结果。测试运行成功与真实 HTTP 访问成功是两个检查点。[Spring Boot 官方入门教程](https://docs.spring.io/spring-boot/3.3/tutorial/first-application/index.html)

### 9.7 常见问题和下一步

| 现象 | 检查与处理 |
| --- | --- |
| `mvn: command not found` | Maven 没装好或 PATH 未包含其 bin；先修复，再确认 `mvn -v` |
| `release version 17 not supported` | `mvn -v` 的 Java 太旧；终端和 IDEA Maven Runner 都改用 JDK 17 |
| 18080 已被占用 | 不结束不认识的进程；更换学习工程 `server.port`，同步更换测试 URL |
| 浏览器 404 | 检查路径 `/hello`，以及 Controller 包是否位于启动类包之下 |
| 返回网页而非 JSON | 检查是否写成普通 `@Controller` 且遗漏 `@ResponseBody`；本例使用 `@RestController` |
| YAML 不生效 | 检查文件是否在 `src/main/resources`、缩进是否正确，以及是否有其他来源覆盖相同键 |
| 已启动却收到代理 502 | 检查本机 HTTP 代理是否接管了回环请求；curl 可为本次请求添加 `--noproxy 127.0.0.1`，Reqable 检查对应代理设置，不通过关闭服务器安全规则排障 |

接下来阅读 [Mapper 的完整书籍查询练习](Java分层/Mapper数据库连接层.md)，把流程扩展为“HTTP → Controller → Service → Mapper → 数据库 → JSON”。它使用内存数据库，不要求你先配置云服务器。

## 10. @Configuration、@Bean 与自动配置的作用和逻辑

### 10.1 @Configuration 配置的是什么

`@Configuration` 是 Spring Framework 的类级注解，表示“这个 Java 类提供 Bean 的装配规则”。它不是 Spring Boot 才有的功能，也不是要求框架生成或修改application.yml。

先区分三个概念：

| 概念 | 含义 | 例如 |
| --- | --- | --- |
| 普通 Java 对象 | 某个类在运行时的实例 | 自己调用 `new GreetingFormatter(...)` 得到的对象 |
| Bean | 由 Spring 容器管理的对象 | 通过 `@Bean` 注册的 GreetingFormatter |
| Spring 容器 / ApplicationContext（应用上下文） | 管理 Bean 定义、创建、依赖注入和生命周期的基础设施 | 为 GreetingService 找到并传入所需的 GreetingFormatter |

“Bean 定义”可以理解为对象的创建说明：名称、类型、创建方法、作用域等。注册定义与真正创建实例不是同一件事；默认非延迟单例通常在容器启动过程中创建，延迟加载或其他作用域的创建时机不同。

Java 配置类回答“对象怎样创建和组合”，YAML/properties 回答“端口、地址等参数取什么值”。配置类可以通过属性绑定等机制使用这些参数，但加 `@Configuration` 本身不会自动读取任意目录的配置文件。[Spring Java 配置说明](https://docs.spring.io/spring-framework/reference/core/beans/java/configuration-annotation.html)

### 10.2 这些注解各管一件什么事

| 注解 | 放在哪里 | 主要作用与常见使用位置 |
| --- | --- | --- |
| `@Configuration` | 类 | 声明配置类；常用于当前应用的组件装配 |
| `@Bean` | 方法 | 声明方法返回的对象交给容器管理；适合第三方类或需要明确构造步骤的对象 |
| `@Component` / `@Service` | 类 | 让组件扫描发现并注册这个类；Service 表达业务服务语义 |
| `@AutoConfiguration` | 类 | 声明供 Boot 自动配置机制加载的配置类；常用于公共组件或 Starter |
| `@EnableAutoConfiguration` | 类 | 为应用启用 Boot 自动配置机制，不是声明某个业务 Bean |
| `@SpringBootApplication` | 启动类 | 组合应用配置、组件扫描及启用自动配置的常用入口 |

`@AutoConfiguration` 本身包含 `@Configuration(proxyBeanMethods = false)`；它仍然是一种配置类。什么条件下生效，由 `@ConditionalOnClass`、`@ConditionalOnProperty`、`@ConditionalOnMissingBean` 等注解决定，不是 AutoConfiguration 自动猜测。[AutoConfiguration 注解定义](https://docs.spring.io/spring-boot/3.3/api/java/org/springframework/boot/autoconfigure/AutoConfiguration.html)

选择方式时：自己写的业务 Service 通常交给组件扫描；第三方客户端、编码器或需组装的对象可由配置类的 Bean 方法创建；给多个应用提供可发现、可按条件启用的默认能力，再考虑自动配置。不要把所有 Service 都改成配置类，也不要同时通过 `@Service` 和 `@Bean` 重复注册同一个默认实现。

### 10.3 从启动到注入的顺序

以本节练习的两个对象为例：GreetingFormatter 负责格式化问候，GreetingService 使用它产生结果。

```text
找到 LearningBeanConfiguration
    ↓
解析 @Bean 方法，注册 formatter、service 的创建规则
    ↓
准备创建 GreetingService，发现它需要 GreetingFormatter
    ↓
创建或取得容器中的 GreetingFormatter
    ↓
把 formatter 作为参数交给 greetingService(...) 方法
    ↓
保存创建出的 GreetingService，供后续使用
```

普通配置类必须先被容器发现，例如位于组件扫描范围、被 `@Import` 显式导入，或在创建学习容器时直接注册。Boot 默认扫描启动类所在包及其子包；注解不会让任意磁盘目录中的 Java 类自动生效。`@Configuration` 包含组件注解语义，所以可以被组件扫描发现。

容器根据依赖关系装配对象，不是按 `.java` 文件中方法出现的上下顺序装配。`@Bean` 方法默认以方法名作为 Bean 名称，并使用 singleton（单例）作用域：同一容器内，同一 Bean 定义通常复用一个实例，不是“整个 JVM 中同一种类永远只有一个对象”。单例对象若保存可变状态，仍需自己考虑并发安全。[Bean 的声明、依赖和作用域](https://docs.spring.io/spring-framework/reference/core/beans/java/bean-annotation.html)

### 10.4 动手：创建并验证两个相互依赖的 Bean

目标：不启动 HTTP 服务，只用测试证明配置类能注册 Bean、注入依赖，并复用默认单例。

前置准备：完成第 9 节的独立 `hhjava-learning-basics` 工程，使用同一 JDK 17、Boot 3.3.7 学习基线，已有 test 依赖。所有操作都在 Mac 本机，不需要新增依赖或配置服务器，不把以下类复制进 hhjava。文件路径均相对学习工程根目录；在 IDEA 中先创建 `com.example.learning.beans` 包。

#### 第一步：写一个普通格式化类

文件：`src/main/java/com/example/learning/beans/GreetingFormatter.java`

```java
package com.example.learning.beans;

// 不加 @Component：本例由配置类的 @Bean 方法负责注册它。
public class GreetingFormatter {
    private final String prefix;

    public GreetingFormatter(String prefix) {
        this.prefix = prefix;
    }

    public String format(String name) {
        return prefix + name;
    }
}
```

此时它只是普通 Java 类。`prefix` 是创建时传入的问候前缀，不会自己从 YAML 获得值。

#### 第二步：写一个依赖它的服务类

文件：`src/main/java/com/example/learning/beans/GreetingService.java`

```java
package com.example.learning.beans;

// 本例同样不加 @Service，避免与下一步的 @Bean 重复注册。
public class GreetingService {
    private final GreetingFormatter formatter;

    public GreetingService(GreetingFormatter formatter) {
        this.formatter = formatter;
    }

    public String greet(String name) {
        return formatter.format(name);
    }
}
```

构造器明确要求 GreetingFormatter，调用方必须提供它。类名包含 Service 不会使它自动成为 Bean，注册方式由注解或配置决定。

#### 第三步：用配置类规定对象怎样创建

文件：`src/main/java/com/example/learning/beans/LearningBeanConfiguration.java`

```java
package com.example.learning.beans;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class LearningBeanConfiguration {
    @Bean
    public GreetingFormatter greetingFormatter() {
        return new GreetingFormatter("你好，");
    }

    @Bean
    public GreetingService greetingService(GreetingFormatter formatter) {
        // 方法参数由容器解析并传入，不是这里重新 new 一个 Formatter。
        return new GreetingService(formatter);
    }
}
```

这两个 Bean 的默认名称分别是 `greetingFormatter` 和 `greetingService`。注册对象依然需要实际执行构造代码，所以 Bean 方法中出现 `new` 完全正常：**Spring 按定义调用这个方法，并管理返回值**。这与业务代码随处 new、且不交给容器管理，是不同的使用方式。

方法参数注入让依赖关系直接体现在签名上。在这里只有一个 GreetingFormatter 候选，容器按类型即可找到它；如果将来有多个同类型 Bean，就需要 `@Qualifier` 指明名称或用 `@Primary` 明确首选，不能期待 Spring 随便选一个。

#### 第四步：写测试观察注册、注入和单例

文件：`src/test/java/com/example/learning/beans/LearningBeanConfigurationTest.java`

```java
package com.example.learning.beans;

import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;

class LearningBeanConfigurationTest {
    @Test
    void shouldRegisterBeansAndInjectDependency() {
        // 显式注册配置类，启动一个小型 Spring 容器，不加载整个 Boot 应用。
        try (var context = new AnnotationConfigApplicationContext(LearningBeanConfiguration.class)) {
            GreetingFormatter formatter = context.getBean(GreetingFormatter.class);
            GreetingService service = context.getBean(GreetingService.class);

            assertEquals("你好，Java", service.greet("Java"));
            assertSame(formatter, context.getBean("greetingFormatter"));
            assertSame(service, context.getBean(GreetingService.class));
        }
    }

    @Test
    void shouldDistinguishManagedConfigurationFromManualNew() {
        try (var context = new AnnotationConfigApplicationContext(LearningBeanConfiguration.class)) {
            GreetingFormatter managed = context.getBean(GreetingFormatter.class);
            LearningBeanConfiguration configuration = context.getBean(LearningBeanConfiguration.class);

            // 默认 proxyBeanMethods=true：容器管理的配置对象会拦截此 Bean 方法调用。
            assertSame(managed, configuration.greetingFormatter());
            // 手工 new 的配置对象没有容器增强；此调用只是普通 Java 方法调用。
            assertNotSame(managed, new LearningBeanConfiguration().greetingFormatter());
        }
    }
}
```

`getBean` 按类型或名称取出容器管理的对象；`assertSame` 比较是否为同一个实例，不只是字段内容相等。`try (...)` 在结束时关闭学习容器。本例为了观察容器而主动 getBean，实际 Controller/Service 通常使用构造器注入，不应把到处查容器作为业务编程习惯。

#### 第五步：执行并核对结果

在 Mac 学习工程根目录执行：

```sh
cd /Users/michael/Documents/java_demo/hhjava-learning-basics
mvn -Dtest=LearningBeanConfigurationTest test
```

预期 `BUILD SUCCESS`。第一项测试证明依赖注入后的业务结果正确，并且重复获取默认单例得到同一对象；第二项证明容器管理的配置对象与手工 new 的配置对象不同。这里只运行该学习测试，不启动 HTTP 端口，也不连接数据库或 Nacos。

### 10.5 proxyBeanMethods 是什么意思

proxyBeanMethods 可以理解为“是否代理配置类中的 Bean 方法”。代理是在原对象调用外增加框架处理，不需要初学者自己编写代理类。

| 配置方式 | 在容器管理的配置对象上直接调用 Bean 方法时 |
| --- | --- |
| `@Configuration`，默认 `proxyBeanMethods=true` | Spring 对配置类进行增强，让可代理的 Bean 方法调用遵循容器的作用域语义；本练习的默认单例会被复用 |
| `@Configuration(proxyBeanMethods=false)` | 不拦截方法之间的直接调用，按普通 Java 方法执行；但容器中已注册 Bean 的默认作用域仍然是单例 |
| `@AutoConfiguration` | 固定使用 false；依赖其他 Bean 时应通过方法参数等注入方式表达 |

false **不等于取消 Bean 管理，也不等于把 Bean 改成多例**。它改变的是直接调用方法时有没有容器拦截。不要依赖直接调用另一个 Bean 方法来取得共享依赖；本例 `greetingService(GreetingFormatter formatter)` 的参数注入方式在 true/false 两种配置下都适用。

第二项测试专门验证默认 true 的行为；若设计上采用 false，就不能继续要求直接调用 `configuration.greetingFormatter()` 必须返回容器单例。日常使用优先注入业务 Bean，而不是注入配置类再手工调用它。需要代理的配置类与 Bean 方法也不能使用阻止代理的 final 等声明。[Configuration 的方法调用与代理说明](https://docs.spring.io/spring-framework/reference/core/beans/java/configuration-annotation.html)

### 10.6 对应回 hhjava，以及常见疑问

| 项目位置（相对 hhjava 根目录） | 对应的作用 |
| --- | --- |
| `hhjava-service/hhjava-user/src/main/java/com/hh/security/WebSecurityConfig.java` | 用普通 Configuration 配置 user 自身的编码器、认证 Provider、安全链等 Bean |
| `hhjava-common/src/main/java/com/hh/common/exception/ServletExceptionAutoConfiguration.java` | 用 AutoConfiguration 按应用类型和已有 Bean 条件提供公共异常处理器，流程见第 6 节 |
| `hhjava-basic/hhjava-file-starter/src/main/java/com/hhjava/www/config/MinIOConfig.java` | 按条件创建 MinioClient 和 FileStorageService，后者通过方法参数取得客户端 |

MinIO 的条件注解检查运行时类是否可用、配置属性是否匹配，Bean 方法才负责绑定参数后的对象构建。`@ConditionalOnProperty(prefix="minio", name="endpoint")` 默认要求属性存在且值不是 false，并不负责校验地址可达；自动配置不会替你安装 MinIO、创建云服务器或生成真实访问密钥。

| 现象或疑问 | 原因和检查方法 |
| --- | --- |
| 加了 Configuration，却找不到 Bean | 检查配置类是否被扫描或显式导入、方法是否有 Bean、相关条件是否满足；包外的类不会凭注解自动被找到 |
| 出现多个同类型 Bean，无法注入 | 检查是否重复注册；确实需要多个时，再用 Qualifier 或 Primary 明确选择 |
| 手工 new 配置类后，自动注入没有发生 | 普通 new 不会替你启动容器或自动处理注入；使用容器注册和构造器/方法参数注入 |
| “自动配置”是否会覆盖我的实现 | 取决于是否声明 MissingBean 等条件；AutoConfiguration 本身不保证自动退让 |
| 修改 Nacos 后，所有 Bean 会自动重建吗 | 不会仅因 Configuration 注解就重建；配置刷新和 Bean 的重建策略是另外的机制 |

记忆方式：**Configuration 描述装配规则，Bean 描述要交给 Spring 管理的对象；AutoConfiguration 在此基础上，为公共组件提供 Boot 的自动发现入口，条件注解再决定哪些默认配置生效。**
