# cell点击效果

cell一种常规状态，一种点击状态（其他状态）

#### 取消cell的点击效果

```objective-c
cell.selectionStyle = UITableViewCellSelectionStyleNone;
```

#### 设置cell点击的背景效果：

```objective-c
self.selectedBackgroundView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"icon_selection_state"]];
```

#### cell点击没效果的情况：

```objective-c
self.selectedBackgroundView = [[UIView alloc] init];
```

### 各个控件的点击效果setHighlighted和选中效果setSelected

修改cell中的图片和文字点击效果

```objective-c
        self.icon.contentMode = UIViewContentModeScaleAspectFit;
        [self.icon setImage:[UIImage imageNamed:@"icon_lesson"]];
        [self.icon setHighlightedImage:[UIImage imageNamed:@"icon_lesson_sel"]];
        
        self.titleLabel.font = [UIFont systemFontOfSize:30 * TEXT_FONT_SCALE];
        self.titleLabel.highlightedTextColor = [UIColor colorWithHex:0xffd579];
```
```objective-c
- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];

    if ([self.type isEqualToString:@"lesson"]) {
        self.icon.highlighted = selected;
        self.titleLabel.highlighted = selected;
    }
}
```

```objective-c
- (void)setHighlighted:(BOOL)highlighted
{
    [super setHighlighted:highlighted];
    if (highlighted) {
        //点击状态
    } else {
        //取消点击
    }
}
```

##### cell有几种状态时
1. 设置一个枚举
2. 设置一个变量属性
3. 调用属性setter方法
4. 在setter方法中设置不同的字体颜色大小等状态
5. 在setDataWithModel中 设置不同的类型