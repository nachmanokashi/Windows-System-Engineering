# app/mvc/models/likes/likes_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.mvc.models.likes.rticle_like_entity import ArticleLike
from typing import Dict

class LikesService:
    def __init__(self, db: Session):
        self.db = db
    
    def like_article(self, article_id: int, user_id: int) -> bool:
        """לייק למאמר"""
        # בדוק אם כבר אהב
        existing = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id
        ).first()
        
        if existing:
            return False  # כבר אהב
        
        # צור לייק חדש
        like = ArticleLike(article_id=article_id, user_id=user_id)
        self.db.add(like)
        self.db.commit()
        return True
    
    def unlike_article(self, article_id: int, user_id: int) -> bool:
        """הסרת לייק"""
        like = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id
        ).first()
        
        if not like:
            return False
        
        self.db.delete(like)
        self.db.commit()
        return True
    
    def get_likes_count(self, article_id: int) -> int:
        """כמות לייקים למאמר"""
        return self.db.query(func.count(ArticleLike.id)).filter(
            ArticleLike.article_id == article_id
        ).scalar() or 0
    
    def has_user_liked(self, article_id: int, user_id: int) -> bool:
        """האם משתמש אהב מאמר"""
        return self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id
        ).first() is not None
    
    def get_article_stats(self, article_id: int, user_id: int = None) -> Dict:
        """סטטיסטיקות מאמר"""
        likes_count = self.get_likes_count(article_id)
        user_liked = self.has_user_liked(article_id, user_id) if user_id else False
        
        return {
            "likes_count": likes_count,
            "user_liked": user_liked
        }