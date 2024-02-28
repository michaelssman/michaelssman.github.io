# 清理Xcode

主要清理的文件夹：

可重新生成

1.  删除对旧设备的支持
   > ~/Library/Developer/Xcode/iOS DeviceSupport
   > 这里放的是连接真机生成的文件，保存着对你设备的版本支持，每个版本文件夹都是几个G的大小，可以全部删掉或者把不常用的版本删掉，再次连接设备会自动生成。

2. 删除打包生成的ipa
> ~/Library/Developer/Xcode/Archives

3.  删除DerivedData
> ~/Library/Developer/Xcode/DerivedData
> 模拟器运行每个APP生成的缓存文件，项目的索引文件。

4. 删除log日志记录
> ~/Library/Developer/Xcode/iOS Device Logs

### 移除模拟器

使用`xcrun`命令来清理模拟器。打开终端（Terminal）并使用以下命令：

- 列出所有模拟器设备：

  ```bash
  xcrun simctl list devices
  ```

- 删除特定的模拟器：

  ```bash
  xcrun simctl delete <device_id>
  ```

  其中`<device_id>`是模拟器设备的ID。

- 清除特定模拟器的内容和设置：

  ```bash
  xcrun simctl erase <device_id>
  ```

- 删除所有不再使用的模拟器设备：

  ```bash
  xcrun simctl delete unavailable
  ```

- 重置所有模拟器的内容和设置：

  ```bash
  xcrun simctl erase all
  ```

在使用命令行操作之前，请确保Xcode命令行工具已经安装，并且`xcrun`命令可用。

#### 清理模拟器缓存

> ~/Library/Developer/CoreSimulator/
> 此文件夹目录下的文件夹全都是以模拟器的UDID命名的，可以查看device_set.plist文件根据文件夹命名和plist文件中的内容判断各个文件夹是某版本下某设备类型的模拟器。很多都是之前iOS版本的模拟器，可以全部删除，删除之后，如果立即运行程序会报错，先关闭Xcode，再重新打开程序，运行即可。运行该路径下会立马生成模拟器对应版本的文件。
> 解决方法：
> 在Devices and Simulators中把模拟器删掉，然后重新添加，直接添加即可，Simulator Name也不用写，直接默认的即可，不需下载。



/Library/Developer/Xcode
/Library/Developer/XCTestDevices