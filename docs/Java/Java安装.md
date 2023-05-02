## Java安装

JDK

https://www.oracle.com/java/technologies/downloads/

idea

https://www.jetbrains.com/

变量类型决定占据内存空间的大小。

PPT：https://cloud.fynote.com/share/s/z9JGaVu6

## 快捷键

ctrl+d 复制一行
ctrl+y 删除一行

sout：System.*out*.println();

alt+Insert：类构造器，可以选择多个属性

## 方法重载

同一个类中，**方法名相同**，**形参列表不同**（类型不同、个数不同、顺序不同）的多个方法，构成了方法的重载。

## 数据类型

### 数组

```java
//数据遍历
public static void main(String[] args) {
    int[] arr = new int[4];
    arr[0] = 15;
    arr[1] = 98;
    for (int num:arr){
        System.out.println(num);
    }
}
//15 98 0 0
```

### 集合

![image-20230411223425462](assets\image-20230411223425462.png)

```java
    public static void main(String[] args) {
//定义一个集合
        ArrayList list = new ArrayList();
        System.out.println(list);
        //add
        list.add("aaa");
        list.add("bbb");
        list.add("ccc");
        list.add("ddd");
        System.out.println(list);
//删
        list.remove("bbb");
        System.out.println(list);
        //改
        list.set(0, "eee");
        System.out.println(list);
//查看
        System.out.println(list.get(2));
        //遍历
        for (int i = 0; i <= list.size() - 1; i++) {
            System.out.println(list.get(i));
        }
    }
```
