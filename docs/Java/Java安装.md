## Java安装

JDK

https://www.oracle.com/java/technologies/downloads/

idea

https://www.jetbrains.com/

变量类型决定占据内存空间的大小。

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

![image-20230411223425462](\assets\image-20230411223425462.png)

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

## 多态

同一种行为，不同的子类呈现出来的状态是不同的。

多态跟属性无关，多态指的是方法的多态，而不是属性的多态。

例：猫可以喵喵叫、狗可以汪汪叫。

调用猫是喵喵、调用狗是汪汪。

使用一个动物基类，基类定义一个叫的方法。

猫实现是喵喵，狗实现是汪汪。子类对父类的方法重写。

调用的时候传的是动物基类，定义的时候只需要使用具体的动物类（猫或狗）。父类调用子类重写的方法。



