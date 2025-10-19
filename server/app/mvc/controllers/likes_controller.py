# server/app/mvc/controllers/likes_controller.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.db import get_db
from app.mvc.models.users.user_entity import User
from app.core.auth_utils import get_current_active_user
from app.mvc.models.likes.likes_service import LikesService
import traceback

router = APIRouter(tags=["likes"])

class BatchStatsRequest(BaseModel):
    ids: List[int]


# ============================================
# Like/Dislike Toggle Endpoints
# ============================================

@router.post("/articles/{article_id}/like")
def toggle_like(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle like for an article.
    - If already liked: remove like
    - If disliked: switch to like
    - If no reaction: add like
    """
    try:
        service = LikesService(db)
        stats = service.toggle_like(article_id, current_user.id)
        return {"ok": True, "stats": stats}
    except Exception as e:
        print(f"❌ Controller Error in toggle_like for article {article_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {str(e)}")


@router.post("/articles/{article_id}/dislike")
def toggle_dislike(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle dislike for an article.
    - If already disliked: remove dislike
    - If liked: switch to dislike
    - If no reaction: add dislike
    """
    try:
        service = LikesService(db)
        stats = service.toggle_dislike(article_id, current_user.id)
        return {"ok": True, "stats": stats}
    except Exception as e:
        print(f"❌ Controller Error in toggle_dislike for article {article_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to toggle dislike: {str(e)}")


# ============================================
# Stats Endpoints
# ============================================

@router.get("/articles/{article_id}/stats")
def get_article_stats(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get like/dislike stats for a single article"""
    try:
        service = LikesService(db)
        stats = service.get_article_stats(article_id, current_user.id)
        return stats
    except Exception as e:
        print(f"❌ Controller Error in get_article_stats for article {article_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/articles/batch-stats")
def get_batch_stats(
    payload: BatchStatsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get like/dislike stats for multiple articles"""
    try:
        if not payload.ids:
            return {}
        
        service = LikesService(db)
        results = {}
        
        for article_id in payload.ids:
            results[str(article_id)] = service.get_article_stats(article_id, current_user.id)
        
        return results
    except Exception as e:
        print(f"❌ Controller Error in get_batch_stats: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get batch stats: {str(e)}")