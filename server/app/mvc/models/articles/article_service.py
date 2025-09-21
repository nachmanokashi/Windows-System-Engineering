from typing import List, Optional
from .article_repository import ArticleRepository
from .article_entity import Article, Category

class NewsService:
    def __init__(self, repo: ArticleRepository) -> None:
        self._repo = repo

    def categories(self) -> List[str]:
        return [c.value for c in Category]

    def top(self, limit: int = 20, category: Optional[str] = None) -> List[Article]:
        return self._repo.top(limit, category)

    def search(self, query: str, limit: int = 20, category: Optional[str] = None) -> List[Article]:
        return self._repo.search(query, limit, category)

    def get(self, article_id: str) -> Optional[Article]:
        return self._repo.get(article_id)
