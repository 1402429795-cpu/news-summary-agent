import subprocess
from collections import defaultdict
from config.settings import FEISHU_CHAT_ID
from scrapers.base import Article

CATEGORY_ORDER = ["AI/大模型", "芯片/硬件", "互联网/平台", "出海/国际", "消费电子", "政策/监管", "其他"]


def send_daily_summary(articles: list[Article], date_str: str) -> bool:
    if not FEISHU_CHAT_ID:
        print("[messenger] 未配置 FEISHU_CHAT_ID，跳过消息发送")
        return False

    # 按分类分组
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.category or "其他"].append(a)

    lines = [f"📰 {date_str} 科技资讯日报  共 {len(articles)} 条\n"]

    for cat in CATEGORY_ORDER:
        if cat not in grouped:
            continue
        lines.append(f"【{cat}】")
        for a in grouped[cat]:
            lines.append(f"▸ {a.title}")
            if a.summary:
                lines.append(f"  {a.summary}")
            if a.keywords:
                lines.append(f"  # {' · '.join(a.keywords)}")
            lines.append(f"  {a.url}")
        lines.append("")

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
