XXXX年毕业于XXXX大学计算机科学与技术专业，了解计算机理论知识。

公司经历：直播类型的公司、记账类型的公司、教育类型的公司。

了解iOS底层原理：对象原理、类的结构、消息发送转发、应用程序加载流程、启动优化、图片加载流程、block、多线程和锁、组件化、响应者链、内存管理、自动释放池、weak原理等。

项目中使用的有：crash日志、使用消息转发防应用崩溃、图片圆角避免离屏渲染、使用响应者链处理手势冲突和按钮点击范围、自己做pod组件库、优化预排版、列表按需加载等。

利用 Auto Layout 的自适应布局能力推导tableViewCell高度，并创建tableView分类缓存高度。

利用响应者链处理轮播图和tableView滑动响应冲突问题

在父view上`\- (**nullable** UIView *)hitTest:(CGPoint)point withEvent:(**nullable** UIEvent *)event; `根据`point.y`的大小判断是否在轮播图上



利用适配器模式，适配调用接口。

- 创建分类，AFNetworking3.0适配4.0，设置header。
- 封装MBProgressHUD的调用接口，避免三方库升级导致多处修改。

利用策略模式，解决过多的ifelse条件判断。

- 处理文章资讯版块多种类别的cell。
- 不同类型cell的不同点击事件，使用NSInvocation调用方法。

画图：

- 使用CAGradientLayer实现颜色渐变填充色。
- 带动画的环形图。利用CAShapeLayer画图，CAAnimation子类做动画。