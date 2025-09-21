from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any
from ..views.article_out import ArticleOut
from ..models.articles.article_service import NewsService
from ..models.articles.article_repo_inmemory import InMemoryArticleRepository

router = APIRouter(prefix="/articles", tags=["articles"])

def get_service() -> NewsService:
    return NewsService(InMemoryArticleRepository())

@router.get("", response_model=Dict[str, Any])
def list_articles(limit: int = Query(20, ge=1, le=100),
                  svc: NewsService = Depends(get_service)) -> Dict[str, Any]:
    items = svc.top(limit)
    return {"items": [ArticleOut(**a.__dict__).model_dump() for a in items]}

@router.get("/search", response_model=Dict[str, Any])
def search_articles(q: str, limit: int = Query(20, ge=1, le=100),
                    svc: NewsService = Depends(get_service)) -> Dict[str, Any]:
    items = svc.search(q, limit)
    return {"items": [ArticleOut(**a.__dict__).model_dump() for a in items]}

@router.get("/{article_id}", response_model=Dict[str, Any])
def get_article(article_id: str,
                svc: NewsService = Depends(get_service)) -> Dict[str, Any]:
    item = svc.get(article_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"item": ArticleOut(**item.__dict__).model_dump()}
