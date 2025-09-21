from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional
from ..views.article_out import ArticleOut
from ..models.articles.article_service import NewsService
from ..models.articles.article_repo_inmemory import InMemoryArticleRepository
from ..models.articles.article_entity import Article

router = APIRouter(prefix="/articles", tags=["articles"])

def get_service() -> NewsService:
    return NewsService(InMemoryArticleRepository())

# ממפה ישות דומיין ל-DTO (ומחזיר dict ל-JSON)
def _to_out(a: Article) -> Dict[str, Any]:
    return ArticleOut(
        id=a.id,
        title=a.title,
        summary=a.summary,
        source=a.source,
        published_at=a.published_at,
        category=a.category.value,  # המרה מ-Enum לערך
    ).model_dump()

@router.get("/categories", response_model=Dict[str, Any])
def list_categories(svc: NewsService = Depends(get_service)) -> Dict[str, Any]:
    return {"items": svc.categories()}

@router.get("", response_model=Dict[str, Any])
def list_articles(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(default=None),
    svc: NewsService = Depends(get_service),
) -> Dict[str, Any]:
    items = svc.top(limit, category)
    return {"items": [_to_out(a) for a in items]}

@router.get("/search", response_model=Dict[str, Any])
def search_articles(
    q: str,
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(default=None),
    svc: NewsService = Depends(get_service),
) -> Dict[str, Any]:
    items = svc.search(q, limit, category)
    return {"items": [_to_out(a) for a in items]}

@router.get("/{article_id}", response_model=Dict[str, Any])
def get_article(
    article_id: str,
    svc: NewsService = Depends(get_service),
) -> Dict[str, Any]:
    item = svc.get(article_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"item": _to_out(item)}
