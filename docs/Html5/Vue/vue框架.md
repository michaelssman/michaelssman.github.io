开发工具：HBuilder

Vue项目

新建，项目->新建->vue2.6.10

npm install

运行：npm run serve
打包：npm run build

Vue框架
1，*.vue			class

- data			private var
- props:			构造函数的入参，属性
- computed:		计算
- methods:			方法
- watch:			事件event,listener

2，

Vue生命周期函数

在某一时刻会自动执行的函数

- created()      创建
- mounted()   挂载渲染
- updated()    数据更新
- unmounted()销毁	

- activated()		激活

3，

- mixins:			混合
- components:		(子)组件

4，
$el				Html节点
$refs			引用集合(reference)
$watch			事件event,listener
$set			=

5，
$emit	事件触发

6，指令

- v-text
- v-html
- v-show
- v-if....v-else-if....v-else
- v-for
- v-on:	@
  - 绑定事件，可以简写 @
- v-bind:
  - 绑定
  - v-bind绑定  子组件属性传值
  - 简写 :
- v-model	双向绑定
- xxx.sync

7，key/ref/is

扩展：
https://cn.vuejs.org/v2/guide/class-and-style.html
https://cn.vuejs.org/v2/guide/components-custom-events.html

### 框架

进销存框架：Vue，Framework7，Axios，Vuex，Less，Webpack

- assets
- component	页面 组件
- content	样式 css/less
- scripts	脚本
- store	状态管理
- app.vue	入口文件
- main.js	入口函数 文件引入
- routes.js
- index.html

- vue单文件格式
- 路由
- services.js API接口配置

### framework7

framework7:

​	f7-app

​	f7-view

​	f7-page

​	f7-navbar、f7-subnavbar、f7-toolbar

​	f7-list

​	f7-sheet

​	f7-popup

​	f7router、f7-route