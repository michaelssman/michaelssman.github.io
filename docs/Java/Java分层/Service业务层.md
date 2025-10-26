# service业务层

业务层链接数据库层

创建包`com.hh.service`，包下面创建文件Interface接口

## 接口类

```java
package com.hh.service;

import java.util.List;

public interface BookService {
    public abstract List findAllBooks();
}
```

## 实现类

在com.hh.service包下再new一个包`com.hh.service.impl`

在包下创建接口的实现类BookServiceImpl。

```java
package com.hh.service.impl;

import com.hh.mapper.BookMapper;
import com.hh.service.BookService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service//注解 自动创建对象
public class BookServiceImpl implements BookService {
    @Autowired    //注解  注入对象
    private BookMapper bookMapper;

    public List findAllBooks() {
        return bookMapper.selectAllBooks();
    }
}
```
