# server/scripts/import_news.py
"""
סקריפט לייבוא מאמרים מ-NewsAPI.ai (Event Registry)
"""

import sys
import os

# הוסף את תיקיית ה-server ל-path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.mvc.models.articles.article_entity import Article
from app.gateways.news_api_gateway import NewsAPIGateway
from datetime import datetime


def clear_old_articles(db: Session):
    """נקה מאמרים ישנים (אופציונלי)"""
    print("\n🗑️  האם למחוק מאמרים ישנים? (y/n): ", end="")
    answer = input().strip().lower()
    
    if answer == 'y':
        count = db.query(Article).delete()
        db.commit()
        print(f"✅ נמחקו {count} מאמרים ישנים")
    else:
        print("⏭️  דילגנו על מחיקת מאמרים ישנים")


def import_articles_from_keyword(
    db: Session, 
    keyword: str, 
    limit: int = 20,
    category_name: str = None
) -> int:
    """ייבא מאמרים לפי מילת חיפוש"""
    gateway = NewsAPIGateway()
    
    try:
        print(f"\n📥 מייבא מאמרים עבור: '{keyword}' (מקסימום: {limit})")
        articles = gateway.get_articles_by_keyword(keyword, max_items=limit)
        
        if not articles:
            print(f"⚠️  לא נמצאו מאמרים עבור '{keyword}'")
            return 0
        
        added_count = 0
        skipped_count = 0
        
        for article_data in articles:
            # בדוק אם המאמר כבר קיים (לפי URL)
            existing = db.query(Article).filter(
                Article.url == article_data["url"]
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # קבע קטגוריה
            category = category_name or keyword.capitalize()
            if article_data.get("categories"):
                category = article_data["categories"][0] if article_data["categories"] else category
            
            # המר תאריך
            published_at = None
            if article_data.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(article_data["published_at"].replace("Z", "+00:00"))
                except:
                    pass
            
            # צור מאמר חדש
            article = Article(
                title=article_data["title"],
                summary=article_data.get("description") or article_data["title"][:200],
                content=article_data.get("content") or article_data.get("description"),
                url=article_data["url"],
                source=article_data["source"],
                category=category,
                image_url=article_data.get("image_url"),
                thumb_url=article_data.get("image_url"),  # נשתמש באותה תמונה
                published_at=published_at
            )
            
            db.add(article)
            added_count += 1
            print(f"  ✅ נוסף: {article.title[:60]}...")
        
        db.commit()
        
        print(f"\n✅ סה\"כ נוספו {added_count} מאמרים חדשים")
        if skipped_count > 0:
            print(f"⏭️  דולגו על {skipped_count} מאמרים קיימים")
        
        return added_count
        
    except Exception as e:
        print(f"❌ שגיאה בייבוא: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return 0


def main():
    """פונקציה ראשית"""
    print("=" * 70)
    print("📰 ייבוא מאמרים מ-NewsAPI.ai")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # שאל אם למחוק מאמרים ישנים
        clear_old_articles(db)
        
        # רשימת נושאים לייבוא
        topics = [
            ("technology", "Technology", 15),
            ("business", "Business", 15),
            ("health", "Health", 10),
            ("sports", "Sports", 10),
            ("science", "Science", 10),
        ]
        
        total_imported = 0
        
        for keyword, category, limit in topics:
            count = import_articles_from_keyword(db, keyword, limit, category)
            total_imported += count
        
        print("\n" + "=" * 70)
        print(f"🎉 סה\"כ יובאו {total_imported} מאמרים חדשים!")
        print("=" * 70)
        print("\n💡 עכשיו תוכל לראות את המאמרים החדשים באפליקציה")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()