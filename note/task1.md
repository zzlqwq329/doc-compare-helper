# Task 1 学习笔记：读取、分段和导出

对应代码：[project/reader.py](../project/reader.py)。

## 一、找到并读取样本

### 1. 程序从哪里开始执行

Python 直接运行脚本时，最后两行会调用主函数。

```python
if __name__ == "__main__":
    main()
```

```python
def main() -> None:
```

`def main()` 定义主函数。`-> None` 表示这个函数没有要返回给调用者的值，函数体里的打印和保存文件照常执行。

### 2. 找到要读取的文件

```python
root = Path(__file__).resolve().parents[1]
v1_path = root / "samples" / "expense-v1.md"
```

`__file__` 是当前这份代码的文件路径。`Path(__file__).resolve()` 把它变成绝对路径，也就是 `D:\Java\文档分析项目\project\reader.py`。

`parents` 可以理解为从这个文件开始，一层层往上找文件夹。

- `parents[0]` 是放着脚本的 `project` 文件夹。
- `parents[1]` 是再往上一层的 `文档分析项目` 文件夹。

所以 `root` 指向项目根目录。第二行里，`Path` 对象用 `/` 拼接路径，先进入 `samples`，再加上文件名，得到 `D:\Java\文档分析项目\samples\expense-v1.md`。到这里，`v1_path` 记住了文件的位置，真正读取文件在后面。

### 3. 打开文件

```python
def read_lines(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as source:
        return [line.removesuffix("\n") for line in source]
```

- `read_lines` 接收一个 `Path` 路径，返回一个字符串列表。`list[str]` 表示列表里的每个元素都是字符串。
- 调用 `read_lines(v1_path)` 时，`path` 接收到 `v1_path` 的值。
- `path.open(...)` 打开文件。`encoding="utf-8"` 告诉 Python 用 UTF-8 读取里面的文字。
- `as source` 给打开的文件起个名字，下面就可以用 `source` 来读内容。离开 `with` 代码块时，Python 会自动关闭文件。

### 4. 用列表推导式收集每一行

```python
return [line.removesuffix("\n") for line in source]
```

这行可以展开成熟悉的 `for` 循环：

```python
lines = []
for line in source:
    text = line.removesuffix("\n")
    lines.append(text)
return lines
```

读列表推导式时，可以先读右边，再读左边。

1. `for line in source` 从文件里一行一行取出文字，放进 `line`。
2. `line.removesuffix("\n")` 去掉这一行末尾的换行符，把处理后的字符串放进新列表。

例如，`"第一行\n"` 会变成 `"第一行"`，只有换行符的空行 `"\n"` 会变成 `""`。如果中间有一行空行，返回的列表就是 `["第一行", "", "第三行"]`。

### 5. 读取后给每行编号

```python
for line_number, line in enumerate(read_lines(v1_path), start=1):
    print(f"{line_number}: {line}")
```

`read_lines(v1_path)` 先返回字符串列表。`enumerate(..., start=1)` 再给每个元素配一个从 1 开始的编号。

`enumerate()` 每次给出一对 `(编号, 元素)`，Python 按位置解包。`line_number` 拿到编号，`line` 拿到字符串。第二行是空行时，这对值就是 `(2, "")`。

## 二、把正文整理成记录

### 6. 初始化列表和当前章节

```python
blocks: list[Block] = []
section = ""
```

- `blocks` 用来收集正文。刚开始还没读到正文，因此用 `= []` 创建一个空列表。`: list[Block]` 是类型提示，表示列表里放的是一条条 `Block` 记录。
- `section` 用来记住当前章节。一开始还没读到章节标题，所以设成空字符串 `""`。读到章节标题后，接下来的正文都会用这个章节名，直到遇到下一个章节标题。

### 7. 记住当前章节

```python
if line.startswith("## "):
    section = line.removeprefix("## ").strip()
    continue
```

`startswith("## ")` 检查这一行是否以两个 `#` 加一个空格开头。条件成立时，`removeprefix("## ")` 去掉这个开头，`strip()` 去掉首尾多余的空白，再把结果存到 `section`。

例如，读到 `## 第一章 总则` 时，`section` 就变成 `"第一章 总则"`。`continue` 会直接进入下一次循环，所以这一行不会被存为正文。

### 8. 跳过文档标题和空行

```python
if line.startswith("# ") or not line.strip():
    continue
```

`or` 连接两个条件，只要其中一个成立，就跳到下一行。

- `line.startswith("# ")` 检查这一行是否以一个 `#` 加空格开头，例如 `# 差旅报销制度`。
- `not line.strip()` 检查去掉两端空白后是否为空字符串。

| 原来的 `line` | `line.strip()` | `not line.strip()` | 执行 `continue` |
| --- | --- | --- | --- |
| 三个空格（`"   "`） | `""` | `True` | 是 |
| `"  报销须提交发票。  "` | `"报销须提交发票。"` | `False` | 否 |

### 9. 给正文编号

```python
block_number = len(blocks) + 1
```

`len(blocks)` 表示已经存了几条正文。刚读到 V1 的第一条正文时，列表还是空的，所以 `len(blocks)` 是 `0`，这条正文的序号就是 `0 + 1 = 1`。

在样本里，第一条正文出现在原文件的第 5 行。此时 `line_number` 是 `5`，表示它在原文件里的位置。`block_number` 是 `1`，表示它是第几条正文。

代码用正文序号生成记录的 ID：

```python
block_id=f"{version_id}-P{block_number:03d}",
```

`{version_id}` 会填入版本名，比如 `V1`。`-P` 是固定字符。`03d` 表示把整数显示成至少三位，不足就从左边补零。所以 `2` 会显示成 `002`，拼起来就是 `"V1-P002"`。

### 10. 把正文存进列表

```python
blocks.append(
    Block(
        version_id=version_id,
        block_id=f"{version_id}-P{block_number:03d}",
        section=section,
        line_start=line_number,
        line_end=line_number,
        raw_text=line,
    )
)
```

先读里面的 `Block(...)`。它把这一段正文的信息放进一个字典。拿 `section=section` 来说，等号左边是字段名，右边是变量。如果变量 `section` 里存着 `"第一章 总则"`，字典里就会有 `"section": "第一章 总则"`。

再看外面的 `blocks.append(...)`。一次调用把整个字典作为一条记录加到列表末尾。

### 11. 返回收集好的记录

```python
    return blocks
```

它的缩进和 `for` 对齐，所以它在循环外面。Python 会先读完整个文件，把碰到的正文一条条加进 `blocks`，然后把整个列表交回给调用它的 `main()`。

## 三、把两份结果写成 JSON

### 12. 给两份结果配上文件名

```python
records_by_filename = {
    "blocks-v1.json": parse_blocks(v1_path, "V1"),
    "blocks-v2.json": parse_blocks(v2_path, "V2"),
}
```

花括号里是一个字典。第一项的键是 `"blocks-v1.json"`，值是 `parse_blocks(v1_path, "V1")` 返回的正文列表。第二项用同样的方式把 V2 的正文列表和它的文件名配在一起。

执行完这段时，两份正文列表都已经在内存里。`records_by_filename["blocks-v2.json"]` 用文件名作为键，取出对应的 V2 正文列表。

下面的例子也是用键查找对应的值：

```python
scores = {"小明": 90}
print(scores["小明"])  # 打印 90
```

### 13. 准备输出目录

```python
output_dir = root / "outputs"
output_dir.mkdir(exist_ok=True)
```

第一行把项目根目录 `root` 和 `"outputs"` 拼起来，得到输出目录的路径。第二行的 `mkdir()` 才会尝试创建目录。

`exist_ok=True` 可以读成**“这个目录已经存在也没关系”**。第一次运行，目录还没有，程序会创建它。第二次运行，程序会继续使用已有的目录。

### 14. 遍历结果并写入文件

```python
for filename, records in records_by_filename.items():
    json_text = json.dumps(records, ensure_ascii=False, indent=2)
    (output_dir / filename).write_text(json_text + "\n", encoding="utf-8")
```

1. **取出文件名和正文。** 字典的 `.items()` 每次给出一对 `(键, 值)`，和 `enumerate()` 一样按位置解包。第一次循环时，`filename` 是 `"blocks-v1.json"`，`records` 是 V1 的完整正文列表。
2. **转成 JSON 文本。** `json.dumps()` 把 Python 列表变成 JSON 字符串，存到 `json_text`。`ensure_ascii=False` 让中文直接显示，`indent=2` 让每层缩进两个空格。
3. **写到硬盘。** `output_dir / filename` 拼出文件路径，第一次循环时是 `outputs\blocks-v1.json`。`json_text + "\n"` 在末尾加一个换行符。`write_text(...)` 用 UTF-8 写入文本，文件不存在时创建，已经存在时覆盖内容。

## 四、回顾代码里的其他写法

### 15. 设置终端输出编码

```python
if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
```

`sys.stdout` 是 `print()` 默认把文字送去的地方，通常是终端。`isinstance(...)` 检查它是不是 `TextIOWrapper` 这种可以重新设置编码的文本流。如果是，下一行就把输出编码设为 UTF-8。

`path.open(encoding="utf-8")` 用 UTF-8 **读取文件**，`sys.stdout.reconfigure(encoding="utf-8")` 用 UTF-8 **输出到终端**。`write_text(..., encoding="utf-8")` 用 UTF-8 **保存 JSON**。

### 16. 用 `Block` 声明记录字段

```python
class Block(TypedDict):
    version_id: str
    block_id: str
    section: str
    line_start: int
    line_end: int
    raw_text: str
```

拿 `line_start: int` 来说，它表示字典里有一个叫 `"line_start"` 的键，对应的值应该是整数。这是给读代码的人和编辑器看的类型提示。真正存进去的值是在后面调用 `Block(...)` 时提供的。

### 17. 开头的导入语句

| 导入语句 | 在这份代码里的用途 |
| --- | --- |
| `from __future__ import annotations` | 让 `path: Path`、`-> list[str]` 这类类型注解以字符串形式保存。 |
| `import json` | 用 `json.dumps(...)` 把正文列表转成 JSON 字符串。 |
| `import sys` | 用 `sys.stdout` 找到 `print()` 默认输出文字的地方。 |
| `from io import TextIOWrapper` | 用 `isinstance(sys.stdout, TextIOWrapper)` 检查输出流的类型。 |
| `from pathlib import Path` | 用 `Path` 表示文件路径，可以用 `/` 拼路径、用 `.open()` 打开文件。 |
| `from typing import TypedDict` | 用 `class Block(TypedDict)` 声明每条正文记录有哪些键，以及值的类型。 |

从模块里直接导入 `Path` 后，就可以直接用这个名字：

```python
from pathlib import Path

path = Path(__file__)
```

导入模块时，则通过 `pathlib.Path` 取出同一个名字：

```python
import pathlib

path = pathlib.Path(__file__)
```
