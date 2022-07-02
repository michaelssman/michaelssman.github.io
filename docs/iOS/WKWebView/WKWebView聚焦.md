

https://stackoverflow.com/questions/32449870/programmatically-focus-on-a-form-in-a-webview-wkwebview

# 情景描述

我们知道，UIWebView是有一个 keyboardDisplayRequiresUserAction属性的，默认为YES。如果设置为YES，用户必须明确的点击页面上的元素或者相关联的输入页面来显示键盘；如果设置为NO，一个元素的焦点事件导致输入视图的显示和自动关联这个元素。

那么，如果我们加载一个Web页面时，想一开始唤起键盘，除了web端需要设置input 的focus状态外，我们还需要将keyboardDisplayRequiresUserAction设置为false

# 问题

然而，WKWebView是没有这个属性的，但又想做到以上效果，怎么办呢？只能通过runtime处理了，以下是收集Stack Overflow的方法

```
- (void)allowDisplayingKeyboardWithoutUserAction {
    Class class = NSClassFromString(@"WKContentView");
    NSOperatingSystemVersion iOS_11_3_0 = (NSOperatingSystemVersion){11, 3, 0};
    NSOperatingSystemVersion iOS_12_2_0 = (NSOperatingSystemVersion){12, 2, 0};
    
    if ([[NSProcessInfo processInfo] isOperatingSystemAtLeastVersion: iOS_12_2_0]) {
        SEL selector = sel_getUid("_elementDidFocus:userIsInteracting:blurPreviousNode:changingActivityState:userObject:");
        Method method = class_getInstanceMethod(class, selector);
        IMP original = method_getImplementation(method);
        IMP override = imp_implementationWithBlock(^void(id me, void* arg0, BOOL arg1, BOOL arg2, BOOL arg3, id arg4) {
            ((void (*)(id, SEL, void*, BOOL, BOOL, BOOL, id))original)(me, selector, arg0, TRUE, arg2, arg3, arg4);
        });
        method_setImplementation(method, override);
    }
    else if ([[NSProcessInfo processInfo] isOperatingSystemAtLeastVersion: iOS_11_3_0]) {
        SEL selector = sel_getUid("_startAssistingNode:userIsInteracting:blurPreviousNode:changingActivityState:userObject:");
        Method method = class_getInstanceMethod(class, selector);
        IMP original = method_getImplementation(method);
        IMP override = imp_implementationWithBlock(^void(id me, void* arg0, BOOL arg1, BOOL arg2, BOOL arg3, id arg4) {
            ((void (*)(id, SEL, void*, BOOL, BOOL, BOOL, id))original)(me, selector, arg0, TRUE, arg2, arg3, arg4);
        });
        method_setImplementation(method, override);
    } else {
        SEL selector = sel_getUid("_startAssistingNode:userIsInteracting:blurPreviousNode:userObject:");
        Method method = class_getInstanceMethod(class, selector);
        IMP original = method_getImplementation(method);
        IMP override = imp_implementationWithBlock(^void(id me, void* arg0, BOOL arg1, BOOL arg2, id arg3) {
            ((void (*)(id, SEL, void*, BOOL, BOOL, id))original)(me, selector, arg0, TRUE, arg2, arg3);
        });
        method_setImplementation(method, override);
    }
}
```

## 何时调用

什么时候调用都可以

可以在创建webView的时候调用，也可以在APPDelegate didFinish调用。

+load或者initialize 调用也可以。

