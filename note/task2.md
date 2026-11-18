# Task 2 学习笔记：匹配两版中原文相同的段落

对应代码是 [compare.py](../project/compare.py)，验收要求见 [Task 2](../docs/02-second-task.md)。准备输入的过程见 [Task 1 笔记](task1.md)。

Task 1 把原文整理成带编号、章节和行号的记录。Task 2 读取两份 JSON，把正文完全相同且在两版中各出现一次的段落配对，再按章节标为「未变」或「移动」。

## 一、读取 Task 1 的结果

### 1. 把 JSON 文本转回 Python 列表

```python
v1_text = v1_path.read_text(encoding="utf-8")
v1_blocks = json.loads(v1_text)
```

`v1_text` 是从文件读出的整个字符串。`json.loads()` 把它转成 Python 列表 `v1_blocks`，列表里每一项都是一个段落字典。V2 也是同样的读法。样本读入后，`len(v1_blocks)` 是 `13`，`len(v2_blocks)` 是 `14`。

### 2. 区分整条记录和正文字符串

```python
for block in blocks:
    text = block["raw_text"]
```

`block` 是一条完整记录，包含 `block_id`、`section`、`raw_text` 等字段。`text` 是从这条记录取出的原文字符串。一个简化的例子如下。

```python
block = {"block_id": "V1-P001", "raw_text": "须提供发票"}
text = block["raw_text"]  # "须提供发票"
```

## 二、按正文分组并配对

### 3. 用原文当字典的键

```python
def group_by_text(blocks):
    groups = {}
    for block in blocks:
        text = block["raw_text"]
        if text not in groups:
            groups[text] = []
        groups[text].append(block)
    return groups
```

第一次遇到一句原文时，`groups[text] = []` 给这句原文建一个空列表。`append(block)` 在 `if` 外面，每条记录都会被加到对应的列表里。两条记录的正文相同，即使编号不同，也会放进同一个列表。

如果看到 `groups[text][0]`，可以拆成两步读。`[text]` 用字典的键找到这一组，`[0]` 再从组里的列表取出第一条完整记录。

`group_by_text(v1_blocks)` 和 `group_by_text(v2_blocks)` 各调用一次。每次都从 `groups = {}` 开始，所以两版有各自的分组字典。

### 4. 两边各有一条时才配对

```python
for text, old_matches in v1_groups.items():
    new_matches = v2_groups.get(text, [])
    if len(old_matches) != 1 or len(new_matches) != 1:
        continue

    old_block = old_matches[0]
    new_block = new_matches[0]
```

- `.items()` 每次给出一对 `(键, 值)`。`text` 拿到原文，`old_matches` 拿到 V1 中这句原文对应的记录列表。
- `v2_groups.get(text, [])` 用同一句原文查 V2。找得到就返回对应的列表，找不到就返回空列表 `[]`。
- `!= 1` 表示数量不等于 1。`or` 两边只要有一个条件成立，`continue` 就会跳到下一句原文。两边都恰好有一条时，才用 `[0]` 取出各自的完整记录。

| 同一句原文在 V1 的数量 | 在 V2 的数量 | 结果 |
| --- | --- | --- |
| 1 | 1 | 配成一对 |
| 1 | 0 | V1 的这条留在未匹配列表 |
| 0 | 1 | V2 的这条留在未匹配列表 |
| 2 | 1 | V1 的两条和 V2 的一条都留在各自的未匹配列表 |
| 1 | 2 | V1 的一条和 V2 的两条都留在各自的未匹配列表 |

### 5. 看章节是否相同

```python
if old_block["section"] == new_block["section"]:
    status = "未变"
    unchanged_count += 1
else:
    status = "移动"
    moved_count += 1
```

走到这里时，两段原文已经确认完全相同。`section` 相同记为「未变」，`section` 不同记为「移动」。`+= 1` 给对应的计数加一。

拿凭证保存条款走一遍。相同的原文在 V1 只找到 `V1-P011`，在 V2 只找到 `V2-P003`。旧章是「第三章 归档与监督」，新章是「第二章 报销与审批」，所以这一对记为「移动」。

## 三、存下配对并筛出剩余段落

### 6. 配对列表保存整条记录

```python
pairs.append((status, old_block, new_block))
matched_v1_ids.add(old_block["block_id"])
matched_v2_ids.add(new_block["block_id"])
```

里面的 `(status, old_block, new_block)` 是一个元组，包含分类和两条完整记录。`append()` 把这个元组作为**一个元素**加进 `pairs`，因此每配成一对，`len(pairs)` 增加 `1`。

两个 `matched_*_ids` 各用 `set()` 创建一个空集合，再用 `add()` 存入已配对的编号。配对列表能查到哪两条配在一起，集合能用 `in` 检查某个编号是否已配对。

### 7. 未匹配列表保留完整段落

```python
unmatched_v1 = [
    block for block in v1_blocks if block["block_id"] not in matched_v1_ids
]
```

逐条查看 V1 的记录。编号没有出现在已配对的集合里，就把这个 `block` 放进 `unmatched_v1`。V2 同理，用 V2 的正文列表和编号集合。

例如 `V1-P003` 写「10 个工作日」，`V2-P004` 写「5 个工作日」。两条原文不同，所以各自留在未匹配列表里。它们是否属于同一条款的修改，留到下一步判断。

## 四、打印结果并验算

### 8. 移动行显示旧章和新章

```python
for status, old_block, new_block in pairs:
    message = f"{status} {old_block['block_id']} → {new_block['block_id']}"

    if status == "移动":
        old_section = old_block["section"]
        new_section = new_block["section"]
        message += f"（{old_section} → {new_section}）"

    print(message)
```

`for` 把配对元组按顺序拆成三个变量。每对都先生成带分类和编号的字符串。遇到「移动」时，`+=` 把章节信息接到消息末尾。`print(message)` 在 `if` 外面，所以两种结果都会打印。未匹配段落会逐条打印 `block["block_id"]`。

### 9. 用样本核对结果

在项目根目录运行下面的命令。

```powershell
.\.venv\Scripts\python.exe -X utf8 .\project\compare.py
```

```text
读入 V1正文：13 段，V2正文：14 段
未变 V1-P001 → V2-P001
移动 V1-P011 → V2-P003（第三章 归档与监督 → 第二章 报销与审批）
未变 5 对，移动 1 对
V1 未匹配 7 段，V2 未匹配 8 段
```

共有 `5 + 1 = 6` 对，每对从两版各用掉一段。V1 剩 `13 - 6 = 7` 段，V2 剩 `14 - 6 = 8` 段。把配对和未匹配的编号合起来，样本的 **27 个段落编号各出现一次**。
