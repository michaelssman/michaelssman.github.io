Vscode 创建一个新的文件 保存为html格式

然后输入`!` 和 回车，会自动的插入html代码。

下载插件`open in browser`，右键html文件 选择`Open In Default Browser` 或者快捷键optin + B。

## html标签

### h

```html
<!DOCTYPE html>
<html lang="en">
<head>#内部配置和引用
    <meta charset="UTF-8">	<!-- 编码 -->
    <title>Title</title>	<!-- 浏览器标签页的名字 -->
</head>
<body>
		<h1>1级标题</h1>
		<h2>2级标题</h2>
		<h3>3级标题</h3>
		<h4>4级标题</h4>
		<h5>5级标题</h5>
		<h6>6级标题</h6>
</body>
</html>
```

h标签是块级标签

### div和span

```html
<div>
  <span style="color: red">时间：</span>
  <span>2022-11-15</span>
</div>

<span>回复速度来看</span>
```

div：占一整行，块级标签

span：自己有多大就占多少，行内标签，内联标签。

div里面可以包含span标签。

### 超链接

跳转其它网站

```html
<a href="http://www.chinaunicom.com.cn/about/about.html">点击跳转</a>
```

跳转自己网站其它地址

```html
<a href="http://127.0.0.1:5000/show/info">点击跳转</a>
<a href="/show/info">点击跳转</a>
```

```html
# 当前页面打开
<a href="/show/info">点击跳转</a>
#新tab页打开
<a href="/show/info" target="_blank">点击跳转</a>
```

### 图片

```html
<img style="width: 500px;height:300px" src="图片地址" />
<img style="width: 50%" src="图片地址" /> <!-- 占整个屏幕的50%比例 -->
```

显示自己的图片：

- 项目中创建：static目录，图片放在static目录
- 在页面上引入图片`<img style="width: 500px;height:300px" src="/static/wbq.png" />`

### 列表

无序列表

```html
<ul>
  <li>中国移动</li>
  <li>中国联通</li>
  <li>中国电信</li>
</ul>
```

有序列表

<ol>
  <li>中国移动</li>
  <li>中国联通</li>
  <li>中国电信</li>
</ol>

### 表格table

thead表头 tr行 th列

tbody内容 tr行 td列

border=1：边框

```html
<table border="1">
  <thead>
    <tr> <th>ID</th> <th>Name</th> <th>age</th> </tr>
  </thead>
  <tbody>
    <tr> <td>10</td> <td>蒸蛋</td> <td>18</td> </tr>
        <tr> <td>11</td> <td>但是</td> <td>14</td> </tr>
        <tr> <td>12</td> <td>更多</td> <td>12</td> </tr>
        <tr> <td>13</td> <td>爱国</td> <td>16</td> </tr>
  </tbody>
</table>
```

<table border> 
  <tr><th>表头1</th><th>表头2</th><th>表头3</th><th>表头4</th></tr>
  <tr><td>第1行第1列</td><td rowspan=3>第1，2，3行第2列</td><td>第1行第3列</td><td>第1行第4列</td></tr>
  <tr><td>第2行第1列</td><td>第2行第3列</td><td>第2行第4列</td></tr>
  <tr><td>第3行第1列</td><td>第3行第3列</td><td>第3行第4列</td></tr>
  <tr><td>第4行第1列</td><td>第4行第2列</td><td>第4行第3列</td><td>第4行第4列</td></tr>
  <tr><td>第5行第1列</td><td>第5行第2列</td><td>第5行第3列</td><td>第5行第4列</td></tr>
	<tr><td>第6行第1列</td><td rowspan=2>第6，7行第2列</td><td>第6行第3列</td><td>第6行第4列</td></tr>
  <tr><td>第7行第1列</td><td>第7行第3列</td><td>第7行第4列</td></tr>
</table>
```html
<table border> 
  <tr><th>表头1</th><th>表头2</th><th>表头3</th><th>表头4</th></tr>
  <tr><td>第1行第1列</td><td rowspan=3>第1，2，3行第2列</td><td>第1行第3列</td><td>第1行第4列</td></tr>
  <tr><td>第2行第1列</td><td>第2行第3列</td><td>第2行第4列</td></tr>
  <tr><td>第3行第1列</td><td>第3行第3列</td><td>第3行第4列</td></tr>
  <tr><td>第4行第1列</td><td>第4行第2列</td><td>第4行第3列</td><td>第4行第4列</td></tr>
  <tr><td>第5行第1列</td><td>第5行第2列</td><td>第5行第3列</td><td>第5行第4列</td></tr>
	<tr><td>第6行第1列</td><td rowspan=2>第6，7行第2列</td><td>第6行第3列</td><td>第6行第4列</td></tr>
  <tr><td>第7行第1列</td><td>第7行第3列</td><td>第7行第4列</td></tr>
</table>
```

### input系列

```html
<input type="text">
<input type="password">
<input type="file"> <!--选择文件-->
<!--单选框 name一样的才行-->
<input type="radio" name="n1">男
<input type="radio" name="n1">女
<!--复选框-->
<input type="checkbox">篮球
<input type="checkbox">足球
<input type="checkbox">乒乓球
<input type="checkbox">羽毛球
<!--按钮-->
<!--普通按钮-->
<input type="button" value="提交">
<!--提交表单-->
<input type="submit" value="表单form提交">
```

### 多行文本

```html
<!--rows默认行数-->
<textarea rows="3"></textarea>
```

### 下拉框

```html
<select>
  <option>北京</option> 
  <option>上海</option> 
  <option>深圳</option>
</select>
<!--多选-->
<select multiple>
  <option>北京</option> 
  <option>上海</option> 
  <option>深圳</option>
</select>
```

### form

页面上的数据提交到后台

```html
<form method="get" action="/xxx/xxx/xx">
    <div>
        用户名：<input type="text" name="name">
    </div>
    <div>
        密码：<input type="password" name="pd">
    </div>
    <div>
        <input type="submit" value="submit提交">
    </div>
</form>
```

- form标签包裹要提交的数据的标签
  - 提交方式：method="get"
  - 提交的地址：action="/xxx/xxx/xx"
  - form标签里面必须有一个submit标签
- 在form里面的标签：input、select、textarea，只提交能输入、能用户交互的标签，div、img就不会提交。
  - 一定要写name属性
