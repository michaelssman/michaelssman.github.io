主要清理的文件夹：
### 可重新生成
1.  删除对旧设备的支持
   > ~/Library/Developer/Xcode/iOS DeviceSupport
   > 这里放的是连接真机生成的文件，保存着对你设备的版本支持，每个版本文件夹都是几个G的大小，可以全部删掉或者把不常用的版本删掉，再次连接设备会自动生成。

2. 删除打包ipa
> ~/Library/Developer/Xcode/Archives
> app打包生成的文件，可以删掉不需要的项目打包文件

3.  删除DerivedData
> ~/Library/Developer/Xcode/DerivedData
> 此文件夹内是模拟器运行每个APP生成的缓存文件，项目的索引文件。可以全部删除，或者删除不常用的项目。删除之后只是再重新运行APP时会重新编译耗时较长，并再次生成缓存文件。

4. 删除日志记录
> ~/Library/Developer/Xcode/iOS Device Logs
> 一些log日志

5. 移除模拟器文件，可以清理，运行模拟器会重新生成
> ~/Library/Developer/CoreSimulator/
> 此文件夹目录下的文件夹全都是以模拟器的UDID命名的，可以查看device_set.plist文件根据文件夹命名和plist文件中的内容判断各个文件夹是某版本下某设备类型的模拟器。很多都是之前iOS版本的模拟器，可以全部删除，删除之后，如果立即运行程序会报错，先关闭Xcode，再重新打开程序，运行即可。运行该路径下会立马生成模拟器对应版本的文件。
> 解决方法：
> 在Devices and Simulators中把模拟器删掉，然后重新添加，直接添加即可，Simulator Name也不用写，直接默认的即可，不需下载。



/Library/Developer/Xcode
/Library/Developer/CoreSimulator 模拟器
/Library/Developer/XCTestDevices