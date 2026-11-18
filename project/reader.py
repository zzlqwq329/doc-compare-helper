
"""读取样本 Markdown，保留正文在原文件中的位置。"""

from __future__ import annotations

import json
import sys
from io import TextIOWrapper
from pathlib import Path
from typing import TypedDict


class Block(TypedDict):
    """单行正文及其在文档版本中的定位。"""

    version_id: str
    block_id: str
    section: str
    line_start: int
    line_end: int
    raw_text: str


def read_lines(path: Path) -> list[str]:
    """按原顺序读取 UTF-8 文本，仅去掉各行的换行符。"""
    with path.open(encoding="utf-8") as source:
        return [line.removesuffix("\n") for line in source]


def parse_blocks(path: Path, version_id: str) -> list[Block]:
    """从指定版本的 Markdown 中提取正文记录。"""
    blocks: list[Block] = []
    section = ""

    for line_number, line in enumerate(read_lines(path), start=1):
        if line.startswith("## "):
            section = line.removeprefix("## ").strip()
            continue
        if line.startswith("# ") or not line.strip():
            continue

        block_number = len(blocks) + 1
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

    return blocks


def main() -> None:
    """打印 V1 原始行并导出两个版本的正文记录。"""
    if isinstance(sys.stdout, TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    root = Path(__file__).resolve().parents[1]
    v1_path = root / "samples" / "expense-v1.md"
    v2_path = root / "samples" / "expense-v2.md"

    for line_number, line in enumerate(read_lines(v1_path), start=1):
        print(f"{line_number}: {line}")

    records_by_filename = {
        "blocks-v1.json": parse_blocks(v1_path, "V1"),
        "blocks-v2.json": parse_blocks(v2_path, "V2"),
    }
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)
    for filename, records in records_by_filename.items():
        json_text = json.dumps(records, ensure_ascii=False, indent=2)
        (output_dir / filename).write_text(json_text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    #输出原始V1
    #两个json文件是最终稿交付
