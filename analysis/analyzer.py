import subprocess
import json
from collections import Counter
from datetime import date
from config.settings import FEISHU_BASE_TOKEN, FEISHU_TABLE_ID, FEISHU_CHAT_ID


def _fetch_today_records(date_str: str) -> list[dict]:
    cmd = [
        "lark-cli", "base", "+record-list",
        "--base-token", FEISHU_BASE_TOKEN,
        "--table-id", FEISHU_TABLE_ID,
        "--field-id", "分类", "--field-id", "关键词", "--field-id", "来源",
        "--filter-json", json.dumps({
            "logic": "and",
            "conditions": [["抓取日期", "==", f"ExactDate({date_str})"]]
        }),
        "--format", "json",
        "--limit", "200",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[analyzer] 查询失败: {result.stderr}")
        return []

    data = json.loads(result.stdout)
    fields = data.get("data", {}).get("fields", [])
    rows = data.get("data", {}).get("data", [])

    records = []
    for row in rows:
        record = dict(zip(fields, row))
        records.append(record)
    return records


def _parse_keywords(raw: str) -> list[str]:
    if not raw:
        return []
    for sep in [" / ", " · ", ",", "，", "、"]:
        raw = raw.replace(sep, "|")
    return [k.strip() for k in raw.split("|") if k.strip()]


def analyze(date_str: str | None = None) -> dict:
    date_str = date_str or date.today().strftime("%Y-%m-%d")
    records = _fetch_today_records(date_str)

    if not records:
        return {"date": date_str, "total": 0}

    # 分类统计
    category_counter = Counter()
    keyword_counter = Counter()
    source_counter = Counter()

    for r in records:
        cat = r.get("分类")
        if cat:
            # 来自 select 字段，值是列表
            if isinstance(cat, list):
                cat = cat[0] if cat else None
            if cat:
                category_counter[cat] += 1

        kw_raw = r.get("关键词", "") or ""
        for kw in _parse_keywords(kw_raw):
            keyword_counter[kw] += 1

        src = r.get("来源")
        if isinstance(src, list):
            src = src[0] if src else None
        if src:
            source_counter[src] += 1

    top_keywords = [kw for kw, _ in keyword_counter.most_common(8)]
    top_category = category_counter.most_common(1)[0] if category_counter else ("未知", 0)

    return {
        "date": date_str,
        "total": len(records),
        "category_dist": dict(category_counter.most_common()),
        "top_keywords": top_keywords,
        "source_dist": dict(source_counter),
        "top_category": top_category,
    }
