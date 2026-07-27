# `part` 的作用和使用

`part` 是 Dart 用来把一个 library 拆成多个源文件的语法。它不是普通的 `import`，而是让多个文件共同组成同一个库。

可以把它理解为：主文件声明一个库边界，`part` 文件只是这个库的另一段源码。

## 基本语法

主文件使用 `part` 引入片段文件：

```dart
// user_page.dart
part 'user_form.dart';

class UserPage {
  void _save() {
    // 保存用户信息
  }
}
```

片段文件使用 `part of` 声明自己属于哪个主文件：

```dart
// user_form.dart
part of 'user_page.dart';

void submit(UserPage page) {
  page._save();
}
```

因为两个文件属于同一个 library，`user_form.dart` 可以访问 `user_page.dart` 中的 `_save` 私有方法。

## `part` 的核心特性

- `part` 文件和主文件属于同一个 library。
- 同一个 library 内可以互相访问以下划线开头的私有成员。
- `part` 文件共享主文件的 import/export 上下文。
- `part` 文件不能独立作为普通 Dart library 使用。
- `part of` 必须和主文件中的 `part` 声明互相匹配。

## `part` 和 `import` 的区别

| 对比项 | `part` | `import` |
| --- | --- | --- |
| 关系 | 同一个 library 的源码片段 | 引入另一个独立 library |
| 私有成员访问 | 可以访问同库 `_private` 成员 | 不能访问对方 `_private` 成员 |
| 文件独立性 | `part` 文件通常不能独立使用 | 被导入文件是独立 library |
| 适合场景 | 代码生成、强绑定源码片段 | 业务模块拆分、公共能力复用 |
| 架构边界 | 较弱 | 较清晰 |

## 典型使用场景：代码生成

`part` 最常见、最推荐的场景是代码生成，例如 `json_serializable`、`freezed` 等。

```dart
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String name;
  final int age;

  const User({required this.name, required this.age});

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

生成文件通常长这样：

```dart
part of 'user.dart';

User _$UserFromJson(Map<String, dynamic> json) {
  return User(
    name: json['name'] as String,
    age: json['age'] as int,
  );
}

Map<String, dynamic> _$UserToJson(User instance) {
  return {
    'name': instance.name,
    'age': instance.age,
  };
}
```

这里使用 `part` 很合理，因为生成代码本来就是模型类的一部分，不需要独立复用。

## 业务代码中为什么要谨慎使用

`part` 可以把一个大文件拆成多个文件，但它并不会真正拆分职责。多个 `part` 文件仍然属于同一个 library，仍然可以随意访问私有状态。

如果在页面、controller、repository 中大量使用 `part`，容易出现这些问题：

- 文件变多了，但大类本身没有变小。
- 片段之间可以访问私有字段，职责边界不清楚。
- 依赖关系隐藏在同一个 library 内，阅读时不容易判断谁依赖谁。
- 单元测试和复用更困难。
- 后续想迁移成独立模块时成本更高。

例如下面这种结构，看起来分了文件，但本质上仍是一个大 controller：

```dart
// app_data_controller.dart
part 'app_data_detail_ops.dart';
part 'app_data_account_ops.dart';

class AppDataController {
  final List<String> _details = [];
  final List<String> _accounts = [];
}
```

```dart
// app_data_detail_ops.dart
part of 'app_data_controller.dart';

extension DetailOps on AppDataController {
  void loadDetails() {
    _details.clear();
  }
}
```

这种写法可以工作，但 `DetailOps` 直接依赖 `_details` 私有状态，边界比较弱。

## 更推荐的业务拆分方式

业务代码通常更适合使用普通文件、`import/export`、组合对象、普通类、extension 或 mixin。

### 方式一：普通类组合

```dart
class AppDataController {
  final DetailController detailController;
  final AccountController accountController;

  AppDataController({
    required this.detailController,
    required this.accountController,
  });
}
```

这种方式职责最清晰，适合 controller、service、repository 拆分。

### 方式二：普通 extension 文件

```dart
// app_data_controller.dart
export 'app_data_detail_ops.dart';

class AppDataController {
  final DetailState detailState = DetailState();
}
```

```dart
// app_data_detail_ops.dart
import 'app_data_controller.dart';

extension AppDataControllerDetailOps on AppDataController {
  void loadDetails() {
    detailState.load();
  }
}
```

这种方式比 `part` 边界更清楚，因为扩展文件只能访问公开成员。

### 方式三：mixin 复用行为

```dart
mixin Loggable {
  void log(String message) {
    print(message);
  }
}

class UserService with Loggable {
  void save() {
    log('save user');
  }
}
```

`mixin` 更适合多个类复用同一组行为。

## 小结

`part` 的本质是“同一个 library 的源码拆片”。

它适合代码生成和强绑定源码片段，不适合承担业务架构拆分。业务代码里如果想让职责更清晰、依赖更可控、测试更容易，通常应该选择普通类、组合对象、extension、mixin 和 `import/export`。
