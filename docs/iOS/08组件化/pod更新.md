# pod更新

当执行`pod install`的时候，新加了一个友盟的第三方，提示错误

>Analyzing dependencies
>
>[!] CocoaPods could not find compatible versions for pod "UMCCommon":
>
>  In snapshot (Podfile.lock):
>
>​    UMCCommon (= 2.1.1)
>
>
>
>  In Podfile:
>
>​    UMCCommon
>
>
>
>None of your spec sources contain a spec satisfying the dependencies: `UMCCommon, UMCCommon (= 2.1.1)`.
>
>
>
>You have either:
>
> \* out-of-date source repos which you can update with `pod repo update` or with `pod install --repo-update`.
>
> \* mistyped the name or version.
>
> \* not added the source repo that hosts the Podspec to your Podfile.
>
>
>
>Note: as of CocoaPods 1.0, `pod repo update` does not happen on `pod install` by default.

提示错误是：

1. 过时的源代码库，您可以使用`pod repo update`或`pod install --repo-update`进行更新。
2. 错误输入了名称或版本。
3. 未将承载Podspec的源代码添加到您的Podfile。

注意：从CocoaPods 1.0开始，默认情况下`pod install`不会发生`pod repo update`。

原因是第一种，源代码库过时了，和项目中的不符，需要更新。