# server/app/gateways/news_api_gateway.py
"""
API Gateway for NewsAPI.ai (Event Registry)
מממש את תבנית Gateway לגישה לשירות החיצוני
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class NewsAPIGateway:
    """Gateway לשירות NewsAPI.ai (Event Registry) החיצוני"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "http://eventregistry.org/api/v1"
        
        if not self.api_key:
            raise ValueError("❌ NEWS_API_KEY לא מוגדר ב-.env")
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """בצע בקשה ל-API עם error handling"""
        try:
            params["apiKey"] = self.api_key
            url = f"{self.base_url}/{endpoint}"
            
            print(f"🌐 שולח בקשה ל-NewsAPI.ai: {endpoint}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # בדיקת שגיאות בפורמט של Event Registry
            if "error" in data:
                raise Exception(f"NewsAPI.ai Error: {data.get('error', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ שגיאה בקריאה ל-NewsAPI.ai: {e}")
            raise
    
    def _normalize_articles(self, raw_articles: List[Dict]) -> List[Dict]:
        """המר מאמרים מפורמט Event Registry לפורמט אחיד"""
        normalized = []
        
        for article in raw_articles:
            try:
                # חלץ את המקור
                source = article.get("source", {})
                source_name = source.get("title", "Unknown")
                
                # המר תאריך
                date_str = article.get("dateTimePub") or article.get("dateTime")
                published_at = self._parse_date(date_str)
                
                # בנה את המאמר המנורמל
                normalized_article = {
                    "source": source_name,
                    "author": ", ".join(article.get("authors", [])) if article.get("authors") else None,
                    "title": article.get("title", ""),
                    "description": article.get("body", "")[:200] + "..." if article.get("body") else None,
                    "url": article.get("url", ""),
                    "image_url": article.get("image"),
                    "published_at": published_at.isoformat() if published_at else None,
                    "content": article.get("body"),
                    "language": article.get("lang", "en"),
                    "sentiment": article.get("sentiment"),
                    "categories": [cat.get("label") for cat in article.get("categories", [])],
                }
                
                normalized.append(normalized_article)
            except Exception as e:
                print(f"⚠️  שגיאה בנירמול מאמר: {e}")
                continue
        
        return normalized
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """המר תאריך מ-Event Registry לפורמט שלנו"""
        if not date_str:
            return None
        
        try:
            # Event Registry מחזיר תאריכים בפורמט ISO 8601
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            print(f"⚠️  שגיאה בפירוש תאריך: {date_str} - {e}")
            return None
    
    def get_articles_by_keyword(
        self, 
        keyword: str,
        language: str = "eng",
        max_items: int = 20,
        sort_by: str = "date"
    ) -> List[Dict]:
        """
        קבל מאמרים לפי מילת חיפוש
        
        Args:
            keyword: מילת החיפוש
            language: שפה (eng, heb, deu, spa וכו')
            max_items: מספר מקסימלי של תוצאות
            sort_by: date, rel (relevance), socialScore
        """
        params = {
            "action": "getArticles",
            "keyword": keyword,
            "articlesPage": 1,
            "articlesCount": min(max_items, 100),
            "articlesSortBy": sort_by,
            "articlesSortByAsc": "false",
            "dataType": ["news", "blog"],
            "resultType": "articles",
            "lang": language,
        }
        
        data = self._make_request("article/getArticles", params)
        
        articles = data.get("articles", {}).get("results", [])
        print(f"✅ התקבלו {len(articles)} מאמרים מ-NewsAPI.ai")
        
        return self._normalize_articles(articles)
    
    def get_top_headlines(
        self, 
        category: Optional[str] = None,
        country: str = "us",
        page_size: int = 20
    ) -> List[Dict]:
        """
        קבל כותרות עיקריות (נסה לחקות את הפונקציונליות המקורית)
        
        Categories: business, technology, sports וכו'
        """
        # Event Registry עובד אחרת - נשתמש בחיפוש לפי מילת מפתח במקום קטגוריה
        if category:
            # במקום URIs מורכבים, פשוט נחפש לפי מילת המפתח
            keyword = category.lower()
            
            params = {
                "action": "getArticles",
                "keyword": keyword,
                "articlesPage": 1,
                "articlesCount": min(page_size, 100),
                "articlesSortBy": "date",
                "articlesSortByAsc": "false",
                "dataType": ["news"],
                "resultType": "articles",
                "lang": "eng",
            }
        else:
            # ללא קטגוריה - פשוט מאמרים אחרונים
            params = {
                "action": "getArticles",
                "articlesPage": 1,
                "articlesCount": min(page_size, 100),
                "articlesSortBy": "date",
                "articlesSortByAsc": "false",
                "dataType": ["news"],
                "resultType": "articles",
                "lang": "eng",
            }
        
        data = self._make_request("article/getArticles", params)
        
        articles = data.get("articles", {}).get("results", [])
        print(f"✅ התקבלו {len(articles)} מאמרים מ-NewsAPI.ai (קטגוריה: {category or 'כללי'})")
        
        return self._normalize_articles(articles)
    
    def search_articles(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "eng",
        page_size: int = 20
    ) -> List[Dict]:
        """
        חפש מאמרים לפי מילות חיפוש
        """
        params = {
            "action": "getArticles",
            "keyword": query,
            "articlesPage": 1,
            "articlesCount": min(page_size, 100),
            "articlesSortBy": "rel",  # relevance
            "articlesSortByAsc": "false",
            "dataType": ["news"],
            "resultType": "articles",
            "lang": language,
        }
        
        if from_date:
            params["dateStart"] = from_date.strftime("%Y-%m-%d")
        
        if to_date:
            params["dateEnd"] = to_date.strftime("%Y-%m-%d")
        
        data = self._make_request("article/getArticles", params)
        
        articles = data.get("articles", {}).get("results", [])
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