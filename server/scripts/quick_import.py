# server/scripts/quick_import.py
"""
ייבוא מהיר של כמה מאמרים לבדיקה
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.mvc.models.articles.article_entity import Article
from app.gateways.news_api_gateway import NewsAPIGateway
from datetime import datetime


def quick_import():
    """ייבא 10 מאמרים מהירים לבדיקה"""
    print("🚀 ייבוא מהיר של 10 מאמרים...")
    
    db = SessionLocal()
    gateway = NewsAPIGateway()
    
    try:
        # קבל 10 מאמרים על טכנולוגיה
        articles = gateway.get_articles_by_keyword("technology", max_items=10)
        
        if not articles:
            print("❌ לא נמצאו מאמרים")
            return
        
        added = 0
        for article_data in articles:
            # בדוק אם קיים
            existing = db.query(Article).filter(Article.url == article_data["url"]).first()
            if existing:
                continue
            
            # המר תאריך
            published_at = None
            if article_data.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(article_data["published_at"].replace("Z", "+00:00"))
                except:
                    pass
            
            # הוסף למסד
            article = Article(
                title=article_data["title"],
                summary=article_data.get("description") or article_data["title"][:200],
                content=article_data.get("content") or article_data.get("description"),
                url=article_data["url"],
                source=article_data["source"],
                category="Technology",
                image_url=article_data.get("image_url"),
                thumb_url=article_data.get("image_url"),
                published_at=published_at
            )
            
            db.add(article)
            added += 1
            print(f"✅ {article.title[:50]}...")
        
        db.commit()
        print(f"\n🎉 נוספו {added} מאמרים חדשים!")
        print("💡 עכשיו תוכל לראות אותם בשרת")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    quick_import()