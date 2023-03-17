# Animation

## CAKeyframeAnimation

### 上下跳动的动画

```objective-c
//1: 动画
CAKeyframeAnimation *keyFramA = [CAKeyframeAnimation animationWithKeyPath:@"position"];
//2: 设置每针动画的起始和结束点
CGPoint point1 = CGPointMake((kscreenWidth / 2.0), kscreenheightNoNANoTab - 205 - SafeAreaBottomHeight + 47);
CGPoint point2 = CGPointMake((kscreenWidth / 2.0), kscreenheightNoNANoTab - 205 - SafeAreaBottomHeight + 37);
NSValue *pointV1 = [NSValue valueWithCGPoint:point1];
NSValue *pointV2 = [NSValue valueWithCGPoint:point2];
keyFramA.values = @[pointV1,pointV2,pointV1];
//3: 设置动画的时间（指的是完成整个动画所用的时间）
keyFramA.duration = 2;
//4: 设置动画重复的次数
keyFramA.repeatCount = MAXFLOAT;
//5: 将动画添加到对应的控件Layer层上
[imgV.layer addAnimation:keyFramA forKey:nil];
```

## CABasicAnimation

### 加载动画，转圈的动画

```objective-c
//设置动画
CABasicAnimation *rotationAnimation = [CABasicAnimation animationWithKeyPath:@"transform.rotation.z"];
rotationAnimation.toValue = [NSNumber numberWithFloat: M_PI * 2.0 ];
rotationAnimation.duration = 1;
rotationAnimation.cumulative = YES;
rotationAnimation.repeatCount = MAXFLOAT;
//开始动画
[imgV.layer addAnimation:rotationAnimation forKey:@"rotationAnimation"];
```

## 视图整体缩小一定的比例

```objective-c
[UIView animateWithDuration:0.25 animations:^{
  self.view.transform = CGAffineTransformMakeScale(0.95, 0.95);
}];
```

