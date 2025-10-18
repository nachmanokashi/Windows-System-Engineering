# server/app/mvc/models/likes/like_repository.py
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.mvc.models.likes.like_entity import ArticleLike

class LikeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # >>> מחזיר {article_id: {likes, dislikes}} עבור כמה מאמרים
    def batch_stats(self, ids: List[int]) -> Dict[int, Dict[str, int]]:
        if not ids:
            return {}
        rows = (
            self.db.query(
                ArticleLike.article_id,
                func.count(ArticleLike.id).label("likes")
            )
            .filter(ArticleLike.article_id.in_(ids))
            .group_by(ArticleLike.article_id)
            .all()
        )
        out: Dict[int, Dict[str, int]] = {i: {"likes": 0, "dislikes": 0} for i in ids}
        for article_id, likes in rows:
            out[int(article_id)]["likes"] = int(likes or 0)
        return out

    # >>> מחזיר {"likes": X, "dislikes": 0} למאמר יחיד
    def single_stats(self, article_id: int) -> Dict[str, int]:
        count = (
            self.db.query(func.count(ArticleLike.id))
            .filter(ArticleLike.article_id == article_id)
            .scalar()
        )
        return {"likes": int(count or 0), "dislikes": 0}

    # אופציונלי: פעולות לייק/ביטול לייק (לקריאות POST/DELETE)
    def exists(self, article_id: int, user_id: int) -> bool:
        return bool(
            self.db.query(ArticleLike.id)
                   .filter(ArticleLike.article_id == article_id,
                           ArticleLike.user_id == user_id)
                   .first()
        )

    def add(self, article_id: int, user_id: int) -> None:
        if self.exists(article_id, user_id):
            return
        self.db.add(ArticleLike(article_id=article_id, user_id=user_id))
        self.db.commit()

    def remove(self, article_id: int, user_id: int) -> int:
        q = (self.db.query(ArticleLike)
                    .filter(ArticleLike.article_id == article_id,
                            ArticleLike.user_id == user_id))
        n = q.delete()
        self.db.commit()
        return n
