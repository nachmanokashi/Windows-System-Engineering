import httpx
from typing import Any, Dict, Optional


class NewsApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1") -> None:
        self._client = httpx.Client(
            base_url=base_url, 
            timeout=30.0  
        )
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
        try:
            r = self._client.get(path, params=params, headers=self._get_headers())
            r.raise_for_status()
            return r.json()
        except httpx.TimeoutException:
            print(f"⏰ Timeout on GET {path}")
            raise
        except Exception as e:
            print(f"❌ Error on GET {path}: {e}")
            raise
    
    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST request"""
        try:
            r = self._client.post(path, json=json, headers=self._get_headers())
            r.raise_for_status()
            return r.json()
        except httpx.TimeoutException:
            print(f"⏰ Timeout on POST {path}")
            raise
        except Exception as e:
            print(f"❌ Error on POST {path}: {e}")
            raise
    
    def put(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUT request"""
        try:
            r = self._client.put(path, json=json, headers=self._get_headers())
            r.raise_for_status()
            return r.json()
        except httpx.TimeoutException:
            print(f"⏰ Timeout on PUT {path}")
            raise
        except Exception as e:
            print(f"❌ Error on PUT {path}: {e}")
            raise
    
    def delete(self, path: str) -> Dict[str, Any]:
        """DELETE request"""
        try:
            r = self._client.delete(path, headers=self._get_headers())
            r.raise_for_status()
            return r.json() if r.content else {}
        except httpx.TimeoutException:
            print(f"⏰ Timeout on DELETE {path}")
            raise
        except Exception as e:
            print(f"❌ Error on DELETE {path}: {e}")
            raise
    
    def close(self) -> None:
        """סגירת החיבור"""
        self._client.close()
