# File和IO流

## File类的作用

File 类对象可封装要操作的文件，可通过 File 类的对象对文件进行操作，如查看文件的大小、判断文件是否隐藏、判断文件是否可读等。

局限：File类的相关操作，并不涉及文任内容相关的操作，这是单独依靠 File 类对象无法实现的操作，此时需要借助 1/0 流完成。

## I/O流的作用

将I/0流理解为程序和文件之间的一根 “管子〞。I为Input， O为Output, I/0流即输入输出流，可以理解为两个流向的“管子〞。

## IO流的分类

- 按照方向划分
  - 输入流、输出流
- 按照处理单元划分
  - 字节流、字符流
- 按照功能划分
  - 字节流（一个流）、处理流（多个流）

## IO流的体系结构

| 分类       | 字节输入流           | 字节输出流            | 字符输入流        | 字符输出流         |
| ---------- | :------------------- | --------------------- | ----------------- | ------------------ |
| 抽象基类   | InputStream          | OutputStream          | Reader            | Writer             |
| 访问文件   | FileInputStream      | FileOutputStream      | FileReader        | FileWriter         |
| 访问数组   | ByteArrayInputStream | ByteArrayOutputStream | CharArrayReader   | CharArrayWriter    |
| 访问管道   | PipedInputStream     | PipedOutputStream     | PipedReader       | PipedWriter        |
| 访问字符串 |                      |                       | StringReader      | StringWriter       |
| 缓冲流     | BufferdInputStream   | BufferedOutputStream  | BufferedReader    | BufferedWriter     |
| 转换流     |                      |                       | InputStreamReader | OutputStreamWriter |
| 对象流     | ObjectInputStream    | ObjectOutputStream    |                   |                    |
|            | FilterInputStream    | FilterOutputStream    | FilterReader      | FilterWriter       |
| 打印流     |                      | PrintStream           |                   | PrintWriter        |
| 推回输入流 | PushbackInputStream  |                       | PushbackReader    |                    |
| 数据流     | DataInputStream      | Data0utputStream      |                   |                    |

### 案例

```java
package com.hh.test01;

import java.io.*;
import java.util.ArrayList;
import java.util.Scanner;

public class HelloWorld {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        while (true) {
            //打印菜单
            System.out.println("-------------欢迎------------------");
            System.out.println("1.展示书籍");
            System.out.println("2.上新书籍");
            System.out.println("3.下架书籍");
            System.out.println("4.退出应用");
            //键盘输入 扫描类
            Scanner sc = new Scanner(System.in);
            System.out.println("请录入序号");
            //键盘录入序号
            int choice = sc.nextInt();
            if (choice == 1) {
                System.out.println("[老妈书城]>>>>>1.展示书籍");
                //从文件中读取list
                String s = "C:\\Users\\micha\\Documents\\JavaDemo\\demo.txt";
                File f = new File(s);
                if (f.exists() == true) {//文件存在
                    //流
                    FileInputStream fis = new FileInputStream(f);
                    ObjectInputStream ois = new ObjectInputStream(fis);
                    ArrayList list = (ArrayList) (ois.readObject());
                    for (int i = 0; i < list.size(); i++) {
                        Book b = (Book) list.get(i);
                        System.out.println(b.getbNo() + "---" + b.getbName() + "--- " + b.getbAuthor());
                    }
                } else {
                    System.out.println("当前没有上新书籍");
                }
            }
            if (choice == 2) {
                System.out.println("[老妈书城]>>>>>2.上新书籍");
                System.out.println("请录入书籍编号：");
                int bNo = sc.nextInt();
                System.out.println("请录入书籍名字：");
                String bName = sc.next();
                System.out.println("请录入书籍作者：");
                String bAuthor = sc.next();
                Book b = new Book(bNo, bName, bAuthor);


                //从文件中读取list
                String s = "C:\\Users\\micha\\Documents\\JavaDemo\\demo.txt";
                File f = new File(s);
                if (f.exists() == true) {//文件存在
                    //流
                    FileInputStream fis = new FileInputStream(f);
                    ObjectInputStream ois = new ObjectInputStream(fis);
                    ArrayList list = (ArrayList) (ois.readObject());
                    list.add(b);
                    //需要流
                    FileOutputStream fos = new FileOutputStream(f);
                    ObjectOutputStream oos = new ObjectOutputStream(fos);
                    //将list写出去
                    oos.writeObject(list);
//关闭流
                    oos.close();
                } else {
                    ArrayList list = new ArrayList();
                    list.add(b);
                    //需要流
                    FileOutputStream fos = new FileOutputStream(f);
                    ObjectOutputStream oos = new ObjectOutputStream(fos);
                    //将list写出去
                    oos.writeObject(list);
//关闭流
                    oos.close();
                }


            }
            if (choice == 3) {
                System.out.println("[老妈书城]>>>>>2.上新书籍");
//                System.out.println("请录入要下架的书籍的编号：");
//                int delNo = sc.nextInt();
//                for (int i = 0; i < list.size(); i++) {
//                    Book b = (Book) list.get(i);
//                    if (b.getbNo() == delNo) {
//                        list.remove(b);
//                        System.out.println("下架成功");
//                        break;
//                    }
//                }
            }
            if (choice == 4) {
                break;//推出循环
            }
        }
    }
}
```

#### book

```java
package com.hh.test01;

import java.io.Serializable;

public class Book implements Serializable {
    //属性
    private int bNo;
    private String bName;
    private String bAuthor;

    public int getbNo() {
        return bNo;
    }

    public void setbNo(int bNo) {
        this.bNo = bNo;
    }

    public String getbName() {
        return bName;
    }

    public void setbName(String bName) {
        this.bName = bName;
    }

    public String getbAuthor() {
        return bAuthor;
    }

    public void setbAuthor(String bAuthor) {
        this.bAuthor = bAuthor;
    }

    //构造器


    public Book(int bNo, String bName, String bAuthor) {
        this.bNo = bNo;
        this.bName = bName;
        this.bAuthor = bAuthor;
    }

    public Book() {
    }
}
```

