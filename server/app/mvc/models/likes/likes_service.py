from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app.mvc.models.likes.article_like_entity import ArticleLike
from typing import Dict, Optional
import traceback

class LikesService:
    def __init__(self, db: Session):
        self.db = db

    def toggle_like(self, article_id: int, user_id: int) -> Dict:
        """
        Toggle like for an article.
        - If user already liked: remove like
        - If user disliked: switch to like
        - If no reaction: add like
        """
        try:
            existing = self.db.query(ArticleLike).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.user_id == user_id
            ).first()

            if existing:
                if existing.is_like:
                    self.db.delete(existing) 
                    print(f"User {user_id} removed like from article {article_id}")
                else: 
                    existing.is_like = True 
                    print(f"User {user_id} switched dislike to like on article {article_id}")
            else:
                new_like = ArticleLike(article_id=article_id, user_id=user_id, is_like=True)
                self.db.add(new_like)
                print(f"User {user_id} liked article {article_id}")

            self.db.commit()
            
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"❌ DB Error in toggle_like for article {article_id}, user {user_id}: {e}")
            traceback.print_exc()
            raise 
            
        # החזר סטטוס מעודכן
        return self.get_article_stats(article_id, user_id)


    def toggle_dislike(self, article_id: int, user_id: int) -> Dict:
        """
        Toggle dislike for an article.
        """
        try:
            existing = self.db.query(ArticleLike).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.user_id == user_id
            ).first()

            if existing:
                if not existing.is_like: 
                    self.db.delete(existing)
                    print(f"User {user_id} removed dislike from article {article_id}")
                else: 
                    existing.is_like = False
                    print(f"User {user_id} switched like to dislike on article {article_id}")
            else:
                new_dislike = ArticleLike(article_id=article_id, user_id=user_id, is_like=False)
                self.db.add(new_dislike)
                print(f"User {user_id} disliked article {article_id}")

            self.db.commit()

        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"❌ DB Error in toggle_dislike for article {article_id}, user {user_id}: {e}")
            traceback.print_exc()
            raise

        return self.get_article_stats(article_id, user_id)

    # ========================================
    # Helper Methods for Stats
    # ========================================

    def _get_likes_count(self, article_id: int) -> int:
        """סופר לייקים"""
        try:
            count = self.db.query(func.count(ArticleLike.id)).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.is_like == True
            ).scalar() # scalar() מחזיר את הערך הבודד
            return count or 0
        except SQLAlchemyError as e:
            print(f"❌ DB Error in _get_likes_count for article {article_id}: {e}")
            traceback.print_exc()
            return 0 

    def _get_dislikes_count(self, article_id: int) -> int:
        """סופר דיסלייקים"""
        try:
            count = self.db.query(func.count(ArticleLike.id)).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.is_like == False
            ).scalar()
            return count or 0
        except SQLAlchemyError as e:
            print(f"❌ DB Error in _get_dislikes_count for article {article_id}: {e}")
            traceback.print_exc()
            return 0

    def _get_user_reaction(self, article_id: int, user_id: int) -> Optional[bool]:
        """בודק מה הריאקציה של המשתמש: True=לייק, False=דיסלייק, None=אין"""
        try:
            # .first() יחזיר שורה (Tuple) או None
            reaction = self.db.query(ArticleLike.is_like).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.user_id == user_id
            ).first()
            
            return reaction[0] if reaction else None # reaction[0] יכיל True או False
        except SQLAlchemyError as e:
            print(f"❌ DB Error in _get_user_reaction for article {article_id}, user {user_id}: {e}")
            traceback.print_exc()
            return None

    def get_article_stats(self, article_id: int, user_id: Optional[int] = None) -> Dict:
        """מרכז את כל הסטטיסטיקות עבור מאמר"""
        likes_count = self._get_likes_count(article_id)
        dislikes_count = self._get_dislikes_count(article_id)
        
        user_liked = False
        user_disliked = False
        
        if user_id is not None:
            user_reaction = self._get_user_reaction(article_id, user_id)
            if user_reaction is True:
                user_liked = True
            elif user_reaction is False:
                user_disliked = True
        
        stats = {
            "article_id": article_id,
            "likes_count": likes_count,
            "dislikes_count": dislikes_count,
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "total_reactions": likes_count + dislikes_count
        }
        
        print(f"📊 Stats for article {article_id}: {stats}")
        return stats

LikeService = LikesService