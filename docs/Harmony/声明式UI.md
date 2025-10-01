# 声明式UI

**声明式UI**

开发时只需要去描述UI应该呈现的结果，不用关系内部如何实现，过程交由框架来实现。

**状态驱动视图更新**

开发过程中不直接操作UI，而是通过操作状态数据来间接的改变UI内容，

状态：驱动应用变化的数据源

视图：与状态相关联的UI内容

当状态改变时框架会自动更新与状态相关联的视图，实现内容的动态。

## 自定义组件

通过多种组件的组合，封装为可重用的UI单元。

### @Component

ArkTS通过struct声明组件名，使用@Component装饰自定义组件。

### @Entry

@Entry表示这是一个入口页面，可以通过UIAbility进行加载，也可以通过路由被访问。

使用@Entry和@Component装饰的自定义组件作为页面的入口，会在页面加载时首先进行渲染。

```less
@Entry
@Componentstruct 
ToDoListPage {...}
```

例如ToDoListPage组件对应如下整个待办页面。

**图1** ToDoListPage待办列表

![点击放大](https://alliance-communityfile-drcn.dbankcdn.com/FileServer/getFile/cmtyPub/011/111/111/0000000000011111111.20240506144606.39820942366689487050649182128721:50001231000000:2800:9C8B3287E3F3424F5264DFF838EE9C9200A44297D98D955052B9F08D9172D719.png?needInitFileName=true?needInitFileName=true)

使用@Component装饰的自定义组件，如ToDoItem这个自定义组件则对应如下内容，作为页面的组成部分。

```less
@Componentstruct ToDoItem {...}
```

**图2** ToDoItem
![点击放大](https://alliance-communityfile-drcn.dbankcdn.com/FileServer/getFile/cmtyPub/011/111/111/0000000000011111111.20240506144606.40304201154235822212672741114548:50001231000000:2800:9A87D9ADE82FC1CE1A0EB3CF36BAD312D3547C506E821A98A698C54389767710.png?needInitFileName=true?needInitFileName=true)

### build函数

在struct自定义组件内使用build方法来进行**UI描述**。

build方法内可以容纳内置组件和其他自定义组件，如Column和Text都是内置组件，由ArkUI框架提供，ToDoItem为自定义组件。

```typescript
@Entry
@Component
struct ToDoListPage {
  //...
  build() {
    Column(...) {
      Text(...)
      //...
      ForEach(..., (item: string) => {
        ToDoItem(...)
      }, ...)
    }
   //...
  }
}
```

### 配置属性

自定义组件的组成使用基础组件和容器组件等内置组件进行组合。但有时内置组件的样式并不能满足我们的需求，ArkTS提供了属性方法用于描述界面的样式。属性方法支持以下使用方式：

- 常量传递

  例如使用fontSize(50)来配置字体大小。

  ```typescript
  Text('Hello World') 
      .fontSize(50)
  ```

- 变量传递

  在组件内定义了相应的变量后，例如组件内部成员变量size，就可以使用this.size方式使用该变量。

  ```typescript
  Text('Hello World') 
      .fontSize(this.size)
  ```

- 链式调用

  在配置多个属性时，ArkTS提供了链式调用的方式，通过'.'方式连续配置。

  ```typescript
  Text('Hello World') 
      .fontSize(this.size) 
      .width(100)  
      .height(100)
  ```

- 表达式传递

  属性中还可以传入普通表达式以及三目运算表达式。

  ```typescript
  Text('Hello World')
      .fontSize(this.size) 
      .width(this.count + 100) 
      .height(this.count % 2 === 0 ? 100 : 200)
  ```

- 内置枚举类型

  除此之外，ArkTS中还提供了内置枚举类型，如Color，FontWeight等，例如设置fontColor改变字体颜色为红色，并添加fontWeight属性使字体加粗。

  ```typescript
  Text('Hello World')
      .fontSize(this.size) 
      .width(this.count + 100) 
      .height(this.count % 2 === 0 ? 100 : 200)  
      .fontColor(Color.Red)  
      .fontWeight(FontWeight.Bold)
  ```

## 布局

### 容器组件

对于有多种组件需要进行组合时，容器组件则是描述了这些组件应该如何排列的结果。

ArkTS使用容器组件采用花括号语法，内部放置UI描述。

这里我们将介绍最基础的两个布局——列布局和行布局。

### Row

```typescript
Row() { 
    Image($r('app.media.ic_default')) 
    //... 
    Text(this.content) 
    //...
}
```

### Column

```typescript
Column() {
  Text($r('app.string.page_title'))
  //...

  ForEach(this.totalTasks,(item: string) => {
    TodoItem({content:item})
    },...)
}
```

## 改变组件状态

实际开发中由于交互，页面的内容可能需要产生变化，以每一个ToDoItem为例，其在完成时的状态与未完成时的展示效果是不一样的。

不同状态的视图
![点击放大](https://alliance-communityfile-drcn.dbankcdn.com/FileServer/getFile/cmtyPub/011/111/111/0000000000011111111.20240506144606.31987077012045903026724779361504:50001231000000:2800:6BBA256887E3B27133C6C9E1EC9391FF48BBA45361900E0167EEB82EE0748873.png?needInitFileName=true?needInitFileName=true)

声明式UI的特点就是UI是随数据更改而自动刷新的。

### @State

定义状态变量isComplete，其被@State装饰后，框架内建立了数据和视图之间的绑定，其值的改变影响UI的显示。

```java
@State isComplete: boolean = false;
```

**图6** @State装饰器的作用
![点击放大](https://alliance-communityfile-drcn.dbankcdn.com/FileServer/getFile/cmtyPub/011/111/111/0000000000011111111.20240506144606.47813030467595551310811455585426:50001231000000:2800:21A6D100298D09DEE959FEFD6DB4E5BBC3F143F222770A355BAEDC12F1EE4DC4.png?needInitFileName=true?needInitFileName=true)



用圆圈和对勾这样两个图片，分别来表示该项是否完成，这部分涉及到内容的切换，需要使用条件渲染if / else语法来进行组件的显示与消失，当判断条件为真时，组件为已完成的状态，反之则为未完成。

```typescript
if (this.isComplete) { 
    Image($r('app.media.ic_ok'))    
        .objectFit(ImageFit.Contain)    
        .width($r('app.float.checkbox_width'))    
        .height($r('app.float.checkbox_width'))    
        .margin($r('app.float.checkbox_margin'))
} else { 
    Image($r('app.media.ic_default'))    
        .objectFit(ImageFit.Contain)    
        .width($r('app.float.checkbox_width'))    
        .height($r('app.float.checkbox_width'))    
        .margin($r('app.float.checkbox_margin'))
}
```

### @Builder

由于两个Image的实现具有大量重复代码，ArkTS提供了@Builder装饰器，来修饰一个函数，快速生成布局内容，从而可以避免重复的UI描述内容。这里使用@Bulider声明了一个labelIcon的函数，参数为icon，对应要传给Image的图片路径。

```typescript
@Builder labelIcon(icon: Resource) { 
    Image(icon)  
        .objectFit(ImageFit.Contain)    
        .width($r('app.float.checkbox_width'))    
        .height($r('app.float.checkbox_width'))    
        .margin($r('app.float.checkbox_margin'))
}
```

使用时只需要使用@Builder装饰的函数名，即可快速创建布局。

```typescript
if (this.isComplete) { 
    this.labelIcon($r('app.media.ic_ok'));
} else { 
    this.labelIcon($r('app.media.ic_default'));
}
```

为了让待办项带给用户的体验更符合已完成的效果，给内容的字体也增加了相应的样式变化，这里使用了三目运算符来根据状态变化修改其透明度和文字样式，如opacity是控制透明度，decoration是文字是否有划线。通过isComplete的值来控制其变化。

```typescript
Text(this.content) 
//...  
    .opacity(this.isComplete ? CommonConstants.OPACITY_COMPLETED : CommonConstants.OPACITY_DEFAULT) 
    .decoration({ type: this.isComplete ? TextDecorationType.LineThrough : TextDecorationType.None })
```

### onClick

最后，为了实现与用户交互的效果，在Row组件上添加了onClick点击事件，当用户点击该待办项时，数据isComplete的更改就能够触发UI的更新。

```typescript
@Component
struct ToDoItem { 
    @State isComplete : boolean = false; 
    @Builder labelIcon(icon: Resource) {...}  
    //...  
    build() {  
        Row() {  
            if (this.isComplete) {        
                this.labelIcon($r('app.media.ic_ok')); 
            } else {  
                this.labelIcon($r('app.media.ic_default'));   
            }    
            //...   
        } 
        //...   
        .onClick(() => {   
            this.isComplete= !this.isComplete;  
        }) 
    }
}
```

## 循环渲染列表数据

刚刚只是完成了一个ToDoItem组件的开发，当有多条待办数据需要显示在页面时，就需要使用到ForEach循环渲染语法。

例如这里我们有五条待办数据需要展示在页面上。

```typescript
totalTasks: Array<string> = [ 
    '早起晨练', 
    '准备早餐',
    '阅读名著',
    '学习ArkTS', 
    '看剧放松'
]
```

ForEach基本使用中，只需要了解要渲染的数据以及要生成的UI内容两个部分，例如这里要渲染的数组为以上的五条待办事项，要渲染的内容是ToDoItem这个自定义组件，也可以是其他内置组件。

**图7** ForEach基本使用

ForEach有两个参数

1. 数据源
2. 生成器函数

![点击放大](https://alliance-communityfile-drcn.dbankcdn.com/FileServer/getFile/cmtyPub/011/111/111/0000000000011111111.20240506144606.84980533491365151694524215978081:50001231000000:2800:EA70321349EDF54403383B509CF3AEC6480CECB9CB5A2653A68FD3D506AB58DB.png?needInitFileName=true?needInitFileName=true)

ToDoItem这个自定义组件中，每一个ToDoItem要显示的文本参数content需要外部传入，参数传递使用花括号的形式，用content接受数组内的内容项item。

最终完成的代码及其效果如下。

```typescript
@Entry
@Component
struct ToDoListPage {
   //...
   build() {
       Column() {
         Text(...)
           //...
         ForEach(this.totalTasks,(item: string) => {
           TodoItem({content: item})
         },...)
       }
       .width('100%')
       .height('100%')
   }
 }
```
