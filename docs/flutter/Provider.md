# Provider

状态管理的框架

管理页面数据，也可以使用数据共享，数据共享是单向传递。Provider更加方便。各个页面共享数据。

传递数据，通讯。

数据要放在根页面，父页面之上。

性能优化：最小颗粒度的渲染刷新UI。使用`Consumer`。