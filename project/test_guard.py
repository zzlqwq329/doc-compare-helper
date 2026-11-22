from pytest import MonkeyPatch

from test_compare import build_items, load_expected_changes, make_key


# 它检查的是：相似度门槛调高后，程序会不会漏掉更多人工已经确认的修改。
# guard（防护测试）：它要防的是重构时有人把阈值在函数里写死，或者漏掉了 score < MIN_SIMILARITY 这道门槛判断。
# !r 会给字符串自动套上引号、把换行符显示成 \n，专门用来在测试断言和调试日志里防止「隐形字符」或「类型混淆」骗过眼睛。
def test_higher_similarity_threshold_loses_annotated_modifications(
    monkeypatch: MonkeyPatch,
) -> None:
    expected = {
        make_key(change["type"], change["old"], change["new"])
        for change in load_expected_changes()
        if change["type"] == "modified"
    }
    baseline_keys = {
        make_key(item["type"], item["old"], item["new"]) for item in build_items()
    }
    baseline_missing = expected - baseline_keys

    monkeypatch.setattr("compare.MIN_SIMILARITY", 0.95)
    stricter_keys = {
        make_key(item["type"], item["old"], item["new"]) for item in build_items()
    }
    stricter_missing = expected - stricter_keys

    assert stricter_missing > baseline_missing, (
        f"门槛升到 0.95 后应漏掉更多人工标注的修改；"
        f"原门槛漏报 {sorted(baseline_missing)!r}，"
        f"提高后漏报 {sorted(stricter_missing)!r}"
    )

