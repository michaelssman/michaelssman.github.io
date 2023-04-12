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

