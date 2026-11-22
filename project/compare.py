import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Final

MIN_SIMILARITY: Final = 0.60

#把同一版里原文相同的段落归到一起
def group_by_text(blocks):
    groups = {}
    for block in blocks:
        text = block["raw_text"]
        if text not in groups:
            groups[text] = []
        #让第二次出现的相同原文直接找到对应的键进列表，而不是再次新建列表
        # 同一句话只占一个键，这个键对应的列表里可以有多条段落记录
        groups[text].append(block)
    return groups


def unique_best_candidate(candidates: list[tuple[str, float]]) -> str | None:
    """只有当候选人得分最高且唯一时才返回候选人ID。"""
    best_score = max((score for _, score in candidates), default=0.0)
    best_ids = [block_id for block_id, score in candidates if score == best_score]
    return best_ids[0] if len(best_ids) == 1 else None
    #len(best_ids) == 1满足唯一，执行best_ids[0]找出候选人，否则返回None


def compare_versions(v1_blocks, v2_blocks):
    v1_groups = group_by_text(v1_blocks)
    v2_groups = group_by_text(v2_blocks)

    pairs = []
    matched_v1_ids = set()
    matched_v2_ids = set()
    unchanged_count = 0
    moved_count = 0

    # old_matches和new_matches是两版里说了同一句话的记录列表
    for text, old_matches in v1_groups.items():
        new_matches = v2_groups.get(text, [])
        # 两边都只有一条时才可配对，程序比较它们的章节
        if len(old_matches) != 1 or len(new_matches) != 1:
            continue

        old_block = old_matches[0]
        new_block = new_matches[0]

        if old_block["section"] == new_block["section"]:
            status = "未变"
            unchanged_count += 1
        else:
            status = "移动"
            moved_count += 1

        # 配对结果放进pairs，两端的编号也各自加入已配对集合
        pairs.append((status, old_block, new_block))
        matched_v1_ids.add(old_block["block_id"])
        matched_v2_ids.add(new_block["block_id"])

    # 给剩余段落找候选
    unmatched_v1 = [
        block for block in v1_blocks if block["block_id"] not in matched_v1_ids
    ]
    unmatched_v2 = [
        block for block in v2_blocks if block["block_id"] not in matched_v2_ids
    ]

    candidates_by_old: dict[str, list[tuple[str, float]]] = {}
    candidates_by_new: dict[str, list[tuple[str, float]]] = {}
    print("----------候选分数-----------")
    for old_block in unmatched_v1:
        # 处理前一轮因为原文重复而没能配上的段落
        old_text = old_block["raw_text"]
        if old_text in v2_groups:
            continue #会发现新版确实有这句原文，于是跳过打分，留给「待核对」

        #新版没有一字不差的原文的情况
        old_id = old_block["block_id"]

        for new_block in unmatched_v2:
            if old_block["section"] != new_block["section"]:
                continue

            #取出新版段落的原文，检查这句话在旧版里有没有出现过
            new_text = new_block["raw_text"]
            if new_text in v1_groups:
                continue  #出现就跳过

            #打分
            score = SequenceMatcher(None, old_text, new_text).ratio()
            if score < MIN_SIMILARITY:
                continue

            # 取出新版段落的编号，把它和分数放进当前旧段落的候选列表
            new_id = new_block["block_id"]
            #用旧编号找到候选列表。如果初次遇到这个旧编号，就先建一个空列表，再把这次找到的候选加进列表里
            candidates_by_old.setdefault(old_id, []).append((new_id, score))
            #把同一对候选按反方向记下来，方便以后从新版段落查回旧版候选
            candidates_by_new.setdefault(new_id, []).append((old_id, score))
            print(f"{old_id} → {new_id}：{score:.2f}")

    #元组按顺序放旧段落编号、新段落编号
    modified_pairs: list[tuple[str, str]] = []
    #逐个旧段落检查候选。old_id 拿到字典的键，`candidates` 拿到这个键对应的值且拿到的是整个列表
    for old_id, candidates in candidates_by_old.items():
        # 检查旧段落有没有选出唯一的第一名（新版候选）
        new_id = unique_best_candidate(candidates)
        #candidates_by_new[new_id]取出来的是列表内嵌元组
        # unique_best_candidate(candidates_by_new[new_id])新版段落反过来选中的编号若与旧编号一样，则判定修改
        if new_id is None or unique_best_candidate(candidates_by_new[new_id]) != old_id:
            continue

        #算进已匹配
        matched_v1_ids.add(old_id)
        matched_v2_ids.add(new_id)
        modified_pairs.append((old_id, new_id))

    print("----------确认修改-----------")
    for old_id, new_id in modified_pairs:
        print(f"修改 {old_id} → {new_id}")

    # 从旧版的未匹配列表里筛掉刚刚确认修改的段落
    unmatched_v1 = [
        block for block in unmatched_v1 if block["block_id"] not in matched_v1_ids
    ]
    unmatched_v2 = [
        block for block in unmatched_v2 if block["block_id"] not in matched_v2_ids
    ]

    deleted_blocks = [] #「删除」
    added_blocks = []#「新增」
    review_v1_blocks = []#旧版「待核对」
    review_v2_blocks = []#新版「待核对」

    # 处理V1剩下的段落
    for block in unmatched_v1:
        if block["raw_text"] in v2_groups or block["block_id"] in candidates_by_old:
            review_v1_blocks.append(block)
            #两版都有重复原文，或原本有达标候选却没配上，都留为待核对
        else:
            deleted_blocks.append(block)

    # 处理V2剩下的段落
    for block in unmatched_v2:
        if block["raw_text"] in v1_groups or block["block_id"] in candidates_by_new:
            review_v2_blocks.append(block)
        else:
            added_blocks.append(block)
    #两份「待核对」列表接起来，方便后面统计总数
    review_blocks = review_v1_blocks + review_v2_blocks

    print("----------判断章节是否移动-----------")
    for status, old_block, new_block in pairs:
        message = f"{status} {old_block['block_id']} → {new_block['block_id']}"

        if status == "移动":
            old_section = old_block["section"]
            new_section = new_block["section"]
            message += f"（{old_section} → {new_section}）"

        print(message)

    print(f"\n未变 {unchanged_count} 对，移动 {moved_count} 对，修改 {len(modified_pairs)} 对")
    print(f"删除 {len(deleted_blocks)} 段，新增 {len(added_blocks)} 段，待核对 {len(review_blocks)} 段")

    print("\n----------剩余段落分类-----------")
    for status, blocks in (("删除", deleted_blocks), ("新增", added_blocks), ("待核对", review_blocks)):
        for block in blocks:
            print(f"{status} {block['block_id']}")

    type_by_status = {"未变": "unchanged", "移动": "moved"}
    items = []
    for status, old_block, new_block in pairs:
        items.append({"type": type_by_status[status], "old": old_block, "new": new_block})

    # 修改配对只存了编号，建字典是为了按编号找回两端的完整记录。
    old_by_id = {block["block_id"]: block for block in v1_blocks}
    new_by_id = {block["block_id"]: block for block in v2_blocks}
    for old_id, new_id in modified_pairs:
        items.append({"type": "modified", "old": old_by_id[old_id], "new": new_by_id[new_id]})

    for block in deleted_blocks:
        items.append({"type": "deleted", "old": block, "new": None})
    for block in added_blocks:
        items.append({"type": "added", "old": None, "new": block})
    for block in review_v1_blocks:
        items.append({"type": "needs_review", "old": block, "new": None})
    for block in review_v2_blocks:
        items.append({"type": "needs_review", "old": None, "new": block})

    return items


def main():
    root = Path(__file__).resolve().parents[1]
    v1_path = root / "outputs" / "blocks-v1.json"
    v2_path = root / "outputs" / "blocks-v2.json"

    v1_text = v1_path.read_text(encoding="utf-8")
    v2_text = v2_path.read_text(encoding="utf-8")
    #把 JSON 字符串转回段落列表
    v1_blocks = json.loads(v1_text)
    v2_blocks = json.loads(v2_text)
    print(f"读入 V1正文：{len(v1_blocks)} 段，V2正文：{len(v2_blocks)} 段")

    items = compare_versions(v1_blocks, v2_blocks)

    output_path = root / "outputs" / "comparison.json"
    output_text = json.dumps({"items": items}, ensure_ascii=False, indent=2)
    output_path.write_text(output_text + "\n", encoding="utf-8")
    print("\n已保存 outputs/comparison.json")


if __name__ == "__main__":
    main()
