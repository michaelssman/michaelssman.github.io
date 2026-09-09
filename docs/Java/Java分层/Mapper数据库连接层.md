# Mapper 数据库访问层

本文先讲原理和 hhjava 对应关系，第 7 节提供从建表到 HTTP 查询的完整练习。第一次学习时，不必先理解登录协议。

### 阅读前先认识这些词

| 词语 | 基础含义 |
| --- | --- |
| 数据库、表、行、列 | 数据库管理数据；表描述一种数据；行是一条记录；列是记录的属性，例如书籍的 id 和名称 |
| 主键 | 唯一标识一条记录的字段或字段组合；本练习使用 Long 类型的 id |
| SQL（Structured Query Language，结构化查询语言） | 操作关系数据库的语言；SELECT 查询，INSERT 新增，UPDATE 修改，DELETE 删除 |
| JDBC（Java Database Connectivity，Java 数据库连接） | Java 访问关系数据库的标准接口；驱动负责和具体数据库通信 |
| DataSource（数据源） | 为程序提供数据库连接的对象；连接池复用连接，减少每次重新连接的成本 |
| ResultSet（结果集） | JDBC 查询获得的行列结果；MyBatis 根据映射规则转换成 Java 对象 |
| DAO（Data Access Object，数据访问对象） | 对数据访问职责的抽象；Mapper 是本项目实现这类职责的接口形式 |
| CRUD（Create、Read、Update、Delete） | 新增、读取、修改、删除的合称 |
| XML（Extensible Markup Language，可扩展标记语言） | 使用成对标签表达结构；本文用于把 SQL 与 Java 方法关联 |
| 事务 | 把多个数据库操作作为一组提交或回滚；例如注册的账号和角色关联应一起成功 |

## 1. Mapper 是什么

Mapper 是数据访问接口：Java 方法表达“要查什么或写什么”，MyBatis 负责执行绑定的 SQL，并把结果转换成 Java 对象。

在三层架构中，Controller 处理 HTTP，Service 编排业务和事务，Mapper 负责数据库访问。不要把登录规则、密码比较或 HTTP 响应放到 Mapper 中。

```text
Controller → Service → Mapper → 数据库
                       ↑
                接口方法 + SQL 映射
```

接口由 MyBatis 创建代理实现，通常不需要自己写 `RoleMapperImpl`，也不需要业务代码手工调用 `SqlSession.selectList("某个字符串")`。

## 2. MyBatis 和 MyBatis-Plus 如何配合

MyBatis 可以通过 XML 或注解定义 SQL；MyBatis-Plus 的 `BaseMapper<T>` 进一步提供常用 CRUD 方法。当前 hhjava 两种方式一起使用：

- 简单主键查询、插入等使用 `BaseMapper` 提供的方法。
- 用户名查询、角色关联查询等使用明确的自定义 Mapper 方法和 XML。
- 不是每个 Mapper 都必须有一个 XML 文件。

例如，`UserRoleMapper extends BaseMapper<UserRole>` 供注册流程调用 `insert(userRole)`。当前没有自定义关联查询方法，因此不需要对应的 `UserRoleMapper.xml`。

## 3. 用户角色怎样一次查询出来

当前涉及三张表：

| 表 | 含义 |
| --- | --- |
| `user` | 用户账号 |
| `role` | 角色定义 |
| `user_role` | 用户与角色的关联，包含 `user_id`、`role_id` |

一个用户可以对应多个角色，同一角色也可以属于多个用户，所以用关联表表达多对多关系。

`RoleMapper` 中的方法声明为：

```java
// 方法节选：参数名与 XML 中的 #{userId} 对应。
List<Role> findRolesByUserId(@Param("userId") Long userId);
```

`RoleMapper.xml` 中的当前查询：

```xml
<select id="findRolesByUserId" resultMap="BaseResultMap">
    select distinct r.id, r.name
    from role r
    inner join user_role ur on ur.role_id = r.id
    where ur.user_id = #{userId,jdbcType=BIGINT}
    order by r.id
</select>
```

理解这条 SQL：

1. 根据 `user_id` 筛选该用户的关联记录。
2. 使用 `role_id = r.id` 找到实际存在的角色。
3. `distinct` 避免重复关联让同一个角色返回多次。
4. `order by r.id` 提供稳定顺序；没有匹配角色时，集合查询返回空列表。

这里“角色一次查询”不等于“整个登录只执行一次 SQL”。`UserServiceImpl` 先查询用户，再通过这条 JOIN 查询角色，合计两条账号读取 SELECT；登录还包含密码计算、会话写入等操作。

移动端密码认证成功后直接复用 `AuthenticatedUser` 中的用户 ID 和角色快照，不重复调用用户查询。Refresh Token 刷新则仍查询当前用户和角色。原因见 [认证和授权](../认证授权和网关/认证和授权.md)。

## 4. 接口和 XML 怎么对应

当前文件位置如下，均相对于 hhjava 根目录：

```text
hhjava-service/hhjava-user/src/main/
├── java/com/hh/user/mapper/
│   ├── UserMapper.java
│   ├── RoleMapper.java
│   └── UserRoleMapper.java
└── resources/com/hh/user/mapper/
    ├── UserMapper.xml
    └── RoleMapper.xml
```

需要同时满足：

- Mapper 接口被项目的 MyBatis Mapper 扫描发现。
- XML 的 `namespace` 是接口全限定名，例如 `com.hh.user.mapper.RoleMapper`。
- SQL 标签的 `id` 与接口方法名一致。
- `resultMap="BaseResultMap"` 引用本 XML 中实际定义的映射，负责结果列到 `Role` 属性的对应。
- XML 被打包到 classpath，且符合应用实际的 Mapper XML 加载配置。

`resources` 内容会按 Maven 资源规则进入产物。Spring Boot 集成不要求每个项目都另外手工维护 `mybatis.xml`；先检查当前项目配置，不要同时添加重复的加载入口。

## 5. 参数安全与常见错误

`#{userId}` 通过预编译参数绑定传值，不是把请求字符串拼入 SQL。`${...}` 是文本替换，不要用它直接接收用户输入作为查询条件。[MyBatis Mapper XML 参数说明](https://mybatis.org/mybatis-3/sqlmap-xml.html)

遇到 `Invalid bound statement`，按顺序检查扫描、namespace、方法名、XML 资源加载和构建产物，而不是直接增加一个无内容的 XML 文件。

新增业务时优先判断 `BaseMapper` 是否已经提供所需操作；确实需要关联或复杂筛选时再写自定义 SQL。事务应放在 Service，保证注册中的用户记录与角色关联一起成功或回滚。

## 6. 验证步骤

在 hhjava 根目录执行：

```sh
mvn -pl hhjava-service/hhjava-user -am test
```

检查多角色、重复关联、无角色、孤立关联的查询结果，并确认 `BaseMapper` 的关联插入等操作仍可用。内存数据库测试不能替代真实 MySQL 的索引、SQL 执行计划和 Flyway 验证；是否需要新增索引应依据实际表结构与执行计划决定。

## 7. 动手：写一个可运行的书籍查询接口

目标：GET `/books?minPrice=30` 从数据库筛选书籍，返回 JSON。先完成 [Spring Boot 第 9 节](../SpringBoot.md) 的 `hhjava-learning-basics`，下文文件路径相对这个**独立学习工程**，操作都在 Mac。不向 hhjava 或远端 MySQL 新增表。

### 7.1 添加依赖

在学习工程 `pom.xml` 已有的 `<dependencies>` 内追加下面两个 dependency，不新建第二个 dependencies 标签：

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.7</version>
</dependency>
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

MyBatis-Plus 版本与当前 hhjava 对照，不表示最新版本。Boot 3 使用对应的 boot3 Starter，不再同时加另一套 MyBatis Starter。H2 是可嵌入 Java 进程的关系数据库，本例使用内存模式，退出进程后数据消失。IDEA 重新加载 Maven，确认依赖下载完成。[MyBatis-Plus 官方接入说明](https://baomidou.com/en/getting-started/)

### 7.2 配置数据源并准备演示表

将学习工程的配置替换为以下**完整文件**，不要把它原样追加到已有 YAML 后造成重复 `spring` 键。

文件：`src/main/resources/application.yml`

```yaml
spring:
  application:
    name: hhjava-learning-basics
  datasource:
    url: jdbc:h2:mem:learning;DB_CLOSE_DELAY=-1
    username: sa
    password: ""
    driver-class-name: org.h2.Driver
  sql:
    init:
      mode: always
server:
  address: 127.0.0.1
  port: 18080
mybatis-plus:
  mapper-locations: classpath:/mapper/*.xml
```

`jdbc:h2:mem:learning` 指本进程的 learning 内存库，不连接 ECS；`DB_CLOSE_DELAY=-1` 让连接暂时关闭时保留内存库，进程退出仍丢失。空密码仅用于此不开放控制台的内存练习，不能用作 MySQL/服务器配置。`mode: always` 让 Boot 加载后面的建表及数据文件；正式 hhjava 使用 Flyway 迁移，不能复制这套启动初始化方案覆盖已有数据库。

文件：`src/main/resources/schema.sql`

```sql
CREATE TABLE IF NOT EXISTS book (
    id BIGINT PRIMARY KEY,
    book_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

文件：`src/main/resources/data.sql`

```sql
MERGE INTO book (id, book_name, price) KEY(id)
VALUES (1, 'Java 入门', 29.90), (2, 'Spring Boot 入门', 49.90);
```

`DECIMAL(10,2)` 保留两位小数，Java 使用 `BigDecimal` 对应，避免用二进制浮点表示金额引入误差。`MERGE ... KEY` 是本练习的 H2 写法，按主键插入或更新便于重复初始化，不能当作 MySQL 通用语句。

### 7.3 创建实体

文件：`src/main/java/com/example/learning/book/Book.java`

```java
package com.example.learning.book;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;

@TableName("book")
public class Book {
    @TableId
    private Long id;
    @TableField("book_name")
    private String name;
    private BigDecimal price;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
}
```

数据库的 `book_name` 与 Java 的 `name` 不相同：`@TableField` 指导 MyBatis-Plus 生成的 SQL，下一步的 resultMap 指导自定义 SQL 的结果映射，两者各有用途。getter/setter 是读取、设置属性的方法，先显式写出以便理解；不是不装 Lombok 就无法使用 MyBatis。

### 7.4 编写 Mapper 接口和 XML

文件：`src/main/java/com/example/learning/book/BookMapper.java`

```java
package com.example.learning.book;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import java.math.BigDecimal;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface BookMapper extends BaseMapper<Book> {
    List<Book> findByMinPrice(@Param("minPrice") BigDecimal minPrice);
}
```

`interface` 只声明“能做什么”；框架运行时生成代理对象，调用接口时代理寻找 SQL。`@Mapper` 让集成组件识别它，也可在配置类统一使用 `@MapperScan`，本例只用前者。`BaseMapper<Book>` 表示通用增删改查针对 Book，不需要手工实现 `selectById`。

文件：`src/main/resources/mapper/BookMapper.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.learning.book.BookMapper">
    <resultMap id="BookResultMap" type="com.example.learning.book.Book">
        <id column="id" property="id"/>
        <result column="book_name" property="name"/>
        <result column="price" property="price"/>
    </resultMap>
    <select id="findByMinPrice" resultMap="BookResultMap">
        SELECT id, book_name, price
        FROM book
        WHERE price &gt;= #{minPrice}
        ORDER BY id
    </select>
</mapper>
```

逐项对照：namespace 对应接口全名；select 的 id 对应方法名；`@Param("minPrice")` 对应 `#{minPrice}`；resultMap 把行映射到 Book。`&gt;` 是 XML 中 `>` 的实体写法，不改变 SQL 比较含义。

如果 SQL 使用 `book_name AS name` 且其他列与属性已匹配，也可以使用 `resultType="com.example.learning.book.Book"`，不必再写 resultMap；两者不要同时填写在同一个 select 上。类型别名可缩短全限定名，但不是必需配置，本例用全名方便定位。[MyBatis 结果映射说明](https://mybatis.org/mybatis-3/sqlmap-xml.html)

### 7.5 创建 Service 和 Controller

文件：`src/main/java/com/example/learning/book/BookService.java`

```java
package com.example.learning.book;

import java.math.BigDecimal;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class BookService {
    private final BookMapper bookMapper;

    // 构造器注入：Spring 把生成的 Mapper 代理传进来，无需自己 new 一个实现类。
    public BookService(BookMapper bookMapper) {
        this.bookMapper = bookMapper;
    }

    public List<Book> findByMinPrice(BigDecimal minPrice) {
        return bookMapper.findByMinPrice(minPrice);
    }
}
```

简单练习直接使用一个 Service 类即可，不为每个类机械增加接口和 Impl。真实业务包含多步写入时，在 Service 定义事务与规则；本例只有一次查询。

文件：`src/main/java/com/example/learning/book/BookController.java`

```java
package com.example.learning.book;

import com.example.learning.ApiResponse;
import java.math.BigDecimal;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class BookController {
    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @GetMapping("/books")
    public ApiResponse<List<Book>> books(
            @RequestParam(name = "minPrice", defaultValue = "0") BigDecimal minPrice) {
        return ApiResponse.success(bookService.findByMinPrice(minPrice));
    }
}
```

练习实体仅有公开书籍字段，直接返回便于观察映射。用户实体有密码等秘密，真实接口应转换为安全响应 DTO，不能照搬“直接返回实体”。

### 7.6 启动并验证完整链路

1. 在学习工程根目录运行 `mvn test`，应仍通过问候接口测试。
2. 停止之前的学习进程，重新运行 `mvn spring-boot:run`，确保新代码和初始化文件已加载。
3. 在另一 Mac 终端执行下面请求；Reqable 使用同样 URL、GET、无请求体。

```sh
curl -i 'http://127.0.0.1:18080/books?minPrice=30'
curl -i 'http://127.0.0.1:18080/books?minPrice=100'
```

第一条预期 HTTP 200、data 只有 id 为 2 的书；第二条 HTTP 200、data 是空数组 `[]`。JSON 数字可能显示 `49.9` 或 `49.90`，数值含义一致。

```json
{"code":200,"message":"成功","data":[{"id":2,"name":"Spring Boot 入门","price":49.90}]}
```

### 7.7 把查询结果写成测试

文件：`src/test/java/com/example/learning/BookQueryTest.java`

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
class BookQueryTest {
    @Autowired
    private MockMvc mvc;

    @Test
    void shouldFilterBooksFromDatabase() throws Exception {
        mvc.perform(get("/books").param("minPrice", "30"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].name").value("Spring Boot 入门"));
    }

    @Test
    void shouldReturnEmptyArrayWhenNothingMatches() throws Exception {
        mvc.perform(get("/books").param("minPrice", "100"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").isEmpty());
    }
}
```

在学习工程根目录执行 `mvn -Dtest=BookQueryTest test`，预期通过。这里走到真实 H2 查询，不是把 Mapper 返回值写死的模拟测试；仍不等于真实 MySQL 兼容性验证。

### 7.8 出错时沿调用链定位

| 错误 | 原因与处理 |
| --- | --- |
| 找不到 BookMapper Bean | 检查 `@Mapper`、包位置、Starter 是否引入以及 Maven 是否重新加载 |
| `Invalid bound statement` | 对照 namespace、方法名、mapper-locations；构建后确认 `target/classes/mapper/BookMapper.xml` 存在 |
| 表不存在 | 检查 schema.sql 在 resources 下、sql.init 是否启用、是否误连另一数据源 |
| 数据有值但 name 是 null | 检查 `book_name → name` 的 resultMap；只有 `@TableField` 不代表任意手写 SQL 都已配置结果映射 |
| 请求返回 400 | 例如 `minPrice=abc` 不能转成 BigDecimal；提交数字，不要修改 SQL 来掩盖请求格式错误 |

若 XML 必须放在 Java 源码树内，需要明确配置 Maven 的资源复制；本练习选择标准 resources 目录，少一项构建约定。不要为解决资源缺失，把全部 `.java` 源码作为运行资源打包。
