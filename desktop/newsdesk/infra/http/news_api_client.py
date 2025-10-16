# newsdesk/infra/http/news_api_client.py
import httpx
from typing import Any, Dict, Optional

class NewsApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1") -> None:
        self._client = httpx.Client(base_url=base_url, timeout=10.0)
        self._auth_token: Optional[str] = None
    
    def set_auth_token(self, token: str) -> None:
        """הגדרת JWT token לכל הקריאות"""
        self._auth_token = token
    
    def clear_auth_token(self) -> None:
        """ניקוי הטוקן"""
        self._auth_token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """בניית headers עם authentication"""
        headers = {"Content-Type": "application/json"}
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET request"""
        r = self._client.get(path, params=params, headers=self._get_headers())
        r.raise_for_status()
        return r.json()
    
    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST request"""
        r = self._client.post(path, json=json, headers=self._get_headers())
        r.raise_for_status()
        return r.json()
    
    def put(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUT request"""
        r = self._client.put(path, json=json, headers=self._get_headers())
        r.raise_for_status()
        return r.json()
    
    def delete(self, path: str) -> Dict[str, Any]:
        """DELETE request"""
        r = self._client.delete(path, headers=self._get_headers())
        r.raise_for_status()
        return r.json() if r.content else {}
    
    