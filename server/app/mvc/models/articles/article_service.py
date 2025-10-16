# server/app/mvc/models/articles/article_service.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.mvc.models.articles.article_repository import ArticleRepository
from app.mvc.models.articles.article_entity import Article

class ArticleService:
    def __init__(self, db: Session):
        self.repo = ArticleRepository(db)

    def create(self, data: dict) -> Article:
        # Convert Pydantic Url to string
        if 'url' in data and data['url'] is not None:
            data['url'] = str(data['url'])
        
        # Convert datetime if needed
        if 'published_at' in data and data['published_at'] is not None:
            if hasattr(data['published_at'], 'isoformat'):
                data['published_at'] = data['published_at']
            elif isinstance(data['published_at'], str):
                from datetime import datetime
                data['published_at'] = datetime.fromisoformat(data['published_at'])
        
        return self.repo.create(data)

    def get(self, article_id: int) -> Optional[Article]:
        return self.repo.get(article_id)

    def list(self, category: Optional[str], page: int, page_size: int) -> Tuple[List[Article], int]:
        return self.repo.list(category, page, page_size)

    def search(self, q: str, category: Optional[str]) -> List[Article]:
        return self.repo.search(q, category)