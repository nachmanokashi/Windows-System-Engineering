from fastapi import APIRouter, Depends, HTTPException, Body,Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

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
    title: str = Field(..., min_length=5, max_length=300)
    summary: str = Field(..., min_length=10, max_length=2000)
    content: str = Field(..., min_length=20)
    url: str = Field(..., max_length=500)
    source: str = Field(..., max_length=200)
    category: Optional[str] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    auto_classify: bool = True  # האם לסווג אוטומטית


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


class ClassifyRequest(BaseModel):
    """בקשה לסיווג מאמר"""
    article_id: int
    

class BatchClassifyRequest(BaseModel):
    """בקשה לסיווג מרובה"""
    article_ids: List[int]
    category_filter: Optional[str] = None  # סווג רק מאמרים בקטגוריה זו


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
    """
    יצירת מאמר חדש (Admin בלבד)
    עם סיווג אוטומטי אופציונלי
    """
    try:
        # סיווג אוטומטי אם מבוקש
        category = payload.category
        classification_result = None
        
        if payload.auto_classify and not category:
            print("🤖 Auto-classifying article...")
            classifier = get_classification_service()
            classification_result = classifier.classify_article(
                title=payload.title,
                content=payload.content,
                summary=payload.summary
            )
            category = classification_result.get("category", "General")
            print(f"✅ Classified as: {category}")
        
        # צור מאמר
        article = Article(
            title=payload.title,
            summary=payload.summary,
            content=payload.content,
            url=payload.url,
            source=payload.source,
            category=category or "General",
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
            "category": article.category,
            "classification": classification_result
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


@router.put("/articles/{article_id}")
def update_article(
    article_id: int,
    payload: ArticleUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """עדכון מאמר קיים (Admin בלבד)"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # עדכן שדות
        if payload.title is not None:
            article.title = payload.title
        if payload.summary is not None:
            article.summary = payload.summary
        if payload.content is not None:
            article.content = payload.content
        if payload.url is not None:
            article.url = payload.url
        if payload.source is not None:
            article.source = payload.source
        if payload.category is not None:
            article.category = payload.category
        if payload.image_url is not None:
            article.image_url = payload.image_url
        if payload.thumb_url is not None:
            article.thumb_url = payload.thumb_url
        
        db.commit()
        
        return {
            "success": True,
            "article_id": article.id,
            "message": "Article updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")


@router.delete("/articles/{article_id}")
def delete_article(
    article_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """מחיקת מאמר (Admin בלבד)"""
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
    """
    סווג מאמר קיים עם AI
    מחזיר הצעות אבל לא משנה בפועל
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # סווג עם AI
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
    """
    סווג והחל את הקטגוריה החדשה
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # סווג
        classifier = get_classification_service()
        result = classifier.classify_article(
            title=article.title,
            content=article.content or "",
            summary=article.summary or ""
        )
        
        # עדכן
        old_category = article.category
        new_category = result.get("category", "General")
        article.category = new_category
        
        db.commit()
        
        return {
            "success": True,
            "article_id": article.id,
            "old_category": old_category,
            "new_category": new_category,
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
            
            # סווג והחל
            classifier = get_classification_service()
            classification = classifier.classify_article(
                title=article.title,
                content=article.content or "",
                summary=article.summary or ""
            )
            
            old_category = article.category
            new_category = classification.get("category", "General")
            article.category = new_category
            
            results.append({
                "article_id": article.id,
                "success": True,
                "old_category": old_category,
                "new_category": new_category,
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
    """קבל מאמרים ללא קטגוריה או עם 'General'"""
    try:
        articles = db.query(Article).filter(
            (Article.category == None) | (Article.category == "General")
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
    """קבל את כל המאמרים - אדמין בלבד"""
    try:
        query = db.query(Article)
        
        if category:
            query = query.filter(Article.category == category)
        
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
        """קבל פרטי מאמר בודד - אדמין בלבד"""
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