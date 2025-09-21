from typing import List, Optional
from datetime import datetime
from .article_repository import ArticleRepository
from .article_entity import Article, Category

class InMemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._items: List[Article] = [
            Article(id="1", title="Local Derby Highlights",
                    summary="Home team wins the derby", source="SportsNet",
                    published_at=datetime(2025, 9, 20, 20, 30), category=Category.sports),
            Article(id="2", title="Market Rally",
                    summary="Stocks surge as rates expected to fall", source="BizWire",
                    published_at=datetime(2025, 9, 19, 15, 30), category=Category.economy),
            Article(id="3", title="Election Debate",
                    summary="Key moments from last night's debate", source="PoliToday",
                    published_at=datetime(2025, 9, 18, 21, 0), category=Category.politics),
            Article(id="4", title="Championship Preview",
                    summary="What to expect in the finals", source="SportsNet",
                    published_at=datetime(2025, 9, 21, 9, 0), category=Category.sports),
        ]

    def _sort(self, items: List[Article]) -> List[Article]:
        return sorted(items, key=lambda a: a.published_at, reverse=True)

    def top(self, limit: int = 20, category: Optional[str] = None) -> List[Article]:
        items = self._items
        if category:
            items = [a for a in items if a.category.value == category]
        return self._sort(items)[:limit]

    def search(self, query: str, limit: int = 20, category: Optional[str] = None) -> List[Article]:
        q = query.lower()
        items = [a for a in self._items if q in a.title.lower()
                 or q in a.summary.lower() or q in a.source.lower()]
        if category:
            items = [a for a in items if a.category.value == category]
        return self._sort(items)[:limit]

    def get(self, article_id: str) -> Optional[Article]:
        return next((a for a in self._items if a.id == article_id), None)
