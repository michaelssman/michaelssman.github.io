### 组件

Vue 里都是组件

组件化开发 降低耦合性。每个人负责一个组件 合成整个页面

```vue
    app.component('my-title',{
        template:'<h1 style="text-align:center">象牙山洗脚城</h1>'
    })
```

静态组件

动态组件

子组件是被调用的。



### Vue设计模式

面向DOM-->面向数据

mvvm

m：数据

v：视图view

vm：viewModel 数据视图链接层



Vue.createApp创建应用

app.mount挂载到DOM元素上。返回Vue的根组件

template模版中：单引号可以换行，双引号时一行。



双括号{{}}自面量。插值表达式。



### 阻止默认事件

```javascript
 <form action="https://jspang.com" @click="handleButton">
            <button type="submit">submit</button>
            </form>
```

```vue
  methods:{
            handleButton(e){
                e.preventDefault()
            }
        },
```

模版修饰符prevent自动阻止了默认事件

```
 <form action="https://jspang.com" @click.prevent="handleButton">
            <button type="submit">submit</button>
            </form>
```



### 事件绑定

停止冒泡 .stop

.self点击自己才会触发，子元素不会触发

prevent阻止默认行为的修饰符. 阻止from表单的跳转

capture捕获模式。和冒泡模式调用方法顺序相反

once第一次点击好使，以后再点击都不好使了。

#### 按键修饰符

.enter按回车才会调用

### 双向数据绑定

v-model

输入框input 多行输入框textarea 多选checkbox 单选radio

