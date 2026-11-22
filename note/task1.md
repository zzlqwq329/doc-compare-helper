# Task 1 学习笔记 · 读取、分段和导出

对应代码是 [project/reader.py](../project/reader.py)，练习要求见 [Task 1](../docs/01-first-task.md)。

## 函数做什么

| 函数 | 我的理解 |
| --- | --- |
| `read_lines(path)` | 用 UTF-8 读取一份文件，返回字符串列表。每项对应原文件的一行，行末换行符去掉，空行保留为 `""`。 |
| `parse_blocks(path, version_id)` | 一次处理一份 Markdown，接收它的路径和版本标识。记住当前章节，把每条正文存成一条 `Block` 记录，保留版本、段落编号、章节、原始行号和原文。最后返回记录列表。 |
| `main()` | 打印 V1 的原文和行号，分别调用 `parse_blocks()` 处理两版，再把两个列表写进 `outputs/blocks-v1.json` 和 `outputs/blocks-v2.json`。V1 有 13 条正文，V2 有 14 条。 |

## 我卡过的地方

- **看到两个 `reader.py`，以为升级 Python 后代码变了。** 根目录的 [reader.py](../reader.py) 负责启动，读取、分段和写文件的实现都在 `project/reader.py`。
- **复述 `parse_blocks()` 的输入时漏了版本。** 读新版要传 `parse_blocks(v2_path, "V2")`。路径用来找到文件，`"V2"` 用来填每条记录的 `version_id` 并生成段落编号。
- **把 `enumerate()` 的两个值和正文序号混在一起。** 它每轮按 `(行号, 这一行的内容)` 给值，从 1 开始编号时，第二行即使为空也会给出 `(2, "")`。例如，第一条正文在原文件第 5 行，它的 `line_start` 是 `5`，段落编号仍是 `V1-P001`。在它前面加一个空行，只会把原始行号推到第 6 行。
- **没看懂 `not line.strip()`。** 一行只有空格时，`strip()` 得到 `""`，`not ""` 为 `True`，所以会跳过这一行。有正文时，`strip()` 的结果仍有内容，`not` 得到 `False`。保存 `raw_text` 时用的是原来的那行，首尾空格仍然留在记录里。
- **高估了循环里提前 `return` 能收集的段落数。** 如果把 `return blocks` 缩进到 `append()` 后面，第一条正文存进去就会结束函数，只返回 1 条。现在 `return` 在循环外面，读完整份文件才返回。
- **以为用文件名查字典会取回文件名。** `records_by_filename["blocks-v2.json"]` 用文件名当键，取到的是 V2 的正文列表。要数有多少条，才用 `len()`。
- **把转换、建目录和写文件混在一起。** `json.dumps()` 只在内存里生成 JSON 字符串。`mkdir(exist_ok=True)` 允许沿用已有目录。真正创建或覆盖 JSON 文件的是 `write_text()`。
- **把读取文件和打印中文的编码当成同一件事。** `path.open(encoding="utf-8")` 管样本怎么读，`sys.stdout.reconfigure(encoding="utf-8")` 管终端怎么输出。打印乱码时可以先看输出端。
