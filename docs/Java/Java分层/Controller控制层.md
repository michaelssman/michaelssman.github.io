# Controller控制层

前端请求到这个类里的具体方法

##### 6.4.1、响应数据

从前端、服务端、数据库一层一层的查找数据，然后再从数据库、服务端一层一层返还到前端。

响应页面或者响应数据，响应数据需要加注解`@ResponseBody`，数据就可以return出去。

```java
package com.hh.controller;

import com.hh.pojo.Book;
import com.hh.service.BookService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;

@Controller //通过注解 创建对象
public class BookController {
    @Autowired //注入对象
    private BookService bookService;//业务层的对象

    //前端请求路径
    @RequestMapping(value = "/findAllBooks", produces = "text/html;charset=utf-8")
    @ResponseBody//注解，把对应响应的数据响应到浏览器
    public String findAll() {//控制单元
        System.out.println("--");
        List list = bookService.findAll();
        System.out.println("一共有书籍数量：" + list.size());
        //定义一个字符串用来接收响应的字符串：
        String s = "";
        for (int i = 0; i < list.size(); i++) {
            Book book = (Book) list.get(i);
            s += book.getName() + "," + book.getAuthor() + "\n";
        }
        return s;
        //响应一个页面
        //return "/index.jsp";
    }
}
```

@ResponseBody注解作用：直接在方法上添加上@ResponseBody，Spring MVC会把返回值设置到响应流中。