import re
from pathlib import Path

import pytest

from compare import compare_versions
from reader import parse_blocks
from report import render_report


@pytest.fixture(scope="module")
def rendered_report() -> str:
    """从两份样本现算对比结果，再渲染成报告。"""
    root = Path(__file__).resolve().parents[1]
    old_blocks = parse_blocks(root / "samples" / "expense-v1.md", "V1")
    new_blocks = parse_blocks(root / "samples" / "expense-v2.md", "V2")
    return render_report(compare_versions(old_blocks, new_blocks))


def _change_sections(report: str) -> list[str]:
    """用二级标题划分条目，便于在同一条目内核对两版证据。"""
    return re.split(r"(?m)(?=^## )", report)[1:]


def test_report_has_ten_change_entries(rendered_report: str) -> None:
    headings = [
        part.splitlines()[0] for part in _change_sections(rendered_report)
    ]

    assert len(headings) == 10, (
        f"预期 10 个二级标题，实际有 {len(headings)} 个：{headings!r}"
    )


def test_report_has_expected_change_types(rendered_report: str) -> None:
    headings = [
        part.splitlines()[0] for part in _change_sections(rendered_report)
    ]
    expected = {"修改": 6, "移动": 1, "删除": 1, "新增": 2}
    actual = {
        kind: sum(kind in heading for heading in headings) for kind in expected
    }

    assert actual == expected, (
        f"预期类型分布 {expected!r}，实际 {actual!r}，标题为 {headings!r}"
    )
    unchanged_lines = [
        line for line in rendered_report.splitlines() if "未变" in line
    ]
    assert not unchanged_lines, f"预期报告省略未变，实际出现 {unchanged_lines!r}"


def test_report_has_expected_evidence_totals(rendered_report: str) -> None:
    old_count = rendered_report.count("**旧版**")
    new_count = rendered_report.count("**新版**")
    actual = (old_count, new_count, old_count + new_count)

    assert actual == (8, 9, 17), f"预期旧版 8、新版 9、合计 17，实际为 {actual!r}"


def test_report_keeps_deadline_evidence_on_correct_version(
    rendered_report: str,
) -> None:
    evidence_pairs: list[tuple[str, str]] = []
    for section in _change_sections(rendered_report):
        if "修改" not in section.splitlines()[0]:
            continue
        parts = re.split(r"\*\*(旧版|新版)\*\*", section)
        evidence = dict(zip(parts[1::2], parts[2::2], strict=True))
        evidence_pairs.append((evidence.get("旧版", ""), evidence.get("新版", "")))

    assert any(
        "第 11 行" in old
        and "10个工作日" in old
        and "第 13 行" in new
        and "5个工作日" in new
        for old, new in evidence_pairs
    ), (
        f"预期同一条修改的旧版证据是第 11 行和 10个工作日，"
        f"新版证据是第 13 行和 5个工作日，实际修改条目证据为 {evidence_pairs!r}"
    )
