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

每个存储的数据结构都有一个唯一的主键，主键可以自己指定，比如用户的uid 不会重复，就可以作为一个主键，如果不指定主键，则会自动给你配置自增主键。

覆盖数据的依据 一般是根据主键来，速度快，这是一种覆盖方法，可以update 可以replace 主要看你业务需求

另外一种则是可能判断虽然主键不同，但是内容相同的也需要覆盖，这种情况直接查询内容对比然后 update或者replace 

#### 存在的话就更新，不存在的话就插入

使用`INSERT OR REPLACE`

```sql
INSERT OR REPLACE INTO TABLENAME ('articleID','editDate') VALUES ('1001','20220101')
```

## 删除数据delete

```sql
delete from Students where stu_id = 5 and stu_id = 18;
```

## 删除表

```sql
drop Table Students;
```

## 删除数据库

```sql
drop Database Students;
```

## 更新某一条指定的数据update

```sql
UPDATE ${TABLENAME} SET stu_name = '隔壁老王', stu_age = 25 WHERE stu_id = 7;
```

## 查找SELECT

```sql
SELECT * FROM TABLENAME WHERE 字段1 = '<#值#>' AND showtime < '1517904068.1524' ORDER BY 字段2 DESC LIMIT 10 OFFSET %d ;

根据字段2倒序排序 查找字段1等于某个值 并且showtime小于1517904068.1524 的数据，并且分页，每页10个。
```

`*`代表所有属性列的内容，如果其中一部分的话需要特别指明 如下的这句

```sql
SELECT stu_name,stu_gender FROM Students
```

### 根据条件排序查找

假设你的表名是`my_table`，并且`date`和`id`是你的字段名，可以使用以下SQL语句来实现你的需求：

```sql
-- 选择my_table表中的所有字段
SELECT * 
FROM my_table -- 从my_table表中选取数据
WHERE editDate < 'last_edit_date' -- 选择editDate小于上次查询的最后一条数据的editDate的数据
ORDER BY date DESC, id DESC -- 首先根据date字段降序排序，如果date相同，那么再根据id字段降序排序
LIMIT 100 -- 限制结果集的数量为100
```

`DESC`关键字表示降序排序，升序排序使用`ASC`关键字。

### 根据日期查找的数据，按年 按月 按日倒序分组。

要按年、月和日对数据库表中的日期字段进行分组，您可以使用SQL查询语句。以下是一些示例SQL查询，可以帮助您实现这一目标，假设您有一个名为"your_table"的表，其中包含日期字段"date_field"。

按年分组：
```sql
-- 通过年份分组并计算每个年份的记录数
SELECT YEAR(date_field) AS year, COUNT(*) AS count
FROM your_table
GROUP BY YEAR(date_field)
ORDER BY YEAR(date_field) DESC;
```

按月分组：
```sql
-- 通过年份和月份分组，然后计算每个月份的记录数
SELECT YEAR(date_field) AS year, MONTH(date_field) AS month, COUNT(*) AS count
FROM your_table
GROUP BY YEAR(date_field), MONTH(date_field)
ORDER BY YEAR(date_field) DESC, MONTH(date_field) DESC;
```

按日分组：
```sql
-- 通过年份、月份和日期分组，并计算每个日期的记录数
SELECT YEAR(date_field) AS year, MONTH(date_field) AS month, DAY(date_field) AS day, COUNT(*) AS count
FROM your_table
GROUP BY YEAR(date_field), MONTH(date_field), DAY(date_field)
ORDER BY YEAR(date_field) DESC, MONTH(date_field) DESC, DAY(date_field) DESC;
```

"date_field" 是一个日期（date）类型的字段，而不是文本（text）类型。日期类型字段用于存储日期和时间信息，允许您进行日期和时间相关的操作，例如按年、月和日分组、排序和计算日期差异，以便可以对其进行查询和分组。文本字段不具备这些日期操作的能力。

在大多数关系型数据库管理系统中，日期类型的字段通常被定义为"DATE"，"DATETIME"，"TIMESTAMP"等，具体的命名可能会因数据库系统而异。确保在创建数据库表时，将日期字段指定为适当的日期类型，以便能够正确地存储和处理日期数据。

这些查询将从"your_table"表中选择日期数据，并将其按年、月和日进行分组，同时计算每个组中的记录数。

### GROUP BY

根据某个字段分组数据。

数据库有一个记账明细表MC_DETAIL_TEXT，里面的字段是id、from_ac_id、to_ac_id、ac_detail_date（日期）、ac_detail_type（类型）、ac_detail_amount（金额）。
要求写一个sql语句，取出每个月类型为收入的总金额。

你可以使用SQL的`SUM`函数和`GROUP BY`子句来实现这个需求。以下是一个可能的SQL查询语句：

```sql
SELECT 
    DATE_FORMAT(ac_detail_date, '%Y-%m') AS Month, 
    SUM(ac_detail_amount) AS TotalIncome
FROM 
    MC_DETAIL_TEXT
WHERE 
    ac_detail_type = '收入'
GROUP BY 
    Month;
```

这个查询语句将首先筛选出类型为"收入"的记录，然后按照月份（年-月）对金额进行求和。`DATE_FORMAT`函数用于将日期字段`ac_detail_date`格式化为"年-月"的形式。`SUM`函数用于计算每个月的总收入，`GROUP BY`子句用于按月份进行分组。



上面的例子，如果想要知道每一个月类型为收入的总金额和支出的总金额。应该怎么写。

你可以使用条件求和（conditional aggregation）的方式来实现这个需求。以下是一个可能的SQL查询语句：

```sql
SELECT 
    DATE_FORMAT(ac_detail_date, '%Y-%m') AS Month, 
    SUM(CASE WHEN ac_detail_type = '收入' THEN ac_detail_amount ELSE 0 END) AS TotalIncome,
    SUM(CASE WHEN ac_detail_type = '支出' THEN ac_detail_amount ELSE 0 END) AS TotalExpenditure
FROM 
    MC_DETAIL_TEXT
GROUP BY 
    Month;
```

这个查询语句将首先筛选出类型为"收入"或"支出"的记录，然后按照月份（年-月）对金额进行求和。`CASE`语句用于根据`ac_detail_type`的值决定是否将`ac_detail_amount`加入到总和中。如果`ac_detail_type`的值为"收入"，则将`ac_detail_amount`加入到收入的总和中；如果`ac_detail_type`的值为"支出"，则将`ac_detail_amount`加入到支出的总和中。如果`ac_detail_type`的值既不是"收入"也不是"支出"，则将0加入到相应的总和中。`SUM`函数用于计算每个月的总收入和总支出，`GROUP BY`子句用于按月份进行分组。

请注意，这个查询语句假定`ac_detail_date`是一个日期类型的字段，`ac_detail_amount`是一个数值类型的字段，`ac_detail_type`是一个文本类型的字段，且"收入"和"支出"是表示收入类型和支出类型的准确值。如果你的数据库中的设置不同，可能需要对查询语句进行适当的修改。







删除、修改、查找都可以使用where条件

