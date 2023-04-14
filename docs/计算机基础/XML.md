# XML

XML指可扩展标记语言 (EXtensible Markup Language)

## XML的作用

XML 是**不作为**的，XML 不会做任何事情。XML被设计用来**结构化、存储以及传输信息**。它**仅仅是纯文本**而已。它仅仅将信息包装在 XML标签中。我们需要编写软件或者程序，才能传送、接收和显示出这个文档。

XML是语言，可自定义标签。

## XML定义

1、必须有声明语句。

XML声明是XML文档的第一句，其格式如下：

```xml
<?xml version="1.0" encoding="utf-8"?>
```

2、XML文档有且只有一个根元素

良好格式的XML文档必须有一个根元素，就是紧接着声明后面建立的第一个元素，其他元素都是这个根元素的子元素，根元素完全包括文档中其他所有的元素。

3、注意大小写

在XML文档中，大小写是有区别的。“A”和“a〞是不同的标记。

4、所有的标记必须有相应的结束标记

所有标记必须成对出现，有一个开始标记，就必须有一个结束标记，否则将被视为错误。

5、属性值使用引号

所有属性值必须加引号（可以是单引号，也可以是双引号，建议使用双引号），否则将被视为错误。

6、XML中可以加入注释

注释格式：`<!-- -->`

### 案例代码

创建一个`students.xml`文件

```xml
<?xml version="1.0" encoding="utf-8" ?>
<!--
注释
stuents:根标签，只有一个。
id:标签的属性
-->
<stuents>
    <student id="1">
        <name>九九</name>
        <age>18</age>
        <sex>女</sex>
        <score>98.7</score>
    </student>
    <student id="2">
        <name>健康</name>
        <age>15</age>
        <sex>男</sex>
        <score>28.7</score>
    </student>
    <student id="3">
        <name>解开</name>
        <age>34</age>
        <sex>男</sex>
        <score>57.7</score>
    </student>
</stuents>
```

## XML解析

### DOM解析

需要使用工具dom4j，是一个jar包。

下载dom4j 2.1.3.jar工具包，安装。

### 代码

项目创建一个文件夹，名字lib。

拷贝dom4j的jar包到项目lib。

在项目中选中jar包，右键`Add as Library`。

通过Iterator的hasNext()判断是否有下一个元素。

```java
package com.hh.xml;

import org.dom4j.io.SAXReader;

import java.io.File;
import java.util.Iterator;
import java.util.List;

import org.dom4j.Attribute;
import org.dom4j.Document;
import org.dom4j.DocumentException;
import org.dom4j.Element;

public class Test {
    public static void main(String[] args) throws DocumentException {
        int num = 10;
        //读取XML：
        //1.创建一个xml解析器对象：（就是一个流）
        SAXReader sr = new SAXReader();
        //2.读取xml文件，返回Document对象出来：
        //dom是students.xml文档
        Document dom = sr.read(new File("FirstModule/src/students.xml"));//xml文件路径
        System.out.println(dom);//这里就相当于将整个文档封装为Document对象了啊！
        //3.获取根节点：（根节点只有一个啊！）students根元素
        Element studentsEle = dom.getRootElement();
        //4.获取根节点下的多个子节点：
        Iterator<Element> it1 = studentsEle.elementIterator();
        while (it1.hasNext()) {
            //4.1获取到子节点：
            Element studentEle = it1.next();
            //4.2获取子节点的属性：
            List<Attribute> atts = studentEle.attributes();
            for (Attribute a : atts) {
                System.out.println("该子节点的属性：" + a.getName() + "---" + a.getText());
            }
            //4.3获取到子节点的子节点：
            Iterator<Element> it2 = studentEle.elementIterator();
            while (it2.hasNext()) {
                Element eles = it2.next();
                System.out.println("节点：" + eles.getName() + "---" + eles.getText());
            }
            //5.每组输出后加一个换行：
            System.out.println();
        }
    }

}
/*
输出结果：
"C:\Program Files\Java\jdk-17\bin\java.exe" "-javaagent:C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2023.1\lib\idea_rt.jar=57646:C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2023.1\bin" -Dfile.encoding=UTF-8 -classpath C:\Users\micha\Documents\JavaDemo\JavaDemo\out\production\FirstModule;C:\Users\micha\Documents\JavaDemo\JavaDemo\FirstModule\lib\dom4j-2.1.3.jar com.hh.xml.Test
org.dom4j.tree.DefaultDocument@71bc1ae4 [Document: name file:///C:/Users/micha/Documents/JavaDemo/JavaDemo/FirstModule/src/students.xml]
该子节点的属性：id---1
节点：name---九九
节点：age---18
节点：sex---女
节点：score---98.7

该子节点的属性：id---2
节点：name---健康
节点：age---15
节点：sex---男
节点：score---28.7

该子节点的属性：id---3
节点：name---解开
节点：age---34
节点：sex---男
节点：score---57.7
 */
```

