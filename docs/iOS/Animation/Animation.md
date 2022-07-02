# Animation

## 上下跳动的动画

```
//1. 先创建一个imageView
UIImageView *imgV = [[UIImageView alloc]initWithImage:[UIImage imageNamed:@"scanAnimation"]];
imgV.frame = CGRectMake((kscreenWidth - 240) / 2.0, kscreenheightNoNANoTab - 205 - SafeAreaBottomHeight, 240, 94);
[_noInvoiceView addSubview:imgV];
//2. 创建动画
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

self.keyFramA = keyFramA;
self.imgV = imgV;
```

## 加载动画，转圈的动画

```
    //自定义动画
    UIImageView *gifImageView = [UIImageView new];
    gifImageView.image = [UIImage imageNamed:@"loadAnimationIcon"];
    //设置动画
    CABasicAnimation *rotationAnimation = [CABasicAnimation animationWithKeyPath:@"transform.rotation.z"];
    rotationAnimation.toValue = [NSNumber numberWithFloat: M_PI * 2.0 ];
    rotationAnimation.duration = 1;
    rotationAnimation.cumulative = YES;
    rotationAnimation.repeatCount = MAXFLOAT;
    //开始动画
    [gifImageView.layer addAnimation:rotationAnimation forKey:@"rotationAnimation"];
```

## 视图整体缩小一定的比例

```
        [UIView animateWithDuration:0.25 animations:^{
            self.view.transform =CGAffineTransformMakeScale(0.95, 0.95);
        }];
```

