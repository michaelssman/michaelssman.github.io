# SpringMVC和WebFlux

在Spring Security的配置中，存在两个同名的Bean，一个来自`WebSecurityConfiguration`（Spring MVC的配置），另一个来自`WebFluxSecurityConfiguration`（属于WebFlux，即响应式配置）。Spring默认不允许Bean覆盖，因此导致冲突。

项目使用了Spring Cloud Gateway，而Gateway是基于WebFlux的响应式框架。同时，用户的依赖中可能引入了Spring MVC相关的starter，比如`spring-boot-starter-web`，这会导致同时存在Servlet和Reactive两种配置，从而引发冲突。

Spring Boot官方文档指出，同时引入`spring-boot-starter-web`和`spring-boot-starter-webflux`会导致应用默认使用Spring MVC，因为前者会优先。但在Spring Cloud Gateway这种基于WebFlux的项目中，应该只使用WebFlux，避免引入MVC相关的依赖。

------

### 解决方案

#### 移除冲突的依赖

Spring Cloud Gateway基于WebFlux构建，需确保**移除所有Servlet依赖**（如`spring-boot-starter-web`）

如果项目中存在公共common模块，需确保该模块**没有引入Servlet依赖**。

------

## WebFlux和Servlet区别

### 核心架构差异
| **特性**     | **Servlet（Spring MVC）**                      | **WebFlux（响应式）**                                   |
| ------------ | ---------------------------------------------- | ------------------------------------------------------- |
| **编程模型** | 基于 **阻塞式 I/O**（每个请求占用一个线程）    | 基于 **非阻塞 I/O**（事件驱动，少量线程处理高并发）     |
| **线程模型** | 依赖线程池（如 Tomcat 的线程池），线程数量有限 | 使用 `EventLoop`（如 Netty），线程数通常与 CPU 核数相关 |
| **资源消耗** | 高并发时线程数激增，内存和 CPU 开销大          | 高并发下资源占用更稳定，适合长连接、流式场景            |
| **背压支持** | 不支持                                         | 支持响应式流背压（如 `Flux`/`Mono` 控制数据流速）       |
| **适用场景** | 传统 CRUD 应用、同步阻塞操作（如 JDBC）        | 高并发、低延迟（如实时推送、API 网关、微服务通信）      |

### 需要避免混合使用
- **Spring Cloud Gateway 的依赖本质**：  
  Gateway 基于 WebFlux 构建，强制依赖 `spring-boot-starter-webflux`。若同时引入 `spring-boot-starter-web`（Servlet），会导致：
  - **Bean 冲突**（如你遇到的 `conversionServicePostProcessor` 重复定义）
  - **运行时模式不兼容**：Servlet 容器（如 Tomcat）与 Netty 无法共存，应用无法确定启动方式。

- **安全配置冲突**：  
  Spring Security 对 Servlet 和 WebFlux 的配置是独立的（`WebSecurityConfigurerAdapter` vs `SecurityWebFilterChain`），混合配置会导致不可预见的错误。

---

### 如何正确选择
#### 场景 1：构建 API 网关（如 Spring Cloud Gateway）
- **必须使用 WebFlux**：  
  网关需要高并发处理能力，WebFlux 的非阻塞模型能有效应对大量路由转发、限流、鉴权等操作。
- **禁止引入 Servlet 依赖**：  
  检查所有模块（尤其是公共模块）的 `pom.xml`，确保无 `spring-boot-starter-web`。

#### 场景 2：传统 CRUD 应用
- **使用 Servlet（Spring MVC）**：  
  若依赖 JDBC（阻塞式数据库访问）、MyBatis 等同步库，Servlet 更简单且生态支持完善。
- **避免引入 WebFlux**：  
  除非有明确的响应式需求（如集成 MongoDB Reactive）。

---

### 依赖冲突排查与解决
#### 步骤 1：检查依赖树
通过 Maven 命令定位 `spring-boot-starter-web` 的来源：
```bash
mvn dependency:tree -Dincludes=spring-boot-starter-web
```

#### 步骤 2：排除 Servlet 依赖
在父工程或子模块中移除或排除 Servlet 依赖：
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

#### 步骤 3：验证启动模式
应用启动时观察日志，确认使用 Netty 而非 Tomcat：
```log
2025-04-28 15:28:23.494  INFO 25832 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port 8080
```

---

### 迁移现有代码到 WebFlux
若需将部分 Servlet 代码迁移到 WebFlux：
- **Controller 层**：  
  使用 `@RestController` + 返回 `Mono<T>`/`Flux<T>`。
  
  ```java
  @GetMapping("/users/{id}")
  public Mono<User> getUser(@PathVariable String id) {
      return userRepository.findById(id);
  }
  ```
  
- **数据库访问**：  
  选择响应式驱动（如 R2DBC for MySQL/PostgreSQL，MongoDB Reactive）。

- **阻塞代码处理**：  
  若必须调用阻塞 API（如 JDBC），使用 `Schedulers.boundedElastic()` 隔离阻塞操作：
  
  ```java
  Mono.fromCallable(() -> blockingJdbcCall())
      .subscribeOn(Schedulers.boundedElastic());
  ```

---

### 关键注意事项
- **避免混用两种模型**：  
  同一应用中同时使用 Servlet 和 WebFlux 会导致不可预测的行为，如线程模型冲突、安全配置失效。
- **响应式编程学习曲线**：  
  WebFlux 需要熟悉 `Flux`、`Mono`、`Schedulers` 等概念，建议从简单路由开始逐步迁移。
- **监控与调试**：  
  WebFlux 的堆栈跟踪可能更复杂，可结合 Micrometer 和 Reactor Debug Agent 进行诊断：
  
  ```java
  @PostConstruct
  public void init() {
      ReactorDebugAgent.init();
  }
  ```

---

通过明确技术选型、严格管理依赖，可彻底避免 Bean 冲突问题，并充分发挥 WebFlux 在高并发场景下的性能优势。