"""
对照 fixtures/expected-changes.json 的人工标注答案，验证 compare_versions 的比对结果。

三个问题（想清楚答案，写在这段 docstring 里）：
1. 重构后 comparison.json 和改之前一模一样，能不能说明重构没改变行为？边界在哪？
        不能、输出一致只证明已经执行到的分支没被改坏。重构改的是代码结构，
             最容易出错的地方恰恰是那些这次没执行到的分支——它们在对比的时候不会露出任何痕迹
        边界：证明“没坏”，不证明“没隐患”。
2. 如果 compare.py 里第 100 行那句双向校验被误删，这个测试靠什么发现？
        发现不了，给的数据过于简单
3. 为什么只断言「expected 的每条都在 items 里」不够？
        漏掉误报只查了漏报
"""
from pathlib import Path
import json

from compare import compare_versions
from reader import parse_blocks

ROOT = Path(__file__).resolve().parents[1]


def build_items():
    """从两份样本现造 block 列表，不依赖 outputs/ 里已有的 json。"""
    v1 = parse_blocks(ROOT / "samples" / "expense-v1.md", "V1")
    v2 = parse_blocks(ROOT / "samples" / "expense-v2.md", "V2")
    return compare_versions(v1, v2)


def load_expected_changes():
    path = ROOT / "fixtures" / "expected-changes.json"
    return json.loads(path.read_text(encoding="utf-8"))["changes"]


def make_key(item_type, old_block, new_block):
    """把一条变化压成一个可比较的键。None 换成固定字符串。"""
    old_id = old_block["block_id"] if old_block else "无"
    new_id = new_block["block_id"] if new_block else "无"
    return (item_type, old_id, new_id)


def test_比对结果与人工标注答案一致():
    items = build_items()
    expected = load_expected_changes()

    actual_keys = {make_key(i["type"], i["old"], i["new"]) for i in items}
    expected_keys = {make_key(c["type"], c["old"], c["new"]) for c in expected}

    missing = expected_keys - actual_keys
    extra = {k for k in actual_keys - expected_keys if k[0] != "unchanged"}

    assert not missing, f"人工标注了但程序没识别出来的变化: {missing}"
    assert not extra, f"程序识别出来但人工标注里没有的变化: {extra}"


