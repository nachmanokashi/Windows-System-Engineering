# server/app/mvc/models/likes/likes_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
# ודא שהמודל הנכון מיובא
from app.mvc.models.likes.article_like_entity import ArticleLike
from typing import Dict, Optional

class LikesService:
    def __init__(self, db: Session):
        self.db = db

    def like(self, article_id: int, user_id: int) -> bool:
        """
        לייק למאמר. אם יש דיסלייק, מסיר אותו.
        מחזיר True אם הלייק נוסף, False אם כבר היה קיים.
        """
        # בדוק אם כבר יש like
        existing_like = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first()

        if existing_like:
            return False  # כבר אהב

        # בדוק אם יש dislike והסר אותו אם כן
        existing_dislike = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first()

        if existing_dislike:
            self.db.delete(existing_dislike)
            # אין צורך ב-commit כאן, הוא יקרה בהוספת הלייק

        # צור like חדש
        like = ArticleLike(
            article_id=article_id,
            user_id=user_id,
            is_like=True
        )
        self.db.add(like)
        self.db.commit()
        return True

    def unlike(self, article_id: int, user_id: int) -> bool:
        """
        הסרת לייק.
        מחזיר True אם הלייק הוסר, False אם לא היה קיים.
        """
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

    def dislike(self, article_id: int, user_id: int) -> bool:
        """
        דיסלייק למאמר. אם יש לייק, מסיר אותו.
        מחזיר True אם הדיסלייק נוסף, False אם כבר היה קיים.
        """
        # בדוק אם כבר יש dislike
        existing_dislike = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first()

        if existing_dislike:
            return False # כבר לא אהב

        # בדוק אם יש like והסר אותו אם כן
        existing_like = self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first()

        if existing_like:
            self.db.delete(existing_like)
            # אין צורך ב-commit כאן, הוא יקרה בהוספת הדיסלייק

        # צור dislike חדש
        dislike = ArticleLike(
            article_id=article_id,
            user_id=user_id,
            is_like=False # <-- חשוב: מגדירים כ-False
        )
        self.db.add(dislike)
        self.db.commit()
        return True

    def remove_dislike(self, article_id: int, user_id: int) -> bool:
        """
        הסרת דיסלייק.
        מחזיר True אם הדיסלייק הוסר, False אם לא היה קיים.
        """
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

    # --- פונקציות לקבלת סטטוס ---

    def _get_likes_count(self, article_id: int) -> int:
        """כמות לייקים למאמר"""
        return self.db.query(func.count(ArticleLike.id)).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.is_like == True
        ).scalar() or 0

    def _get_dislikes_count(self, article_id: int) -> int:
        """כמות דיסלייקים למאמר"""
        return self.db.query(func.count(ArticleLike.id)).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.is_like == False
        ).scalar() or 0

    def _has_user_liked(self, article_id: int, user_id: int) -> bool:
        """האם משתמש ספציפי אהב מאמר"""
        return self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == True
        ).first() is not None

    def _has_user_disliked(self, article_id: int, user_id: int) -> bool:
        """האם משתמש ספציפי לא אהב מאמר"""
        return self.db.query(ArticleLike).filter(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user_id,
            ArticleLike.is_like == False
        ).first() is not None

    def get_article_stats(self, article_id: int, user_id: Optional[int] = None) -> Dict:
        """
        סטטיסטיקות מאמר מלאות.
        אם user_id מסופק, כולל מידע האם המשתמש הספציפי אהב/לא אהב.
        """
        likes_count = self._get_likes_count(article_id)
        dislikes_count = self._get_dislikes_count(article_id)

        user_liked = False
        user_disliked = False

        if user_id is not None:
            user_liked = self._has_user_liked(article_id, user_id)
            user_disliked = self._has_user_disliked(article_id, user_id)

        return {
            "likes_count": likes_count,
            "dislikes_count": dislikes_count,
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "total_reactions": likes_count + dislikes_count
        }

# --- נשאיר את השם הזה לתאימות עם הקוד שהשתמש בו קודם ---
LikeService = LikesService