import subprocess
import json
from collections import defaultdict
from datetime import date
from config.settings import FEISHU_CHAT_ID
from scrapers.base import Article

CATEGORY_ORDER = ["AI/大模型", "芯片/硬件", "互联网/平台", "出海/国际", "消费电子", "政策/监管", "其他"]


def _article_element(article: Article) -> dict:
    keywords = "  ·  ".join(article.keywords) if article.keywords else ""
    content = f"**[{article.title}]({article.url})**\n{article.summary}"
    if keywords:
        content += f"\n<font color='grey'>{keywords}</font>"
    return {"tag": "div", "text": {"tag": "lark_md", "content": content}}


def _build_card(articles: list[Article], date_str: str) -> dict:
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.category or "其他"].append(a)

    active_categories = [c for c in CATEGORY_ORDER if c in grouped]
    subtitle = f"{date_str}  ·  {len(articles)} 条  ·  {len(active_categories)} 个领域"

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"<font color='grey'>今日共收录资讯 {len(articles)} 条，{active_categories[0] if active_categories else ''}领域最活跃</font>"
            }
        },
        {"tag": "hr"},
    ]

    for cat in active_categories:
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**{cat}**"}
        })
        for article in grouped[cat]:
            elements.append(_article_element(article))
        elements.append({"tag": "hr"})

    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "由 每日速递 机器人自动生成"}]
    })

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "科技资讯日报"},
            "subtitle": {"tag": "plain_text", "content": subtitle},
            "template": "indigo"
        },
        "elements": elements
    }


def send_daily_summary(articles: list[Article], date_str: str) -> bool:
    if not FEISHU_CHAT_ID:
        print("[messenger] 未配置 FEISHU_CHAT_ID，跳过消息发送")
        return False

    card = _build_card(articles, date_str)
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--chat-id", FEISHU_CHAT_ID,
        "--msg-type", "interactive",
        "--content", json.dumps(card, ensure_ascii=False),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("[messenger] 消息发送成功")
        return True
    else:
        print(f"[messenger] 消息发送失败: {result.stderr}")
        return False
