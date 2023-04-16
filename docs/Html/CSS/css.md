# css层叠样式表

专门用来美化html标签

## 应用方式

### 1、在标签上

```html
<img style="width: 500px;height:300px" src="图片地址" />
<div style="color: red">中国联通</div>
```

### 2、在head标签中写style标签

#### 2.1、类选择器

定义样式名字.c1，用的时候class，`.`和`class`对应。方便复用和修改。

设置class为inputBase的style

```css
.inputBase{
}
```

#### 2.2、id选择器

`#`和`id`。

#### 2.3、标签选择器

html标签的style，例：li、div

```css
button{
}
```

id是唯一的，标签会很多，所以用类选择器比较多。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        .c1{
             color:red;
         }
      	#c2{
             color:red;
         }
      	li{
          		color:red;
        }
    </style>
</head>
<body>
<h1 class="c1">用户登录</h1>
<h1 id="c2">用户注册</h1>
  
<ul>
    <li>中国移动</li>
    <li>中国联通</li>
    <li>中国电信</li>
</ul>
  
</body>
</html>
```

属性选择器

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
      	input[type='text']{
            border: 1px solid red;
         }
    </style>
</head>
<body>
<form method="post" action="/login">
    用户名：<input type="text" name="username">
    密码：<input type="password" name="password">
</form>
</body>
</html>
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        .v1[xx="hehe"]{
            color:gold;
        }
    </style>
</head>
<body>
<div>
    <span style="color: red">时间：</span>
    <span>2022-11-15</span>
</div>
<div class="v1" xx="haha">
    中国联合网络通信集团有限公司（简称“中国联通”）于2009年1月6日由原中国网通和原中国联通合并重组而成，公司在国内31个省（自治区、直辖市）和境外多个国家和地区设有分支机构，以及130多个境外业务接入点，拥有覆盖全国、通达世界的现代通信网络和全球客户服务体系，主要经营固定通信业务，移动通信业务，国内、国际通信设施服务业务，数据通信业务，网络接入业务，各类电信增值业务，与通信信息业务相关的系统集成业务等。目前，用户规模达到4.6亿。
</div>
<div class="v1" xx="hehe">
    中国联通是目前唯一一家整体进行混合所有制改革试点的中央企业。公司在2021年《财富》世界500强中位列第260位。作为支撑党政军系统、各行各业、广大人民群众的基础通信企业，中国联通在国民经济中具有基础性、支柱性、战略性、先导性的基本功能与地位作用，具有技术密集、全程全网、规模经济、服务经济社会与民生的特征与属性。
</div>
</body>
</html>
```

后代选择器

```css
.yy li{
  color:pink;
}
.yy > a{
  color:dodgerblue;
}
```

```html
<div class="yy">
  <a>百度</a>
  <div>
    <a>谷歌</a>
  </div>
  <ul>
    <li>美国</li>
    <li>日本</li>
    <li>韩国</li>
  </ul>
</div>
```

#### 多个样式

如果有多个样式，里面有重复的，下面定义的样式会覆盖上面的。

```css
.c1{
  color: red !important;
  border: 1px solid red;
}
.c2{
  color: green;
  font-size: 28px
}
```

```html
<div class="c1 c2">
  好的技术开发的进口国
</div>
```

##### !important

如果不想让下面的覆盖上面的，使用`!important`优先级提高。

### 3、将样式写到文件中

`<link rel="stylesheet" href="common.css">`导入，多个页面使用样式。

```css
.c1{
  height:100px;
}
.c2{
  color:red;
}
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <link rel="stylesheet" href="common.css">
</head>
<body>
<h1 class="c2">用户登录</h1>
<form method="post" action="/login">
    用户名：<input type="text" name="username">
    密码：<input type="text" name="password">
</form>
</body>
</html>
```

## 样式

### 宽度和高度

```css
.c1{
  height:200px;
  width:50%;
}
```

注意：

- 宽度支持百分比，高度不支持。
- 设置宽度和高度：对行内标签默认无效，对块级标签默认有效（宽度占满，即使留空白，不给别的使用）。

1. 设置宽度：`width: -webkit-calc(100% - 30px); ` 屏幕宽度减去30像素

设置按钮宽度60px和右边的距离0px

margin-left: -webkit-calc(100% - 60px);

Safari 和 Chrome 需要前缀`-webkit-`

## 块级标签和行内标签

使用css样式：标签`display:inline-block`，同时有行内标签和块级标签特性。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        .c1{
        display: inline-block;
        height: 100px;
        width: 300px;
        border: 1px solid red;
        }
    </style>
</head>
<body>
<h1>详细信息</h1>
<span class="c1">中国</span>
<span class="c1">联通</span>
</body>
</html>
```

display可以把行内标签改为块级标签，把块级标签改为行内标签

```html
<div style="display: inline;">哈哈</div>
<span style="display: block;">很好</span>
```

## 背景色

```css
background-color: #42B983;
```

### 透明度

`opacity: 0.7;`。

## 字体

```css
.c1{
  height: 59px;
  
  /*字体颜色*/
  color: red;
  color: #FF2F1F;
	color: rgba(0, 0, 0, 0.45); 
  
  font-size: 18px;/*字体大小*/
  font-weight: 100;/*加粗*/
  font-family: Microsoft Yahei;/*字体*/
  
  /*文字对齐方式*/
  text-align: center;/*水平方向居中*/ 
  line-height: 59px;/*垂直方向居中，只需要设置高度等于整个的高度（针对一行）*/
}
```

文字限制一行

```css
overflow: hidden;
white-space: nowrap;
text-overflow: ellipsis;
```

## 尺寸

```css
position: fixed;
bottom: 0rem;
right: 0rem;
width: 100%;
height: 45px;
```

## 显示不同的字体颜色

```html
<div :style="billData.VendName?'color:#0D0D0D':'color:#D7D7D7'">哈哈哈哈哈</div>
```

## 浮动

```html
<div>
    <span>左边</span>
    <span style="float:right">右边</span>
</div>
```

div默认是块级标签，如果浮动起来就和行内标签一样了。

一旦浮动起来，就撑不起来父级的div，需要最后加上`<div style="clear: both;"></div>`这样才能撑起来父级标签。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        .item{
        float: left;
        width: 200px;
        height: 170px;
        border: 1px solid red;
        }
    </style>
</head>
<body>
<div style="background-color: dodgerblue">
    <div class="item"></div>
    <div class="item"></div>
    <div class="item"></div>
    <div class="item"></div>
    <div style="clear: both;"></div>
</div>
</body>
</html>
```

## 内边距

内边距可以扩大点击响应范围

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        .outer{
          border: 1px solid red;
          height: 200px;
          width: 200px;
          padding-top: 20px;
          padding-left: 20px;
          padding-right: 20px;
        }
    </style>
</head>
<body>
<h1>边距</h1>
<div class="outer">
    <div style="background-color: gold;">听妈妈的话</div>
    <div>好浮夸的身份的方式</div>
</div>
</body>
</html>
```

```css
padding-top: 20px;
padding-left: 20px;
padding-right: 20px;
padding-bottom: 20px;

padding: 20px 10px 5px 20px;
padding: 20px
```

## 外边距

```html
<div style="background-color: red;height: 100px;margin-top:10px"> </div>
```

body标签默认有一个边距，造成页面四边都有白色间隙，如何去除：

```css
body{
  margin: 0px;
}
```

## 居中

文字居中：`line-height: 100px;`

图片居中使用外边距`margin-top: 22px`。

内容居中auto `margin: 0 auto 4px;`：顶部0px，左右居中，下部4px。

## a

a标签是行内标签，行内标签的高度、外边距默认无效。

去除下划线`text-decoration: none;`。

鼠标放上去高亮颜色：

```css
a:hover {
  color: red;
}
```

## 伪类

### hover

鼠标放上去的样式

```css
.c1 {
  color: green;
  opacity: 0.7;
  font-size: 15px;
  border-left: 3px solid green;
}
.c1:hover {
  color: red;
  opacity: 1;
  font-size: 19px;
  border-left: 3px solid red;
}
```

放上去之后，显示标签。

```css
.download {
  display: none;
}

.app:hover .download {
  display: block;
}

.app:hover .title {
  color: red;
}
```

```html
<div class="app">
  <div class="title">
    下载app
  </div>
  <div class="download">
    <img src="/static/download.png" style="width:45px; height:45px;" alt="">
  </div>
</div>
```

### after

标签尾部加一个东西。

```css
.c1:after{
  content: "大帅哥";
}
```

```html
<div class="c1">张三</div>
<div class="c1">李四</div>
```

应用

浮动，最后加`<div style="clear: both;"></div>`可以使用after代替。

```css
.clearfix:after{
  content: "";
  display: block;
  clear: both;
}
.item{
  float: left;
}
```

```html
<div class="clearfix">
  <div class="item">1</div> 
  <div class="item">2</div>
  <div class="item">3</div>
</div>
```

## position

固定位置，不随页面滑动而滑动。

### 1、fixed

固定在窗口的某个位置

#### 1.1、返回顶部

```css
.back {
  position: fixed;
  width: 60px;
  height: 60px;
  border: 1px solid red;
  right: 0px;
  bottom: 50px;
}
```

```html
<div class="back"></div>
```

#### 1.2、对话框

```css
.mask {
  position: fixed;
  background-color: black;
  left: 0px;
  right: 0px;
  top: 0px;
  bottom: 0px;
  opacity: 0.7;
  z-index: 999;
}

.dialog {
  position: fixed;
  width: 500px;
  height: 300px;
  background-color: white;
  left: 0px;
  right: 0px;
  margin: 0 auto;
  top: 200px;
  z-index: 1000;
}
```

```html
<div class="mask"></div>
<div class="dialog"></div>
```

### 2、relative和absolute

相对显示

```css
.d1 {
  height: 300px;
  width: 500px;
  border: 1px solid red;
  margin: 100px;
  position: relative;
}

.d1 .d2 {
  height: 59px;
  width: 59px;
  background-color: #00FF7F;
  position: absolute;
  right: 20px;
  top: 0;
}
```

```html
<div class="d1">
  <div class="d2"></div>
</div>
```

## border

`border: 1px solid red; `。1px：边框宽度，solid：实线，red边框颜色。

`border: 1px solid transparent; `。transparent：透明色。

```css
border: none;
border-radius: 12.5px;

border-left: 1px solid red;
border-right: 1px solid red;
```

例

```css
.c1{
  height: 50px;
  width: 500px;
  margin: 100px;
  background-color: #5f5750;
  border-left: 1px solid transparent;
}
.c1:hover{
    border-left: 1px solid red;
}
```

```html
<div class="c1">菜单</div>
```

## BootStrap

别人写好的css样式。

下载BootStrap

使用

- 在页面上引用BootStrap
- 编写HTML时，按照BootStrap的规定来编写+自定制。
