# app/mvc/models/likes/likes_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.mvc.models.likes.article_like_entity import ArticleLike
from typing import Dict

class LikesService:
    def __init__(self, db: Session):
        self.db = db
    
    def like_article(self, article_id: int, user_id: int) -> bool:
        """
        לייק למאמר
        אם יש dislike - מסיר אותו ושם like במקום
        """
        # בדוק אם כבר יש like
        existing_like = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first()
        
        if existing_like:
            return False  # כבר אהב
        
        # בדוק אם יש dislike
        existing_dislike = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first()
        
        if existing_dislike:
            # מחק את ה-dislike
            self.db.delete(existing_dislike)
        
        # צור like חדש
        like = ArticleLike(
            article_id=article_id,
            user_id=user_id,
            is_like=True
        )
        self.db.add(like)
        self.db.commit()
        return True
    
    def unlike_article(self, article_id: int, user_id: int) -> bool:
        """הסרת לייק"""
        like = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first()
        
        if not like:
            return False
        
        self.db.delete(like)
        self.db.commit()
        return True
    
    def dislike_article(self, article_id: int, user_id: int) -> bool:
        """
        דיסלייק למאמר
        אם יש like - מסיר אותו ושם dislike במקום
        """
        # בדוק אם כבר יש dislike
        existing_dislike = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first()
        
        if existing_dislike:
            return False  # כבר לא אהב
        
        # בדוק אם יש like
        existing_like = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first()
        
        if existing_like:
            # מחק את ה-like
            self.db.delete(existing_like)
        
        # צור dislike חדש
        dislike = ArticleLike(
            article_id=article_id,
            user_id=user_id,
            is_like=False
        )
        self.db.add(dislike)
        self.db.commit()
        return True
    
    def remove_dislike(self, article_id: int, user_id: int) -> bool:
        """הסרת דיסלייק"""
        dislike = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first()
        
        if not dislike:
            return False
        
        self.db.delete(dislike)
        self.db.commit()
        return True
    
    def get_likes_count(self, article_id: int) -> int:
        """כמות לייקים למאמר"""
        return self.db.query(func.count(ArticleLike.id)).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.is_like == True
        ).scalar() or 0
    
    def get_dislikes_count(self, article_id: int) -> int:
        """כמות דיסלייקים למאמר"""
        return self.db.query(func.count(ArticleLike.id)).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.is_like == False
        ).scalar() or 0
    
    def has_user_liked(self, article_id: int, user_id: int) -> bool:
        """האם משתמש אהב מאמר"""
        return self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first() is not None
    
    def has_user_disliked(self, article_id: int, user_id: int) -> bool:
        """האם משתמש לא אהב מאמר"""
        return self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first() is not None
    
    def get_article_stats(self, article_id: int, user_id: int = None) -> Dict:
        """סטטיסטיקות מאמר מלאות"""
        likes_count = self.get_likes_count(article_id)
        dislikes_count = self.get_dislikes_count(article_id)
        
        user_liked = False
        user_disliked = False
        
        if user_id:
            user_liked = self.has_user_liked(article_id, user_id)
            user_disliked = self.has_user_disliked(article_id, user_id)
        
        return {
            "likes_count": likes_count,
            "dislikes_count": dislikes_count,
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "total_reactions": likes_count + dislikes_count
        }