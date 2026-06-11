import subprocess
import json
from config.settings import FEISHU_CHAT_ID
from scrapers.base import Article


def send_daily_summary(articles: list[Article], date_str: str) -> bool:
    if not FEISHU_CHAT_ID:
        print("[messenger] 未配置 FEISHU_CHAT_ID，跳过消息发送")
        return False

    lines = [f"📰 **{date_str} 科技资讯日报**\n共抓取 {len(articles)} 条资讯\n"]
    for i, a in enumerate(articles, 1):
        lines.append(f"**{i}. [{a.source}] {a.title}**")
        if a.summary:
            lines.append(f"　{a.summary}")
        if a.keywords:
            lines.append(f"　🏷 {' · '.join(a.keywords)}")
        lines.append(f"　🔗 {a.url}\n")

    content = "\n".join(lines)

    cmd = [
        "lark-cli", "im", "+messages-send",
        "--chat-id", FEISHU_CHAT_ID,
        "--text", content,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("[messenger] 消息发送成功")
        return True
    else:
        print(f"[messenger] 消息发送失败: {result.stderr}")
        return False
