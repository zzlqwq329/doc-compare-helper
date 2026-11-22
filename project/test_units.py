"""测的是 compare.py 的函数、也从 reader.py 导入了 Block，这里的 Block 是一条正文记录的数据格式。"""

from compare import compare_versions, group_by_text, unique_best_candidate
from reader import Block


def _make_block(version_id: str, ordinal: int, raw_text: str) -> Block:
    return Block(
        version_id=version_id,
        block_id=f"{version_id}-P{ordinal:03d}",
        section="报销与审批",
        line_start=ordinal,
        line_end=ordinal,
        raw_text=raw_text,
    )


# 只有一个候选的测试，覆盖不到函数在有多个候选时，函数如果总选第一项会漏掉了分数更高的那项
def test_unique_best_candidate_returns_only_candidate() -> None:
    actual = unique_best_candidate([("V2-P001", 0.75)])
    # 逗号后的提示信息仅在断言失败时求值并输出
    assert actual == "V2-P001", f"唯一候选应为 V2-P001，实际为 {actual!r}"


# 这条测试「选中唯一最高分」
def test_unique_best_candidate_selects_highest_score() -> None:
    candidates = [("V2-P001", 0.70), ("V2-P002", 0.90), ("V2-P003", 0.80)]

    actual = unique_best_candidate(candidates)

    assert actual == "V2-P002", f"最高分候选应为 V2-P002，实际为 {actual!r}"


# 测最高分并列的情况。它要防的是：最高分不唯一时，函数本该返回 None，却任意选中了一个候选。
def test_unique_best_candidate_rejects_tied_highest_scores() -> None:
    candidates = [("V2-P001", 0.90), ("V2-P002", 0.70), ("V2-P003", 0.90)]

    actual = unique_best_candidate(candidates)

    assert actual is None, f"最高分并列时应返回 None，实际为 {actual!r}"


# 测候选名单是空的。它要防的错是：没有候选时，函数还去找最高分，结果直接报错。
def test_unique_best_candidate_returns_none_for_empty_input() -> None:
    actual = unique_best_candidate([])

    assert actual is None, f"候选为空时应返回 None，实际为 {actual!r}"


# 两段文字一模一样，就应该放进同一组，而且两段都要保留。这条测试要防的是：放入第二段时，把第一段盖掉了
def test_group_by_text_preserves_blocks_with_the_same_text() -> None:
    first = _make_block("V1", 1, "报销申请须经审批。")
    different = _make_block("V1", 2, "报销申请须附凭证。")
    duplicate = _make_block("V1", 3, first["raw_text"])
    expected = {
        first["raw_text"]: [first, duplicate],
        different["raw_text"]: [different],
    }

    actual = group_by_text([first, different, duplicate])

    assert actual == expected, f"按正文分组应为 {expected!r}，实际为 {actual!r}"


# 收到空名单时会怎样。它要防的是：一段正文都没有，函数却凭空造出了一个分组
def test_group_by_text_returns_empty_groups_for_empty_input() -> None:
    actual = group_by_text([])

    assert actual == {}, f"正文列表为空时应返回空字典，实际为 {actual!r}"


# 怎么给新旧段落配对。它要防的是：同一条新版段落被认成两条旧版段落各自修改后的结果。
def test_compare_versions_requires_reciprocal_best_candidate() -> None:
    old_a = _make_block("V1", 1, "报销申请需附机票和酒店发票。")
    new_b = _make_block("V2", 1, "报销申请需附车票和酒店收据。")
    old_c = _make_block("V1", 2, "报销申请需附车票和酒店发票。")

    # A 和 C 都能选中 B，但 B 给 C 的分数更高。
    items = compare_versions([old_a, old_c], [new_b])
    actual = [
        (item["old"]["block_id"], item["new"]["block_id"])
        for item in items
        if item["type"] == "modified"
    ]
    expected = [(old_c["block_id"], new_b["block_id"])]

    assert actual == expected, f"只应确认互选配对 {expected!r}，实际为 {actual!r}"

