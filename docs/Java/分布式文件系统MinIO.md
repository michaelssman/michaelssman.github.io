# 分布式文件系统MinIO

## 对象存储的方式对比

|    存储方式    |            优点            |   缺点   |
| :------------: | :------------------------: | :------: |
|   服务器磁盘   |      开发便捷，成本低      | 扩展困难 |
| 分布式文件系统 |        容易实现扩容        | 复杂度高 |
|   第三方存储   | 开发简单，功能强大，免维护 |   收费   |

## 分布式文件系统

| 存储方式 | 优点                                                         | 缺点                                                         |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| FastDFS  | 1，主备服务，高可用<br />2，支持主从文件，支持自定义扩展名<br />3，支持动态扩容 | 1，没有完备官方文档，近几年没有更新<br />2，环境搭建较为麻烦 |
| MinIO    | 1，性能高，准硬件条件下它能达到55GB/s的读、35GB/s的写速率<br />2，部署自带管理界面<br />3，MinIO.Inc运营的开源项目，社区活跃度高<br />4，提供了所有主流开发语言的SDK | 1，不支持动态增加节点                                        |

## 对象存储服务MinIO 

基于Apache License v2.0开源协议的对象存储服务。

采用Golang实现，服务端可以工作在Windows、Linux、OS X和FreeBSD上。

配置简单，基本是复制可执行程序，单行命令可以运行起来。

MinIO兼容亚马逊S3**云存储**服务接口，非常适合于存储大容量非结构化的数据，例如图片、视频、日志文件、备份数据和容器/虚拟机镜像等，而一个对象文件可以是任意大小，从几kb到最大5T不等。

**S3 （ Simple Storage Service简单存储服务）**

基本概念

- bucket – 类比于文件系统的目录
- Object – 类比文件系统的文件
- Keys – 类比文件名

官网文档：http://docs.minio.org.cn/docs/

## MinIO特点 

- 数据保护

  Minio使用Minio Erasure Code（纠删码）来防止硬件故障。即便损坏一半以上的driver，但是仍然可以从中恢复。

- 高性能

  在标准硬件条件下它能达到55GB/s的读、35GB/s的写速率

- 可扩容

  不同MinIO集群可以组成联邦，并形成一个全局的命名空间，并跨越多个数据中心

- SDK支持

  它得到类似Java、Python或Go等语言的sdk支持

- 有操作页面

  面向用户友好的简单操作界面，非常方便的管理Bucket及里面的文件资源

- 功能简单

  这一设计原则让MinIO不容易出错、更快启动

- 丰富的API

  支持文件资源的分享连接及分享链接的过期策略、存储桶操作、文件列表访问及文件上传下载的基本功能等。

- 文件变化主动通知

  存储桶（Bucket）如果发生改变，比如上传对象和删除对象，可以使用存储桶事件通知机制进行监控，并通过以下方式发布出去：AMQP、MQTT、Elasticsearch、Redis、NATS、MySQL、Kafka、Webhooks等。

## Docker安装MinIO

**1、拉取镜像**

```sh
docker pull quay.io/minio/minio
```

**2、创建持久化存储目录**

```sh
mkdir -p ~/minio/data
```

**3、运行容器**

```sh
docker run -d \
	--restart=always \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -v ~/minio/data:/data \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=your_strong_password" \
  quay.io/minio/minio server /data --console-address ":9001"
```

**参数说明**：

- `-p 9000:9000`：API访问端口（S3协议）
- `-p 9001:9001`：Web控制台端口
- `-v ~/minio/data:/data`：挂载数据目录（本地目录:容器目录）
- `MINIO_ROOT_USER`：管理员账号（默认`admin`）
- `MINIO_ROOT_PASSWORD`：管理员密码（**至少8字符**）
- `--console-address ":9001"`：强制启用Web控制台

**4、验证安装**

- **查看容器状态**：

  ```sh
  docker ps | grep minio
  ```

- **访问Web控制台**：

  打开浏览器访问：`http://服务器IP:9001`

  用户名密码见上面的docker容器配置

## 封装MinIO为starter

项目里面有各种微服务，如果MinIO在每一个微服务下都去集成的话，非常麻烦，所以抽出来`文件服务-starter`。

### 1、创建模块heima-file-starter

导入依赖

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-autoconfigure</artifactId>
    </dependency>
    <dependency>
        <groupId>io.minio</groupId>
        <artifactId>minio</artifactId>
        <version>8.5.17</version>
    </dependency>
  	<dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-configuration-processor</artifactId>
        <optional>true</optional>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
</dependencies>
```

### 2、配置类

MinIOConfigProperties.java

```java
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.io.Serializable;

@Data
@ConfigurationProperties(prefix = "minio")  // 文件上传 配置前缀minio
public class MinIOConfigProperties implements Serializable {
    private String accessKey;
    private String secretKey;
    private String bucket;
    private String endpoint;
    private String readPath;
}
```

MinIOConfig.java

```java
import io.minio.MinioClient;
import lombok.Data;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MinIO 自动配置类
 * - 仅在 classpath 中存在 MinioClient 并且配置了 minio.endpoint 时生效
 * - 负责创建 MinioClient Bean 并绑定 MinIOConfigProperties
 */
@Data
@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties({MinIOConfigProperties.class})
@ConditionalOnClass(MinioClient.class)
@ConditionalOnProperty(prefix = "minio", name = "endpoint")
public class MinIOConfig {
    private final MinIOConfigProperties minIOConfigProperties;

    public MinIOConfig(MinIOConfigProperties minIOConfigProperties) {
        this.minIOConfigProperties = minIOConfigProperties;
    }

    @Bean
    public MinioClient buildMinioClient() {
        return MinioClient
                .builder()
                .credentials(minIOConfigProperties.getAccessKey(), minIOConfigProperties.getSecretKey())
                .endpoint(minIOConfigProperties.getEndpoint())
                .build();
    }
}
```

### 3、封装操作minIO类

FileStorageService

```java
import java.io.InputStream;

public interface FileStorageService {

    /**
     * 上传图片文件
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @return 文件全路径
     */
    String uploadImgFile(String prefix, String filename, InputStream inputStream);

    /**
     * 上传html文件
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @return 文件全路径
     */
    String uploadHtmlFile(String prefix, String filename, InputStream inputStream);

    /**
     * 上传数据库文件
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @return 文件全路径
     */
    String uploadDbFile(String prefix, String filename, InputStream inputStream);

    /**
     * 删除文件
     *
     * @param pathUrl 文件全路径
     */
    void delete(String pathUrl);

    /**
     * 下载文件
     *
     * @param pathUrl 文件全路径
     * @return
     */
    byte[] downLoadFile(String pathUrl);

}
```

MinIOFileStorageService

```java
import com.hhjava.www.config.MinIOConfigProperties;
import com.hhjava.www.service.FileStorageService;
import io.minio.GetObjectArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Service
@Slf4j
//@EnableConfigurationProperties(MinIOConfigProperties.class)
//@Import(MinIOConfig.class)
public class MinIOFileStorageService implements FileStorageService {

    @Autowired
    private MinioClient minioClient;

    @Autowired
    private MinIOConfigProperties minIOConfigProperties;

    private final static String SEPARATOR = "/";
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy/MM/dd");

    /**
     * 构建文件路径
     *
     * @param dirPath  目录路径
     * @param filename 文件名
     * @return 完整文件路径
     */
    private String buildFilePath(String dirPath, String filename) {
        StringBuilder stringBuilder = new StringBuilder(50);
        if (StringUtils.hasText(dirPath)) {
            stringBuilder.append(dirPath).append(SEPARATOR);
        }
        String todayStr = LocalDate.now().format(DATE_FORMATTER);
        stringBuilder.append(todayStr).append(SEPARATOR).append(filename);
        return stringBuilder.toString();
    }

    /**
     * 通用文件上传方法
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @param contentType 文件类型
     * @return 文件全路径
     */
    private String uploadFile(String prefix, String filename, InputStream inputStream, String contentType) {
        String filePath = buildFilePath(prefix, filename);
        try {
            PutObjectArgs putObjectArgs = PutObjectArgs.builder()
                    .object(filePath)
                    .contentType(contentType)
                    .bucket(minIOConfigProperties.getBucket())
                    .stream(inputStream, inputStream.available(), -1) // 文件流
                    .build();
            minioClient.putObject(putObjectArgs);
            return minIOConfigProperties.getReadPath() + SEPARATOR + minIOConfigProperties.getBucket() +
                    SEPARATOR + filePath;
        } catch (Exception ex) {
            log.error("MinIO 文件上传失败，文件路径: {}, 错误信息: {}", filePath, ex.getMessage(), ex);
            throw new RuntimeException("上传文件失败");
        }
    }

    /**
     * 上传图片文件
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @return 文件全路径
     */
    @Override
    public String uploadImgFile(String prefix, String filename, InputStream inputStream) {
        return uploadFile(prefix, filename, inputStream, "image/*");
    }

    /**
     * 上传html文件
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @return 文件全路径
     */
    @Override
    public String uploadHtmlFile(String prefix, String filename, InputStream inputStream) {
        return uploadFile(prefix, filename, inputStream, "text/html");
    }

    /**
     * 上传数据库文件
     *
     * @param prefix      文件前缀
     * @param filename    文件名
     * @param inputStream 文件流
     * @return 文件全路径
     */
    @Override
    public String uploadDbFile(String prefix, String filename, InputStream inputStream) {
        return uploadFile(prefix, filename, inputStream, "application/x-sqlite3");
    }

    /**
     * 删除文件
     *
     * @param pathUrl 文件全路径
     */
    @Override
    public void delete(String pathUrl) {
        String key = pathUrl.replace(minIOConfigProperties.getEndpoint() + SEPARATOR, "");
        int index = key.indexOf(SEPARATOR);
        String bucket = key.substring(0, index);
        String filePath = key.substring(index + 1);
        // 删除Objects
        RemoveObjectArgs removeObjectArgs = RemoveObjectArgs.builder().bucket(bucket).object(filePath).build();
        try {
            minioClient.removeObject(removeObjectArgs);
            log.info("文件删除成功，路径: {}", pathUrl);
        } catch (Exception e) {
            log.error("MinIO 文件删除失败，路径: {}, 错误信息: {}", pathUrl, e.getMessage(), e);
        }
    }

    /**
     * 下载文件
     *
     * @param pathUrl 文件全路径
     * @return 文件流
     */
    @Override
    public byte[] downLoadFile(String pathUrl) {
        String key = pathUrl.replace(minIOConfigProperties.getEndpoint() + SEPARATOR, "");
        int index = key.indexOf(SEPARATOR);
        String bucket = key.substring(0, index);
        String filePath = key.substring(index + 1);
        try (InputStream inputStream = minioClient.getObject(GetObjectArgs.builder().bucket(bucket).object(filePath).build());
             ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream()) {
            byte[] buff = new byte[4096]; // 缓冲区大小
            int rc;
            while ((rc = inputStream.read(buff)) > 0) {
                byteArrayOutputStream.write(buff, 0, rc);
            }
            log.info("文件下载成功，路径: {}", pathUrl);
            return byteArrayOutputStream.toByteArray();
        } catch (Exception e) {
            log.error("MinIO 文件下载失败，路径: {}, 错误信息: {}", pathUrl, e.getMessage(), e);
            throw new RuntimeException("下载文件失败", e);
        }
    }
}
```

### 4、对外加入自动配置

在 src/main/resources/META-INF/spring/ 下新增文件`org.springframework.boot.autoconfigure.AutoConfiguration.imports`，列出自动配置类全名。

```java
com.hhjava.www.config.MinIOConfig
```

### 5、其他微服务使用

1、pom.xml文件中导入heima-file-starter的依赖

```xml
        <dependency>
            <groupId>com.heima</groupId>
            <artifactId>heima-file-starter</artifactId>
            <version>1.0-SNAPSHOT</version>
        </dependency>
```

2、在微服务`application.yml`中添加minio所需要的配置

注：也可以在nacos中去配置下面内容。

```yaml
minio:
  accessKey: admin
  secretKey: your_strong_password
  bucket: backup
  endpoint: http://47.120.67.123:9000
  readPath: http://47.120.67.123:9001/  # 文件访问域名
```

3、在对应使用的业务类中注入FileStorageService

```java
import com.heima.file.service.FileStorageService;
import com.heima.minio.MinioApplication;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import java.io.FileInputStream;
import java.io.FileNotFoundException;

@SpringBootTest(classes = MinioApplication.class)
@RunWith(SpringRunner.class)
public class MinioTest {

    @Autowired
    private FileStorageService fileStorageService;

    @Test
    public void testUpdateImgFile() {
        try {
            FileInputStream fileInputStream = new FileInputStream("E:\\tmp\\ak47.jpg");
            String filePath = fileStorageService.uploadImgFile("", "ak47.jpg", fileInputStream);
            System.out.println(filePath);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }
}
```
