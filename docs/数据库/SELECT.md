### 查找

```
SELECT * FROM <#表名#> WHERE articleID = '<#值#>';

SELECT * FROM <#表名#> ORDER BY <#字段名#> DESC;

SELECT * FROM <#表名#> WHERE type = '<#值#>' ORDER BY dispOrder DESC LIMIT 10 OFFSET <#(n-1) * 10#>;

SELECT * FROM <#表名#> WHERE 字段1 = '%@' ORDER BY 字段2 DESC LIMIT 10 OFFSET %d ;
根据字段2倒序排序 查找字段1等于某个值的数据，并且分页，每页10个。
```



```
SELECT * FROM newsTB where isTopNews = '1' and showtime < '1517904068.1524'  order by showtime desc LIMIT 10;
```

解释：
查找数据库中头条的文章，某一个日期之前的10条数据， 整个表所有数据按照日期倒序排列。





//查询所有数据（属性）

```
select * from Students
```

“ * " 代表所有属性列的内容，如果其中一部分的话需要特别指明 如下的这句

```
select stu_name,stu_gender from Students
```

//查询指定的某一条数据

```
select * from Students where stu_id = 1
```

