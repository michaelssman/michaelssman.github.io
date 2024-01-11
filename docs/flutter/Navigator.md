# Navigator

## Navigator.pushReplacement

在Flutter中，如果你想要从页面A跳转到页面B1，然后从页面B1跳转到页面B2，从页面B2返回时直接回到页面A。可以使用`Navigator.pushReplacement`方法。这个方法会替换当前的路由，使得用户在页面B2按下返回键时，不会回到页面B1，而是直接回到页面A。

这里是如何实现的：

```dart
// 在页面A中，正常跳转到页面B1
Navigator.of(context).push(
  MaterialPageRoute(builder: (context) => PageB1()),
);

// 在页面B1中，使用 pushReplacement 跳转到页面B2
Navigator.of(context).pushReplacement(
  MaterialPageRoute(builder: (context) => PageB2()),
);
```

当你在页面B1中调用`pushReplacement`方法时，页面B1会被页面B2替换。这样，当用户从页面B2返回时，他们会直接回到页面A，因为页面B1已经不在导航堆栈中了。

## Navigator.pushAndRemoveUntil

如果想要更多的灵活性或者需要执行更复杂的导航操作，可以使用`Navigator.pushAndRemoveUntil`方法。这个方法可以让你跳转到新页面，并且允许你定义一个条件，来决定哪些页面应该被移除。

```dart
// 在页面B1中，跳转到页面B2并移除页面B1（及其之前的所有页面，直到满足条件）
Navigator.of(context).pushAndRemoveUntil(
  MaterialPageRoute(builder: (context) => PageB2()),
  (Route<dynamic> route) => route.isFirst, // 这里的条件是保留第一个页面，即页面A
);
```

在这个例子中，`route.isFirst`的条件意味着导航堆栈中的所有页面都会被移除，直到到达第一个页面。这样，页面B2就会成为堆栈中的第二个页面，当用户从页面B2返回时，他们会直接回到堆栈中的第一个页面，即页面A。