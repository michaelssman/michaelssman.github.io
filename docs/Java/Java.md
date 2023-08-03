# Java

PPT：https://cloud.fynote.com/share/s/z9JGaVu6

## Java安装

### JDK

https://www.oracle.com/java/technologies/downloads/

Java Development Kit (JDK) 是 Sun 公司（已被 Oracle 收购）针对 Java 开发员的**软件开发工具包**。自从 Java 推出以来，JDK 已经成为使用最广泛的 Java SDK（Software development kit）。

Java SE 8（LTS）、Java SE 11（LTS）、Java SE 17（LTS）企业用的比较多，长期支持版本。

### idea

写代码的工具。

https://www.jetbrains.com/

旗舰版/社区版

## 快捷键

- ctrl+d：复制一行
- ctrl+y：删除一行
- sout：System.*out*.println();
- alt+Insert：类构造器，可以选择多个属性

## 方法重载

同一个类中，**方法名相同**，**形参列表不同**（类型不同、个数不同、顺序不同）的多个方法，构成了方法的重载。

## 目录结构

Create New Project --> Empty Project

Empty Project：作为一个工作空间，相当于一个大文件夹容器。里面放所有的项目（Module模块）。

手动导入jar包的位置：Empty Project|Module|lib|mysql-connector-java-8.0.11.jar|然后右键jar包|Add as Library|

Java文件位置：Empty Project|Module|src|package包名|创建java文件

### maven项目

#### src

##### 1、main

所有业务代码都放在main下。

##### 1.1、java

源码都放在java里。java文件夹下创建Package（例com.hh.test01），包下面创建类。

###### com.hh.pojo

实体类一般是pojo包

##### 1.2、resources

配置文件.properties、.xml资源文件

###### mapper

映射文件

##### 2、test

测试代码

##### 2.1、java

类似main下的java

##### 2.2、resources

类似main下的resources

#### pom.xml

导包的坐标写在这里面。
