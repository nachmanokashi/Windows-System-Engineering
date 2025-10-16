# server/app/mvc/models/articles/article_repository.py
from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.mvc.models.articles.article_entity import Article

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Article:
        row = Article(**data)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get(self, article_id: int) -> Optional[Article]:
        return self.db.query(Article).filter(Article.id == article_id).first()

    def list(self, category: Optional[str], page: int, page_size: int) -> Tuple[List[Article], int]:
        query = self.db.query(Article)
        
        if category:
            query = query.filter(Article.category == category)

        total = query.count()
        
        # MSSQL sorting
        query = query.order_by(desc(Article.created_at))
        offset = (page - 1) * page_size
        articles = query.offset(offset).limit(page_size).all()
        
        return articles, total

    def search(self, q: str, category: Optional[str]) -> List[Article]:
        query = self.db.query(Article)
        q_like = f"%{q}%"
        search_filter = or_(
            Article.title.like(q_like),
            Article.summary.like(q_like),
            Article.source.like(q_like),
        )
        query = query.filter(search_filter)
        if category:
            query = query.filter(Article.category == category)
        return query.order_by(desc(Article.created_at)).limit(100).all()