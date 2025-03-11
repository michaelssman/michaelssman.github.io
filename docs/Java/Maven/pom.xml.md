# Pom.xml

## `<project>`

```xml
<?xml version="1.0" encoding="UTF-8"?>

<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.hh</groupId>
    <artifactId>TestSSM</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>war</packaging>
  

</project>
```

### `<parent>`

```xml
<!-- 继承Spring boot工程 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.3.9.RELEASE</version>
</parent>
```

指定该模块继承自hhjava-service父项目。

```xml
<parent>
    <artifactId>hhjava-service</artifactId>
    <groupId>com.hhjava.www</groupId>
    <version>1.0-SNAPSHOT</version>
</parent>
```

### `<modules>`

加入子模块

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

### `<properties>`

定义一些项目属性，如Java版本、编码格式和Spring Boot版本。

```xml
<properties>
    <java.version>1.8</java.version>
    <!-- 项目源码及编译输出的编码 -->
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <!-- 项目编译JDK版本 -->
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
    <!-- 依赖包版本管理 -->
    <spring-boot.version>2.6.13</spring-boot.version>
</properties>
```

### `<dependencies>`

导入依赖，引入各种jar包的坐标都在这里面写。

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

#### `<exclusions>`

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

### `<dependencyManagement>`

管理依赖版本，通常用于多模块项目的父POM中。子模块可以引用这些依赖项，而不必指定版本号。

`<dependencyManagement>` 中的 `<dependencies>` 和直接的 `<dependencies>` 有以下区别：

1. **`<dependencyManagement>` 中的 `<dependencies>`**:
   - 用于定义项目中所有模块共享的依赖版本和范围。
   - 这些依赖不会自动引入到项目中，而是提供一个版本管理的参考。
   - 子模块在声明依赖时可以不指定版本号，直接继承父模块中定义的版本号。

2. **直接的 `<dependencies>`**:
   - 用于定义当前模块需要的具体依赖。
   - 这些依赖会自动引入到项目中，供当前模块使用。
   - 必须明确指定每个依赖的版本号，除非该版本号已经在 `<dependencyManagement>` 中定义。

`<dependencyManagement>` 中的 `<dependencies>` 是为了统一管理依赖版本，而直接的 `<dependencies>` 是为了实际引入依赖。

### `<build>`

构建过程中的插件配置，包括Maven编译插件和Spring Boot插件。

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

### `<repositories>`

Maven 中央仓库

```xml
<repositories>
    <repository>
        <id>central</id>
        <url>https://repo.maven.apache.org/maven2</url>
        <releases>
            <enabled>true</enabled>
        </releases>
        <snapshots>
            <enabled>false</enabled>
        </snapshots>
    </repository>
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
    <!--阿里云镜像-->
    <repository>
        <id>alimaven</id>
        <name>aliyun maven</name>
        <url>https://maven.aliyun.com/nexus/content/groups/public/</url>
        <releases>
            <enabled>true</enabled>
        </releases>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```

## 多重继承

在Maven中，多重继承的结构是常见的，尤其是在多模块项目中。你的项目结构中，`hhjava-service/hhjava-user/pom.xml`会继承`hhjava/pom.xml`中的配置。这是因为Maven的继承机制允许子模块继承父模块及其祖先模块的配置。

### 继承的内容

1. **依赖管理**：如果`hhjava/pom.xml`中有`<dependencyManagement>`，那么`hhjava-service/hhjava-user/pom.xml`可以继承其中声明的依赖版本。

2. **插件管理**：类似地，`<build>`中的插件配置也会被继承。

3. **属性**：`<properties>`中定义的属性可以被子模块使用。
   1. 在顶层 POM (`hhjava/pom.xml`) 中设置这些属性后，子模块 POM (`hhjava-service/hhjava-user/pom.xml`) 通常不需要重复设置这些属性，因为它们会被自动继承。但是，子模块可以覆盖这些属性，如果需要不同的配置。

4. **其他配置**：如`<repositories>`、`<distributionManagement>`等。

### 使用建议

1. **集中管理版本**：
   - 在顶层POM（`hhjava/pom.xml`）中使用`<dependencyManagement>`来定义依赖的版本。这样，所有子模块都能引用这些依赖而无需重复指定版本。

2. **模块化结构**：
   - 在中间层（如`hhjava-service/pom.xml`），可以定义与该层相关的特定依赖和插件。

3. **子模块配置**：
   - 在子模块（如`hhjava-service/hhjava-user/pom.xml`），只需声明特定于该模块的依赖和配置。

### 示例

**顶层 POM (`hhjava/pom.xml`)**：

```xml
<project>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
                <version>3.0.0</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

**中间层 POM (`hhjava-service/pom.xml`)**：

```xml
<project>
    <parent>
        <artifactId>hhjava</artifactId>
        <groupId>com.hhjava.www</groupId>
        <version>1.0-SNAPSHOT</version>
    </parent>
</project>
```

**子模块 POM (`hhjava-service/hhjava-user/pom.xml`)**：

```xml
<project>
    <parent>
        <artifactId>hhjava-service</artifactId>
        <groupId>com.hhjava.www</groupId>
        <version>1.0-SNAPSHOT</version>
    </parent>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
```

这样，`hhjava-service/hhjava-user`模块可以直接使用`spring-boot-starter-web`，而无需在每个子模块中指定版本号。通过这种结构，项目的依赖管理变得更加简洁和一致。
