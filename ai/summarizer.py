import os
from openai import OpenAI
from scrapers.base import Article

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)

CATEGORIES = "AI/大模型、芯片/硬件、互联网/平台、出海/国际、消费电子、政策/监管、其他"

PROMPT_TEMPLATE = """\
请根据以下科技新闻的标题和正文，完成三项任务：
1. 用2-3句话提炼核心观点（不是复述，要有分析）
2. 提取3-5个关键词
3. 从以下类别中选一个最匹配的分类：{categories}

标题：{title}
正文：{body}

请严格按以下格式回复，每项占一行：
摘要：xxx
关键词：词1,词2,词3
分类：xxx"""


def summarize(articles: list[Article]) -> list[Article]:
    for article in articles:
        try:
            content = article.body if article.body else article.title
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=400,
                messages=[
                    {
                        "role": "user",
                        "content": PROMPT_TEMPLATE.format(
                            categories=CATEGORIES,
                            title=article.title,
                            body=content,
                        ),
                    }
                ],
            )
            text = response.choices[0].message.content.strip()
            lines = {
                line.split("：", 1)[0]: line.split("：", 1)[1]
                for line in text.splitlines()
                if "：" in line
            }
            article.summary = lines.get("摘要", "").strip()
            article.category = lines.get("分类", "其他").strip()
            keywords_raw = lines.get("关键词", "")
            article.keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        except Exception as e:
            print(f"[summarizer] 处理失败 {article.title}: {e}")
    return articles
