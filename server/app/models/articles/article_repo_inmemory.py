from typing import List, Optional
from datetime import datetime
from .article_repository import ArticleRepository
from .article_entity import Article

class InMemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._items: List[Article] = [
            Article(id="1", title="Local Update",
                    summary="Short local summary", source="Local",
                    published_at=datetime(2025, 9, 20, 8, 0, 0)),
            Article(id="2", title="Tech News",
                    summary="New gadget released", source="TechWire",
                    published_at=datetime(2025, 9, 19, 15, 30, 0)),
            Article(id="3", title="Sports Highlights",
                    summary="Team wins the cup", source="SportsNet",
                    published_at=datetime(2025, 9, 18, 21, 0, 0)),
        ]

    def top(self, limit: int = 20) -> List[Article]:
        return sorted(self._items, key=lambda a: a.published_at, reverse=True)[:limit]

    def search(self, query: str, limit: int = 20) -> List[Article]:
        q = query.lower()
        res = [a for a in self._items
               if q in a.title.lower() or q in a.summary.lower() or q in a.source.lower()]
        return sorted(res, key=lambda a: a.published_at, reverse=True)[:limit]

    def get(self, article_id: str) -> Optional[Article]:
        return next((a for a in self._items if a.id == article_id), None)
