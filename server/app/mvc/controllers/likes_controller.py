# server/app/mvc/controllers/likes_controller.py
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.mvc.models.users.user_entity import User
# --- 1. שינינו את הייבוא כאן ---
from app.core.auth_utils import get_current_active_user
from app.mvc.models.likes.likes_service import LikesService

router = APIRouter(tags=["likes"])

# --- מודל קלט חדש עבור בקשת ה-POST של batch-stats ---
class BatchStatsRequest(BaseModel):
    ids: List[int]

# --- 2. הוספנו תלות (Depends) לקבלת המשתמש המחובר בפונקציות ---

@router.post("/articles/{article_id}/like")
def like_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # <-- הוספנו
):
    """לייק למאמר - משתמש במשתמש המחובר"""
    try:
        # --- 3. משתמשים ב-current_user.id במקום ב-GUEST_USER_ID ---
        LikesService(db).like(article_id, current_user.id)
        # מחזירים את הסטטוס העדכני למשתמש הספציפי
        stats = LikesService(db).get_article_stats(article_id, current_user.id)
        return {"ok": True, "stats": stats}
    except Exception as e:
        print("like_article error:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to toggle like")

@router.delete("/articles/{article_id}/like")
def unlike_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # <-- הוספנו
):
    """הסרת לייק - משתמש במשתמש המחובר"""
    try:
        # --- 3. משתמשים ב-current_user.id במקום ב-GUEST_USER_ID ---
        LikesService(db).unlike(article_id, current_user.id)
        # מחזירים את הסטטוס העדכני למשתמש הספציפי
        stats = LikesService(db).get_article_stats(article_id, current_user.id)
        return {"ok": True, "stats": stats}
    except Exception as e:
        print("unlike_article error:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to toggle like")

@router.post("/articles/{article_id}/dislike")
def dislike_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # <-- הוספנו
):
    """דיסלייק למאמר"""
    try:
        # --- 3. משתמשים ב-current_user.id ---
        LikesService(db).dislike(article_id, current_user.id) # (נצטרך להוסיף את dislike ל-Service)
        stats = LikesService(db).get_article_stats(article_id, current_user.id)
        return {"ok": True, "stats": stats, "note": "dislike logic might need implementation in LikesService"}
    except Exception as e:
        print("dislike_article error:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to toggle dislike")


@router.delete("/articles/{article_id}/dislike")
def remove_dislike(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # <-- הוספנו
):
    """הסרת דיסלייק"""
    try:
        # --- 3. משתמשים ב-current_user.id ---
        LikesService(db).remove_dislike(article_id, current_user.id) # (נצטרך להוסיף את remove_dislike ל-Service)
        stats = LikesService(db).get_article_stats(article_id, current_user.id)
        return {"ok": True, "stats": stats, "note": "remove_dislike logic might need implementation in LikesService"}
    except Exception as e:
        print("remove_dislike error:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to remove dislike")


# --- הפונקציות הבאות צריכות גם את המשתמש המחובר כדי להחזיר user_liked/user_disliked ---

@router.post("/articles/batch-stats")
async def get_batch_stats(
    payload: BatchStatsRequest,
    current_user: User = Depends(get_current_active_user), # <-- הוספנו
    db: Session = Depends(get_db)
):
    """קבלת סטטיסטיקות למספר מאמרים בבת אחת עבור המשתמש הנוכחי"""
    try:
        if not payload.ids:
            return {}
        
        service = LikesService(db)
        results = {}
        for article_id in payload.ids:
            # --- 3. מעבירים את current_user.id ---
            results[str(article_id)] = service.get_article_stats(article_id, current_user.id)
        
        return results
    except Exception as e:
        print(f"!!! ERROR in get_batch_stats: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@router.get("/articles/{article_id}/stats")
def get_article_stats(
    article_id: int,
    current_user: User = Depends(get_current_active_user), # <-- הוספנו
    db: Session = Depends(get_db)
):
    """קבלת סטטיסטיקות למאמר יחיד עבור המשתמש הנוכחי"""
    try:
        service = LikesService(db)
        # --- 3. מעבירים את current_user.id ---
        stats = service.get_article_stats(article_id, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))