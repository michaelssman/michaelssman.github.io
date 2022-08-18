# AVFoundation

照片/视频捕捉功能

小视频/直播

## 捕捉会话AVCaptureSession

## 捕捉设备（摄像头、麦克风）AVCaptureDevice

device修改（前后摄像后、聚焦、曝光、手电筒），需要加锁解锁。

### 捕捉设备输入（摄像头、麦克风）AVCaptureDeviceInput

### 捕捉设备输出（图片、视频）: AVCaptureOutput抽象类

- AVCaptureStillImageOutput静态图片

- AVCaptureMovieFileOutput视频文件

- AVCaptureAudioDataOutput

- AVCaptureVideoDataOutput

## 捕捉连接: AVCaptureConnection

## 捕捉预览: AVCaptureVideoPreviewLayer

AVCaptureVideoPreviewLayer定义2个方法：摄像头/屏幕坐标系转换

captureDevicePointForPoint：获取屏幕坐标系的CGPoint数据，返回转换得到摄像头设备坐标系的CGPoint数据。

pointForCaptureDevicePointOfInterest：获取摄像头的坐标系的CGPoint，返回转换得到的屏幕坐标系CGPoint坐标。

- 切换摄像头

## 采集视频音频

手机app有很多，修改设备需要先锁定设备。

配置session

## 人脸识别

1. 视频采集

2. 为session添加一个元数据的输出AVCaptureMetadataOutput

3. 设置元数据的范围（人脸识别、二维码数据、一维码...）

4. 开始捕捉（设置捕捉完成代理）

5. 获取到捕捉人脸相关信息：代理方法中可以获取

   ```objective-c
   - (void)captureOutput:(AVCaptureOutput *)captureOutput
   didOutputMetadataObjects:(NSArray *)metadataObjects
          fromConnection:(AVCaptureConnection *)connection
   ```

6. 对人脸数据的处理：将人脸框出来（涉及比较多细节）

## 二维码识别

分类

- QR码：移动营销
- Aztec码：登机牌
- PDF417：商品运输



















