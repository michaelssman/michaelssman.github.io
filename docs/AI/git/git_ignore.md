# Git 忽略规则

## 当前仓库的本地忽略：.git/info/exclude

`.git/info/exclude` 用于忽略当前仓库中不需要纳入版本管理的个人文件。规则只在本地当前仓库生效，不随提交或推送共享，适合个人笔记、临时文件等。

在仓库根目录编辑 `.git/info/exclude`，按 `.gitignore` 的语法每行写一条规则，例如：

```gitignore
/local-notes/
/debug.log
```

上面分别忽略仓库根目录的 `local-notes` 文件夹和 `debug.log` 文件。保存后自动生效，无需额外配置。可在仓库根目录检查匹配的规则及来源：

```bash
git check-ignore -v debug.log
```

忽略规则只影响尚未被 Git 跟踪的文件，不会删除文件，也不会停止跟踪已有文件。

参考：[Git 官方忽略规则说明](https://git-scm.com/docs/gitignore)。

## 全局忽略：.gitignore_global

全局ignore，文件路径：`~/.gitignore_global`。

## iOS

有些二进制文件（比如 Xcode 的 `.xcuserstate` 文件）产生了冲突。这些文件通常是用户特定的，不应该被包含在版本控制中。

```
*~
.DS_Store
WorkspaceSettings.xcsettings
xcschememanagement.plist
IDEWorkspaceChecks.plist
*.xcworkspacedata
_CodeSignature/
Podfile.lock

# Xcode
#
# gitignore contributors: remember to update Global/Xcode.gitignore, Objective-C.gitignore & Swift.gitignore

## User settings
*.xcuserstate
xcuserdata/

## Build generated
build/
DerivedData/

## Various settings
*.pbxuser
!default.pbxuser
*.mode1v3
!default.mode1v3
*.mode2v3
!default.mode2v3
*.perspectivev3
!default.perspectivev3

## Other
*.moved-aside
*.xccheckout
*.xcscmblueprint

## Obj-C/Swift specific
*.hmap

## App packaging
*.ipa
*.dSYM.zip
*.dSYM

## Playgrounds
timeline.xctimeline
playground.xcworkspace

# Swift Package Manager
#
# Add this line if you want to avoid checking in source code from Swift Package Manager dependencies.
# Packages/
# Package.pins
# Package.resolved
# *.xcodeproj
#
# Xcode automatically generates this directory with a .xcworkspacedata file and xcuserdata
# hence it is not needed unless you have added a package configuration file to your project
# .swiftpm

.build/

# CocoaPods
#
# We recommend against adding the Pods directory to your .gitignore. However
# you should judge for yourself, the pros and cons are mentioned at:
# https://guides.cocoapods.org/using/using-cocoapods.html#should-i-check-the-pods-directory-into-source-control
Pods/

# Add this line if you want to avoid checking in source code from the Xcode workspace
# *.xcworkspace

# Carthage
#
# Add this line if you want to avoid checking in source code from Carthage dependencies.
# Carthage/Checkouts

Carthage/Build/

# Accio dependency management
Dependencies/
.accio/

# fastlane
#
# It is recommended to not store the screenshots in the git repo.
# Instead, use fastlane to re-generate the screenshots whenever they are needed.
# For more information about the recommended setup visit:
# https://docs.fastlane.tools/best-practices/source-control/#source-control

fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots/**/*.png
fastlane/test_output

# Code Injection
#
# After new code Injection tools there's a generated folder /iOSInjectionProject
# https://github.com/johnno1962/injectionforxcode

injected_container

iOSInjectionProject/
```

## Flutter

```
# Miscellaneous
*.class
*.log
*.pyc
*.swp
.DS_Store
.atom/
.buildlog/
.history
.svn/

# IntelliJ related
*.iml
*.ipr
*.iws
.idea/

# The .vscode folder contains launch configuration and tasks you configure in
# VS Code which you may wish to be included in version control, so this line
# is commented out by default.
#.vscode/

# Flutter/Dart/Pub related
**/doc/api/
**/ios/Flutter/.last_build_id
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
/build/

# Web related
lib/generated_plugin_registrant.dart

# Symbolication related
app.*.symbols

# Obfuscation related
app.*.map.json

# Android Studio will place build artifacts here
/android/app/debug
/android/app/profile
/android/app/release
```
