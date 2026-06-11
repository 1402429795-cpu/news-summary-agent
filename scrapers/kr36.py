import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime
from .base import Article

RSS_URL = "https://www.ithome.com/rss/"


def fetch(max_articles: int = 10) -> list[Article]:
    feed = feedparser.parse(RSS_URL)
    articles = []

    for entry in feed.entries[:max_articles]:
        published_at = None
        if hasattr(entry, "published"):
            try:
                published_at = parsedate_to_datetime(entry.published)
            except Exception:
                pass

        articles.append(Article(
            title=entry.title,
            url=entry.link,
            source="36氪",
            published_at=published_at,
        ))

    return articles
