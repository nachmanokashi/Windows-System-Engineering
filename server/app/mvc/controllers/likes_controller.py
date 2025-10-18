# server/app/mvc/controllers/likes_controller.py
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.mvc.models.users.user_entity import User
from app.core.auth_utils import get_current_active_user
from app.mvc.models.likes.likes_service import LikesService

router = APIRouter(tags=["likes"])

GUEST_USER_ID = 3  

def get_optional_user(request: Request) -> Optional[User]:
    try:
        return get_current_active_user(request)
    except Exception:
        return None

@router.post("/articles/{article_id}/like")
def like_article(article_id: int, db: Session = Depends(get_db)):
    try:
        LikesService(db).like(article_id, GUEST_USER_ID)
        return {"ok": True}
    except Exception as e:
        # לוג קצר לזיהוי (חשוב!)
        print("like_article error:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to toggle like")

@router.delete("/articles/{article_id}/like")
def unlike_article(article_id: int, db: Session = Depends(get_db)):
    try:
        LikesService(db).unlike(article_id, GUEST_USER_ID)
        return {"ok": True}
    except Exception as e:
        print("unlike_article error:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to toggle like")

@router.post("/articles/{article_id}/dislike")
def dislike_article(article_id: int):
    return {"ok": True, "note": "dislike is not persisted yet"}

@router.delete("/articles/{article_id}/dislike")
def remove_dislike(article_id: int):
    return {"ok": True}
