# server/app/gateways/news_api_gateway.py
"""
API Gateway for News API
מממש את תבנית Gateway לגישה לשירות חיצוני
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class NewsAPIGateway:
    """Gateway לשירות News API החיצוני"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = os.getenv("NEWS_API_BASE_URL", "https://newsapi.org/v2")
        
        if not self.api_key:
            raise ValueError("❌ NEWS_API_KEY לא מוגדר ב-.env")
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """בצע בקשה ל-API עם error handling"""
        try:
            params["apiKey"] = self.api_key
            url = f"{self.base_url}/{endpoint}"
            
            print(f"🌐 שולח בקשה ל-News API: {endpoint}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                raise Exception(f"News API Error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ שגיאה בקריאה ל-News API: {e}")
            raise
    
    def get_top_headlines(
        self, 
        category: Optional[str] = None,
        country: str = "us",
        page_size: int = 20
    ) -> List[Dict]:
        """
        קבל כותרות עיקריות
        
        Categories: business, entertainment, general, health, science, sports, technology
        Countries: us, gb, il, etc.
        """
        params = {
            "country": country,
            "pageSize": page_size
        }
        
        if category:
            params["category"] = category
        
        data = self._make_request("top-headlines", params)
        
        articles = data.get("articles", [])
        print(f"✅ התקבלו {len(articles)} מאמרים מ-News API")
        
        return self._normalize_articles(articles)
    
    def search_articles(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        page_size: int = 20
    ) -> List[Dict]:
        """
        חפש מאמרים לפי מילות חיפוש
        """
        params = {
            "q": query,
            "language": language,
            "pageSize": page_size,
            "sortBy": "publishedAt"
        }
        
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        
        data = self._make_request("everything", params)
        
        articles = data.get("articles", [])
        print(f"✅ התקבלו {len(articles)} מאמרים עבור חיפוש: '{query}'")
        
        return self._normalize_articles(articles)
    
    def get_articles_by_topic(
        self,
        topic: str,
        days_back: int = 7,
        page_size: int = 20
    ) -> List[Dict]:
        """קבל מאמרים לפי נושא מהימים האחרונים"""
        from_date = datetime.utcnow() - timedelta(days=days_back)
        return self.search_articles(
            query=topic,
            from_date=from_date,
            page_size=page_size
        )
    
    def _normalize_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        המר את פורמט News API לפורמט שלנו
        """
        normalized = []
        
        for article in articles:
            # דלג על מאמרים ללא כותרת או תוכן
            if not article.get("title") or article.get("title") == "[Removed]":
                continue
            
            # המר לפורמט שלנו
            normalized_article = {
                "title": article.get("title", ""),
                "summary": article.get("description", "")[:500] if article.get("description") else "",
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "category": self._map_category(article),
                "image_url": article.get("urlToImage", ""),
                "thumb_url": article.get("urlToImage", ""),
                "published_at": self._parse_date(article.get("publishedAt")),
                "author": article.get("author", "")
            }
            
            normalized.append(normalized_article)
        
        return normalized
    
    def _map_category(self, article: Dict) -> str:
        """נסה לזהות קטגוריה מהמאמר"""
        # ניתן להשתמש בהמון היוריסטיקות כאן
        # לעת עתה, נחזיר "General"
        return "General"
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """המר תאריך מ-News API לפורמט שלנו"""
        if not date_str:
            return None
        
        try:
            # News API מחזיר תאריכים בפורמט ISO 8601
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            print(f"⚠️  שגיאה בפירוש תאריך: {date_str} - {e}")
            return None


# ============================================
# פונקציות עזר לשימוש מהיר
# ============================================

def fetch_tech_news(limit: int = 10) -> List[Dict]:
    """קבל חדשות טכנולוגיה"""
    gateway = NewsAPIGateway()
    return gateway.get_top_headlines(category="technology", page_size=limit)


def fetch_health_news(limit: int = 10) -> List[Dict]:
    """קבל חדשות בריאות"""
    gateway = NewsAPIGateway()
    return gateway.get_top_headlines(category="health", page_size=limit)


def fetch_business_news(limit: int = 10) -> List[Dict]:
    """קבל חדשות עסקים"""
    gateway = NewsAPIGateway()
    return gateway.get_top_headlines(category="business", page_size=limit)


def fetch_sports_news(limit: int = 10) -> List[Dict]:
    """קבל חדשות ספורט"""
    gateway = NewsAPIGateway()
    return gateway.get_top_headlines(category="sports", page_size=limit)


def search_news(query: str, days_back: int = 7, limit: int = 10) -> List[Dict]:
    """חפש חדשות לפי נושא"""
    gateway = NewsAPIGateway()
    return gateway.get_articles_by_topic(query, days_back=days_back, page_size=limit)