from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from sqlalchemy import text
from app.core.db import get_db
from app.core.auth_utils import get_current_active_user
from app.mvc.models.users.user_entity import User
from app.mvc.models.articles.article_entity import Article
from app.services.classification_service import get_classification_service

router = APIRouter(tags=["admin"], prefix="/admin")


# ============================================
# Schemas
# ============================================

class ArticleCreateRequest(BaseModel):
    """בקשה ליצירת מאמר חדש"""
    title: str = Field(..., min_length=1, max_length=300) 
    summary: str = Field(default="", max_length=2000)
    content: str = Field(default="")
    url: str = Field(default="", max_length=500)  
    source: str = Field(default="", max_length=200)  
    category: Optional[str] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    auto_classify: bool = True


class ArticleUpdateRequest(BaseModel):
    """בקשה לעדכון מאמר"""
    title: Optional[str] = Field(None, min_length=5, max_length=300)
    summary: Optional[str] = Field(None, min_length=10, max_length=2000)
    content: Optional[str] = Field(None, min_length=20)
    url: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None


class BatchClassifyRequest(BaseModel):
    """בקשה לסיווג מרובה"""
    article_ids: List[int]
    category_filter: Optional[str] = None 


class DraftClassifyRequest(BaseModel):
    """בקשה לסיווג טיוטה"""
    title: str = Field(..., min_length=1, max_length=300)
    summary: Optional[str] = Field(default="", max_length=2000)
    content: Optional[str] = Field(default="", max_length=50000)


# ============================================
# Helper Functions
# ============================================

def require_admin(current_user: User = Depends(get_current_active_user)):
    """וודא שהמשתמש הוא Admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


# ============================================
# Endpoints
# ============================================

@router.post("/articles")
def create_article(
    payload: ArticleCreateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """יצירת מאמר חדש עם סיווג אוטומטי"""
    try:
        category_name = payload.category
        
        # סיווג אוטומטי אם מבוקש
        if payload.auto_classify and not category_name:
            classifier = get_classification_service()
            result = classifier.classify_article(
                title=payload.title,
                content=payload.content,
                summary=payload.summary
            )
            category_name = result.get("category", "General")
        
        # מציאת category_id לפי השם
        category_id = 3  # ברירת מחדל: General
        if category_name:
            cat_result = db.execute(
                text("SELECT id FROM categories WHERE name = :name"),
                {"name": category_name}
            ).fetchone()
            if cat_result:
                category_id = cat_result[0]
        
        # יצירת URL ייחודי אם ריק
        url_value = payload.url or f"https://example.com/article/{uuid.uuid4()}"
        
        # יצירת המאמר
        article = Article(
            title=payload.title,
            summary=payload.summary or "",
            content=payload.content or "",
            url=url_value,
            source=payload.source or "Manual",
            category=category_id,  # שמירת ID ולא שם
            image_url=payload.image_url,
            thumb_url=payload.thumb_url or payload.image_url,
            published_at=datetime.utcnow()
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        return {
            "success": True,
            "article_id": article.id,
            "category": category_name
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


@router.delete("/articles/{article_id}")
def delete_article(
    article_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """מחיקת מאמר"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        db.delete(article)
        db.commit()
        
        return {
            "success": True,
            "message": f"Article {article_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")


@router.post("/articles/{article_id}/classify")
def classify_article(
    article_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """סיווג מאמר קיים - מחזיר הצעות בלבד"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        classifier = get_classification_service()
        result = classifier.classify_article(
            title=article.title,
            content=article.content or "",
            summary=article.summary or ""
        )
        
        return {
            "article_id": article.id,
            "current_category": article.category,
            "suggested_category": result.get("category"),
            "confidence": result.get("confidence"),
            "all_suggestions": result.get("suggestions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.post("/articles/{article_id}/apply-classification")
def apply_classification(
    article_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """סיווג והחלת קטגוריה חדשה"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # סיווג המאמר
        classifier = get_classification_service()
        result = classifier.classify_article(
            title=article.title,
            content=article.content or "",
            summary=article.summary or ""
        )
        
        # מציאת category_id
        category_name = result.get("category", "General")
        cat_result = db.execute(
            text("SELECT id FROM categories WHERE name = :name"),
            {"name": category_name}
        ).fetchone()
        category_id = cat_result[0] if cat_result else 3
        
        # עדכון המאמר
        old_category = article.category
        article.category = category_id
        
        db.commit()
        
        return {
            "success": True,
            "article_id": article.id,
            "old_category": old_category,
            "new_category": category_name,
            "confidence": result.get("confidence")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to apply classification: {str(e)}")


@router.post("/articles/batch-classify")
def batch_classify_articles(
    payload: BatchClassifyRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """סיווג מרובה של מאמרים"""
    try:
        results = []
        
        for article_id in payload.article_ids:
            article = db.query(Article).filter(Article.id == article_id).first()
            
            if not article:
                results.append({
                    "article_id": article_id,
                    "success": False,
                    "error": "Article not found"
                })
                continue
            
            # סיווג והחלה
            classifier = get_classification_service()
            classification = classifier.classify_article(
                title=article.title,
                content=article.content or "",
                summary=article.summary or ""
            )
            
            # מציאת category_id
            category_name = classification.get("category", "General")
            cat_result = db.execute(
                text("SELECT id FROM categories WHERE name = :name"),
                {"name": category_name}
            ).fetchone()
            category_id = cat_result[0] if cat_result else 3
            
            old_category = article.category
            article.category = category_id
            
            results.append({
                "article_id": article.id,
                "success": True,
                "old_category": old_category,
                "new_category": category_name,
                "confidence": classification.get("confidence")
            })
        
        db.commit()
        
        return {
            "success": True,
            "total": len(payload.article_ids),
            "results": results
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")


@router.get("/articles/uncategorized")
def get_uncategorized_articles(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """קבל מאמרים ללא קטגוריה"""
    try:
        # ID 3 הוא General
        articles = db.query(Article).filter(
            (Article.category == None) | (Article.category == 3)
        ).limit(limit).all()
        
        return {
            "count": len(articles),
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "category": a.category,
                    "published_at": a.published_at.isoformat() if a.published_at else None
                }
                for a in articles
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
def get_available_categories(admin_user: User = Depends(require_admin)):
    """קבל רשימת קטגוריות זמינות"""
    classifier = get_classification_service()
    return {
        "categories": classifier.get_available_categories()
    }


@router.get("/articles")
def get_all_articles_admin(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None
):
    """קבל את כל המאמרים"""
    try:
        query = db.query(Article)
        
        if category:
            # המרה משם לID
            cat_result = db.execute(
                text("SELECT id FROM categories WHERE name = :name"),
                {"name": category}
            ).fetchone()
            if cat_result:
                query = query.filter(Article.category == cat_result[0])
        
        query = query.order_by(Article.published_at.desc())
        articles = query.limit(limit).all()
        
        items = [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary,
                "content": a.content,
                "source": a.source,
                "category": a.category,
                "url": a.url,
                "image_url": a.image_url,
                "thumb_url": a.thumb_url,
                "published_at": a.published_at.isoformat() if a.published_at else None
            }
            for a in articles
        ]
        
        return {
            "articles": items,
            "total": len(items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")


@router.get("/articles/{article_id}")
def get_article_by_id(
    article_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """קבל פרטי מאמר בודד"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "article": {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "content": article.content,
                "source": article.source,
                "category": article.category,
                "url": article.url,
                "image_url": article.image_url,
                "thumb_url": article.thumb_url,
                "published_at": article.published_at.isoformat() if article.published_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")


@router.post("/classify-draft")
def classify_draft(
    payload: DraftClassifyRequest,
    admin_user: User = Depends(require_admin)
):
    """סיווג טיוטה לפני יצירה"""
    try:
        classifier = get_classification_service()
        result = classifier.classify_article(
            title=payload.title,
            content=payload.content or "",
            summary=payload.summary or ""
        )
        return {
            "suggested_category": result.get("category"),
            "confidence": result.get("confidence"),
            "all_suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft classification failed: {str(e)}")