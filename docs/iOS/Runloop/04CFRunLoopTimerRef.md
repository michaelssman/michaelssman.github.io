# CFRunLoopTimerRef

**CFRunLoopTimerRef**：基于时间的触发器，CFRunLoopTimerRef是Core Foundation提供的基础定时器，NSTimer则是建立在CFRunLoopTimerRef之上的高层组件。

当Timer被加入到RunLoop时，RunLoop会注册对应的时间点，当达到时间时，RunLoop会被唤醒，执行创建Timer时的回调。

```swift
// 创建一个每秒触发一次的定时器
let timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { timer in
    print("Timer fired!")
    // 你的代码...
}
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
        //根据mode名字找到mode
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

## 执行timer

1. timer依赖mode去run
2. runloop run的时候：
3. 遍历timers
4. __CFRunLoopDoTimer
   1. 根据mode拿到runloop中的timer
   2. 执行回调`__CFRUNLOOP_IS_CALLING_OUT_TO_A_TIMER_CALLBACK_FUNCTION__`

```c
// rl and rlm are locked on entry and exit
static Boolean __CFRunLoopDoTimers(CFRunLoopRef rl, CFRunLoopModeRef rlm, uint64_t limitTSR) {    /* DOES CALLOUT */
    Boolean timerHandled = false;
    CFMutableArrayRef timers = NULL;
  //先找到runloop里的所有timer，可能不止一个
    for (CFIndex idx = 0, cnt = rlm->_timers ? CFArrayGetCount(rlm->_timers) : 0; idx < cnt; idx++) {
        CFRunLoopTimerRef rlt = (CFRunLoopTimerRef)CFArrayGetValueAtIndex(rlm->_timers, idx);
        
        if (__CFIsValid(rlt) && !__CFRunLoopTimerIsFiring(rlt)) {
            if (rlt->_fireTSR <= limitTSR) {
                if (!timers) timers = CFArrayCreateMutable(kCFAllocatorSystemDefault, 0, &kCFTypeArrayCallBacks);
                CFArrayAppendValue(timers, rlt);
            }
        }
    }
    
  //遍历 执行。__CFRunLoopDoTimer
    for (CFIndex idx = 0, cnt = timers ? CFArrayGetCount(timers) : 0; idx < cnt; idx++) {
        CFRunLoopTimerRef rlt = (CFRunLoopTimerRef)CFArrayGetValueAtIndex(timers, idx);
        Boolean did = __CFRunLoopDoTimer(rl, rlm, rlt);
        timerHandled = timerHandled || did;
    }
    if (timers) CFRelease(timers);
    return timerHandled;
}
```

### NSTimer相关代码

```objective-c
/*
（1）runloop一启动就会选中一种模式，当选中了一种模式之后其它的模式就都不管了。一个mode里面可以添加多个NSTimer,也就是说以后当创建NSTimer的时候，可以指定它是在什么模式下运行的。
（2）它是基于时间的触发器，说直白点那就是时间到了就触发一个事件，触发一个操作。基本上说的就是NSTimer
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

### DispatchSourceTimer

```swift
let queue = DispatchQueue(label: "com.example.timer")
let timer = DispatchSource.makeTimerSource(queue: queue)

timer.schedule(deadline: .now(), repeating: 1.0)

timer.setEventHandler {
    print("Timer fired!")
    // 你的代码...
}

// 启动定时器
timer.resume()

// 当完成时，取消定时器，释放资源。
timer.cancel()
```

