# server/app/mvc/models/likes/like_entity.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from app.core.db import Base

class ArticleLike(Base):
    __tablename__ = "article_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.getdate())
