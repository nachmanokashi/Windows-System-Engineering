from typing import Dict, Any, List, Optional
from newsdesk.infra.http.news_api_client import NewsApiClient


class HttpAdminService:
    """שירות ניהול מאמרים למנהלים"""
    
    def __init__(self, api: NewsApiClient):
        self._api = api
    
    def create_article(
        self,
        title: str,
        summary: str,
        content: str,
        url: str,
        source: str,
        category: Optional[str] = None,
        image_url: Optional[str] = None,
        auto_classify: bool = True
    ) -> Dict[str, Any]:
        """
        צור מאמר חדש
        
        Returns:
            {
                "success": True,
                "article_id": 123,
                "category": "Technology",
                "classification": {...}
            }
        """
        payload = {
            "title": title,
            "summary": summary,
            "content": content,
            "url": url,
            "source": source,
            "auto_classify": auto_classify
        }
        
        if category:
            payload["category"] = category
        if image_url:
            payload["image_url"] = image_url
            payload["thumb_url"] = image_url
        
        return self._api.post("/admin/articles", json=payload)
    
    def update_article(
        self,
        article_id: int,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        url: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """עדכן מאמר קיים"""
        payload = {}
        
        if title is not None:
            payload["title"] = title
        if summary is not None:
            payload["summary"] = summary
        if content is not None:
            payload["content"] = content
        if url is not None:
            payload["url"] = url
        if source is not None:
            payload["source"] = source
        if category is not None:
            payload["category"] = category
        if image_url is not None:
            payload["image_url"] = image_url
            payload["thumb_url"] = image_url
        
        return self._api.put(f"/admin/articles/{article_id}", json=payload)
    
    def delete_article(self, article_id: int) -> Dict[str, Any]:
        """מחק מאמר"""
        return self._api.delete(f"/admin/articles/{article_id}")
    
    def classify_article(self, article_id: int) -> Dict[str, Any]:
        """
        קבל הצעת סיווג למאמר
        
        Returns:
            {
                "article_id": 123,
                "current_category": "General",
                "suggested_category": "Technology",
                "confidence": 0.95,
                "all_suggestions": [...]
            }
        """
        return self._api.post(f"/admin/articles/{article_id}/classify")
    
    def apply_classification(self, article_id: int) -> Dict[str, Any]:
        """החל סיווג אוטומטי על מאמר"""
        return self._api.post(f"/admin/articles/{article_id}/apply-classification")
    
    def batch_classify(self, article_ids: List[int]) -> Dict[str, Any]:
        """סווג מספר מאמרים בבת אחת"""
        return self._api.post("/admin/articles/batch-classify", json={"article_ids": article_ids})
    
    def get_uncategorized_articles(self, limit: int = 50) -> Dict[str, Any]:
        """קבל מאמרים ללא קטגוריה"""
        return self._api.get("/admin/articles/uncategorized", params={"limit": limit})
    
    def get_available_categories(self) -> List[str]:
        """קבל רשימת קטגוריות זמינות"""
        result = self._api.get("/admin/categories")
        return result.get("categories", [])