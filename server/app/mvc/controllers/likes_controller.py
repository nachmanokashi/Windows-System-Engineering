# app/mvc/controllers/likes_controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.auth_utils import get_current_active_user
from app.mvc.models.users.user_entity import User
from app.mvc.models.likes.likes_service import LikesService

router = APIRouter(tags=["likes"])

@router.post("/articles/{article_id}/like")
def like_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """לייק למאמר - מסיר dislike אם קיים"""
    try:
        service = LikesService(db)
        result = service.like_article(article_id, current_user.id)
        
        return {
            "message": "Article liked" if result else "Already liked",
            "stats": service.get_article_stats(article_id, current_user.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/articles/{article_id}/like")
def unlike_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """הסרת לייק"""
    try:
        service = LikesService(db)
        success = service.unlike_article(article_id, current_user.id)
        
        return {
            "message": "Like removed" if success else "Not liked",
            "stats": service.get_article_stats(article_id, current_user.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/articles/{article_id}/dislike")
def dislike_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """דיסלייק למאמר - מסיר like אם קיים"""
    try:
        service = LikesService(db)
        result = service.dislike_article(article_id, current_user.id)
        
        return {
            "message": "Article disliked" if result else "Already disliked",
            "stats": service.get_article_stats(article_id, current_user.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/articles/{article_id}/dislike")
def remove_dislike(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """הסרת דיסלייק"""
    try:
        service = LikesService(db)
        success = service.remove_dislike(article_id, current_user.id)
        
        return {
            "message": "Dislike removed" if success else "Not disliked",
            "stats": service.get_article_stats(article_id, current_user.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/{article_id}/stats")
def get_article_stats(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """סטטיסטיקות מאמר - likes + dislikes"""
    try:
        service = LikesService(db)
        stats = service.get_article_stats(article_id, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/batch-stats")
def get_batch_stats(
    article_ids: str,  # comma-separated IDs: "1,2,3,4"
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """קבלת סטטיסטיקות למספר מאמרים בבת אחת"""
    try:
        service = LikesService(db)
        ids = [int(id.strip()) for id in article_ids.split(",")]
        
        results = {}
        for article_id in ids:
            results[article_id] = service.get_article_stats(article_id, current_user.id)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))