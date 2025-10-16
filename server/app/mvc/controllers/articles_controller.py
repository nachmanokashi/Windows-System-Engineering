from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.core.auth_utils import get_current_active_user
from app.mvc.models.users.user_entity import User
from app.mvc.models.articles.article_service import ArticleService
from app.mvc.models.articles.article_schemas import ArticleCreate, ArticleRead
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=["articles"])

# Public routes (לא דורשות אימות)
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
            }
            for row in rows
        ]
        
        return {"items": items}
    except Exception as e:
        print(f"Error searching articles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search articles: {str(e)}")

@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """פרטי מאמר - פומבי"""
    try:
        service = ArticleService(db)
        row = service.get(article_id)
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        return row
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get article: {str(e)}")

# Protected routes (דורשות אימות)
@router.post("/articles", response_model=ArticleRead, status_code=201)
def create_article(
    payload: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """יצירת מאמר - דורש אימות"""
    try:
        service = ArticleService(db)
        row = service.create(payload.model_dump())
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