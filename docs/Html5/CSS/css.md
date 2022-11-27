# css样式

专门用来美化html标签

## 应用方式

### 1、在标签上

```html
<img style="width: 500px;height:300px" src="图片地址" />
<div style="color: red">中国联通</div>
```

### 2、在head标签中写style标签

类选择器：定义样式名字.c1 用的时候class，`.`和`class`对应。方便复用和修改。

id选择器：`#`和`id`。

标签选择器：html标签，例：li、div

id是唯一的，标签会很多，所以用类选择器比较多。

属性选择器

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
      	input[type='text']{
            border: 1px solid red;
         }
    </style>
</head>
<body>
<h1 class="c1">用户登录</h1>
<h1 id="c2">用户注册</h1>
<form method="post" action="/login">
    用户名：<input type="text" name="username">
    密码：<input type="password" name="password">
</form>
  
<ul>
    <li>中国移动</li>
    <li>中国联通</li>
    <li>中国电信</li>
</ul>
  
</body>
</html>
```

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





## !important

!important优先级提高。

## 设置宽度

1. 使用百分比：`width: 100%;`

2. 设置宽度：`width: -webkit-calc(100% - 30px); ` 屏幕宽度减去30像素

设置按钮宽度60px和右边的距离0px

margin-left: -webkit-calc(100% - 60px);

Safari 和 Chrome 需要前缀`-webkit-`



设置class为inputBase的style

```css
	.inputBase{
	}
```

设置控件style

```css
	button{
	}
```

## 颜色

背景色

```css
background-color: #42B983;
```

字体颜色

```css
color: #FF2F1F;
color: rgba(0, 0, 0, 0.45);  
```

## 字体

```css
font-size: 18px;
text-align: left;
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

## 边框

```css
border: none;
border-radius: 12.5px;
```

## 显示不同的字体颜色

```html
<div :style="billData.VendName?'color:#0D0D0D':'color:#D7D7D7'">哈哈哈哈哈</div>
```

