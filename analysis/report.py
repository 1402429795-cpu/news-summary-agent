import subprocess
import json
from config.settings import FEISHU_CHAT_ID


def _bar(count: int, total: int, width: int = 10) -> str:
    filled = round(count / total * width) if total else 0
    return "█" * filled + "░" * (width - filled)


def send_analysis_card(result: dict) -> bool:
    if not FEISHU_CHAT_ID or result.get("total", 0) == 0:
        print("[report] 无数据或未配置 CHAT_ID，跳过")
        return False

    date_str = result["date"]
    total = result["total"]
    category_dist = result.get("category_dist", {})
    top_keywords = result.get("top_keywords", [])
    source_dist = result.get("source_dist", {})
    top_cat_name, top_cat_count = result.get("top_category", ("—", 0))

    # 分类分布区块
    cat_lines = []
    for cat, count in category_dist.items():
        pct = round(count / total * 100)
        cat_lines.append(f"{cat}  {_bar(count, total)}  {count} 条  {pct}%")
    cat_block = "\n".join(cat_lines) if cat_lines else "暂无分类数据"

    # 来源分布
    src_parts = []
    for src, count in source_dist.items():
        src_parts.append(f"{src} {count} 条")
    src_line = "  ·  ".join(src_parts) if src_parts else "—"

    # 高频关键词
    kw_line = "  ·  ".join(top_keywords) if top_keywords else "—"

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"今日收录 **{total}** 条资讯，来自 {src_line}"
            }
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": "**领域分布**"}
        },
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"```\n{cat_block}\n```"}
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": "**今日高频关键词**"}
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"<font color='grey'>{kw_line}</font>"
            }
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**今日最热领域**  {top_cat_name}，共 {top_cat_count} 条"
            }
        },
        {"tag": "hr"},
        {
            "tag": "note",
            "elements": [{"tag": "plain_text", "content": "数据来源：飞书多维表格  ·  由 每日速递 机器人自动分析"}]
        }
    ]

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "今日资讯分析"},
            "subtitle": {"tag": "plain_text", "content": date_str},
            "template": "indigo"
        },
        "elements": elements
    }

    cmd = [
        "lark-cli", "im", "+messages-send",
        "--chat-id", FEISHU_CHAT_ID,
        "--msg-type", "interactive",
        "--content", json.dumps(card, ensure_ascii=False),
    ]
    result_proc = subprocess.run(cmd, capture_output=True, text=True)
    if result_proc.returncode == 0:
        print("[report] 分析报告发送成功")
        return True
    else:
        print(f"[report] 分析报告发送失败: {result_proc.stderr}")
        return False
