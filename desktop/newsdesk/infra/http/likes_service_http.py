# newsdesk/infra/http/likes_service_http.py
from typing import Dict, Any
from newsdesk.infra.http.news_api_client import NewsApiClient

class HttpLikesService:
    """שירות Likes"""
    
    def __init__(self, api: NewsApiClient) -> None:
        self._api = api
    
    def like_article(self, article_id: int) -> Dict[str, Any]:
        """לייק למאמר"""
        return self._api.post(f"/articles/{article_id}/like")
    
    def unlike_article(self, article_id: int) -> Dict[str, Any]:
        """הסרת לייק"""
        return self._api.delete(f"/articles/{article_id}/like")
    
    def get_article_stats(self, article_id: int) -> Dict[str, Any]:
        """קבלת סטטיסטיקות"""
        return self._api.get(f"/articles/{article_id}/stats")