# SDImageCache

查看缓存，删除缓存，存入缓存

### 内存缓存

SDImageCache中包含SDMemoryCache

SDMemoryCache继承NSCache

NSCache优点：

1. 线程安全
2. 自动清理
3. key不会拷贝

字典做内存缓存。需要线程安全。收到内存警告需要手动清除。字典的key要遵循NSCopying

NSCache setObject:forKey: 中key做hash

### 硬盘缓存	

data写入文件

