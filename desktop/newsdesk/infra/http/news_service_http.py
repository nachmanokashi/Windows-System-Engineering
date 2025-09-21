from typing import List, Optional, Dict, Any
from datetime import datetime
from newsdesk.mvp.model.article import Article
from newsdesk.infra.http.news_api_client import NewsApiClient

class HttpNewsService:
    def __init__(self, api: NewsApiClient) -> None:
        self._api = api

    def _parse(self, data: Dict[str, Any]) -> Article:
        return Article(
            id=str(data["id"]),
            title=data["title"],
            summary=data.get("summary", ""),
            source=data.get("source", ""),
            published_at=datetime.fromisoformat(data["published_at"]),
            category=data.get("category", ""),
        )

    def categories(self) -> List[str]:
        res = self._api.get("/articles/categories")
        return list(res.get("items", []))

    def top(self, limit: int = 20, category: Optional[str] = None) -> List[Article]:
        params: Dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = category
        res = self._api.get("/articles", params=params)
        return [self._parse(a) for a in res.get("items", [])]

    def search(self, query: str, limit: int = 20, category: Optional[str] = None) -> List[Article]:
        params: Dict[str, Any] = {"q": query, "limit": limit}
        if category:
            params["category"] = category
        res = self._api.get("/articles/search", params=params)
        return [self._parse(a) for a in res.get("items", [])]

    def get(self, article_id: str) -> Optional[Article]:
        res = self._api.get(f"/articles/{article_id}")
        item = res.get("item")
        return self._parse(item) if item else None
