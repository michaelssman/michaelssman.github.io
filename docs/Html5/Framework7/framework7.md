安装指定版本framework7

```
npm install framework7@5.7.14
```

页面跳转

```
			toList(path, type) {
				this.$f7router.navigate(path, {
					context: {
						type: type,
					}
				});
			},
```

`				<div class="fake-search-box" @click="$f7router.navigate('/resource-search/')">`


