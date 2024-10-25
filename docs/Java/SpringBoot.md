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

Spring框架在项目中作用是Spring整合各种其他技术，让其他技术使用更加方便。

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

### 3、编写YML配置文件

springboot可以添加个性化配置。上下文路径、端口等。

#### properties

创建`项目\maven项目文件\src\main\resources\application.properties`，`application.properties`名字固定。

springBoot会自动找到这个配置文件。

例如：

```properties
server.port=8080
server.servlet.context-path=/springboot01
```

#### yml

springboot官方推荐的配置文件是yml文件，yml是用**层级来表示关系**的一种配置文件。

yml中没有标签，而是通过两个空格的**缩进来表示层级结构**。注意**冒号后有一个空格**。

创建`项目\maven项目文件\src\main\resources\application.yml`，`application.yml`文件名字application开头，不能随意动。

连数据库，把数据源信息写到配置文件里。

```yaml
server:
  port: 9999
  servlet:
    context-path: /springbootssm
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/msb?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=GMT%2B8&allowPublicKeyRetrieval=true
    driver-class-name: com.mysql.cj.jdbc.Driver	#驱动
    username: root
    password: asdf123456
mybatis:
  type-aliases-package: com.hh.pojo #加入别名配置
  mapper-locations: classpath:mybatis/*.xml	#加入映射文件位置
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

