# CFRunloopRef

```c
CFRunLoopRef CFRunLoopGetMain(void) {
    CHECK_FOR_FORK();
    static CFRunLoopRef __main = NULL; // no retain needed
    if (!__main) __main = _CFRunLoopGet0(pthread_main_thread_np()); // no CAS needed
    return __main;
}

CFRunLoopRef CFRunLoopGetCurrent(void) {
    CHECK_FOR_FORK();
    //创建子runloop或者线程保活 + source (为什么加source？：因为底层加判断 finish，如果是主线程，不需要加false，其它线程的话需要判断_sources0，_sources1，_timers)
  
  	//类似缓存 key-value获取runloop
    CFRunLoopRef rl = (CFRunLoopRef)_CFGetTSD(__CFTSDKeyRunLoop);
    if (rl) return rl;
  
  	//获取不了 就拿当前线程去获取 线程为key，取出value
    return _CFRunLoopGet0(pthread_self());
}
```

```c
// should only be called by Foundation
// t==0 is a synonym for "main thread" that always works
CF_EXPORT CFRunLoopRef _CFRunLoopGet0(pthread_t t) {
		//如果传进来的线程是nil 默认就是主线程
    if (pthread_equal(t, kNilPthreadT)) {
        t = pthread_main_thread_np();//main线程
    }
  	//
    __CFLock(&loopsLock);
    if (!__CFRunLoops) {//全局的字典： __CFRunLoops
        __CFUnlock(&loopsLock);
        
		//为空就创建一个 可变字典
    CFMutableDictionaryRef dict = CFDictionaryCreateMutable(kCFAllocatorSystemDefault, 0, NULL, &kCFTypeDictionaryValueCallBacks);
        
		//传进来的线程为key 创建runloop，通过线程创建runloop
    CFRunLoopRef mainLoop = __CFRunLoopCreate(pthread_main_thread_np());
        
    // 进行绑定 dict[@"pthread_main_thread_np"] = mainLoop
    //key - value 的形式存放，主线程绑定主runloop  
    CFDictionarySetValue(dict, pthreadPointer(pthread_main_thread_np()), mainLoop);
        
    if (!OSAtomicCompareAndSwapPtrBarrier(NULL, dict, (void * volatile *)&__CFRunLoops)) {
        CFRelease(dict);
    }
    CFRelease(mainLoop);
        __CFLock(&loopsLock);
    }
  	//通过线程直接从dict中获取loop
    CFRunLoopRef loop = (CFRunLoopRef)CFDictionaryGetValue(__CFRunLoops, pthreadPointer(t));
    __CFUnlock(&loopsLock);
  	//如果没有 则通过线程创建一个loop
    if (!loop) {
    		CFRunLoopRef newLoop = __CFRunLoopCreate(t);
        __CFLock(&loopsLock);
  		  loop = (CFRunLoopRef)CFDictionaryGetValue(__CFRunLoops, pthreadPointer(t));
    if (!loop) {
      	//再次确认没有loop，则添加到全局可变字典中
        CFDictionarySetValue(__CFRunLoops, pthreadPointer(t), newLoop);
        loop = newLoop;
    }
        // don't release run loops inside the loopsLock, because CFRunLoopDeallocate may end up taking it
        __CFUnlock(&loopsLock);
  		  CFRelease(newLoop);
    }
    if (pthread_equal(t, pthread_self())) {
     	  //注册一个回调，当线程销毁时，顺便也销毁其对应的Runloop。
        _CFSetTSD(__CFTSDKeyRunLoop, (void *)loop, NULL);
        if (0 == _CFGetTSD(__CFTSDKeyRunLoopCntr)) {
            _CFSetTSD(__CFTSDKeyRunLoopCntr, (void *)(PTHREAD_DESTRUCTOR_ITERATIONS-1), (void (*)(void *))__CFFinalizeRunLoop);
        }
    }
    return loop;
}
```

## 获取runloop的流程

- CFRunLoopGetMain或CFRunLoopGetCurrent
- 通过_CFRunLoopGet0函数传入一条线程。
- 判断线程是否为主线程并且判断是否已经存在__CFRunLoops（全局CFMutableDictionaryRef）。
- 如果不存在，说明第一次进入，初始化全局dict，并先为主线程创建一个 RunLoop。并将mainLoop添加到dict中。
- 如果__CFRunLoops存在，会通过对应线程在全局的__CFRunLoops中查找对应的RunLoop。
- 如果对应RunLoop不存在，会创建一个新的RunLoop，并添加到__CFRunLoops中。
- 注册一个回调，当线程销毁时，顺便也销毁其对应的 RunLoop。
- 返回RunLoop。

## 线程和runloop是一一绑定的关系。

RunLoop对象是利用字典来进行存储，而且key对应的线程Value为该线程对应的RunLoop。

只能通过CFRunLoopGetMain函数或者CFRunLoopGetCurrent函数来获取RunLoop，无论是CFRunLoopGetMain函数还是CFRunLoopGetCurrent函数，都是通过对应的线程获取对应的RunLoop，**线程和RunLoop是一一对应的**，不会重复创建。

## 主线程的runloop是默认创建和开启的，子线程的runloop需要手动创建和开启。

开一个子线程创建runloop，不是通过alloc init方法创建，而是直接通过调用currentRunLoop方法来创建，它本身是一个懒加载的。

在子线程中，如果不主动获取RunLoop的话，那么子线程内部是不会创建RunLoop的。

在主线程，系统会帮我们创建RunLoop，来处理事件。而子线程RunLoop并不会默认开启。

子线程操作完成后，线程就被销毁了，如果我们想线程不被销毁，得主动获取一个RunLoop，并且在RunLoop中添加Timer/Source/Observer其中的一个。

## 创建runloop

```c
static CFRunLoopRef __CFRunLoopCreate(pthread_t t) {
    CFRunLoopRef loop = NULL;
    CFRunLoopModeRef rlm;
    uint32_t size = sizeof(struct __CFRunLoop) - sizeof(CFRuntimeBase);
    loop = (CFRunLoopRef)_CFRuntimeCreateInstance(kCFAllocatorSystemDefault, CFRunLoopGetTypeID(), size, NULL);
    if (NULL == loop) {
    	return NULL;
    }
    (void)__CFRunLoopPushPerRunData(loop);
    __CFRunLoopLockInit(&loop->_lock);
    loop->_wakeUpPort = __CFPortAllocate();
    if (CFPORT_NULL == loop->_wakeUpPort) HALT;
    __CFRunLoopSetIgnoreWakeUps(loop);
    loop->_commonModes = CFSetCreateMutable(kCFAllocatorSystemDefault, 0, &kCFTypeSetCallBacks);//set类型的commonModes 无序的集合
    CFSetAddValue(loop->_commonModes, kCFRunLoopDefaultMode);
    loop->_commonModeItems = NULL;
    loop->_currentMode = NULL;
    loop->_modes = CFSetCreateMutable(kCFAllocatorSystemDefault, 0, &kCFTypeSetCallBacks);
    loop->_blocks_head = NULL;//头
    loop->_blocks_tail = NULL;//尾
    loop->_counterpart = NULL;
    loop->_pthread = t;
#if DEPLOYMENT_TARGET_WINDOWS
    loop->_winthread = GetCurrentThreadId();
#else
    loop->_winthread = 0;
#endif
    rlm = __CFRunLoopFindMode(loop, kCFRunLoopDefaultMode, true);
    if (NULL != rlm) __CFRunLoopModeUnlock(rlm);
    return loop;
}
```

## Runloop结构体：__CFRunLoop

打印[NSRunLoop currentRunLoop] 打印出来的是一个**CFRunLoop**结构体

```c
struct __CFRunLoop {
    CFRuntimeBase _base;
    _CFRecursiveMutex _lock;			/* locked for accessing mode list */
    __CFPort _wakeUpPort;			// used for CFRunLoopWakeUp 
    volatile _per_run_data *_perRunData;              // reset for runs of the run loop
    _CFThreadRef _pthread;  //对应的线程	runloop和线程一一对应的关系
    uint32_t _winthread;
    CFMutableSetRef _commonModes;//集合，CFString，字符串的集合
    CFMutableSetRef _commonModeItems;//observer，timer，source 集合类型
    CFRunLoopModeRef _currentMode;//DefaultMode，TrackingMode
    CFMutableSetRef _modes;
    struct _block_item *_blocks_head;
    struct _block_item *_blocks_tail;
    CFAbsoluteTime _runTime;
    CFAbsoluteTime _sleepTime;
    CFTypeRef _counterpart;
    _Atomic(uint8_t) _fromTSD;
    CFLock_t _timerTSRLock;
};
```

