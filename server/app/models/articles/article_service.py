from typing import List, Optional
from .article_repository import ArticleRepository
from .article_entity import Article

class NewsService:
    def __init__(self, repo: ArticleRepository) -> None:
        self._repo = repo

    def top(self, limit: int = 20) -> List[Article]:
        return self._repo.top(limit)

    def search(self, query: str, limit: int = 20) -> List[Article]:
        return self._repo.search(query, limit)

    def get(self, article_id: str) -> Optional[Article]:
        return self._repo.get(article_id)
