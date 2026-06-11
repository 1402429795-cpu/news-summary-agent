from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    title: str
    url: str
    source: str
    published_at: datetime | None = None
    summary: str = ""
    keywords: list[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
