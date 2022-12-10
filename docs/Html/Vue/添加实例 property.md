## [基本的示例](https://cn.vuejs.org/v2/cookbook/adding-instance-properties.html#基本的示例)

你可能会在很多组件里用到数据/实用工具，但是不想[污染全局作用域](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/scope-closures/ch3.md)。这种情况下，你可以通过在原型上定义它们使其在每个 Vue 的实例中可用。

```
Vue.prototype.$appName = 'My App'
```

这样 `$appName` 就在所有的 Vue 实例中可用了，甚至在实例被创建之前就可以。如果我们运行：

```
new Vue({
  beforeCreate: function () {
    console.log(this.$appName)
  }
})
```

则控制台会打印出 `My App`。就这么简单！

## [为实例 property 设置作用域的重要性](https://cn.vuejs.org/v2/cookbook/adding-instance-properties.html#为实例-property-设置作用域的重要性)

你可能会好奇：

> “为什么 `appName` 要以 `$` 开头？这很重要吗？它会怎样？”

这里没有什么魔法。`$` 是在 Vue 所有实例中都可用的 property 的一个简单约定。这样做会避免和已被定义的数据、方法、计算属性产生冲突。

> “你指的冲突是什么意思？”

另一个好问题！如果你写成：

```
Vue.prototype.appName = 'My App'
```

那么你希望下面的代码输出什么呢？

```
new Vue({
  data: {
    // 啊哦，`appName` *也*是一个我们定义的实例 property 名！😯
    appName: 'The name of some other app'
  },
  beforeCreate: function () {
    console.log(this.appName)
  },
  created: function () {
    console.log(this.appName)
  }
})
```

日志中会先出现 `"My App"`，然后出现 `"The name of some other app"`，因为 `this.appName` 在实例被创建之后被 `data` [覆写了](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch5.md)。我们通过 `$` 为实例 property 设置作用域来避免这种事情发生。你还可以根据你的喜好使用自己的约定，诸如 `$_appName` 或 `ΩappName`，来避免和插件或未来的插件相冲突。