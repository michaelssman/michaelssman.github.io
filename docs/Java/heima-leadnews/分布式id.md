# 分布式id

随着业务的增长，文章表可能要占用很大的物理存储空间，为了解决该问题，后期使用数据库分片技术。将一个数据库进行拆分，通过数据库中间件连接。

表中数据越来越多，超过了一千万，表的存储达到极限。可以在同一个库下面进行分表。

如果数据库中该表选用ID自增策略，则可能产生重复的ID，此时应该使用分布式ID生成策略来生成ID。

分布式id-技术选型

| 方案          | 优势                                        | 劣势                                                         |
| ------------- | ------------------------------------------- | ------------------------------------------------------------ |
| redis         | （INCR）生成一个全局连续递增 的数字类型主键 | 增加了一个外部组件的依赖，Redis不可用，则整个数据库将无法在插入 |
| UUID          | 全局唯一，Mysql也有UUID实现                 | 36个字符组成（字符串类型），占用空间大                       |
| snowflake算法 | 全局唯一 ，数字类型，存储成本低             | 机器规模大于1024台无法支持                                   |

snowflake是Twitter开源的分布式ID生成算法，结果是一个long型的ID。

其核心思想是：

- 使用41bit作为毫秒数
- 10bit作为机器的ID
  - 5个bit是数据中心（机房ID）
  - 5个bit的机器ID
- 12bit作为毫秒内的流水号（意味着每个节点在每毫秒可以产生 4096 个 ID）
- 最后还有一个符号位，永远是0

![image-20210505005509258](assets/image-20210505005509258.png)

mybatis-plus已经集成了雪花算法，完成以下两步即可在项目中集成雪花算法

第一：在实体类中的id上加入如下配置，指定类型为id_worker

```java
@TableId(value = "id",type = IdType.ID_WORKER)
private Long id;
```

第二：在application.yml文件中配置数据中心id和机器id

```yaml
mybatis-plus:
  mapper-locations: classpath*:mapper/*.xml
  # 设置别名包扫描路径，通过该属性可以给包中的类注册别名
  type-aliases-package: com.heima.model.article.pojos
  global-config:
    datacenter-id: 1 #数据中心id(取值范围：0-31)
    workerId: 1			 #机器id(取值范围：0-31)
```
