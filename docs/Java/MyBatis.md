# MyBatis

## MyBatis是持久层框架

**持久层**是分层开发中专门负责访问数据源的一层，把访问数据源的代码和业务逻辑代码分离开，有利于后期维护和团队分工开发。同时也增加了数据访问代码的复用性。

Java项目中每一层都有自己的作用

## MyBatis是ORM框架

**ORM**(Object Relation Mapping)，中文名称：对象/关系 映射。是一种解决数据库发展和面向对象编程语言发展不匹配问题而出现的技术。

![image-20230420215343107](assets/image-20230420215343107.png)

## 搭建MyBatis框架

### 1、创建数据库表

直接在MySQL中，创建表和数据。

### 2、创建Maven项目

通过Maven导入对应框架。

### 3、在pom.xml文件中添加依赖

```xml
    <dependencies>
        
        <!--MySQL依赖，mybatis链接数据库需要mysql驱动-->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.28</version>
        </dependency>
        <!--Mybatis依赖-->
        <dependency>
            <groupId>org.mybatis</groupId>
            <artifactId>mybatis</artifactId>
            <version>3.5.6</version>
        </dependency>

    </dependencies>
```

### 4、创建MyBatis全局配置文件

（mybaits中文网址：https://mybatis.org/mybatis-3/zh/getting-started.html）

4.1、在`项目|模块|src|main|resources`中创建`db.properties`文件

```properties
url=jdbc:mysql://localhost:3306/msb?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=GMT%2B8&allowPublicKeyRetrieval=true
driver=com.mysql.cj.jdbc.Driver
username=数据库名字
password=数据库密码
```

4.2、在`项目|模块|src|main|resources`中创建`mybatis.xml`文件

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <properties resource="db.properties"></properties>
    <typeAliases>
        <package name="com.msb.pojo"/>
    </typeAliases>
    
    <environments default="mysql">
        <!--链接MySQL数据库的数据源配置-->
        <environment id="mysql">
            <!--配置mybatis中的事务管理-->
            <transactionManager type="JDBC"></transactionManager>
            <dataSource type="POOLED">
                <property name="driver" value="${driver}"/>
                <property name="url" value="${url}"/>
                <property name="username" value="${username}"/>
                <property name="password" value="${password}"/>
            </dataSource>
        </environment>
    </environments>
    <!--资源扫描、接口对应的实现类-->
    <mappers>
        <mapper resource="com/msb/mapper/BookMapper.xml"></mapper>
    </mappers>

</configuration>
```

#### 别名设置

MyBatis提供了别名机制可以对某个类起别名或给某个包下所有类起别名，简化resultType取值的写法。

在核心配置文件中，通过`<typeAlias>`标签明确设置类型的别名。

- type:类型全限定路径
- alias:别名名称

##### 1、具体的类起别名

```xml
<typeAliases>  
    <typeAlias type="com.msb.pojo.People" alias="p"></typeAlias>
</typeAliases>
```

##### 2、指定的包起别名

当类个数较多时，明确指定别名工作量较大，可以通过`<package>`标签指定包下全部类的别名。指定后所有类的别名就是类名。（也不区分大小写）

```xml
<typeAliases> 
    <package name="com.msb.pojo"/>
</typeAliases>
```

PS:明确指定别名和指定包的方式可以同时存在

### 5、创建实体类

在`项目|module|src|main|java|package（com.hh.pojo）`创建Book实体类。

### 6、创建接口类

在`项目|module|src|main|java|package（com.hh.mapper）`创建BookMapper。

```java
package com.msb.mapper;

import com.msb.pojo.Book;

import java.util.List;

public interface BookMapper {
    /*public abstract */List selectAllBooks();

    public abstract Book selectOneBook(String name, String author);

    public abstract Book selectOneBook2(Book book);

    public abstract Book selectOneBook3(String name, Book book);

    public abstract int insertBook(Book book);
}

```

### 6、创建映射文件，在核心配置文件中进行扫描

对数据库做操作的sq。增删改查。

在`项目|module|src|main|resources`下创建package（com.hh.mapper)，然后在mapper文件夹中创建`BookMapper.xml`。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.msb.mapper.BookMapper">
    <select id="selectAllBooks" resultType="Book">
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
    <insert id="insertBook">
        insert into t_book (id,name,author,price) values (#{id},#{name},#{author},#{price})
    </insert>
</mapper>
```

映射文件默认不会被程序加载，如果想要被项目加载，需要配置到上面的核心配置文件中`<mappers>`。 

### 7、编写测试类，启动项目

```java
package com.hh.test;

import com.hh.pojo.Book;

import org.apache.ibatis.io.Resources;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

public class Test {
    public static void main(String[] args) throws IOException {
        //指定核心配置文件的路径：
        String resource = "mybatis.xml";
        //获取加载配置文件的输入流：
        InputStream inputStream = Resources.getResourceAsStream(resource);
        //加载配置文件，创建工厂类
        SqlSessionFactory sqlSessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
        //通过工厂类获取一个会话：
        SqlSession sqlSession = sqlSessionFactory.openSession();
        //执行查询：
        List list = sqlSession.selectList("a.b.selectAllBooks");
        //遍历：
        for (int i = 0; i <= list.size() - 1; i++) {
            Book b = (Book) list.get(i);
            System.out.println(b.getName() + "---" + b.getAuthor());
        }
        //关闭资源：
        sqlSession.close();
    }
}
```

