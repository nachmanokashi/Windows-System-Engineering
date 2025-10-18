from typing import Dict, List
from sqlalchemy.orm import Session

try:
    from app.mvc.models.likes.like_repository import LikeRepository as _Repo
except ImportError:
    from app.mvc.models.likes.like_repository import LikesRepository as _Repo  # fallback

class LikesService:
    def __init__(self, db: Session) -> None:
        self.repo = _Repo(db)

    def batch_stats(self, ids: List[int]) -> Dict[int, Dict[str, int]]:
        return self.repo.batch_stats(ids)

    def single_stats(self, article_id: int) -> Dict[str, int]:
        return self.repo.single_stats(article_id)

    def like(self, article_id: int, user_id: int) -> None:
        if hasattr(self.repo, "add"):
            self.repo.add(article_id, user_id)

    def unlike(self, article_id: int, user_id: int) -> None:
        if hasattr(self.repo, "remove"):
            self.repo.remove(article_id, user_id)

LikeService = LikesService
