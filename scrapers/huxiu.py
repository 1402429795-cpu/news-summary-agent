import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from email.utils import parsedate_to_datetime
from .base import Article

RSS_URL = "https://www.ithome.com/rss/"


def _extract_body(entry) -> str:
    html = entry.get("summary", "") or entry.get("description", "")
    if not html:
        return ""
    text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
    return text[:2000]


def fetch(max_articles: int = 10) -> list[Article]:
    feed = feedparser.parse(RSS_URL)
    articles = []

    # 取第二批，避免与 kr36.py 重复
    for entry in feed.entries[max_articles:max_articles * 2]:
        published_at = None
        if hasattr(entry, "published"):
            try:
                published_at = parsedate_to_datetime(entry.published)
            except Exception:
                pass

        articles.append(Article(
            title=entry.title,
            url=entry.link,
            source="虎嗅",
            published_at=published_at,
            body=_extract_body(entry),
        ))

    return articles
