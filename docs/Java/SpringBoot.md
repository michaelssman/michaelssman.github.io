# SpringBoot

Spring Boot是Spring公司的一个顶级项目，和Spring Framework是一个级别的。

Spring Boot利用Spring Framework 4 自动配置特性完成。编写项目时不需要编写xml文件，简化配置。

Spring Boot具有很大的生态圈，各种主流技术已经都提供了Spring Boot的**启动器**。

**为什么使用springBoot**

spring问题：编写大量xml配置。管理依赖，版本，坐标等。

核心思想：**约定大于配置**。默认配置好了通用配置。程序员只需要关注业务代码。

springBoot不止可以整合SSM，还可以整合其它框架。

## 启动器和启动类

**启动器**

Spring框架在项目中作用是：整合各种其他技术，让其他技术使用更加方便。

Spring Boot的启动器实际上就是一个依赖。**这个依赖中包含了整个这个技术的相关jar包，还包含了这个技术的自动配置**，以前绝大多数XML配置都不需要配置了。以后每次使用Spring Boot整合其他技术时首先需要考虑导入启动器。

**启动类**

Spring Boot的启动类的作用是启动Spring Boot项目。

**启动类与启动器区别**

启动类表示项目的启动入口

启动器表示jar包的坐标

## SpringBoot整合SSM

### 1、创建maven工程

用SpringBoot创建普通的maven的jar工程就可以运行web应用。

### 2、pom.xml导入依赖

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.hh</groupId>
    <artifactId>TestSpringBoot</artifactId>
    <version>1.0-SNAPSHOT</version>
    
    <!--选择springboot的版本-->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>2.7.6</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <!--整合springmvc用到的包，添加启动器-->
    <dependencies>
        <!--添加springmvc的启动器-->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.7.6</version>
        </dependency>
        <!--依赖 添加mybatis的启动器-->
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>2.1.3</version>
        </dependency>
        <!--mybatis链接数据库需要mysql驱动-->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.21</version>
        </dependency>
    </dependencies>

</project>
```

### 3、配置文件

springboot可以添加个性化配置。上下文路径、端口等。

#### application.properties

创建`项目\maven项目文件\src\main\resources\application.properties`，`application.properties`名字固定。

springBoot会自动找到这个配置文件。

例如：

```properties
server.port=8080
server.servlet.context-path=/springboot01
```

#### application.yml

springboot官方推荐的配置文件是yml文件，yml是用**层级来表示关系**的一种配置文件。

yml中没有标签，而是通过两个空格的**缩进来表示层级结构**。注意**冒号后有一个空格**。

创建`项目\maven项目文件\src\main\resources\application.yml`，`application.yml`文件名字application开头，不能随意动。

spring配置：连数据库，把数据源信息写到配置文件里

```yaml
server:
  port: 9999
  servlet:
    context-path: /springbootssm
spring:
	#mysql驱动
  datasource:
	  driver-class-name: com.mysql.cj.jdbc.Driver	#驱动
    url: jdbc:mysql://ip地址:端口/数据库名?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=GMT%2B8&allowPublicKeyRetrieval=true
    username: root
    password: asdf123456
```

mybatis配置：

```yaml
mybatis:
  type-aliases-package: com.hh.pojo #加入别名配置
  mapper-locations: classpath:mybatis/*.xml	#加入映射文件位置
```

mybatis-plus配置：

```yaml
# 设置Mapper接口所对应的XML文件位置，如果你在Mapper接口中有自定义方法，需要进行该配置
mybatis-plus:
  # 设置别名包扫描路径，通过该属性可以给包中的类注册别名
  type-aliases-package: com.heima.model.user.pojos
  mapper-locations: classpath*:mapper/*.xml
```

**层级结构怎么找（SpringBoot常见配置，查看官网文档）：**

https://docs.spring.io/spring-boot/docs/2.7.6/reference/html/application-properties.html#appendix.application-properties

yml配置文件和properties配置文件可以并存。

### 4、实体类

#### 4.1、yml配置文件加入别名配置

```yaml
mybatis: 
	type-aliases-package: com.hh.pojo
```

对数据库表操作的话，代码需要实体类与数据库表对应。

### 5、mapper层

 [Mapper数据库连接层](Java分层/Mapper数据库连接层.md) 

#### 5.1、mapper接口

#### 5.2、mapper.xml映射文件

在resource下新建mybatis文件夹，mapper.xml文件名没有要求了，不需要和接口名完全对应了，是根据namespace去找接口。但是最好还是和接口名字保持一致。

#### 5.3、yml配置文件中加入映射文件位置

```yaml
mybatis:  
	mapper-locations: classpath:mybatis/*.xml
```

### 6、定义启动类，在启动类加入mapper的包扫描

**启动类基于mian方法来运行的。**

在`项目\TestSpringBoot\src\main\java`文件夹下创建`com.hh.TestSpringBootApplication`

```java
package com.hh;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication //注解 标识当前类是一个启动类
@MapperScan("com.hh.mapper")//扫描mapper包
public class TestSpringBootApplication {
    public static void main(String[] args) {
        SpringApplication.run(TestSpringBootApplication.class,args);
        //扫描TestSpringBootApplication类同包和子包下的注解，service层mapper层controller层都会扫到。
    }
}
```

### 7、service层

 [Service业务层](Java分层/Service业务层.md) 

### 8、controller层

 [Controller控制层](Java分层/Controller控制层.md) 

### 9、运行

浏览器访问`http://localhost:9999/findBooks`测试

## spring-boot-starter-XXX

使用spring boot**自动配置**的starer，可以简化代码，并使其正常工作。当在这个类路径上检测到这个特定的jar文件的时候，将激活这个自动化的配置。

最简单的使用方法就是依赖spring-boot-starters，例如要与redis进行集成，可以像下面的这样配置:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

在这些启动器的帮助下，一些繁琐的配置可以很好的集成在一起，并协同工作。并且都是通过了测试和验证的。

### spring-boot-starter

- **功能**: 这是一个基础的启动器，用于支持 Spring Boot 应用程序的核心功能。
- 包含的依赖:
  - Spring 核心库。
  - 日志（如 SLF4J 和 Logback）。
- **使用场景**: 适用于任何需要 Spring Boot 基础功能的应用，不限于 Web 应用。

### spring-boot-starter-web

- **功能**: 这是一个 Spring Boot 启动器（starter），用于快速构建基于 Spring 的 **Web 应用程序**。
- **包含的依赖**:
  - Spring MVC: 用于构建基于 MVC 的 Web 应用。
  - Tomcat: 默认的嵌入式服务器。
  - Jackson: 用于 JSON 处理。
  - Hibernate Validator: 用于验证框架。
  
#### 使用场景

- **Web 应用开发**: 适合开发 RESTful Web 服务和传统的 Web 应用。
- **快速启动**: 提供了一个开箱即用的 Web 应用开发环境，减少了配置和依赖管理的复杂性。

这样，Spring Boot 会自动配置一个 Web 环境，并提供所需的基础设施来构建和运行你的 Web 应用。

### 创建自己的spring boot starter

像一些公共的组件，可以抽象出自己的starter。比如统一的API日志、国际化、上传文件、支付、redis操作、统一的序列化、统一的权限验证等等，都可以封装成一个starter，供其它项目去引用。因为这些都是基于spring boot的自动化配置，使用起来也非常方便。

## spring.factories

`spring.factories` 文件是 Spring Boot 用于自动配置的一个关键文件。它位于 `META-INF` 目录下，包含了许多 Spring Boot 自动配置类的全限定名。

Spring Boot 在启动时会扫描 `META-INF/Spring.factories` 文件，并根据 `org.springframework.boot.autoconfigure.EnableAutoConfiguration` 键的值加载相应的自动配置类。这使得你可以通过简单的配置来启用和配置第三方库，而不需要在代码中显式地进行配置。

例如`Spring.factories` 文件的内容：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.hh.common.swagger.SwaggerConfiguration
```

这个配置的作用是告诉 Spring Boot 在启动时自动加载 `com.hh.common.swagger.SwaggerConfiguration` 类。`SwaggerConfiguration` 类使用了 `@Configuration` 注解，表示它是一个配置类，并且使用了 `@EnableSwagger2` 注解来启用 Swagger2。

## 其它微服务使用common

要在 `hhjava-user` 服务中使用 `hhjava-common` 中的 Swagger 配置，你需要确保 `hhjava-common` 模块已经作为依赖添加到 `hhjava-user` 模块中，并且 `hhjava-common` 中的 `SwaggerConfiguration` 已经被正确加载。

**在 `hhjava-user` 的 `pom.xml` 中添加 `hhjava-common` 依赖**：

```xml
<dependencies>
    <!-- 引入依赖模块 -->
    <dependency>
        <groupId>com.hhjava.www</groupId>
        <artifactId>hhjava-common</artifactId>
        <version>1.0-SNAPSHOT</version>
    </dependency>
</dependencies>
```
