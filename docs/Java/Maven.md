# Maven

Maven是使用Java语言编写的基于项目对象模型（POM）**项目管理工具软件**。开发者可以通过一小段描述信息来管理项目构建、报告和文档。使用Maven可以更好的帮助我们完成项目的管理。

## 非Maven项目的缺点

问题一：

项目中的jar包资源需要我们自己从网上下载后，手动导入到项目中使用，不好管理。

问题二:

jar包版本控制麻烦

## Maven的仓库

中央仓库(Central Repository):Maven官方服务器。里面存放了绝大多数市面上流行的jar。允许用户注册后，上传自己的项目到官方服务器。网址在国外，经常访问不了。https://mvnrepository.com/

本地仓库(Local Repository): 本机的文件夹作为本地仓库，本地仓库指本机的一份拷贝，用来缓存远程下载，包含你尚未发布的临时构件。

镜像仓库(Mirror Repository): 对于国内来说，访问国外的Maven仓库会特别慢。镜像仓库就是另一台备份/复制了中央仓库的服务器。平时使用时国内开发者多使用阿里云镜像或华为云镜像，这样可以大大提升从中央仓库下载资源的速度。但它的角色仍然是一个远程库

![image-20230416230835436](assets/image-20230416230835436.png)

## Maven的资源坐标

GroupId: 一般是逆向公司域名 com.msb。同一个公司的GroupId都是相同的。

ArtifactId: 一般是项目(jar)名 mysql-connector-java。

Version: 版本号 8.0.28。

**Maven的下载和安装**

从maven官网下载Maven,官网地址:[https://maven.apache.org](https://maven.apache.org/)

