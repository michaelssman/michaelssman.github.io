# SpringBoot

**springBoot概念简介**

Spring Boot是Spring公司的一个顶级项目，和Spring Framework是一个级别的。

Spring Boot实际上是利用Spring Framework 4 自动配置特性完成。编写项目时不需要编写xml文件。发展到现在，Spring Boot已经具有很很大的生态圈，各种主流技术已经都提供了Spring Boot的启动器。

**为什么使用springBoot**

spring问题：要写大量xml配置。

核心思想：约定大于配置。默认配置好了。

springBoot不止可以整合SSM，还可以整合其它框架。

**启动器、启动类**

**什么是启动器**

Spring框架在项目中作用是Spring整合各种其他技术，让其他技术使用更加方便。Spring Boot的启动器实际上就是一个依赖。这个依赖中包含了整个这个技术的相关jar包，还包含了这个技术的自动配置，以前绝大多数XML配置都不需要配置了。以后每次使用Spring Boot整合其他技术时首先需要考虑导入启动器。

**什么是启动类**

Spring Boot的启动类的作用是启动Spring Boot项目，是基于Main方法来运行的。

**启动类与启动器区别**

启动类表示项目的启动入口

启动器表示jar包的坐标

## SpringBoot项目搭建

**案例：整合SpringMVC**

（1）创建maven工程

普通的maven的jar工程就可以。

（2）pom.xml

```xml
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
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.7.6</version>
        </dependency>
```

开发一个Controller

```java
@Controller //通过注解 创建对象
public class MyController { 
    @RequestMapping("/firstController") 
    @ResponseBody  
    public String firstController(){ 
        return "hello springboot"; 
    }
}
```

启动类编写

基于mian方法，启动。

```java
@SpringBootApplicationpublic//注解 标识是启动类
class TestSpringBootApplication { 
    public static void main(String[] args) {   
        SpringApplication.run(TestSpringBootApplication.class, args);//扫描同包和子包下的注解
    }
}
```

运行，浏览器访问测试



