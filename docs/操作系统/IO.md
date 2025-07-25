# IO

计算机组成原理中，会接触到冯诺依曼结构。

<table>
<tr>
    <td rowspan="5">输入设备</td>
    <td>控制器</td>
    <td rowspan="5">输出设备</td>
</tr>
<tr><td>运算器</td></tr>
<tr><td>存储器</td></tr>
</table>

上面的输入输出就代表了IO的过程

IO主要是磁盘IO和网络IO。

如果每个应用都直接去操作磁盘或者网络的话，操作系统就乱套了，为了将应用程序的执行环境和操作系统内核的执行环境隔离开来，操作系统划分了用户空间和内核空间。

应用运行在用户空间，一些系统性的操作都在内核空间完成，当用户空间的程序想要使用系统性操作，比如操作系统磁盘IO的时候，需要向内核空间发起一次系统调用`System Call`。

### 同步阻塞IO模型

应用程序发起一个读数据的请求，内核空间去准备数据，数据准备就绪之后，把数据拷贝给应用，这个过程中线程一直处于堵塞状态，这就是同步阻塞IO模型。

### 同步非阻塞IO模型

**应用程序发起读IO请求后，会立即返回执行其它的任务**，但是需要**周期性的轮询去确定数据是否准备好**，等到数据准备就绪后，执行从内核空间拷贝数据到用户空间的操作，这个拷贝过程依旧是阻塞的，这个过程比较消耗CPU。

### IO多路复用模型

Linux中的select、poll、epoll都可以实现IO多路复用模型，在这个模型下，应用程序可以**同时监视多个IO操作**，当发现有数据准备就绪之后，内核系统会通知应用，这个时候应用再来读取数据，实现从内核空间到用户空间的数据拷贝，这个拷贝过程依旧是阻塞状态。IO多路复用相比轮询方式，显著减少了对CPU的消耗。

### 异步IO模型

比IO多路复用模型更快的模型，AIO基于回调机制实现。首先也是发起一个读请求，但是会直接返回，接着就不需要再管了，当数据准备完成后会通过回调的方式去做数据的拷贝。

## Java

### File和IO流

### File类的作用

File 类对象可封装要操作的文件，可通过 File 类的对象对文件进行操作，如查看文件的大小、判断文件是否隐藏、判断文件是否可读等。

局限：File类的相关操作，并不涉及文任内容相关的操作，这是单独依靠 File 类对象无法实现的操作，此时需要借助 I/O 流完成。

### I/O流的作用

将I/0流理解为程序和文件之间的一根两个流向的 “管子〞。

创建I/O流的时候，会传一个文件的路径地址，让程序和文件之间建立一个通道。

I为Input， O为Output，I/0流即输入输出流。

> 文件上传下载是一片一片的**流**的形式，避免下载大文件时内存会爆掉。
>
> 流：
>
> \- inputstream （读文件到内存）
>
> \- outputstream （从内存写到nsdata，socket，文件）
>
> 数据源：nsdata，socket，文件
>
> O：网络请求下载文件，下载的文件都放在内存会爆的，所以下载一点存储一点。

### IO流的分类

- 按照方向划分
  - 输入流、输出流
- 按照处理单元划分
  - 字节流、字符流
- 按照功能划分
  - 字节流（一个流）、处理流（多个流）

### IO流的体系结构

| 分类       | 字节输入流           | 字节输出流            | 字符输入流        | 字符输出流         |
| ---------- | :------------------- | :-------------------- | ----------------- | ------------------ |
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
                break;//退出循环
            }
        }
    }
}
```