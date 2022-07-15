# UITextView

## textView文字内容与textView上下左右的边距。

```
textView.textContainerInset = UIEdgeInsetsMake(20, 20, 20, 20);
```

## UITextView加载html文本

```
NSString *strHtml = @"<b>提示</b><br/>1、测试测试测试测试测试测试测试测试测试测试测试测试<br/>2、测试测试测试测试测试测试测试测试测试测试";
NSAttributedString * strAtt = [[NSAttributedString alloc] initWithData:[strHtml dataUsingEncoding:NSUnicodeStringEncoding] options:@{ NSDocumentTypeDocumentAttribute: NSHTMLTextDocumentType } documentAttributes:nil error:nil];
self.labelContent.attributedText = strAtt;
self.textViewContent.attributedText = strAtt;
```

## 限制字数

中文输入法可以连续在键盘输入一串内容而不选中，当选中之后文字内容就可能超出限制的字数范围。

UITextRange：

```
UITextRange *selectedRange = [textView markedTextRange];
```

UITextRange打印log可以看到和NSRange差不多，起始的位置和文字范围。

UITextPosition:

## 中文输入，确定之后才做操作

解决方法：输入内容时，仅在不是高亮状态下获取输入的文字

```
- (void)textViewDidChange:(UITextView *)textView
{
    UITextRange *selectedRange = textView.markedTextRange;
    if (!(selectedRange == nil || selectedRange.empty))
    {
        return;
    }
    /*
    写确定之后的操作
    */
}	
```

