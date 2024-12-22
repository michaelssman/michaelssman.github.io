# Pom.xml

## 添加依赖包

引入各种jar包的坐标都在这里面写。

```xml
<?xml version="1.0" encoding="UTF-8"?>

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.hh</groupId>
    <artifactId>TestSSM</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>war</packaging>

    <!-- 里面添加各种依赖 -->	
    <dependencies>
        <!-- 【1】mybatis的依赖 -->
        <dependency>
            <groupId>org.mybatis</groupId>
            <artifactId>mybatis</artifactId>
            <version>3.5.9</version>
        </dependency>
        <!-- 【2】连接mysql的依赖 -->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.28</version>
        </dependency>
        <!-- 【3】log4j的依赖 -->
        <dependency>
            <groupId>log4j</groupId>
            <artifactId>log4j</artifactId>
            <version>1.2.17</version>
        </dependency>
        <!-- 【4】spring的核心依赖 -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-context</artifactId>
            <version>5.3.16</version>
        </dependency>
        <!-- 【5】springjdbc依赖-->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-jdbc</artifactId>
            <version>5.3.16</version>
        </dependency>
        <!-- 【6】spring整合mybatis的依赖 -->
        <dependency>
            <groupId>org.mybatis</groupId>
            <artifactId>mybatis-spring</artifactId>
            <version>2.0.7</version>
        </dependency>
        <!-- 【7】springwebmvc的依赖 -->
        <!-- 依赖了Spring框架核心功能的5个依赖以及Spring整合Web的依赖spring-web -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-webmvc</artifactId>	<!--SpringMVC-->
            <version>5.3.16</version>
        </dependency>
    </dependencies>

</project>
```

## 加入插件

在`pom.xml`的`<build>`中添加Tomcat插件。

```xml
<!-- 加入tomcat插件 -->
<pluginRepositories>
    <pluginRepository>
        <id>mvnrepository</id>
        <url>https://artifacts.alfresco.com/nexus/content/repositories/public/</url>
    </pluginRepository>
</pluginRepositories>
<build>
    <plugins>
        <!-- Tomcat插件 -->
        <plugin>
            <groupId>org.apache.tomcat.maven</groupId>
            <artifactId>tomcat8-maven-plugin</artifactId>
            <version>3.0-r1756463</version>
            <configuration>
                <port>8888</port>	<!-- 端口-->
                <path>/ssm</path>	<!--指定项目的上下文路径-->
            </configuration>
        </plugin>
    </plugins>
</build>
```

## 加入子模块

```xml
<modules>
    <module>heima-leadnews-user</module>
    <module>heima-leadnews-article</module>
    <module>heima-leadnews-wemedia</module>
    <module>heima-leadnews-schedule</module>
    <module>heima-leadnews-search</module>
    <module>heima-leadnews-admin</module>
    <module>heima-leadnews-behavior</module>
</modules>
```

## `<exclusions>`

忽略的包，因为其它地方已经导入过了。

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams</artifactId>
    <exclusions>
        <exclusion>
            <artifactId>connect-json</artifactId>
            <groupId>org.apache.kafka</groupId>
        </exclusion>
        <exclusion>
            <groupId>org.apache.kafka</groupId>
            <artifactId>kafka-clients</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

## Maven 中央仓库

```xml
<repositories>
    <repository>
        <id>spring</id>
        <url>https://maven.aliyun.com/repository/spring</url>
        <releases>
            <enabled>true</enabled>
        </releases>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
