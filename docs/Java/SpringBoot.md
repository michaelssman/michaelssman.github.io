# SpringBoot

Spring Boot是Spring公司的一个顶级项目，和Spring Framework是一个级别的。

Spring Boot实际上是利用Spring Framework 4 自动配置特性完成。编写项目时不需要编写xml文件，简化配置。

发展到现在，Spring Boot已经具有很很大的生态圈，各种主流技术已经都提供了Spring Boot的启动器。

**为什么使用springBoot**

spring问题：要写大量xml配置。

核心思想：约定大于配置。默认配置好了。

springBoot不止可以整合SSM，还可以整合其它框架。

## 启动器

Spring框架在项目中作用是Spring整合各种其他技术，让其他技术使用更加方便。Spring Boot的启动器实际上就是一个依赖。这个依赖中包含了整个这个技术的相关jar包，还包含了这个技术的自动配置，以前绝大多数XML配置都不需要配置了。以后每次使用Spring Boot整合其他技术时首先需要考虑导入启动器。

## 启动类

Spring Boot的启动类的作用是启动Spring Boot项目，是基于Main方法来运行的。

**启动类与启动器区别**

启动类表示项目的启动入口

启动器表示jar包的坐标

## SpringBoot整合SSM（SpringMVC+Mybatis）

### 1、创建maven工程

普通的maven的jar工程就可以。

### 2、pom.xml导入依赖

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.msb</groupId>
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

springboot支持`.properties`配置文件。创建`项目\maven项目文件\src\main\resources\application.properties`，application.properties名字固定。

例如：

**properties中：**

```properties
server.port=8080
```

springboot官方推荐的配置文件是yml文件，yml是用**层级来表示关系**的一种配置文件。

yml中没有标签，而是通过两个空格的缩进来表示层级结构。

**yml中：**

连数据库，把数据源信息写到配置文件里。

```yaml
server:
  port: 9999
  servlet:
    context-path: /springbootssm
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/msb?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=GMT%2B8&allowPublicKeyRetrieval=true
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: root
mybatis:
  type-aliases-package: com.msb.pojo
  mapper-locations: classpath:mybatis/*.xml
```

driver-class-name：驱动

**层级结构怎么找（SpringBoot常见配置，查看官网文档）：**

https://docs.spring.io/spring-boot/docs/2.7.6/reference/html/application-properties.html#appendix.application-properties

注意：文件名字为：`application.yml`，文件名字application开头，不能随意动。

注意冒号后空格。

yml配置文件和properties配置文件可以并存。

### 4、编写实体类，配置文件中加入别名

项目|src|main|java|创建com.msb.pojo包里面放实体类

在application.yml文件加入`mybatis: type-aliases-package: com.msb.pojo`

### 5、mapper层

#### 5.1、定义mapper接口

#### 5.2、定义mapper.xml映射文件

在resource下新建mybatis文件夹，mapper.xml文件名没有要求了，不需要和接口名完全对应了，是根据namespace去找接口。但是最好还是和接口名字保持一致

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.msb.mapper.BookMapper">
    <select id="selectAll" resultType="book">
        select * from t_book
    </select>
</mapper>
```

### 6、配置文件中加入映射文件位置：

mybatis:  mapper-locations: classpath:mybatis/*.xml

### 7、定义启动类，在启动类加入mapper的包扫描

基于mian方法，启动。

```java
@SpringBootApplication	//注解 标识是启动类
@MapperScan("com.msb.mapper")	//扫描mapper包
public class MyApplication {  
    public static void main(String[] args) { 
        SpringApplication.run(MyApplication.class,args);  //扫描同包和子包下的注解
    }
}
```

### 8、service层代码编写

创建包com.hh.service，包下面创建文件Interface接口

```java
package com.msb.service;

import java.util.List;

public interface BookService {
    List findAll();
}
```

编写上面接口的实现类

创建包com.hh.impl，包下面创建接口的实现类

```java
package com.msb.service.impl;

import com.msb.mapper.BookMapper;
import com.msb.service.BookService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service	//注解构建对象
public class BookServiceImpl implements BookService {
    @Autowired	//注解 自动注入
    private BookMapper bookMapper;

    public List findAll() {
        return bookMapper.selectAll();
    }

}
```

### 9、controller层

开发一个Controller

```java
package com.msb.controller;

import com.msb.pojo.Book;
import com.msb.service.BookService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;

@Controller //通过注解 创建对象
public class BookController {
    @Autowired
    private BookService bookService;

    @RequestMapping(value = "/findAllBooks", produces = "text/html;charset=utf-8")
    @ResponseBody
    public String findAll() {
        List list = bookService.findAll();
        System.out.println("一共有几本书籍：" + list.size());
        //定义一个字符串用来接收响应的字符串：
        String books = "";
        for (int i = 0; i < list.size(); i++) {
            Book book = (Book) list.get(i);
            books = books + book.getName();
            books = books + book.getAuthor();
        }
        return books;
    }

}
```

运行，浏览器访问`http://localhost:9999/firstController`测试

