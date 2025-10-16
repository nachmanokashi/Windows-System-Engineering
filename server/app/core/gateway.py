"""
API Gateway - מנהל את כל הקריאות לשירותים חיצוניים
מיישם: Rate Limiting, Caching, Error Handling, Retry Logic
"""

import requests
import time
from typing import Optional, Dict, Any
from functools import lru_cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class APIGateway:
    """
    Gateway לניהול קריאות API חיצוניות
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.request_count = {}
        self.cache = {}
        
    def _check_rate_limit(self, service_name: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """בדיקת Rate Limiting"""
        current_time = time.time()
        
        if service_name not in self.request_count:
            self.request_count[service_name] = []
        
        # נקה requests ישנים
        self.request_count[service_name] = [
            req_time for req_time in self.request_count[service_name]
            if current_time - req_time < window_seconds
        ]
        
        # בדוק אם עברנו את הלימיט
        if len(self.request_count[service_name]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {service_name}")
            return False
        
        # הוסף את הrequest הנוכחי
        self.request_count[service_name].append(current_time)
        return True
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """יצירת cache key"""
        param_str = str(sorted(params.items())) if params else ""
        return f"{url}:{param_str}"
    
    def _get_from_cache(self, cache_key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """קבלת תוצאה מה-cache"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < ttl_seconds:
                logger.info(f"Cache hit for {cache_key}")
                return cached_data
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """שמירה ב-cache"""
        self.cache[cache_key] = (data, time.time())
    
    def request(
        self,
        method: str,
        url: str,
        service_name: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: int = 30,
        max_retries: int = 3,
        cache_ttl: Optional[int] = None,
        rate_limit: int = 100
    ) -> Dict[str, Any]:
        """
        ביצוע request עם כל התכונות של Gateway
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            service_name: שם השירות (לrate limiting)
            headers: HTTP headers
            params: Query parameters
            json: JSON body
            timeout: Timeout in seconds
            max_retries: מספר ניסיונות חוזרים
            cache_ttl: זמן שמירה ב-cache (רק ל-GET)
            rate_limit: מקסימום requests לדקה
        """
        
        # בדיקת Rate Limit
        if not self._check_rate_limit(service_name, max_requests=rate_limit):
            raise Exception(f"Rate limit exceeded for {service_name}")
        
        # בדיקת Cache (רק ל-GET requests)
        if method.upper() == "GET" and cache_ttl:
            cache_key = self._get_cache_key(url, params)
            cached_result = self._get_from_cache(cache_key, cache_ttl)
            if cached_result:
                return cached_result
        
        # ביצוע Request עם Retry Logic
        last_exception = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Requesting {service_name}: {method} {url} (attempt {attempt + 1}/{max_retries})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    timeout=timeout
                )
                
                response.raise_for_status()
                result = response.json() if response.content else {}
                
                # שמירה ב-cache
                if method.upper() == "GET" and cache_ttl:
                    cache_key = self._get_cache_key(url, params)
                    self._set_cache(cache_key, result)
                
                logger.info(f"Request successful for {service_name}")
                return result
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout on attempt {attempt + 1} for {service_name}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error for {service_name}: {e}")
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.error(f"Request failed for {service_name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Unexpected error for {service_name}: {e}")
                raise
        
        # אם הגענו לכאן, כל הניסיונות נכשלו
        raise Exception(f"Failed to request {service_name} after {max_retries} attempts: {last_exception}")
    
    def get(self, url: str, service_name: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return self.request("GET", url, service_name, **kwargs)
    
    def post(self, url: str, service_name: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return self.request("POST", url, service_name, **kwargs)
    
    def clear_cache(self, service_name: Optional[str] = None):
        """ניקוי cache"""
        if service_name:
            self.cache = {k: v for k, v in self.cache.items() if service_name not in k}
        else:
            self.cache.clear()
        logger.info(f"Cache cleared for {service_name or 'all services'}")


# Singleton instance
_gateway_instance: Optional[APIGateway] = None

def get_gateway() -> APIGateway:
    """קבלת instance של Gateway"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = APIGateway()
    return _gateway_instance