## 类

ArkTS支持基于类的面向对象的编程方式。类的声明描述了所创建的对象共同的属性和方法。

在以下示例中，定义了Person类，该类具有字段name和surname、构造函数和方法fullName：

```typescript
class Person { 
    name: string = '' 
    surname: string = '' 
    constructor (n: string, sn: string) { 
        this.name = n;  
        this.surname = sn; 
    }
    fullName(): string {
        return this.name + ' ' + this.surname; 
    }
}
```

如果需要实例化不同的对象，可以自定义constructor，在constructor中给对应的属性传入初值，在new的时候，传入需要接受的参数，就可以创建不同的实例对象。

定义类后，可以使用关键字new创建实例：

```typescript
let p = new Person('John', 'Smith');
console.log(p.fullName());
```

或者，可以使用对象字面量创建实例：

```typescript
class Point { 
    x: number = 0 
    y: number = 0
}
let p: Point = {x: 42, y: 42};
```

### 字段

字段是直接在类中声明的某种类型的变量。

类可以具有实例字段或者静态字段。

**实例字段**

实例字段存在于类的每个实例上。每个实例都有自己的实例字段集合。

要访问实例字段，需要使用类的实例。

```typescript
class Person {  name: string = ''  age: number = 0  constructor(n: string, a: number) {    this.name = n;    this.age = a;  }
  getName(): string {    return this.name;  }}
let p1 = new Person('Alice', 25);p1.name;let p2 = new Person('Bob', 28);p2.getName();
```

**静态字段**

使用关键字static将字段声明为静态。静态字段属于类本身，类的所有实例共享一个静态字段。

要访问静态字段，需要使用类名：

```typescript
class Person {  static numberOfPersons = 0  constructor() {     // ...     Person.numberOfPersons++;     // ...  }}
Person.numberOfPersons;
```

**字段初始化**

为了减少运行时的错误和获得更好的执行性能，

ArkTS要求所有字段在声明时或者构造函数中显式初始化。这和标准TS中的strictPropertyInitialization模式一样。

以下代码是在ArkTS中不合法的代码。

```typescript
class Person {  name: string // undefined    setName(n:string): void {    this.name = n;  }    getName(): string {    // 开发者使用"string"作为返回类型，这隐藏了name可能为"undefined"的事实。    // 更合适的做法是将返回类型标注为"string | undefined"，以告诉开发者这个API所有可能的返回值。    return this.name;  }}
let jack = new Person();// 假设代码中没有对name赋值，例如调用"jack.setName('Jack')"jack.getName().length; // 运行时异常：name is undefined
```

在ArkTS中，应该这样写代码。

```typescript
class Person {  name: string = ''    setName(n:string): void {    this.name = n;  }    // 类型为'string'，不可能为"null"或者"undefined"  getName(): string {    return this.name;  }}  
let jack = new Person();// 假设代码中没有对name赋值，例如调用"jack.setName('Jack')"jack.getName().length; // 0, 没有运行时异常
```

接下来的代码展示了如果name的值可以是undefined，那么应该如何写代码。

```typescript
class Person {  name?: string // 可能为`undefined`
  setName(n:string): void {    this.name = n;  }
  // 编译时错误：name可以是"undefined"，所以将这个API的返回值类型标记为string  getNameWrong(): string {    return this.name;  }
  getName(): string | undefined { // 返回类型匹配name的类型    return this.name;  }}
let jack = new Person();// 假设代码中没有对name赋值，例如调用"jack.setName('Jack')"
// 编译时错误：编译器认为下一行代码有可能会访问undefined的属性，报错jack.getName().length;  // 编译失败
jack.getName()?.length; // 编译成功，没有运行时错误
```

**getter和setter**

setter和getter可用于提供对对象属性的受控访问。

在以下示例中，setter用于禁止将age属性设置为无效值：

```typescript
class Person {  name: string = ''  private _age: number = 0  get age(): number { return this._age; }  set age(x: number) {    if (x < 0) {      throw Error('Invalid age argument');    }    this._age = x;  }}
let p = new Person();p.age; // 输出0p.age = -42; // 设置无效age值会抛出错误
```

在类中可以定义getter或者setter。

### 方法

方法属于类。类可以定义实例方法或者静态方法。静态方法属于类本身，只能访问静态字段。而实例方法既可以访问静态字段，也可以访问实例字段，包括类的私有字段。

**实例方法**

以下示例说明了实例方法的工作原理。

calculateArea方法通过将高度乘以宽度来计算矩形的面积：

```typescript
class RectangleSize {  private height: number = 0  private width: number = 0  constructor(height: number, width: number) {    // ...  }  calculateArea(): number {    return this.height * this.width;  }}
```

必须通过类的实例调用实例方法：

```typescript
let square = new RectangleSize(10, 10);square.calculateArea(); // 输出：100
```

**静态方法**

使用关键字static将方法声明为静态。静态方法属于类本身，只能访问静态字段。

静态方法定义了类作为一个整体的公共行为。

必须通过类名调用静态方法：

```typescript
class Cl {  static staticMethod(): string {    return 'this is a static method.';  }}console.log(Cl.staticMethod());
```

### 继承

子类继承父类的特征和行为，使子类具有父类相同的行为，减少重复代码，实现代码的复用和层次化设计。

继承使用extends关键字。

一个类可以继承另一个类（称为基类），并使用以下语法实现多个接口：

```typescript
class [extends BaseClassName] [implements listOfInterfaces] { 
    // ...
}
```

继承类继承基类的字段和方法，但不继承构造函数。继承类可以新增定义字段和方法，也可以覆盖基类定义的方法。

基类也称为“父类”或“超类”。继承类也称为“派生类”或“子类”。

示例：

```typescript
class Person { 
    name: string = '' 
    private _age = 0 
    get age(): number { 
        return this._age; 
    }
}
class Employee extends Person {
    salary: number = 0  
    calculateTaxes(): number {  
        return this.salary * 0.42;
    }
}
```

包含implements子句的类必须实现列出的接口中定义的所有方法，但使用默认实现定义的方法除外。

```typescript
interface DateInterface { 
    now(): string;
}
class MyDate implements DateInterface { 
    now(): string {  
        // 在此实现 
        return 'now is now';
    }
}
```

#### 父类访问super

关键字super可用于访问父类的实例字段、实例方法和构造函数。在实现子类功能时，可以通过该关键字从父类中获取所需接口：

```typescript
class RectangleSize { 
    protected height: number = 0 
    protected width: number = 0
    
  constructor (h: number, w: number) { 
      this.height = h;    this.width = w; 
  }
  draw() { 
      /* 绘制边界 */ 
  }
}

class FilledRectangle extends RectangleSize { 
    color = '' 
    constructor (h: number, w: number, c: string) {  
        super(h, w); // 父类构造函数的调用 
        this.color = c;  
    }
    
  draw() {   
      super.draw(); // 父类方法的调用   
      // super.height -可在此处使用  
      /* 填充矩形 */ 
  }
}
```

**方法重写**

子类可以重写其父类中定义的方法的实现。重写的方法必须具有与原始方法相同的参数类型和相同或派生的返回类型。

```typescript
class RectangleSize {  // ...  area(): number {    // 实现    return 0;  }}class Square extends RectangleSize {  private side: number = 0  area(): number {    return this.side * this.side;  }}
```

**方法重载签名**

通过重载签名，指定方法的不同调用。具体方法为，为同一个方法写入多个同名但签名不同的方法头，方法实现紧随其后。

```typescript
class C {  foo(x: number): void;            /* 第一个签名 */  foo(x: string): void;            /* 第二个签名 */  foo(x: number | string): void {  /* 实现签名 */  }}let c = new C();c.foo(123);     // OK，使用第一个签名c.foo('aa'); // OK，使用第二个签名
```

如果两个重载签名的名称和参数列表均相同，则为错误。

### 构造函数

类声明可以包含用于初始化对象状态的构造函数。

构造函数定义如下：

```typescript
constructor ([parameters]) {  // ...}
```

如果未定义构造函数，则会自动创建具有空参数列表的默认构造函数，例如：

```typescript
class Point {  x: number = 0  y: number = 0}let p = new Point();
```

在这种情况下，默认构造函数使用字段类型的默认值来初始化实例中的字段。

**派生类的构造函数**

构造函数函数体的第一条语句可以使用关键字super来显式调用直接父类的构造函数。

```typescript
class RectangleSize {  constructor(width: number, height: number) {    // ...  }}class Square extends RectangleSize {  constructor(side: number) {    super(side, side);  }}
```

**构造函数重载签名**

我们可以通过编写重载签名，指定构造函数的不同调用方式。具体方法为，为同一个构造函数写入多个同名但签名不同的构造函数头，构造函数实现紧随其后。

```typescript
class C {  constructor(x: number)             /* 第一个签名 */  constructor(x: string)             /* 第二个签名 */  constructor(x: number | string) {  /* 实现签名 */  }}let c1 = new C(123);      // OK，使用第一个签名let c2 = new C('abc');    // OK，使用第二个签名
```

如果两个重载签名的名称和参数列表均相同，则为错误。

### 可见性修饰符

类的方法和属性都可以使用可见性修饰符。

可见性修饰符包括：private、protected和public。默认可见性为public。

**Public（公有）**

public修饰的类成员（字段、方法、构造函数）在程序的任何可访问该类的地方都是可见的。

**Private（私有）**

private修饰的成员不能在声明该成员的类之外访问。

私有的变量无法通过对象进行直接访问，访问只能通过getter或者自定义的方法进行访问。这样就只暴露了接口进行访问和操作数据。修改和访问时需要通过get和set来进行。

```typescript
class C { 
    public x: string = '' 
    private y: string = '' 
    set_y (new_y: string) { 
        this.y = new_y; // OK，因为y在类本身中可以访问 
    }
}
let c = new C();
c.x = 'a'; // OK，该字段是公有的
c.y = 'b'; // 编译时错误：'y'不可见
```

**Protected（受保护）**

protected修饰符的作用与private修饰符非常相似，不同点是protected修饰的成员**允许在派生类中访问**，例如：

```typescript
class Base { 
    protected x: string = '' 
    private y: string = ''
}
class Derived extends Base { 
    foo() {  
        this.x = 'a'; // OK，访问受保护成员  
        this.y = 'b'; // 编译时错误，'y'不可见，因为它是私有的 
    }
}
```

### 对象字面量

对象字面量是一个表达式，可用于创建类实例并提供一些初始值。它在某些情况下更方便，可以用来代替new表达式。

对象字面量的表示方式是：封闭在花括号对({})中的'属性名：值'的列表。

```typescript
class C {  n: number = 0  s: string = ''}
let c: C = {n: 42, s: 'foo'};
```

ArkTS是静态类型语言，如上述示例所示，对象字面量只能在可以推导出该字面量类型的上下文中使用。其他正确的例子：

```typescript
class C {  n: number = 0  s: string = ''}
function foo(c: C) {}
let c: C
c = {n: 42, s: 'foo'};  // 使用变量的类型foo({n: 42, s: 'foo'}); // 使用参数的类型
function bar(): C {  return {n: 42, s: 'foo'}; // 使用返回类型}
```

也可以在数组元素类型或类字段类型中使用：

```typescript
class C {  n: number = 0  s: string = ''}let cc: C[] = [{n: 1, s: 'a'}, {n: 2, s: 'b'}];
```

**Record类型的对象字面量**

泛型Record<K, V>用于将类型（键类型）的属性映射到另一个类型（值类型）。常用对象字面量来初始化该类型的值：

```typescript
let map: Record<string, number> = {  'John': 25,  'Mary': 21,}
map['John']; // 25
```

类型K可以是字符串类型或数值类型，而V可以是任何类型。

```typescript
interface PersonInfo {  age: number  salary: number}let map: Record<string, PersonInfo> = {  'John': { age: 25, salary: 10},  'Mary': { age: 21, salary: 20}}
```

## 多态

多态常常和继承一起，表示子类继承父类，并且重写父类方法。父类和子类的实例对象在同一行为下就可以有不同的表现。

## 接口

接口是定义代码协定的常见方式。

任何一个类的实例只要实现了特定接口，就可以通过该接口实现多态。

接口通常包含属性和方法的声明

示例：

```typescript
interface Style { 
    color: string // 属性
}
interface AreaSize { 
    calculateAreaSize(): number // 方法的声明 
    someMethod(): void;     // 方法的声明
}
```

实现接口的类示例：

```typescript
// 接口：
interface AreaSize { 
    calculateAreaSize(): number // 方法的声明
    someMethod(): void;     // 方法的声明
}
// 实现：
class RectangleSize implements AreaSize {
    private width: number = 0 
    private height: number = 0
    someMethod(): void {  
        console.log('someMethod called');
    } 
    calculateAreaSize(): number { 
        this.someMethod(); // 调用另一个方法并返回结果  
        return this.width * this.height; 
    }
}
```

### 接口属性

接口属性可以是字段、getter、setter或getter和setter组合的形式。

属性字段只是getter/setter对的便捷写法。以下表达方式是等价的：

```typescript
interface Style {  color: string}
interface Style {  get color(): string  set color(x: string)}
```

实现接口的类也可以使用以下两种方式：

```typescript
interface Style {  color: string}
class StyledRectangle implements Style {  color: string = ''}
interface Style {  color: string}
class StyledRectangle implements Style {  private _color: string = ''  get color(): string { return this._color; }  set color(x: string) { this._color = x; }}
```

### 接口继承

接口可以继承其他接口，如下面的示例所示：

```typescript
interface Style {  color: string}
interface ExtendedStyle extends Style {  width: number}
```

继承接口包含被继承接口的所有属性和方法，还可以添加自己的属性和方法。

## 泛型类型和函数

泛型类型和函数允许创建的代码在各种类型上运行，而不仅支持单一类型。

### 泛型类和接口

类和接口可以定义为泛型，将参数添加到类型定义中，如以下示例中的类型参数Element：

```typescript
class CustomStack<Element> {  public push(e: Element):void {    // ...  }}
```

要使用类型CustomStack，必须为每个类型参数指定类型实参：

```typescript
let s = new CustomStack<string>();s.push('hello');
```

编译器在使用泛型类型和函数时会确保类型安全。参见以下示例：

```typescript
let s = new CustomStack<string>();s.push(55); // 将会产生编译时错误
```

### 泛型约束

泛型类型的类型参数可以绑定。例如，HashMap<Key, Value>容器中的Key类型参数必须具有哈希方法，即它应该是可哈希的。

```typescript
interface Hashable {  hash(): number}class HasMap<Key extends Hashable, Value> {  public set(k: Key, v: Value) {    let h = k.hash();    // ...其他代码...  }}
```

在上面的例子中，Key类型扩展了Hashable，Hashable接口的所有方法都可以为key调用。

### 泛型函数

使用泛型函数可编写更通用的代码。比如返回数组最后一个元素的函数：

```typescript
function last(x: number[]): number {  return x[x.length - 1];}last([1, 2, 3]); // 3
```

如果需要为任何数组定义相同的函数，使用类型参数将该函数定义为泛型：

```typescript
function last<T>(x: T[]): T {  return x[x.length - 1];}
```

现在，该函数可以与任何数组一起使用。

在函数调用中，类型实参可以显式或隐式设置：

```typescript
// 显式设置的类型实参last<string>(['aa', 'bb']);last<number>([1, 2, 3]);
// 隐式设置的类型实参// 编译器根据调用参数的类型来确定类型实参last([1, 2, 3]);
```

### 泛型默认值

泛型类型的类型参数可以设置默认值。这样可以不指定实际的类型实参，而只使用泛型类型名称。下面的示例展示了类和函数的这一点。

```typescript
class SomeType {}interface Interface <T1 = SomeType> { }class Base <T2 = SomeType> { }class Derived1 extends Base implements Interface { }// Derived1在语义上等价于Derived2class Derived2 extends Base<SomeType> implements Interface<SomeType> { }
function foo<T = number>(): T {  // ...}foo();// 此函数在语义上等价于下面的调用foo<number>();
```