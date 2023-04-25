# Maven

Maven是使用Java语言编写的基于项目对象模型（POM）**项目管理工具软件**。开发者可以通过一小段描述信息来管理项目构建、报告和文档。使用Maven可以更好的帮助我们完成项目的管理。

## 非Maven项目的缺点

1. 项目中的jar包资源需要我们自己从网上下载后，手动导入到项目中使用，不好管理。
2. jar包版本控制麻烦

## Maven的仓库

中央仓库(Central Repository):Maven官方服务器。里面存放了绝大多数市面上流行的jar。允许用户注册后，上传自己的项目到官方服务器。网址在国外。https://mvnrepository.com/

本地仓库(Local Repository): 本机的文件夹作为本地仓库，本地仓库指本机的一份拷贝，用来缓存远程下载，包含你尚未发布的临时构件。

镜像仓库(Mirror Repository): 对于国内来说，访问国外的Maven仓库会特别慢。镜像仓库就是另一台备份/复制了中央仓库的服务器。平时使用时国内开发者多使用阿里云镜像或华为云镜像，这样可以大大提升从中央仓库下载资源的速度。但它的角色仍然是一个远程库。

### 查找依赖流程

- maven项目 找依赖
- 先在本地仓库找
  - 没找到
    - 配置文件`setting.xml`中是否指定镜像仓库
      - 指定了就在镜像仓库找
      - 没指定就在中央仓库找
  - 找到了
    - 找到后放入本地仓库以备下次使用

## Maven的资源坐标

- GroupId: 一般是逆向公司域名 com.hh。同一个公司的GroupId都是相同的。
- ArtifactId: 一般是项目(jar)名 mysql-connector-java。
- Version: 版本号 8.0.28。

## Maven的下载和安装

从maven官网下载Maven,官网地址:[https://maven.apache.org](https://maven.apache.org/)

## Maven的常用配置

### 本地仓库

1.随便选择一个目录作为本地仓库，可以使用我提供的本地仓库

2.在配置文件`C:\Users\micha\hhsoftware\apache-maven-3.9.1\conf\settings.xml`中指定本地仓库位置

`<localRepository>D:/repository</localRepository>`

### 镜像仓库

指定阿里云镜像仓库：

```xml
<mirrors> 
    <mirror>  
        <id>alimaven</id> 
        <name>aliyun maven</name>   
        <url>http://maven.aliyun.com/nexus/content/groups/public/</url>   
        <mirrorOf>central</mirrorOf> 
    </mirror>
</mirrors>
```

### 配置JDK

在使用Maven后，项目由Maven来完成编译和打包运行，需要指定使用的JDK版本。

17换成1.8。

```xml
    <profile>
      <id>jdk-17</id>
      <activation>
        <activeByDefault>true</activeByDefault>
        <jdk>17</jdk>
      </activation>
      <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <maven.compiler.compilerVersion>17</maven.compiler.compilerVersion>
      </properties>
    </profile>
```

### 在IDEA中配置Maven

maven：换为低版本3.6.3

JDK：换为低版本8

### 创建Maven项目

#### IDEA

新建项目 --> Empty Project

Empty Project：相当于一个大文件夹容器，里面放多个项目。

`File | Settings | Build, Execution, Deployment | Build Tools | Maven`

![image-20230419215252262](assets/image-20230419215252262.png)

新建Mudule模块，ModuleSDK选择1.8版本的。

![image-20230419215721836](assets/image-20230419215721836.png)

给3个坐标：

![image-20230419215923379](assets/image-20230419215923379.png)

选择手动导入

![image-20230420220415684](assets/image-20230420220415684.png)

在`项目|module|src|main|java|`文件夹下新建包Package（例`com.hh.test01`），包下面创建类。

## pom.xml文件中添加依赖包

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.hh</groupId>
    <artifactId>TestJarProject</artifactId>
    <version>1.0-SNAPSHOT</version>

    <dependencies>
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.28</version>
        </dependency>
    </dependencies>
</project>
```

选择`import change`

