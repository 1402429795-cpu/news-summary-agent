import subprocess
import json
from datetime import datetime
from config.settings import FEISHU_BASE_TOKEN, FEISHU_TABLE_ID
from scrapers.base import Article

FIELDS = ["标题", "来源", "原文链接", "摘要", "关键词", "分类", "抓取日期"]

VALID_CATEGORIES = ["AI/大模型", "芯片/硬件", "互联网/平台", "出海/国际", "消费电子", "政策/监管", "其他"]


def _normalize_category(cat: str) -> str:
    for valid in VALID_CATEGORIES:
        if valid in cat or cat in valid:
            return valid
    return "其他"


def save_articles(articles: list[Article]) -> int:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for article in articles:
        rows.append([
            article.title,
            article.source,
            article.url,
            article.summary,
            " / ".join(article.keywords) if article.keywords else "",
            _normalize_category(article.category),
            now_str,
        ])

    # batch create 每次最多 200 条
    saved = 0
    for i in range(0, len(rows), 200):
        batch = rows[i:i + 200]
        payload = json.dumps({"fields": FIELDS, "rows": batch}, ensure_ascii=False)
        cmd = [
            "lark-cli", "base", "+record-batch-create",
            "--base-token", FEISHU_BASE_TOKEN,
            "--table-id", FEISHU_TABLE_ID,
            "--json", payload,
            "--format", "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            saved += len(data.get("data", {}).get("record_id_list", []))
        else:
            print(f"[bitable] 写入失败: {result.stderr}")

    return saved
