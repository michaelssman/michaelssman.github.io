# CFRunLoopTimerRef

**CFRunLoopTimerRef**：基于时间的触发器，CFRunLoopTimerRef是Core Foundation提供的基础定时器，NSTimer则是建立在CFRunLoopTimerRef之上的高层组件。当Timer被加入到RunLoop时，RunLoop会注册对应的时间点，当达到时间时，RunLoop会被唤醒，执行创建Timer时的回调。

```objective-c
    [NSTimer scheduledTimerWithTimeInterval:1 repeats:YES block:^(NSTimer * _Nonnull timer) {
        NSLog(@"天王盖地虎");//在这行打断点
    }];
```

控制台`bt`可以看到堆栈流程

>**(lldb) bt**
>
>\* thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
>
>\* frame #0: 0x000000010ba30243 01-Runloop初探`__28-[ViewController sourceDemo]_block_invoke(.block_descriptor=0x000000010ba320a8, timer=0x000060000091c240) at ViewController.m:32:9
>
>frame #1: 0x00007fff2085e951 Foundation`__NSFireTimer + 67
>
>frame #2: 0x00007fff2039178a CoreFoundation`__CFRUNLOOP_IS_CALLING_OUT_TO_A_TIMER_CALLBACK_FUNCTION__ + 20
>
>frame #3: 0x00007fff2039127c CoreFoundation`__CFRunLoopDoTimer + 924
>
>frame #4: 0x00007fff2039081a CoreFoundation`__CFRunLoopDoTimers + 265
>
>frame #5: 0x00007fff2038ae69 CoreFoundation`__CFRunLoopRun + 2013
>
>frame #6: 0x00007fff2038a1a7 CoreFoundation`CFRunLoopRunSpecific + 567
>
>frame #7: 0x00007fff2b874d85 GraphicsServices`GSEventRunModal + 139
>
>frame #8: 0x00007fff246c14df UIKitCore`-[UIApplication _run] + 912
>
>frame #9: 0x00007fff246c639c UIKitCore`UIApplicationMain + 101
>
>frame #10: 0x000000010ba30451 01-Runloop初探`main(argc=1, argv=0x00007ffee41cfc60) at main.m:21:16
>
>frame #11: 0x00007fff2025abbd libdyld.dylib`start + 1
>
>**(lldb)** 

### CFRunLoopAddTimer

把timer加到runloop

```c
void CFRunLoopAddTimer(CFRunLoopRef rl, CFRunLoopTimerRef rlt, CFStringRef modeName) {
    CHECK_FOR_FORK();
    if (__CFRunLoopIsDeallocating(rl)) return;
    if (!__CFIsValid(rlt) || (NULL != rlt->_runLoop && rlt->_runLoop != rl)) return;
    __CFRunLoopLock(rl);
    if (modeName == kCFRunLoopCommonModes) {
        CFSetRef set = rl->_commonModes ? CFSetCreateCopy(kCFAllocatorSystemDefault, rl->_commonModes) : NULL;
        if (NULL == rl->_commonModeItems) {
            rl->_commonModeItems = CFSetCreateMutable(kCFAllocatorSystemDefault, 0, &kCFTypeSetCallBacks);
        }
        CFSetAddValue(rl->_commonModeItems, rlt);
        if (NULL != set) {
            CFTypeRef context[2] = {rl, rlt};
            /* add new item to all common-modes */
            //设置回调函数
            CFSetApplyFunction(set, (__CFRunLoopAddItemToCommonModes), (void *)context);
            CFRelease(set);
        }
    } else {
        //根据mode名字找到模型
        CFRunLoopModeRef rlm = __CFRunLoopFindMode(rl, modeName, true);
        //如果没有 就创建一个
        if (NULL != rlm) {
            if (NULL == rlm->_timers) {
                CFArrayCallBacks cb = kCFTypeArrayCallBacks;
                cb.equal = NULL;
                rlm->_timers = CFArrayCreateMutable(kCFAllocatorSystemDefault, 0, &cb);
            }
        }
        if (NULL != rlm && !CFSetContainsValue(rlt->_rlModes, rlm->_name)) {
            __CFRunLoopTimerLock(rlt);
            if (NULL == rlt->_runLoop) {
                rlt->_runLoop = rl;
            } else if (rl != rlt->_runLoop) {
                __CFRunLoopTimerUnlock(rlt);
                __CFRunLoopModeUnlock(rlm);
                __CFRunLoopUnlock(rl);
                return;
            }
            CFSetAddValue(rlt->_rlModes, rlm->_name);
            __CFRunLoopTimerUnlock(rlt);
            __CFRunLoopTimerFireTSRLock();
            __CFRepositionTimerInMode(rlm, rlt, false);
            __CFRunLoopTimerFireTSRUnlock();
            if (!_CFExecutableLinkedOnOrAfter(CFSystemVersionLion)) {
                // Normally we don't do this on behalf of clients, but for
                // backwards compatibility due to the change in timer handling...
                if (rl != CFRunLoopGetCurrent()) CFRunLoopWakeUp(rl);
            }
        }
        if (NULL != rlm) {
            __CFRunLoopModeUnlock(rlm);
        }
    }
    __CFRunLoopUnlock(rl);
}
```

（1）NSTimer相关代码

```objective-c
/*
说明：
（1）runloop一启动就会选中一种模式，当选中了一种模式之后其它的模式就都不管了。一个mode里面可以添加多个NSTimer,也就是说以后当创建NSTimer的时候，可以指定它是在什么模式下运行的。
（2）它是基于时间的触发器，说直白点那就是时间到了我就触发一个事件，触发一个操作。基本上说的就是NSTimer
（3）相关代码
*/
- (void)timer2
{
//NSTimer 调用了scheduledTimer方法，那么会自动添加到当前的runloop里面去，而且runloop的运行模式kCFRunLoopDefaultMode
NSTimer *timer = [NSTimer scheduledTimerWithTimeInterval:2.0 target:self selector:@selector(run) userInfo:nil repeats:YES];
//更改模式
[[NSRunLoop currentRunLoop] addTimer:timer forMode:NSRunLoopCommonModes];
}
- (void)timer1
{
NSTimer *timer = [NSTimer timerWithTimeInterval:2.0 target:self selector:@selector(run) userInfo:nil repeats:YES];
//定时器添加到UITrackingRunLoopMode模式，一旦runloop切换模式，那么定时器就不工作
// [[NSRunLoop currentRunLoop] addTimer:timer forMode:UITrackingRunLoopMode];
//定时器添加到NSDefaultRunLoopMode模式，一旦runloop切换模式，那么定时器就不工作
// [[NSRunLoop currentRunLoop] addTimer:timer forMode:NSDefaultRunLoopMode];
//占位模式：common modes标记
//被标记为common modes的模式 kCFRunLoopDefaultMode UITrackingRunLoopMode
[[NSRunLoop currentRunLoop] addTimer:timer forMode:NSRunLoopCommonModes];
// NSLog(@"%@",[NSRunLoop currentRunLoop]);
}
- (void)run
{
NSLog(@"---run---%@",[NSRunLoop currentRunLoop].currentMode);
}
```

（2）GCD中的定时器

```objective-c
//0.创建一个队列
dispatch_queue_t queue = dispatch_get_global_queue(0, 0);
//1.创建一个GCD的定时器
/*
第一个参数：说明这是一个定时器
第四个参数：GCD的回调任务添加到那个队列中执行，如果是主队列则在主线程执行
*/
dispatch_source_t timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, queue);
//2.设置定时器的开始时间，间隔时间以及精准度
//设置开始时间，三秒钟之后调用
dispatch_time_t start = dispatch_time(DISPATCH_TIME_NOW,3.0 *NSEC_PER_SEC);
//设置定时器工作的间隔时间
uint64_t intevel = 1.0 * NSEC_PER_SEC;
/*
第一个参数：要给哪个定时器设置
第二个参数：定时器的开始时间DISPATCH_TIME_NOW表示从当前开始
第三个参数：定时器调用方法的间隔时间
第四个参数：定时器的精准度，如果传0则表示采用最精准的方式计算，如果传大于0的数值，则表示该定时切换i可以接收该值范围内的误差，通常传0
该参数的意义：可以适当的提高程序的性能
注意点：GCD定时器中的时间以纳秒为单位（面试）
*/
dispatch_source_set_timer(timer, start, intevel, 0 * NSEC_PER_SEC);
//3.设置定时器开启后回调的方法
/*
第一个参数：要给哪个定时器设置
第二个参数：回调block
*/
dispatch_source_set_event_handler(timer, ^{
NSLog(@"------%@",[NSThread currentThread]);
});
//4.执行定时器
dispatch_resume(timer);
//注意：dispatch_source_t本质上是OC类，在这里是个局部变量，需要强引用
self.timer = timer;
```

