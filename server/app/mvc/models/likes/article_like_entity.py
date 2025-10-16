# app/mvc/models/likes/article_like_entity.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base

class ArticleLike(Base):
    __tablename__ = "article_likes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_like = Column(Boolean, nullable=False, default=True)  # True=Like, False=Dislike
    created_at = Column(DateTime, nullable=False, default=func.getdate())
    
    # Unique constraint - משתמש יכול להגיב רק פעם אחת (like או dislike)
    __table_args__ = (
        UniqueConstraint('article_id', 'user_id', name='uq_article_user_reaction'),
    )