# app/mvc/controllers/articles_controller.py
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.core.db import get_db
from app.core.auth_utils import get_current_active_user, get_current_user
from app.mvc.models.users.user_entity import User
from app.mvc.models.articles.article_service import ArticleService
from app.mvc.models.articles.article_schemas import ArticleCreate, ArticleRead
from app.mvc.models.articles.article_entity import Article
from app.mvc.models.likes.likes_service import LikeService

# Event Sourcing
from app.event_sourcing.event_store import get_event_store
from app.event_sourcing.events import (
    ArticleCreatedEvent,
    ArticleUpdatedEvent,
    ArticleDeletedEvent,
    ArticleViewedEvent
)

router = APIRouter(tags=["articles"])


# ============================================
# Public Routes (לא דורשות אימות)
# ============================================

@router.get("/articles/categories")
def list_categories(db: Session = Depends(get_db)):
    """רשימת קטגוריות ייחודיות"""
    rows = (
        db.query(Article.category)
          .filter(Article.category.isnot(None))
          .distinct()
          .all()
    )
    items = [r[0] for r in rows if r[0]]
    return {"items": items}


@router.get("/articles")
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """רשימת מאמרים - פומבי"""
    try:
        service = ArticleService(db)
        actual_page_size = limit if limit and limit != 20 else page_size
        rows, total = service.list(category, page, actual_page_size)
        
        # Convert SQLAlchemy objects to dicts
        items = [
            {
                "id": row.id,
                "title": row.title,
                "summary": row.summary,
                "source": row.source,
                "category": row.category,
                "published_at": row.published_at.isoformat() if row.published_at else None,
                "image_url": row.image_url if row.image_url else "",  
                "thumb_url": row.thumb_url if row.thumb_url else "" 
            }
            for row in rows
        ]
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": actual_page_size
        }
    except Exception as e:
        print(f"Error listing articles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list articles: {str(e)}")


@router.get("/articles/search")
def search_articles(
    q: str,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """חיפוש מאמרים - פומבי"""
    try:
        service = ArticleService(db)
        rows = service.search(q, category)
        
        # Convert to dicts
        items = [
            {
                "id": row.id,
                "title": row.title,
                "summary": row.summary,
                "source": row.source,
                "category": row.category,
                "published_at": row.published_at.isoformat() if row.published_at else None,
                "image_url": row.image_url if row.image_url else "",
                "thumb_url": row.thumb_url if row.thumb_url else ""
            }
            for row in rows
        ]
        
        return {"items": items}
    except Exception as e:
        print(f"Error searching articles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search articles: {str(e)}")


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)  # Optional - גם אם לא מחובר
):
    """
    פרטי מאמר - פומבי
    + שמירת Event של צפייה אם המשתמש מחובר
    """
    try:
        service = ArticleService(db)
        event_store = get_event_store(db)
        
        row = service.get(article_id)
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # שמור Event של צפייה (רק אם המשתמש מחובר)
        try:
            if current_user:
                event = ArticleViewedEvent(
                    article_id=article_id,
                    user_id=current_user.id
                )
                event_id = event_store.save_event(event)
                print(f"✅ Article {article_id} viewed by user {current_user.id}, Event ID: {event_id}")
        except Exception as e:
            # אם יש שגיאה בשמירת Event, לא נכשיל את כל הבקשה
            print(f"⚠️ Failed to save view event: {e}")
        
        return row
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get article: {str(e)}")


# ============================================
# Protected Routes (דורשות אימות)
# ============================================

@router.post("/articles", response_model=ArticleRead, status_code=201)
def create_article(
    payload: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    יצירת מאמר - דורש אימות
    + שמירת Event של יצירה
    """
    try:
        service = ArticleService(db)
        event_store = get_event_store(db)
        
        # צור מאמר
        row = service.create(payload.model_dump())
        
        # שמור Event
        event = ArticleCreatedEvent(
            article_id=row.id,
            title=row.title,
            summary=row.summary or "",
            url=row.url,
            image_url=row.image_url or "",
            category=row.category,
            content=row.content,
            source=row.source,
            user_id=current_user.id
        )
        
        event_id = event_store.save_event(event)
        
        print(f"✅ Article {row.id} created by user {current_user.id}, Event ID: {event_id}")
        
        return row
    except IntegrityError as e:
        msg = str(e.orig)
        if "2627" in msg or "2601" in msg:
            raise HTTPException(status_code=409, detail="Article with this URL already exists")
        raise
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


@router.put("/articles/{article_id}")
def update_article(
    article_id: int,
    payload: ArticleCreate,  # או צור ArticleUpdate schema נפרד
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    עדכון מאמר - דורש אימות
    + שמירת Event של עדכון
    """
    try:
        service = ArticleService(db)
        event_store = get_event_store(db)
        
        # בדוק שהמאמר קיים
        existing = service.get(article_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # עדכן מאמר
        updated_data = payload.model_dump(exclude_unset=True)
        
        # עדכן בפועל (תלוי באיך ArticleService שלך עובד)
        # אם אין update method, תצטרך להוסיף
        for key, value in updated_data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        
        db.commit()
        db.refresh(existing)
        
        # שמור Event
        event = ArticleUpdatedEvent(
            article_id=article_id,
            updated_fields=updated_data,
            user_id=current_user.id
        )
        
        event_id = event_store.save_event(event)
        
        print(f"✅ Article {article_id} updated by user {current_user.id}, Event ID: {event_id}")
        
        return {
            "message": "Article updated successfully",
            "article_id": article_id,
            "event_id": event_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")


@router.delete("/articles/{article_id}")
def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    מחיקת מאמר - דורש אימות
    + שמירת Event של מחיקה
    """
    try:
        service = ArticleService(db)
        event_store = get_event_store(db)
        
        # בדוק שהמאמר קיים
        existing = service.get(article_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # מחק מאמר
        db.delete(existing)
        db.commit()
        
        # שמור Event
        event = ArticleDeletedEvent(
            article_id=article_id,
            user_id=current_user.id
        )
        
        event_id = event_store.save_event(event)
        
        print(f"✅ Article {article_id} deleted by user {current_user.id}, Event ID: {event_id}")
        
        return {
            "message": "Article deleted successfully",
            "article_id": article_id,
            "event_id": event_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")


# ============================================
# Stats Routes (לייקים)
# ============================================

@router.post("/articles/batch-stats")
def batch_stats(
    ids: List[int] = Body(..., embed=True), 
    db: Session = Depends(get_db)
):
    """סטטיסטיקות לייקים למספר מאמרים"""
    stats = LikeService(db).batch_stats(ids)
    return stats


@router.get("/articles/{article_id}/stats")
def article_stats(
    article_id: int, 
    db: Session = Depends(get_db)
):
    """סטטיסטיקות לייקים למאמר יחיד"""
    stats = LikeService(db).single_stats(article_id)
    return stats