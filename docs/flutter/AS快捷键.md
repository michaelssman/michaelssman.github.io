`command -`折叠代码

`command shift -`全部折叠

`command +`展开代码

`option 回车` 快速导入头文件

`command \`热重载

`option command m`选中的代码{}提取到某个方法中

## 代码块

### StatelessWidget和StatefulWidget 

快速创建基于StatelessWidget和StatefulWidget的小部件，这两组代码块是最常见的了。

只需要输入 `stless` 就可以创建一个StatelessWidget。

只需要输入 `stful` 就可以创建一个StatefulWidget。

### 自定义代码块

AS中可以设置代码块。Settings -> Editor -> Live Templates

我们可以参考自带的slful代码块进行设置。点击👉的 + 就可添加代码块了。

![img](https://cdn.nlark.com/yuque/0/2020/png/935549/1590336186541-2a02a3d2-cfd5-4386-84e8-b0e08b4f7411.png)



## 快捷键

#### Ctrl + option + O 删除未使用的import

#### option + Enter 自动import未导入的文件

如果你有一个文件的import被删除了，直接对报错的类名称使用option + Enter搞定导入的动作。

如果你不想每次创建类都导入文件，那么我们可以直接根据提示创建对象。将类名输入，然后AS就不需要你手动import了。

![img](https://cdn.nlark.com/yuque/0/2020/png/935549/1590337062527-9393aea9-538e-474b-a851-9d58042c11b1.png)

#### Shift + F6 重命名（如果是Touch Bar就是Shift + Rename...）

#### CMD + -/+ 折起/展开代码块

#### CMD + .  折起/展开选中代码

#### CMD + ,  进入设置页面

#### CMD + [  光标回到上一次编辑的位置

#### CMD + ]  光标回到下一次编辑的位置

#### CMD + L  定位某一行，甚至某一个字符

![img](https://cdn.nlark.com/yuque/0/2020/png/935549/1590337510444-b93d86ca-136b-4e83-bb5a-aaed2cfca75e.png)

#### CMD + / 注释

#### CMD + Y 查看选中类的属性

#### CMD + O 快速打开（一般用于快速打开某个文件）

#### option + Enter 扩展功能(很重要！)

#### 查看小部件源码 

- CMD + Click(鼠标左键)
- CMD + B

- CMD + Down（小键盘↓）
- F4（非Touch Bar键盘）

#### Option + up(↑) 选中上一层代码（比如选中当前光标的单词，选中当前小部件的所有代码，自己试~）

#### CMD + option + L  格式化代码

#### CMD + Shift + -/+ 折起/展开所有代码块

#### Option + Shift + Up/Down 上下移动行

#### Command + Shift + Up/Down  上下移动方法

#### 自动格式化代码 （这是一个AS的设置）

Settings -> Editor -> Languages & Frameworks -> Flutter -> Editor

选中Format code on save 也可以勾选子选项 Organize imports on save

注意：我这里使用的是V 3.6.3 可能将来会有变化。

![img](https://cdn.nlark.com/yuque/0/2020/png/935549/1590338852201-311be50e-b852-4b91-a123-701e110f2b89.png)
