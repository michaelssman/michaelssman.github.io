# css

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

