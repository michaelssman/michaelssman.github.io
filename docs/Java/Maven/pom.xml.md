# Pom.xml

## hhjava 当前 POM 基线（2026-08-28）

当前项目是 Java 17、Spring Boot 3.3.7 的 Maven 多模块工程，根项目坐标为 `com.hhjava.www:hhjava:1.0-SNAPSHOT`，打包类型为 `pom`。主要受管版本如下：

| 组件 | 版本 |
| --- | --- |
| Spring Boot | 3.3.7 |
| Spring Cloud | 2023.0.5 |
| Spring Cloud Alibaba | 2023.0.1.0 |
| MyBatis-Plus | 3.5.7 |
| MinIO Java SDK | 8.5.17 |

完整 Reactor 共 9 个项目：根项目、`hhjava-common`、`hhjava-unify`、`hhjava-service`、`hhjava-user`、`hhjava-backup-file`、`hhjava-basic`、`hhjava-file-starter` 和 `hhjava-gateway`。根项目、service、basic 是聚合/父 POM；common、unify、file-starter 是共享 Jar；user、backup-file、gateway 是可运行服务。

常用验证命令：

```bash
mvn clean test
mvn -DskipTests package
mvn -pl hhjava-service/hhjava-user -am package
mvn -pl hhjava-gateway -am package
mvn -pl hhjava-service/hhjava-backup-file -am package
```

2026-08-28 执行根项目测试时，9 个 Reactor 项目均构建成功；实际执行的 6 个自动化测试全部位于 user 模块，覆盖 RSA、JWT 和 Authorization Server 基础配置。gateway、backup-file、Nacos 连接和业务接口尚无自动化测试覆盖。

完整模块关系和启动依赖见 [hhjava 项目业务与代码逻辑](../hhjava项目业务与代码逻辑.md)。

## POM 常用配置

### `<exclusions>`

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

## 多层 POM 继承

在 Maven 多模块工程中，多层 POM 继承链很常见，尤其是在多模块项目中。你的项目结构中，`hhjava-service/hhjava-user/pom.xml`会继承`hhjava/pom.xml`中的配置。这是因为Maven的继承机制允许子模块继承父模块及其祖先模块的配置。

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
                <version>${spring.boot.version}</version>
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

## 常用依赖

```xml
<!--解析json-->
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
</dependency>
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
</dependency>
```
