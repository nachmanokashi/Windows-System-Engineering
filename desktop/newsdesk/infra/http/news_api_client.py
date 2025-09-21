import httpx
from typing import Any, Dict, Optional

class NewsApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1") -> None:
        self._client = httpx.Client(base_url=base_url, timeout=5.0)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        r = self._client.get(path, params=params)
        r.raise_for_status()
        return r.json()
