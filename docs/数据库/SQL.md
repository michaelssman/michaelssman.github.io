# SQL

SQL (Structured Query Language）是一种操作数据库的语言。

在数据库管理系统中，使用SQL语言来实现数据的存取、查询、更新等功能。

SQL是一种非过程化语言，只需提出**做什么**，而不需要指明**怎么做**。

## 表

**表(Table）是数据库中数据存储最常见和最简单的一种形式**，数据库可以将复杂的数据结构用较为简单的**二维表**来表示。二维表是由行和列组成的，分别都包含着数据。

| 书籍编号 | 书籍名称             | 书籍作者       | 书籍定价 |
| -------- | -------------------- | -------------- | -------- |
| 1        | 项目驱动零起点学java | 马士兵、赵珊珊 | 69.8     |
| 2        | 活着                 | 余华           | 45       |
| 3        | 红高粱               | 莫言           | 49       |

每个表都是由若干行和列组成的，行被称为**记录**，列被称为这些记录的**字段**。

## 创建数据库

## 创建表

```sql
--创建表
CREATE TABLE IF NOT EXISTS student (
  ‘id’ INT AUTO_INCREMENT PRIMARY KEY AUTOINCREMENT,
  ‘name’ VARCHAR(255) NOT NULL DEFAULT ‘’ COMMENT ‘姓名’,
  ‘age’ TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT ‘年龄’,
  ‘Create at’ INT NOT NULL DEFAULT 0 COMMENT ‘新增时间’
) ENGINE=InnoDB DEFAULT CHARSET=UTF8 AUTO_INCREMENT=1001 COMMENT=‘学生表’;
```

- primary key：主键，区分每一条数据，主键的值不能相同。
- autoincrement：自增，修饰的属性在每一次增加数据的时候值都会自动加1。

### 新增字段ALTER

在建表后增加新字段

```sql
ALTER TABLE %@ ADD COLUMN %@ %@
```

## 插入数据insert

```sql
INSERT INTO Students(stu_name, stu_gender, stu_age) VALUES ('哇哈哈','男',23);
```

### 防止重复插入数据

#### 可以使用主键

每个存储的数据结构都有一个唯一的主键，主键可以自己指定，比如用户的uid 不会重复，就可以作为一个主键，又或者，每个根据时间戳来的消息id 也会重复，也会作为主键，如果不指定主键，则会自动给你配置自增主键。

覆盖数据的依据 一般是根据主键来，速度快，这是一种覆盖方法，可以update 可以replace 主要看你业务需求

另外一种则是可能判断虽然主键不同，但是内容相同的也需要覆盖，这种情况直接查询内容对比然后 update或者replace 

#### 存在的话就更新，不存在的话就插入。

使用`INSERT OR REPLACE`

```sql
INSERT OR REPLACE INTO TABLENAME ('articleID','editDate') VALUES ('1001','20220101')
```

## 删除数据delete

```sql
delete from Students where stu_id = 5 and stu_id = 18;
```

删除整个表

```sql
drop Table Students;
```

删除数据库

```sql
drop Database Students;
```

## 更新某一条指定的数据update

```sql
UPDATE ${TABLENAME} SET stu_name = '隔壁老王', stu_age = 25 WHERE stu_id = 7;
```

## 查找SELECT

```sql
SELECT * FROM TABLENAME ORDER BY <#字段名#> DESC;

SELECT * FROM TABLENAME WHERE 字段1 = '<#值#>' AND showtime < '1517904068.1524' ORDER BY 字段2 DESC LIMIT 10 OFFSET %d ;

根据字段2倒序排序 查找字段1等于某个值 并且showtime小于1517904068.1524 的数据，并且分页，每页10个。
```

`*`代表所有属性列的内容，如果其中一部分的话需要特别指明 如下的这句

```sql
SELECT stu_name,stu_gender FROM Students
```

### 根据条件排序查找

假设你的表名是`my_table`，并且`date`和`id`是你的字段名，那么你可以使用以下SQL语句来实现你的需求：

```sql
-- 选择my_table表中的所有字段
SELECT * 
FROM my_table -- 从my_table表中选取数据
ORDER BY date DESC, id DESC -- 首先根据date字段降序排序，如果date相同，那么再根据id字段降序排序
```

`DESC`关键字表示降序排序，如果你想进行升序排序，你可以使用`ASC`关键字。

删除、修改、查找都可以使用where条件

