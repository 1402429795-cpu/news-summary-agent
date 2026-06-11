import os
from openai import OpenAI
from scrapers.base import Article

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)


def summarize(articles: list[Article]) -> list[Article]:
    for article in articles:
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"请根据以下科技新闻标题，生成一段2-3句话的中文摘要，并提取3-5个关键词。\n\n"
                            f"标题：{article.title}\n来源：{article.source}\n\n"
                            f"请按以下格式回复：\n摘要：xxx\n关键词：词1,词2,词3"
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
            keywords_raw = lines.get("关键词", "")
            article.keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        except Exception as e:
            print(f"[summarizer] 摘要生成失败 {article.title}: {e}")
    return articles
