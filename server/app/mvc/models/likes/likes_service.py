# server/app/mvc/models/likes/likes_service.py
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
            # מצא את הריאקציה הקיימת של המשתמש (אם יש)
            existing = self.db.query(ArticleLike).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.user_id == user_id
            ).first()

            if existing:
                if existing.is_like:
                    # כבר יש לייק → מבטל
                    self.db.delete(existing)
                    print(f"👎 User {user_id} removed like from article {article_id}")
                else:
                    # יש דיסלייק → מחליף ללייק
                    existing.is_like = True
                    print(f"🔄 User {user_id} switched from dislike to like on article {article_id}")
            else:
                # אין ריאקציה → מוסיף לייק
                new_like = ArticleLike(article_id=article_id, user_id=user_id, is_like=True)
                self.db.add(new_like)
                print(f"👍 User {user_id} liked article {article_id}")

            self.db.commit()
            
            # החזר את הסטטיסטיקות המעודכנות
            return self.get_article_stats(article_id, user_id)

        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"❌ DB Error in toggle_like for article {article_id}, user {user_id}: {e}")
            traceback.print_exc()
            raise

    def toggle_dislike(self, article_id: int, user_id: int) -> Dict:
        """
        Toggle dislike for an article.
        - If user already disliked: remove dislike
        - If user liked: switch to dislike
        - If no reaction: add dislike
        """
        try:
            # מצא את הריאקציה הקיימת של המשתמש (אם יש)
            existing = self.db.query(ArticleLike).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.user_id == user_id
            ).first()

            if existing:
                if not existing.is_like:
                    # כבר יש דיסלייק → מבטל
                    self.db.delete(existing)
                    print(f"👎 User {user_id} removed dislike from article {article_id}")
                else:
                    # יש לייק → מחליף לדיסלייק
                    existing.is_like = False
                    print(f"🔄 User {user_id} switched from like to dislike on article {article_id}")
            else:
                # אין ריאקציה → מוסיף דיסלייק
                new_dislike = ArticleLike(article_id=article_id, user_id=user_id, is_like=False)
                self.db.add(new_dislike)
                print(f"👎 User {user_id} disliked article {article_id}")

            self.db.commit()
            
            # החזר את הסטטיסטיקות המעודכנות
            return self.get_article_stats(article_id, user_id)

        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"❌ DB Error in toggle_dislike for article {article_id}, user {user_id}: {e}")
            traceback.print_exc()
            raise

    # ========================================
    # Helper Methods for Stats
    # ========================================

    def _get_likes_count(self, article_id: int) -> int:
        """Count total likes for an article"""
        try:
            count = self.db.query(func.count(ArticleLike.id)).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.is_like == True
            ).scalar()
            return count or 0
        except SQLAlchemyError as e:
            print(f"❌ DB Error in _get_likes_count for article {article_id}: {e}")
            traceback.print_exc()
            return 0

    def _get_dislikes_count(self, article_id: int) -> int:
        """Count total dislikes for an article"""
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
        """
        Get user's reaction to an article.
        Returns: True (liked), False (disliked), None (no reaction)
        """
        try:
            reaction = self.db.query(ArticleLike.is_like).filter(
                ArticleLike.article_id == article_id,
                ArticleLike.user_id == user_id
            ).first()
            
            return reaction[0] if reaction else None
        except SQLAlchemyError as e:
            print(f"❌ DB Error in _get_user_reaction for article {article_id}, user {user_id}: {e}")
            traceback.print_exc()
            return None

    def get_article_stats(self, article_id: int, user_id: Optional[int] = None) -> Dict:
        """
        Get full stats for an article.
        Returns likes count, dislikes count, and user's reaction status.
        """
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


# Maintain backward compatibility
LikeService = LikesService