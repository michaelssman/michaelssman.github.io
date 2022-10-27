# Mixin多继承

```dart
///混入（多继承）
///作为混入类，不能实现构造方法。
mixinDemo() {
  D d = D();
  d.a();
  d.b();
  d.c();
  
  E e = E();
  e.b();
}

class A {
  a() => print('a.....'); //闭包a
}

class B {
  b() => print('b.....'); //闭包b
}

class C {
  c() => print('c.....'); //闭包c
}

class D extends A with B, C {}

class E = A with B, C;
```

