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