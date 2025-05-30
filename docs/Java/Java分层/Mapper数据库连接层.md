# Mapper数据库连接层

## interface接口类

项目不写接口类也可以正常使用，但是会存在下面的问题：

- **方法不能直接调用**
- 多个参数问题处理麻烦
- 项目没有规范可言，不利于面向接口编程思想。

BookMapper.xml里面的sql不能作为方法调用。

在`项目|module|src|main|java|package（com.hh.mapper）`创建BookMapper接口interface文件。

com.hh.mapper.BookMapper接口：抽象方法

```java
package com.hh.mapper;

import com.hh.pojo.Book;

import java.util.List;

public interface BookMapper {
    // 定义规则，抽象方法。主要定义方法名，参数，返回值
    /*public abstract */List selectAllBooks();

    public abstract Book selectOneBook(String name, String author);

    public abstract Book selectOneBook2(Book book);

    public abstract Book selectOneBook3(String name, Book book);

    public abstract int insertBook(Book book);
}
```

## 接口的映射文件BookMapper.xml

对数据库做操作的sq信息。增删改查在这个配置文件里。

在`项目|module|src|main|resources`下创建com文件夹->hh文件夹->mapper文件夹，然后在mapper文件夹中创建和接口同名的**映射文件**`BookMapper.xml`。

sql和业务代码解耦，直接在xml中操作。

要求：namespace取值必须是接口的全限定路径、标签中的id属性值必须和接口中的方法名对应。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!--约束 根标签是mapper-->
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<!--namespace：防止其它文件也有同样的名字的sql，所以定义一个命名空间。下面的id方法就是接口对应的实现类-->
<mapper namespace="com.hh.mapper.BookMapper">
    <!--    查询操作-->
    <!--    id类似方法名，resultType是返回值-->
    <!--    id方法名要与接口对应的名字一样-->
    <select id="selectAllBooks" resultType="b">
        select * from t_book
    </select>
    <select id="selectOneBook" resultType="Book">
        select * from t_book where name =#{param1} and author = #{param2}
    </select>
    <select id="selectOneBook2" resultType="Book">
        select * from t_book where name =#{name} and author = #{author}
    </select>
    <select id="selectOneBook3" resultType="Book">
        select * from t_book where name =#{param1} and author = #{param2.author}
    </select>
    <!--    插入操作-->
    <insert id="insertBook">
        insert into t_book (id,name,author,price) values (#{id},#{name},#{author},#{price})
    </insert>
</mapper>
```

**映射文件默认不会被程序加载，如果想要被项目加载，需要配置到核心配置文件mybatis.xml中`<mappers>`。** 

## 文件位置

将`UserMapper.xml`文件放在与`UserMapper.java`相同的`src/main/java`目录下的`mapper`文件夹中会导致问题。这是因为Maven/Gradle在构建项目时，默认只处理`src/main/java`目录下的`.java`文件，而忽略其他文件类型（如XML）。因此，XML映射文件不会被复制到最终构建输出目录中。

### 解决方案：

#### 方法1：移动XML文件到资源目录（推荐）
1. 在`src/main/resources`下创建相同的包路径：
   ```
   src/main/resources/com/hh/user/mapper
   ```
2. 将所有的Mapper XML文件（如`UserMapper.xml`, `RoleMapper.xml`等）移动到该目录

#### 方法2：修改构建配置（适用于需要保留原位置的情况）
在`pom.xml`中添加资源包含配置：
```xml
<build>
    <resources>
        <resource>
            <directory>src/main/java</directory>
            <includes>
                <include>**/*.xml</include>
            </includes>
        </resource>
        <resource>
            <directory>src/main/resources</directory>
        </resource>
    </resources>
</build>
```

### 完整目录结构示例
```markdown
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── hh/
│   │           └── user/
│   │               └── mapper/
│   │                   ├── UserMapper.java
│   │                   ├── RoleMapper.java
│   │                   └── ...其他Java文件
│   │
│   └── resources/
│       └── com/
│           └── hh/
│               └── user/
│                   └── mapper/
│                       ├── UserMapper.xml
│                       ├── RoleMapper.xml
│                       └── ...其他XML文件
└── test/
    └── ...测试文件
```

### 为什么会出现这个错误
当XML文件放在`src/main/java`目录下时：
1. 构建工具不会将其复制到`target/classes`
2. 运行时MyBatis在classpath中找不到对应的XML映射文件
3. 导致`Invalid bound statement`错误

通过将XML文件移动到资源目录或修改构建配置，可以确保这些文件被正确包含在最终构建产物中，从而解决该问题。
