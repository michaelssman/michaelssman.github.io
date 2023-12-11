# Sliver

一块儿一块儿的意思，跟滚动有关系，列表长，需要里面比外面大的东西。

```dart
CustomScrollView(
  //视窗
  slivers: [
    SliverToBoxAdapter(
      child: FlutterLogo(),
    ),
    SliverToBoxAdapter(
      child: Text("hello sliver"),
    ),
    SliverToBoxAdapter(
      child: Column(
        children: [
          FlutterLogo(),
          Text("hello sliver"),
        ],
      ),
    ),
  ],
)
```

