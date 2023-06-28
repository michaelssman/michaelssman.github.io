# Spring

创建一个Student类

```java
Student s = new Student();
```

如果想要改为Person

```java
Person s = new Person();
```

如果有几十处的话，都需要修改。耦合性太大。

创建对象代码从java代码转移到Spring容器中。耦合性低。

这就是控制反转。 

1.对比以往项目，Spring优势有：方便解耦,简化开发；不改变原有代码在它的基础上扩展（AOP切面编程）；声明式事务；整合各种优秀的框架；

2.不重复造轮子

3.使用Spring所需jar包

发明者：Rod Johnson(罗宾·约翰逊)--Java世界的传奇大师，神级人物；Spring FrameWork的缔造者;旷世奇书"葵花宝典"《Expert one on one [J2EE](https://so.csdn.net/so/search?q=J2EE&spm=1001.2101.3001.7020) Design and Development》作者；Servlet2.4和JDO2.0的规范专家;Java Development Community杰出人物。

Spring官网：https://spring.io/ 

## Spring各个模块

![img](assets/56b9acd28d814147aed69e647befb156.png)

## Spring IoC/DI 介绍

IoC(Inversion of Control)中文名称：控制反转，也被称为DI(dependency injection )：依赖注入。

创建对象的权利,或者是控制的位置,**由JAVA代码转移到spring容器,由spring的容器控制对象的创建,就是控制反转**。

由于控制反转概念比较含糊，所以在 2004 年大师级人物Martin Fowler又给出了一个新的名字:“依赖注入”，相对loC而言，“依赖注入”明确描述了“被注入对象依赖loC容器来配置依赖对象”，Dl(英文全称为Dependency Injection，中文译名为依赖注入）是loC的别名。

### 分层处理

从前端获取的数据到从数据库处理之前，所有的逻辑都在java里面，各种功能在一起，程序臃肿，需要划分。

每一层都分为接口+实现类两部分。接口不会变，只需要替换实现类，就可以实现修改。



Java代码不再new创建对象，程序中用一个xml文件，里面配置对象名和类。使用反射。

spring容器里面放各种对象。

## 第一个Spring项目-完成IoC/DI代码的实现

**1.创建项目，添加依赖**

创建普通Maven项目，在项目的pom.xml中添加Spring项目的最基本依赖。

Spring项目想要运行起来必须包含:

- spring-context.jar - 依赖`spring-core`、`spring-aop`、`spring-expression`、`spring-beans`四个jar。

- spring-core.jar - 依赖`spring-jcl.jar`

- spring-aop.jar

- spring-expression.jar

- spring-beans.jar

- spring-jcl.jar

  所以在Maven中想要使用Spring框架只需要在项目中导入spring-context就可以了，其他的jar包根据Maven依赖传递性都可以导入进来。

```xml
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-context</artifactId>
            <version>5.3.23</version>
        </dependency>
    </dependencies>
```

2.创建一个类

3.创建Spring配置文件

在src/main/resources下新建applicationContext.xml文件。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:context="http://www.springframework.org/schema/context"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
        https://www.springframework.org/schema/beans/spring-beans.xsd
        http://www.springframework.org/schema/context
        https://www.springframework.org/schema/context/spring-context.xsd">

	<!-- com.msb.pojo包下component的注解都会扫描到-->
    <context:component-scan base-package="com.msb.pojo"></context:component-scan>

<!--    <bean id="b" class="com.msb.pojo.Book">-->
<!--        <property name="id1" value="1" ></property>-->
<!--        <property name="name1" value="项目驱动零起点学Java"></property>-->
<!--    </bean>-->
    
<!--    <bean id="b2" class="com.msb.pojo.Book">-->
<!--        <constructor-arg name="id2" value="2"></constructor-arg>-->
<!--        <constructor-arg name="name2" value="红高粱"></constructor-arg>-->
<!--    </bean>-->
    
<!--    <bean id="boy" class="com.msb.pojo.Boy">-->
<!--        <property name="age" value="22"></property>-->
<!--        <property name="name" value="小明"></property>-->
<!--    </bean>-->
<!--    <bean id="girl" class="com.msb.pojo.Girl">-->
<!--        <property name="age" value="19"></property>-->
<!--        <property name="name" value="露露"></property>-->
<!--        <property name="boyfriend" ref="boy"></property>-->
<!--    </bean>-->
    
</beans>
```

识别com.msb.pojo.Book这个类，通过反射创建对象。

4.测试，创建容器

```java
package com.msb.test;

import com.msb.pojo.Book;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class Test {
    public static void main(String[] args) {
        //创建Spring容器：
        ApplicationContext context = new ClassPathXmlApplicationContext("applicationContext.xml");
        //获取对象：
        //Book book = (Book)context.getBean("b");
        Book book = (Book)context.getBean("b2");
        //打印对象的信息：
        System.out.println(book.getName() + "---" + book.getId());

    }
}
```

### 属性注入方式

以前：setter方式

```java
Book b = new Book(); 
b.setId(1); 
b.setName("项目驱动零起点学Java")
```

现在：属性注入-设置注入

```xml
<bean id="b" class="com.msb.pojo.Book">
    <property name="id1" value="1" ></property>	<!--name不是属性的名字，是set方法的名字-->
    <property name="name1" value="项目驱动零起点学Java"></property>
</bean>
```

以前：构造器方式

```java
Book b = new Book(1，"项目驱动零起点学Java"); 
```

现在：属性注入-构造注入

```xml
<bean id="b2" class="com.msb.pojo.Book">
    <constructor-arg name="id2" value="2"></constructor-arg>
    <constructor-arg name="name2" value="红高粱"></constructor-arg>
</bean>
```

#### 属性为引用数据类型

**类的属性：**可以是基本数据类型，也可以是引用数据类型。

## IoC/DI相关的注解

| 注解名称       | 解释                                                 |
| -------------- | ---------------------------------------------------- |
| @Component     | 实例化Bean， 默认名称为类名首字母变小写              |
| @Repository    | 作用和@Component一样。用在持久层                     |
| @Service       | 作用和@Component一样。用在业务层                     |
| @Controller    | 作用和@Component一样。用在控制器层                   |
| @Configuration | 作用和@Component一样。用在配置类上                   |
| @Autowired     | 自动注入。默认byType，如果多个同类型bean，使用byName |
| @ Value        | 给普通数据类型属性赋值                               |

### @Component的使用

在要创建对象的类中加入@Component注解，对象名字默认为：类名首字母变小写

注解在哪个包下？要想找到这些注解，需要将注解所在的包进行扫描：设置需要扫描的包。并且需要在applicationContext.xml中添加context命名空间

```xml
<?xml version="1.0" encoding="UTF-8"?> 
<beans xmlns="http://www.springframework.org/schema/beans"     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"     xmlns:context="http://www.springframework.org/schema/context"     xsi:schemaLocation="http://www.springframework.org/schema/beans     https://www.springframework.org/schema/beans/spring-beans.xsd     http://www.springframework.org/schema/context     https://www.springframework.org/schema/context/spring-context.xsd"> 
    
    <context:component-scan base-package="com.msb.service"></context:component-scan> 

</beans>
```

前五个注解作用一样，只所以搞出这么多，就是在语义上给你区别，放入不同层用不同的注解，但是作用都是创建对象。

**@Value的使用**

给普通数据类型赋值的注解，普通数据类型包括：八种基本数据类型+String，并且不需要依赖set方法。

**@Autowired的使用**

添加@Autowired注解后会把容器中的对象**自动注入**进来，并且不需要依赖set方法。