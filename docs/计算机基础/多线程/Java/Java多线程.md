# Java多线程

创建线程有三种方式：

- 方式1：继承Thread类
- 方式2：实现Runnable接口
- 方式3：实现Callable接口

## Thread

```java
/**
 * 创建一个线程类TestThread，需要继承Thread
 */
public class TestThread extends Thread {
    @Override
    public void run() {//线程对应的任务放在一个方法
        for(int i = 0; i < 10; i++){
            System.out.println("子线程" + i);
        }
    }
}
```

使用

```java
TestThread t = new TestThread();
t.start();
```



