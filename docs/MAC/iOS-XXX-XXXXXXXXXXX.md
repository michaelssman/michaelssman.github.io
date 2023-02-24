## 个人信息

<table  border="0"> 
  <tr><td>姓名：XXX</td><td>工作年限：6年</td></tr>
  <tr><td>学历：河南师范大学</td><td>专业：计算机科学与技术</td></tr>
  <tr><td>电话：1XX-XXXX-XXXX</td><td>邮箱：michaelss_work@outlook.com</td></tr>
  <tr><td colspan=2>个人博客：https://michaelssman.github.io/</td></tr>
</table>


---

## 教育背景（2011.09-2015.07）

河南师范大学/本科/计算机与信息工程/计算机科学与技术专业

主修课程：计算机操作系统，数据结构，算法设计，计算机网络，在校学习编程语言包括C语言，Visual C++，Java。

相关奖项：计算机等级证书，数学建模国赛省级一等奖，美国大学生数学建模竞赛国际二等奖，单项奖学金。

---

## 技能清单

- 熟练掌握ARC和MRC，熟练掌握内存管理和内存释放编程技巧
  - 写工具类检测页面是否释放。
  - 解决各种内存问题（例：NSTimer循环引用的内存泄漏问题，block循环引用）。
  - 了解自动释放池底层原理。
  - 了解属性关键字（retain、assign、strong、weak、copy）。
  - 了解weak对象存储的原理和销毁置nil的原理，对象dealloc流程。
- 了解对象的底层原理（alloc流程，isa指针）。
- 了解类的原理和底层数据结构。
- 消息发送和消息转发机制。
- 熟悉Runloop
  - Runloop做性能优化卡顿检测和按需加载
- 熟悉响应者链和事件传递。
- 熟悉Runtime
- 了解Block原理和本质
  - block的类型
  - block的copy和对外界变量的捕获
  - 处理循环引用3种方法和处理内存泄漏问题
- 应用程序加载流程
  - clang插桩和二进制重排原理做启动优化。
  - 类和分类的load加载。
  - Rebase和binding
- 熟悉代理模式、单例模式、观察者模式、工厂模式、建造者模式、策略模式、模版模式、适配器模式等多种设计模式。
- 熟练MVC，MVP，MVVM软件架构模式。
- 具有较强的面向对象编程概念，熟悉响应式编程、链式编程、函数式编程。
- 熟练掌握GCD、NSOperation、NSThread多线程编程技术（设置依赖，并发数和各种锁）。
- 熟悉SDWebImage、fishhook、Aspects、MBProgressHUD、Masonry等第三方类库，进行源码分析。
- 熟悉CoreData、SQLite、归档等数据持久化存储。
- 掌握APNs消息推送机制，熟练极光和友盟推送的实现。
- 了解XMPP，环信，阿里百川.云旺等即时聊天通讯。
- 掌握移动支付技术（支付宝支付、银联支付、微信支付，内购）。
- 熟练各种画图、绘画。动画。
- 了解图片的加载解码渲染显示流程。了解离屏渲染，并进行图片圆角的优化。
- 了解Cocos2d基础知识。
- iOS与JS交互开发。
- 熟悉组件化开发，了解CocoaPods的使用。部分代码抽取创建私有仓库使用组件化开发，使用pod管理。
- 了解KVO底层原理（自定义实现KVO，可以观察多个属性，函数式编程，自动销毁）。
- 了解KVC底层原理（自定义实现KVC）。
- xcconfig和Scheme配置多环境支持。fastlane自动化打包。

---

## 工作经历

### 学习（2022年4月 ~ 至今）

#### iOS底层

#### flutter
- 常用widget：MaterialApp、PageView、Scaffold、ListView、Image、Container、SizeBox等。
- StatelessWidget和StatefulWidget生命周期
- Mixin混入保存部件的数据状态不被刷新
- Key和GlobalKey的使用
- json和map转模型model
- 异步Future，多线程Isolate和compute
- Provider页面传值通讯和InheritedWidget数据共享
- GestureDetector的使用
- 自己写demo练习（仿微信和记账app）。

#### swift
- 使用swift写一个相册选择图片
- 轮播图

#### 音视频
- AVFoundation的简单使用
  - 音视频的采集
  - 人脸识别、二维码、条形码扫描。设置有效的扫描区域(扫描框内的区域)。
- H.264视频编码原理

### 思享无限（北京）科技有限公司 （ 2021年11月 ~ 2022年3月）
#### 蜜疯直播
- XMPP实现直播间公聊区消息，私信聊天，消息通知。
- CoreData存储私信聊天列表和消息记录。
- 处理左滑移除手势问题。
- 封装相册图片选择功能和预览功能，并且实现选中图片的动画。
- 私信动画，送礼动画。
- 开发直播间聊天的表情模块
  - 利用函数式编程思想抽离长按预览大图功能。
- 切换账号（钥匙串保存账号密码），多设备登录（xmpp的resource）。

### 北京云财信息技术有限公司 （ 2017年11月 ~ 2021年10月）
#### 会计学院（2021.07-2021.09）
- 利用策略模式，解决过多的ifelse条件判断。
  - 处理文章资讯版块多种类别的cell。
  - 不同类型cell的不同点击事件，使用NSInvocation调用方法。
- 利用适配器模式，适配调用接口。
  - 创建分类，AFNetworking3.0适配4.0，设置header。
  - 封装MBProgressHUD的调用接口，避免三方库升级导致多处修改。
- 根据Runtime和KVC封装推送和轮播图的任意页面跳转（推送页面跳转）。
- 类似CTMediator，写Router，组件解耦合去model化。
- Runtime封装交换类方法和对象方法。
- 利用响应者链处理轮播图和tableView滑动响应冲突问题
- 课程详细信息和课件详情信息存储本地数据库

#### 进销存1.2.0（2021.02-2021.06）
- 应用程序二进制重新排列做启动优化。
- 模型数组拷贝（利用class_copyIvarList实现NSCoding的自动归档解档）。
- 处理友盟分享微信链接不成功UniversalLink问题。
- 封装多层级类别目录组件，可以展开和收起子目录。
- 利用响应者链扩大UIButton的点击范围。
- Runtime和NSNumber处理数据精确度问题，使用NSDecimalNumberHandler四舍五入，设置保留小数位。金额加千分符和¥符，设置特殊字体，数据转换。

#### 进销存h5（2021.01-2021.02）
- 学习Vue、Framework7、HTML、CSS、JavaScript。
- 修改进销存h5的bug（企业微信和钉钉）。

#### 代账（2020.07-2021.01）
- 画曲线图，支持多条曲线，使用CAGradientLayer实现颜色渐变填充色，手势点击和滑动显示指示窗。
- 带动画的环形图。利用CAShapeLayer画图，CAAnimation子类做动画。
- 自定义UIButton的图片和文字的frame。
- 利用响应者链，判断是否需要回收键盘。
- 项目中的崩溃处理和日志收集功能。
  - 利用消息转发解决对NSNull对象操作导致的崩溃。
  - 使用NSSetUncaughtExceptionHandler收集上传崩溃日志并分析。
  - 使用runloop崩溃处理。runtime处理已知情况（例：数组越界和创建数组类型异常问题）。
- 自定义视图转换成图片。

#### 进销存 （2020.01-2020.07）
- 自定义键盘。根据响应者链获取当前输入框。输入框插入和删除内容。输入框遮挡键盘问题。
- 利用正则表达式 限制小数点精度和输入的格式。
- 封装分区加阴影的tableView组件。
- UIResponder分类查找第一响应者，UIViewController分类添加观察者，防止键盘遮挡输入框。

#### 会计学院（2019.06-2019.12）
#### 会计头条（2018.05-2019.05）
#### 柠檬云记账（2017.11-2018.04）
- 干货模块（类似今日头条）。无限刷新，本地数据库缓存等功能。
- 封装下载任务。
- 性能优化
  - 图片和按钮圆角阴影使用贝塞尔曲线去绘制。
  - 使用UITableView-FDTemplateLayoutCell思想，实现tableViewCell高度自适应，缓存cell高度。
  - 子线程预排版和按需加载
  - layer.contents给UIView添加图片背景
- WKWebView的使用（设置userAgent，原生与js交互，计算内容高度，代理方法）。
- 页面左滑下滑返回功能。
- 消息推送功能（点击进入指定页面，推送支持图片，通知栏消息保存功能，精准推送，实时推送）。
- 封装FMDB数据库存储组件（利用KVC和runtime，支持模型字典和数组存储）。
- 阿里云日志功能。
- 多线程网络请求。
- 计时功能。GCD定时器。
- 文章详情的评论输入框的封装（多行输入，键盘高度等）。
- 处理项目中访问内存崩溃问题。
  - 设置Xcode开发环境变量控制台得到崩溃地址，在活动监视器找到app的进程id，在终端得到更多错误日志。

### 北京博纳清承科技有限公司 （ 2016年03月 ~ 2017年11月）

#### Cocos2d-x（2017.10-2017.11）
- 供幼儿使用的小学习幼教类游戏软件。

#### 优艺通（音乐学生端2017.06-2017.09）
#### 优艺通（音乐老师端2017.02-2017.05）
#### 优艺通（音乐教辅端2016.10-2017.01）
- 列表基类的封装。
- 封装视频播放器， 分层分模块，可以滑动调节音量、亮度、进度。
- 解密、解压缩功能。录音功能。
- 接入阿里云OSS SDK自动管理Token的更新。封装多文件下载和上传工具。
- PDF文件查看，可以翻页跳页和全屏。
- 音频频率匹配问题 EZAudio的简单使用，在麦克风代理之中获取buffer流的音频数据信息然后调EZAudioPlot (基于图形核心的视图基类) 通过FFT快速傅里叶变换计算频率
- 画画功能，根据手指滑动去画图，可以修改大小，拖动线的位置，删除和撤销画画。批改和预览模式的切换。
- 添加录音和图片文字点评数据， 坐标转json发送数据
- 保存草稿功能，把画画和点评数据保存到本地。
- 音频播放功能。
- 直播界面实现弹幕功能。

#### 优艺通（美术学生端）、优艺通（美术老师端）2016.03-2016.09
- 网络请求封装把每一个网络请求封装成对象, 分页请求的时候, 上拉加载. 下拉刷新. 重新设置请求的网络对象.
- 键盘表情：发送评论的时候,遍历评论字符串, 查找出所有的表情, 去替换成字符.请求回来的评论数据, 先用正则查找出所有的符合表情的字符.然后遍历字符.替换. 使用NSTextAttachment实现图片文字混排。
- 图库浏览自定义控制器转场动画功能。
- 多文件下载功能，创建单例，可以多选删除，控制下载的状态。使用CoreData存储下载和已下载列表数据。
- 搜索标签的实现， 可以多个标签搜索。图库详情标签的实现。
- 评画界面的实现， 选择图片， 键盘控制， 文字高度等。
- 完成瀑布流界面的实现，包含头部, 修改每一个item的attributes在prepareLayout中实现。

---

## 个人评价
喜欢研究源码。有较好的自主学习能力和独立解决问题的能力, 能够从过往的经历中总结经验。对新技术比较感兴趣。