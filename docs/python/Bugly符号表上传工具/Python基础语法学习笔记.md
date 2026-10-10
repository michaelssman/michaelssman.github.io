# Python 基础语法学习笔记

先分清两件事：**语法**是 Python 的书写规则，例如 `if`、`for`、`def`；**库 API** 是已经写好的功能，例如 `Path.resolve()`、`json.dumps()`。`print()`、`len()` 是内置函数，不需要导入模块。

## 1. 缩进、注释和文档字符串

Python 用缩进表示代码归属，通常每层使用 **4 个空格**。`if`、`for`、`def`、`class`、`try`、`with` 等语句后的冒号 `:` 表示接下来是代码块。

```python
count = 2
if count > 0:
    print('有可选项目')
print('结束')
```

- `# 说明` 是注释，不参与执行；可独占一行，也可放在代码后面。
- `"""说明"""` 是字符串；放在模块、函数或类的开头时，称为**文档字符串**，可通过 `__doc__` 读取。它与普通注释不同。
- 文件首行 `#!/usr/bin/env python3` 是供系统直接运行脚本时识别解释器的声明；对 Python 来说也是注释。

脚本对应：文件顶部的文档字符串；`main()` 用 `description=__doc__` 将它显示在帮助说明中。

## 2. 导入模块、变量和常量

**模块**是可导入的一组 Python 功能；**标准库**是 Python 自带的模块。

```python
import datetime as dt
from pathlib import Path

name = '示例应用'
count = 3
enabled = True
selected = None
```

`import datetime as dt` 将模块命名为 `dt`，例如 `dt.datetime.now()`。`from pathlib import Path` 只取其中的 `Path`，调用时不用再写模块名。

变量名代表一个对象，不需要先声明类型。`None` 表示没有值。

`DEFAULT_ARCHIVES`、`JAVA` 这样的全大写名字表示“按约定作为常量使用”，Python 并不会禁止重新赋值。脚本还用到 `0o700`，这是**八进制整数**的写法，用于表达目录权限。

常用内置功能可以直接调用：

| 写法 | 含义 |
|---|---|
| `input('请输入：')` | 等待用户输入一行，返回字符串；数字输入也需要再用 `int()` 转换 |
| `str(value)`、`int(text)`、`bool(value)` | 转成字符串、整数、布尔值；转换失败可能抛异常 |
| `isinstance(value, str)` | 检查值是不是字符串，和类型提示不会自动检查类型的行为不同 |
| `type(error).__name__` | 读取对象所属类型的名字，脚本用它报告异常类别 |
| `ord(char)` | 取得单个字符的 Unicode 编码值；脚本用它拒绝指定的控制字符 |

脚本对应：顶部的 `import` 和常量；`upload_selected()` 创建工作目录时传入 `mode=0o700`。

## 3. 字符串和格式化

单引号和双引号都能创建字符串；本脚本主要使用单引号。

```python
text = '  Hello，Python  '
text = text.strip().lower().replace('，', ',')
print(text)  # hello,python

print('{} 第 {:02d} 项'.format('示例', 3))  # 示例 第 03 项
print('; '.join(['A', 'B']))  # A; B
```

`strip()` 去掉两端空白，`lower()` 转小写，`replace()` 替换文字。这些方法返回新字符串。连续写 `.strip().lower()` 称为**方法链**。

`.format(...)` 将参数依次填入 `{}`；`{:02d}` 表示整数至少显示两位，不足时补零。`+` 可以连接字符串，但不能直接将字符串和整数相加，需要先用 `str(整数)` 转换。

- `'第一行\n第二行'` 中的 `\n` 表示换行。
- `r'\d+'` 中的 `r` 表示原始字符串，让反斜线尽量保留原样。本脚本用它书写正则表达式。
- `''.join(列表)` 将多段字符串连起来；`'; '.join(列表)` 则在相邻项之间加上 `; `。

脚本对应：`parse_selection()` 清理输入；`archive_label()` 格式化菜单文字；`upload_one()` 用 `join()` 合并日志。脚本使用 `.format()`，没有使用 f-string。

## 4. 四种常见容器

**容器**用于存放多个值。

| 类型 | 示例 | 特点 |
|---|---|---|
| 列表 `list` | `['A', 'B']` | 有顺序，可修改，可重复 |
| 元组 `tuple` | `('UUID', 'arm64')` | 有顺序，不能替换其中的元素 |
| 字典 `dict` | `{'version': '1.0'}` | 按“键 → 值”查找 |
| 集合 `set` | `{'A', 'B'}` | 自动去重，不用于表示顺序 |

空容器的写法是 `[]`、`()`、`{}`、`set()`。**`{}` 是空字典，不是空集合。** 单元素元组需要逗号，例如 `('A',)`。

```python
items = ['A']
items.append('B')        # 添加一个元素
items.extend(['C', 'D']) # 逐个添加，结果为 ['A', 'B', 'C', 'D']

info = {'version': '1.0'}
print(info['version'])          # 1.0
print(info.get('build', '未知')) # 未知

values = set(['A', 'A', 'B'])
print(len(values))  # 2
```

`info['不存在的键']` 会抛出 `KeyError`；`info.get('键')` 不存在时返回 `None`，也可提供默认值。`setdefault('键', [])` 在键缺失时放入空列表，随后返回该键的值。

集合用 `add(一项)` 或 `update(多个值)` 添加内容。列表的 `remove(值)` 删除一项；字典或列表的 `clear()` 清空内容；列表之间的 `+` 表示拼接。`len()` 获取元素数量。

需要注意**引用**：`item = report['apps'][0]` 不会复制字典；修改 `item['status']` 会修改报告中的同一份字典。`list(directories)` 则会创建列表副本，脚本用它避免一边遍历同一个列表一边删元素。

脚本对应：`choose_archives()` 用字典分组；`discover_archives()` 用集合去重；`upload_selected()` 修改报告记录。

## 5. 索引、解包和比较

```python
items = ['第一项', '第二项']
print(items[0])  # 第一项

version, build = ('1.0', '3')
print(version, build)  # 1.0 3
```

把多个值对应放进多个变量，叫**解包**。变量数量必须与值的数量匹配。`return archives, errors` 也会组成元组，可用 `archives, errors = discover_archives(...)` 接收。

| 写法 | 含义 |
|---|---|
| `a == b` / `a != b` | 值相等 / 不相等 |
| `a < b` / `a > b` | 比较大小 |
| `value in items` / `value not in items` | 是否包含该元素；对字典检查的是键 |
| `value is None` / `value is not None` | 是否是“没有值”这个特殊对象 |

`is` 判断是否为同一个对象；本脚本用它判断 `None`。比较字符串、数字或集合内容时用 `==`、`!=`。集合相等不要求顺序相同，但元素必须完全相同。

脚本对应：`parse_selection()` 判断选择是否重复；`validate_archive()` 比较主程序和 dSYM 的 UUID/架构集合。

## 6. 真假值、短路和条件表达式

条件判断中，`None`、`False`、`0`、空字符串和空容器都视为假；非空字符串即使是 `'0'`，也视为真。

```python
provided = ''
chosen = provided or '默认值'
print(chosen)  # 默认值

items = []
if items and items[0] == 'A':
    print('第一项是 A')
```

第二段不会报索引错误：`and` 左边为假，就不执行右边，这叫**短路**。`or` 左边为真，就不再执行右边。`and`、`or` 会返回所选操作数的值，不一定是 `True` 或 `False`；`not` 则返回布尔值。

脚本用 `args.archive or args.archives_dir or [DEFAULT_ARCHIVES]` 依次选第一个非空来源，也用短路避免对错误类型调用方法、避免访问空列表。

```python
failed = False
exit_code = 1 if failed else 0
print(exit_code)  # 0
```

`A if 条件 else B` 是**条件表达式**，可在赋值或 `return` 中使用。

`all(...)` 要求所有项为真，`any(...)` 要求至少一项为真。注意：`all([])` 为 `True`，`any([])` 为 `False`，因此 `upload_succeeded()` 还用 `bool(statuses)` 要求确实读到状态码。

## 7. 分支和循环

```python
selected = []
for number in range(1, 4):
    if number == 2:
        continue
    selected.append(number)
print(selected)  # [1, 3]

for index, name in enumerate(['A', 'B'], 1):
    print(index, name)  # 分别输出：1 A、2 B
```

`range(1, 4)` 包含 1、不包含 4；`range(3)` 提供 0、1、2。

`enumerate()` 同时提供编号和元素，默认编号从 0 开始；传入 `1` 则从 1 开始。

`for current, directories, _ in ...` 是解包；`_` 是普通变量名，这里按约定表示“有意不用”。

脚本对应：`discover_archives()` 遍历目录；`parse_selection()` 处理编号；`ask_selection()` 反复询问。

## 8. 函数、参数和返回值

```python
def label(name, build='1'):
    return '{}（{}）'.format(name, build)

print(label('示例'))             # 示例（1）
print(label('示例', build='3'))  # 示例（3）
```

`def` 定义函数；定义函数时不会执行里面的流程，`label(...)` 才是调用。`name`、`build` 是参数；`build='1'` 是默认参数；调用时写 `build='3'` 是关键字参数。

`return` 立即结束函数并交回结果；没有显式 `return` 时，返回 `None`。默认参数在定义函数时计算一次，初学时避免使用 `[]`、`{}` 作为需要每次独立创建的默认值。本脚本的 `default=None`、`argv=None` 不存在这个问题。

函数内部还能定义函数。`upload_selected()` 中的 `save_report()` 可以读取外层的 `report` 和 `report_path`；这种保留外层环境的函数常称为**闭包**。`discover_archives()` 将 `walk_error` 函数交给 `os.walk()`，让它在出错时调用，这称为**回调**。

## 9. 推导式、生成器表达式和排序

**推导式**是“遍历、可选筛选、收集结果”的简写。

```python
names = [' A ', ' ', ' B ']
clean = [name.strip() for name in names if name.strip()]
print(clean)  # ['A', 'B']

unique = {name.strip() for name in names if name.strip()}
print(sorted(unique))  # ['A', 'B']
```

`[...]` 得到列表，`{... for ...}` 得到集合。脚本在 `read_archive()` 收集字段，在 `uuid_set()` 生成 UUID/架构集合。

```python
numbers = [1, 2, 3]
checks = (number > 0 for number in numbers)
print(all(checks))  # True
```

`(... for ...)` 是**生成器表达式**：按需逐个提供结果，不先创建完整列表；消费后不要指望再次从头使用。脚本将它传给 `all()`、`any()`、`extend()`、`join()`。作为唯一的函数参数时，可写成 `all(number > 0 for number in numbers)`。

```python
rows = [('旧', 1), ('新', 3), ('中', 2)]
ordered = sorted(rows, key=lambda item: item[1], reverse=True)
print(ordered)  # [('新', 3), ('中', 2), ('旧', 1)]
```

`sorted()` 返回排序后的新列表；`key` 指定比较依据；`reverse=True` 倒序排列。`lambda item: item[1]` 是没有单独名字的小函数。`latest_first()` 用 `(归档时间, 路径)` 作为排序依据：先比时间，相同时再比路径。

## 10. 类、对象、dataclass 和类型提示

**类**描述一种对象的结构；**对象**是实际创建出来的一份数据；属性通过 `对象.属性` 读取。

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Example:
    name: str
    build: Optional[str] = None

    def label(self):
        return self.name

app = Example('示例', '3')
print(app.name, app.label())  # 示例 示例
```

`@dataclass(...)` 是**装饰器**，自动生成初始化、相等比较等方法。`frozen=True` 禁止普通赋值修改字段，例如 `app.name = '其他'` 会报错；它不代表字段内部可能包含的列表、字典也全部被冻结。

`self` 是当前对象；调用 `app.label()` 时，Python 自动将 `app` 传给 `self`。`name: str` 是类型提示，帮助阅读和检查，不是赋值，也不会自动进行运行时类型校验。`Optional[str]` 表示字符串或 `None`。

脚本对应：`Archive` 保存归档信息；`ToolPackage` 保存工具来源，`prepare()` 使用 `self.source`、`self.member`。

## 11. 异常处理和资源管理

**异常**表示操作无法按正常流程继续。`raise` 抛出异常；`try` 中发生指定异常后，进入对应的 `except`；`finally` 用于收尾。

```python
class UserError(Exception):
    """可展示给用户的错误。"""

def parse_number(text):
    try:
        return int(text)
    except ValueError:
        raise UserError('请输入整数') from None

try:
    print(parse_number('abc'))
except UserError as error:
    print(str(error))  # 请输入整数
finally:
    print('处理结束')
```

`class UserError(Exception)` 表示继承内置的异常类。`except ... as error` 将异常对象保存到变量；`from None` 隐藏底层异常链的展示，不是忽略错误。单独的 `raise` 会把当前捕获的异常继续抛出。

`except (OSError, ValueError)` 可以接住任一种所列异常。`finally` 在正常结束、`return` 或异常传播时都会执行；进程被强杀等情况不能保证执行，而且收尾本身也可能报错。

```python
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'demo.txt'
    path.write_text('学习 Python\n', encoding='utf-8')
    with path.open('r', encoding='utf-8') as source:
        print(source.read(), end='')  # 学习 Python
```

`with ... as ...` 是**上下文管理**：离开块时关闭文件或清理临时目录，包括通过异常离开的情况。上例结束后，演示目录会自动删除。

脚本对应：`inside()` 将路径错误转成 `UserError`；`upload_one()` 的 `finally` 清理子进程；`ToolPackage.prepare()` 用 `with` 关闭 ZIP。

## 12. 常用标准库 API

这里介绍的是库功能，不是新的 Python 语法。

| 模块/API | 本脚本中的含义 |
|---|---|
| `Path.home()`、`Path(__file__).parent` | 用户主目录、脚本所在目录 |
| `Path(a) / 'b'` | 拼接路径，`/` 在这里不是数值除法 |
| `expanduser()`、`resolve()` | 展开 `~`；转绝对路径并解析 `..`、符号链接 |
| `name`、`stem`、`suffix`、`parent` | 文件名、去掉末尾扩展名的名字、末尾扩展名、父目录 |
| `is_file()`、`is_dir()`、`glob()` | 检查文件/目录，按通配规则查找 |
| `relative_to()` | 计算相对路径；不在指定父目录下时抛 `ValueError` |
| `os.walk()` | 逐层遍历目录，提供当前路径、子目录名和文件名 |
| `stat`、`lstat()` | 识别普通文件、目录、符号链接等；`lstat()` 不跟随链接 |
| `shutil.copy2()`、`copytree()` | 复制文件、复制目录树 |
| `zipfile.ZipFile()` | 读取 ZIP/JAR 结构；结构合格不证明来源可信 |
| `getpass.getpass()` | 在正常支持的终端中隐藏输入回显 |
| `dt.datetime.now()`、`strftime()` | 获取时间、按格式转换为文字 |
| `replace(tzinfo=...)`、`astimezone()` | 添加时区解释；按已有时区信息换算时间 |

构造 `Path` 只描述位置，不会自动创建文件。`mkdir()`、`write_text()`、复制等 API 才会修改磁盘。`glob()` 的 `*` 是文件名通配规则，和 `re` 的正则规则不同。

文件读写重点：

- `'r'` 读文本，`'rb'` 读二进制，`'w'` 写文本且会覆盖同名文件。
- `encoding='utf-8'` 明确文字与字节的转换编码；`write_bytes()` 写原始字节。
- `plistlib.load(文件)` 读取 Apple 的 plist，通常得到字典；脚本以 `'rb'` 打开它。
- `json.dumps(对象, ensure_ascii=False, indent=2)` 将数据变成 JSON 文本，保留中文并缩进。`Path`、集合不能直接写入 JSON，需要转为字符串、列表等。
- `tempfile.TemporaryDirectory()` 配合 `with` 自动清理；`tempfile.mkdtemp()` 只创建目录，不会自动删除，脚本用后者保留报告。

正则表达式重点：

```python
import re

match = re.fullmatch(r'(\d+)-(\d+)', '1-3')
print(match.group(1), match.group(2))  # 1 3
print(re.findall(r'statusCode: (\d+)', 'statusCode: 0'))  # ['0']
```

`\d+` 表示至少一位数字；圆括号捕获内容；`group(1)` 取第一组。`fullmatch()` 要求整个字符串符合规则，失败时返回 `None`。`findall()` 收集所有匹配；`compile()` 创建可复用规则；`re.I` 表示忽略大小写。脚本对应：`parse_selection()`、`uuid_set()`、`upload_succeeded()`。

读脚本里的较长规则时，还会遇到：`\s`（空白）、`*`（零次或多次）、`?`（零次或一次）、`[0-9A-Fa-f-]`（允许的字符）、`[^/]`（除 `/` 外的字符）、`(?:...)`（只分组，不形成可用 `group()` 取得的捕获组）、`\.`（真正的句点）、`$`（结尾）和 `\b`（单词边界）。这些符号属于正则规则，不是 Python 的运算符。

## 13. 外部命令：run 与 Popen

`subprocess` 让 Python 调用其他程序；命令本身不是 Python 语法。终端里的 `open ...`、`java ...` 也不能直接当成 Python 代码写。

脚本先进行本地准备与核验，再启动上传子进程：

1. `subprocess.run(...)`：启动并等待结束。脚本用它运行 `dwarfdump --uuid`、检查 `java -version`，这些步骤不是上传。
2. `subprocess.Popen(...)`：启动后返回进程对象。`upload_one()` 在这里启动 Java 上传工具，再逐行读取日志，最后调用 `wait()` 等待结束。

命令参数用列表表达，每一项是独立参数；默认不经过 shell，不要手工拼接整条 shell 命令或额外加 shell 引号。

| 参数/方法 | 含义 |
|---|---|
| `capture_output=True`、`text=True` | 收集输出，并作为文本读取 |
| `check=True`、`timeout=30` | 非零退出码时抛异常；限制等待时间 |
| `cwd=work` | 指定子进程工作目录 |
| `stdout=PIPE`、`stderr=STDOUT` | 通过管道读取输出，将错误输出合并进来 |
| `encoding='utf-8', errors='replace'` | 按 UTF-8 解码；坏字节使用替代字符 |
| `wait()` | 等待进程结束，返回退出码；0 通常表示正常结束 |
| `returncode` | 读取进程退出码；对 `Popen` 对象，尚未检测到退出时可能是 `None` |
| `poll()` | 不等待，仍在运行时返回 `None` |
| `terminate()`、`kill()` | 请求终止；必要时强制结束 |

`Popen()` 启动成功不等于服务器接收成功；退出码 0 也不足以判断上传成功。脚本还核对日志证据，之后仍需人工检查 Bugly 网页中的版本和 UUID。

## 14. 命令行参数和脚本入口

`argparse` 是解析命令行参数的标准库；`--check`、`--list` 是这个脚本自定义的选项名，不是 Python 关键字。

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args(['--check'])  # 模拟参数，不读取真实终端输入
print(args.check)  # True
```

- `action='store_true'`：出现该选项为 `True`，不出现为 `False`。
- `action='append'`：允许同一选项重复出现，将值收集为列表。
- `type=Path`：将输入文字转成路径对象，不代表路径已通过有效性检查。
- `default=...`：未提供时使用默认值。
- `add_mutually_exclusive_group()`：组内选项不能同时使用。
- 参数名中的 `-` 会变成属性名中的 `_`，如 `--output-dir` 对应 `args.output_dir`。

脚本的 `main(argv=None)` 在没有传入列表时读取终端参数；测试可传入模拟列表。下面是原脚本的入口片段，用来理解结构，不是独立运行的示例：

```python
if __name__ == '__main__':
    raise SystemExit(main())
```

直接运行文件时 `__name__` 是 `'__main__'`；通过 `import` 导入时是模块名，因而不自动进入 `main()`。`SystemExit` 用于结束进程，`main()` 返回的 0/1 变成退出码。

`print(..., file=sys.stderr)` 将消息写到错误输出流；`flush=True` 及时刷新缓冲；`end=''` 不再额外换行。`KeyboardInterrupt` 常来自 `Ctrl+C`，不属于普通的 `Exception`，脚本单独处理它。

## 15. 练习：只使用模拟数据

可以在终端运行 `python3` 进入交互模式，复制上面的完整小例子练习；退出时按 `Ctrl+D`。需要保存多行例子时，在 VS Code 中新建 `python_demo.py`，复制一个完整例子并保存，再运行 `python3 "文件的实际路径"`。不要把终端提示符 `>>>` 写进 `.py` 文件，也不要单独运行第 14 节的入口片段。

建议先做 1、2，再尝试 3、4。所有练习只处理内存数据或由自己创建的临时文件，不调用 `bugly_upload.py` 的上传入口。

1. **字符串与列表**：把 `[' A ', '', ' B ', 'A']` 清理成 `['A', 'B', 'A']`，再用集合去重并排序，得到 `['A', 'B']`。练习 `strip()`、推导式、真假值、`set()`、`sorted()`。
2. **编号与解包**：用 `enumerate(['正式包', '测试包'], 1)` 显示菜单；给定模拟输入 `'2'`，转整数并减 1，取到 `'测试包'`。再处理 `'9'`，先检查范围，避免索引越界。
3. **排序与 JSON**：准备 `{'name': '旧', 'build': 1}`、`{'name': '新', 'build': 3}` 两份字典，按 `build` 倒序排序，再用 `json.dumps(..., ensure_ascii=False, indent=2)` 输出。预期“新”在前，中文可直接阅读。
4. **异常与临时文件**：参照第 11 节，用 `TemporaryDirectory()` 写入并读回 `demo.txt`；将 `int('abc')` 的错误转成自己的友好消息。确认临时目录在退出 `with` 后被清理。

阅读脚本时，可先看 `main()` 理解整体流程，再看 `Archive`、`parse_selection()` 和 `read_archive()`，最后阅读 `upload_one()` 的子进程与清理逻辑。
