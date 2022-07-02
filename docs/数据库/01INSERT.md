插入数据，如果主键存在，则不会插入。
如果数据的内容都不变，只改变获取的顺序。则可以存一个存储数据的日期。根据这个日期去排序。做查询数据。
更新顺序的话，可以更新一下存储的日期。便可以更新查询的顺序。

### 创建表

```
NSString *sql = [NSString stringWithFormat:@"create table if not exists %@ (articleID text primary key,editDate text,id INTEGER);",tableName];
```
其中的id便是存储数据的时间。

### 插入数据

插入的id是插入时候的时间距离1970年的时间戳。存储的越晚，时间戳越大。

```sql
NSString *sql= [NSString stringWithFormat:
                                @"INSERT INTO %@ ('<#字段1#>','<#字段2#>','<#存储日期#>') VALUES ('%@','%@','%f')",
                                <#tableName#>,<#字段1的值#>,<#字段2的值#>,(double)[[NSDate date] timeIntervalSince1970]];
```

//插入一条数据

```sql
insert into Students(stu_name, stu_gender, stu_age)values('哇哈哈','男',23)
```

## 防止重复插入数据

##### 可以使用主键

每个存储的数据结构都有一个唯一的主键，这个主键你可以自己指定，比如用户的uid 不会重复，这就可以作为一个主键，又或者，每个根据时间戳来的消息id 也会重复，也会作为主键，如果不指定主键，则会自动给你配置自增主键。

覆盖数据的依据 一般是根据主键来，速度快，这是一种覆盖方法，可以update 可以replace 主要看你业务需求

另外一种则是可能判断虽然主键不同，但是内容相同的也需要覆盖，这种情况直接查询内容对比然后 update或者replace 

### 存在的话就更新，不存在的话就插入。

使用`INSERT OR REPLACE`

```sql
NSString *insertSql= [NSString stringWithFormat:
                                      @"INSERT OR REPLACE INTO %@ ('articleID','editDate') VALUES ('%@','%@')",
                                      tableName,item[@"articleID"],item[@"editDate"]];
```