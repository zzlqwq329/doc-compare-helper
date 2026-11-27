import json
from collections import Counter
from pathlib import Path


def render_report(items: list[dict]) -> str:
    """把对比条目渲染成 Markdown 文本，不碰磁盘。"""
    type_labels = {
        "modified": "修改",
        "moved": "移动",
        "deleted": "删除",
        "added": "新增",
        "needs_review": "待核对",
    }
    changes = [item for item in items if item["type"] != "unchanged"]
    counts = Counter(item["type"] for item in changes)
    overview = "、".join(
        f"{label} {counts[item_type]}"
        for item_type, label in type_labels.items()
        if item_type != "needs_review" or counts[item_type] > 0
    )
    report = f"# 文档对比证据报告\n\n共识别 {len(changes)} 处变化：{overview}。"

    sections: list[str] = []
    for number, item in enumerate(changes, start=1):
        old = item["old"]
        new = item["new"]
        old_id = "无" if old is None else old["block_id"]
        new_id = "无" if new is None else new["block_id"]
        label = type_labels[item["type"]]
        parts = [f"## {number}. {label} · {old_id} → {new_id}"]

        for side, block in (("旧版", old), ("新版", new)):
            if block is None:
                continue
            location = (
                f"**{side}**：{block['version_id']} · {block['section']}"
                f" · 第 {block['line_start']} 行"
            )
            # 每行都加引用符，让断行后的原文也留在引用里。
            original_lines = block["raw_text"].splitlines() or [""]
            quote = "\n".join(f"> {line}" for line in original_lines)
            parts.append(f"{location}\n{quote}")

        sections.append("\n\n".join(parts))

    if sections:
        report += "\n\n" + "\n\n---\n\n".join(sections)
    return report + "\n"


def main() -> None:
    """读对比结果，生成并写入 Markdown 证据报告。"""
    root = Path(__file__).resolve().parents[1]
    input_path = root / "outputs" / "comparison.json"
    output_path = root / "outputs" / "comparison-report.md"

    items = json.loads(input_path.read_text(encoding="utf-8"))["items"]
    output_path.write_text(render_report(items), encoding="utf-8", newline="\n")
    print("Generated outputs/comparison-report.md")


if __name__ == "__main__":
    main()
