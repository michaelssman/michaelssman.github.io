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

## 创建表

```sql
--创建表
CREATE TABLE IF NOT EXISTS student (
  ‘id’ INT PRIMARY KEY AUTOINCREMENT,
  ‘name’ VARCHAR(255) NOT NULL DEFAULT ‘’ COMMENT ‘姓名’,
  ‘age’ TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT ‘年龄’,
  ‘Create at’ INT NOT NULL DEFAULT 0 COMMENT ‘新增时间’
) ENGINE=InnoDB DEFAULT CHARSET=UTF8 AUTO_INCREMENT=1001 COMMENT=‘学生表’;
```

- primary key：主键，区分每一条数据，主键的值不能相同。
- autoincrement：自增，修饰的属性在每一次增加数据的时候值都会自动加1。

### ALTER

在已有的表中**新增字段**而不影响现有数据：判断数据库版本号，如果小于最新版本号，则执行`ALTER TABLE` SQL命令来添加新的列。

通常在**数据库版本**升级时进行。

需要注意以下几点：

1. 新增的字段会添加到表的末尾。
2. 新增字段的默认值为 `NULL`，除非你指定了 `DEFAULT` 值。
3. SQLite 不允许一次添加多个字段。
4. `ALTER TABLE`命令在SQLite中有限制，它只支持添加新的列，并且不能删除或修改现有列。

```sql
ALTER TABLE users ADD COLUMN email TEXT DEFAULT 'example@example.com';
```

添加唯一索引

索引不能重复

```sql
ALTER TABLE student ADD constraint uk_mail UNIQUE (email)
```

表信息查询语句

```sql
PRAGMA table_info($tableName)
```

## insert

```sql
INSERT INTO Students(stu_name, stu_gender, stu_age) VALUES ('哇哈哈','男',23);
```

### 存在则更新，不存在则插入

使用`INSERT OR REPLACE`

```sql
INSERT OR REPLACE INTO TABLENAME ('articleID','editDate') VALUES ('1001','20220101')
```

## delete

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

## update

为了避免SQL注入攻击，最好使用**参数化查询**，而不是直接将变量插入到SQL语句中。

```dart
txn.rawUpdate(
  'UPDATE $_tableName SET ${AccountModel.acNameKey} = ?, ${AccountModel.acTypeKey} = ? WHERE id = ?',
  ["haha", "sz", 22]
);
```

`?` 是参数的占位符。`rawUpdate` 方法的第二个参数是一个数组，包含了要插入到SQL语句中的值，这些值将按照顺序替换掉占位符。

这种方式不仅安全，还可以防止因不正确的引号使用而导致的语法错误。

## SELECT

```sql
SELECT * 
FROM TABLENAME 
WHERE editDate < 'last_edit_date' -- 选择editDate小于上次查询的最后一条数据的editDate的数据
	AND name = '倒数离开' 
	AND showtime < '1517904068.1524' 
ORDER BY date DESC, id DESC -- 首先根据date字段降序排序，如果date相同，那么再根据id字段降序排序
LIMIT 10 OFFSET %d ; -- 分页，每页10个。
```

`*`代表所有属性列的内容，如果其中一部分的话需要特别指明 如下的这句

```sql
SELECT stu_name,stu_gender FROM Students
```

`DESC`关键字表示降序排序，升序排序使用`ASC`关键字。

### 根据日期查找的数据，按年 按月 按日倒序分组。

按年、月和日对数据库表中的日期字段进行分组，同时计算每个组中的记录数。

按日分组：
```sql
-- 通过年份、月份和日期分组，并计算每个日期的记录数
SELECT 
	YEAR(date_field) AS year, 
	MONTH(date_field) AS month, 
	DAY(date_field) AS day, 
	COUNT(*) AS count
FROM your_table
GROUP BY YEAR(date_field), MONTH(date_field), DAY(date_field)
ORDER BY YEAR(date_field) DESC, MONTH(date_field) DESC, DAY(date_field) DESC;
```

"date_field" 是一个日期（date）类型的字段，而不是文本（text）类型。日期类型字段用于存储日期和时间信息，允许您进行日期和时间相关的操作，例如按年、月和日分组、排序和计算日期差异，以便可以对其进行查询和分组。

在大多数关系型数据库管理系统中，日期类型的字段通常被定义为"DATE"，"DATETIME"，"TIMESTAMP"等，具体的命名可能会因数据库系统而异。确保在创建数据库表时，将日期字段指定为适当的日期类型，以便能够正确地存储和处理日期数据。

### GROUP BY

根据某个字段分组数据。

数据库有一个记账明细表MC_DETAIL_TEXT，里面的字段是id、from_ac_id、to_ac_id、ac_detail_date（日期）、ac_detail_type（类型）、ac_detail_amount（金额）。
要求写一个sql语句，取出每个月类型为收入的总金额。

可以使用SQL的`SUM`函数和`GROUP BY`子句来实现这个需求。以下是一个可能的SQL查询语句：

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

这个查询语句将首先筛选出类型为"收入"的记录，然后按照月份（年-月）对金额进行求和。

**`DATE_FORMAT`函数用于将日期字段`ac_detail_date`格式化为"年-月"的形式。**

**`SUM`函数用于计算每个月的总收入（或总支出）。**

**`GROUP BY`子句用于按月份进行分组。**

#### 每个月的总收入和总支出

使用条件求和（conditional aggregation）的方式来实现这个需求。

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

首先筛选出类型为"收入"或"支出"的记录，然后按照月份（年-月）对金额进行求和。

`CASE`语句：根据`ac_detail_type`的值决定是否将`ac_detail_amount`加入到总和中。如果`ac_detail_type`的值为"收入"，则将`ac_detail_amount`加入到收入的总和中；如果`ac_detail_type`的值为"支出"，则将`ac_detail_amount`加入到支出的总和中。如果`ac_detail_type`的值既不是"收入"也不是"支出"，则将0加入到相应的总和中。

注意：`ac_detail_date`是一个日期类型的字段，`ac_detail_amount`是一个数值类型的字段，`ac_detail_type`是一个文本类型的字段，且"收入"和"支出"是表示收入类型和支出类型的准确值。

### 关联查询

![微信图片_20251130202833_10_197](assets/微信图片_20251130202833_10_197.jpg)

### LEFT JOIN关联查询

JOIN连接两个表

数据库有两个表：
账户表：MC_TEXT，该表中的字段：id, type, name, balance。
明细表：MC_DETAIL_TEXT，该表中的字段：id, from_ac_id, to_ac_id, ac_detail_date, ac_detail_type, ac_detail_amount。
明细表中的from_ac_id和to_ac_id对应账户表中的id。
应该如何设计表，查询明细表的时候，返回id, from_ac_id, to_ac_id, ac_detail_date, ac_detail_type这些字段的信息，并且加上from_ac_id和to_ac_id对应的账户的信息。

#### 方法

为了在查询明细表时同时获取`from_ac_id`和`to_ac_id`对应的账户信息，需要在查询时进行两次连接（JOIN）操作，一次是将明细表的`from_ac_id`与账户表的`id`连接，另一次是将明细表的`to_ac_id`与账户表的`id`连接。

以下是一个SQL查询示例，展示了如何实现这种连接，并从两个表中检索所需的信息：

```sql
SELECT
    d.id,
    d.from_ac_id,
    f.type AS from_ac_type,
    f.name AS from_ac_name,
    f.balance AS from_ac_balance,
    d.to_ac_id,
    t.type AS to_ac_type,
    t.name AS to_ac_name,
    t.balance AS to_ac_balance,
    d.ac_detail_date,
    d.ac_detail_type,
    d.ac_detail_amount
FROM
    MC_DETAIL_TEXT AS d --详情表别名为d
INNER JOIN
    MC_TEXT AS f
ON
    d.from_ac_id = f.id
INNER JOIN
    MC_TEXT AS t
ON
    d.to_ac_id = t.id;
```

在这个查询中：

- `MC_DETAIL_TEXT` 表被别名为 `d`。
- `MC_TEXT` 表被别名为 `f` 当它与 `from_ac_id` 关联时。
- `MC_TEXT` 表也被别名为 `t` 当它与 `to_ac_id` 关联时。
- `INNER JOIN` 用于连接表，确保只有当账户ID在账户表中存在时，明细表的记录才会被返回。
- 使用 `AS` 关键字为每列提供了别名，如 `from_ac_type`, `from_ac_name`, `from_ac_balance`, `to_ac_type`, `to_ac_name`, `to_ac_balance`。

如果数据库中存在`from_ac_id`或`to_ac_id`没有对应账户记录的情况，可能需要使用`LEFT JOIN`来代替`INNER JOIN`，以确保即使某些账户信息不存在也能返回明细记录。

### SUM

```sql
SELECT SUM(${AccountModel.balanceKey}) as total FROM $_tableName
```

SUM函数来计算所有账户的总余额，结果是一个列表。

## 总结

删除、修改、查找都可以使用where条件

- `and`：和
- `or`：或

## 索引

```sql
-- 建立联合索引
CREATE INDEX idx_name_age ON users(name, age);
--这个查询就用到了覆盖索引
SELECT name, age FROM users WHERE name = '张三';
```

