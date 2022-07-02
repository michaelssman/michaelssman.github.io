### 1. cell个数动态变化
要实现如下图所示的功能：点击开关，下面的cell会变化。

![1892989-583ceecc1b4513b1](assets/1892989-583ceecc1b4513b1.gif)

#### 实现的过程：

- 定义两个（对应开关控件个数）BOOL变量属性去记录开关的状态。
- 使用一个可变数组去存取数据源。
- 刷新tableView的时候，先把数据源晴空，再根据BOOL属性的值从上到下一个个去添加设置数据源。
- 最后调用tableview的reloadData方法，刷新列表。

结构清晰明了。

---

### 2. 模块化显示控制
![1892989-2d532d985a728233](assets/1892989-2d532d985a728233.png)

如上图所示
学员信息和收获地址是根据后台返回的信息去动态显示的。
有可能都不显示，有可能显示其中一个，有可能两个都有。

- 整体：

  为了方便维护，整个的tableView只控制每一模块儿是否显示。

- 模块：

  模块儿内的，自定义单独view，由自己独立维护。

### 3. 模块化显示
![image.png](https://upload-images.jianshu.io/upload_images/1892989-6d846eb5a461d9b2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

1. `子女教育，继续教育，大病医疗，居住扣除，赡养老人`这五大块是5个cell。不必把每一条都弄到整个tableView的cell。不方便管理，这样每一块是cell内部自己管理。容易开发和维护。
2. 观察下面的cell样式有三种，如图所标示`1，2，3`。先把三种基类写出来。`子女教育，继续教育，大病医疗，居住扣除，赡养老人`几个模块里面的视图样式公用。
3. `子女教育，继续教育，大病医疗，居住扣除，赡养老人`这几个模块下面的个数和样式不一样，但是顶部样式是一样的。都是：图标+标题+副标题样式。
所以就可以使用一个基类cell，带着顶部的样式，子类去实现下面的内容和顶部标题的text和点击方法。
另`继续教育，居住扣除，赡养老人`这三个视图个数和样式完全一样，可以直接继承一个基类，然后在子类中给控件赋内容。
4. `子女教育，继续教育，大病医疗，居住扣除，赡养老人`选中和取消选中两种状态，定义BOOL变量记录是否选中，从而去更新cell的高度去展开和闭合，还需要隐藏和显示每个模块儿下方的选项。reload一下点击的cell。
    注：reload的时候 cell里面的控件状态显隐会恢复原来的，需要在cell的代理方法中去设置显隐状态和图标的图片。调用`[tableView reloadRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationNone];`  方法，会重新走`- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath `和`- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath`方法。
#### 界面刷新问题：
调用`[tableView reloadRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationNone];` 方法如果有界面问题的话，就得调用`[tableView reloadData];`，就不会有数据超出界面问题。

例：
`子女教育`模块，选择子女个数还有扣除比例，相应的修改各自的text内容和扣除额数值，这些都是自己控制的，不需要在整个tableView里面去做。每一部分都是独立维护。只需把最后的结果，在`.h`文件中使用一个属性去传出。