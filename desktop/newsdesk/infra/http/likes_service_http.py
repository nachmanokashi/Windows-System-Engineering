from typing import Dict, Any, List
from newsdesk.infra.http.news_api_client import NewsApiClient

class HttpLikesService:
    """שירות Likes"""
    
    def __init__(self, api: NewsApiClient) -> None:
        self._api = api
    
    def like_article(self, article_id: int) -> Dict[str, Any]:
        return self._api.post(f"/articles/{article_id}/like")
    
    def unlike_article(self, article_id: int) -> Dict[str, Any]:
        return self._api.delete(f"/articles/{article_id}/like")

    def dislike_article(self, article_id: int) -> Dict[str, Any]:
        return self._api.post(f"/articles/{article_id}/dislike")

    def remove_dislike(self, article_id: int) -> Dict[str, Any]:
        return self._api.delete(f"/articles/{article_id}/dislike")
    
    def get_article_stats(self, article_id: int) -> Dict[str, Any]:
        return self._api.get(f"/articles/{article_id}/stats")

    def get_batch_stats(self, article_ids: List[int]) -> Dict[str, Any]:
        """קבלת סטטיסטיקות למספר מאמרים בבת אחת באמצעות POST"""
        return self._api.post("/articles/batch-stats", json={"ids": article_ids})