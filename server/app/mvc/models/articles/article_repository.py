# server/app/mvc/models/articles/article_repository.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.mvc.models.articles.article_entity import Article

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Article:
        row = Article(**data)  # יוצר אובייקט ORM מלא
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get(self, article_id: int) -> Optional[Article]:
        # מחזיר אובייקט ORM מלא (לא SELECT חלקי)
        return self.db.query(Article).filter(Article.id == article_id).first()

    def list(self, category: Optional[str], page: int, page_size: int) -> Tuple[List[Article], int]:
        q = self.db.query(Article)
        if category:
            q = q.filter(Article.category == category)

        # סה״כ
        total = q.with_entities(func.count(Article.id)).scalar() or 0

        # מיון מהחדש לישן (SQL Server מסתדר בלי nulls_last)
        rows = (
             q.order_by(Article.published_at.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
             .all()
        )
        return rows, total

    def search(self, qtext: str, category: Optional[str]) -> List[Article]:
        q = self.db.query(Article)
        if category:
            q = q.filter(Article.category == category)

        pattern = f"%{qtext}%"
        q = q.filter(
            (func.lower(Article.title).like(func.lower(pattern))) |
            (func.lower(Article.summary).like(func.lower(pattern))) |
            (func.lower(Article.content).like(func.lower(pattern)))
        )

        return q.order_by(Article.published_at.desc()).limit(50).all()
