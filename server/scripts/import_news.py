# server/scripts/import_news.py
"""
סקריפט לייבוא מאמרים מ-News API
"""

import sys
import os

# הוסף את תיקיית ה-server ל-path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.mvc.models.articles.article_entity import Article
from app.gateways.news_api_gateway import NewsAPIGateway


def import_articles_from_category(
    db: Session, 
    category: str, 
    limit: int = 10
) -> int:
    """ייבא מאמרים מקטגוריה מסוימת"""
    gateway = NewsAPIGateway()
    
    try:
        print(f"\n📥 מייבא מאמרים מקטגוריה: {category}")
        articles = gateway.get_top_headlines(category=category, page_size=limit)
        
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
            
            # צור מאמר חדש
            article = Article(
                title=article_data["title"],
                summary=article_data["summary"],
                content=article_data["content"],
                url=article_data["url"],
                source=article_data["source"],
                category=category.capitalize(),
                image_url=article_data["image_url"],
                thumb_url=article_data["thumb_url"],
                published_at=article_data["published_at"]
            )
            
            db.add(article)
            added_count += 1
            
            # הצג מידע
            title_short = article_data["title"][:60] + "..." if len(article_data["title"]) > 60 else article_data["title"]
            print(f"  ✅ {title_short}")
        
        db.commit()
        
        print(f"  📊 נוספו: {added_count} | דולגו (כפולים): {skipped_count}")
        
        return added_count
        
    except Exception as e:
        print(f"  ❌ שגיאה: {e}")
        db.rollback()
        return 0


def import_by_search(
    db: Session,
    query: str,
    days_back: int = 7,
    limit: int = 10
) -> int:
    """ייבא מאמרים לפי חיפוש"""
    gateway = NewsAPIGateway()
    
    try:
        print(f"\n🔍 מחפש מאמרים: '{query}' ({days_back} ימים אחורה)")
        articles = gateway.get_articles_by_topic(query, days_back=days_back, page_size=limit)
        
        added_count = 0
        skipped_count = 0
        
        for article_data in articles:
            # בדוק אם המאמר כבר קיים
            existing = db.query(Article).filter(
                Article.url == article_data["url"]
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # צור מאמר חדש
            article = Article(
                title=article_data["title"],
                summary=article_data["summary"],
                content=article_data["content"],
                url=article_data["url"],
                source=article_data["source"],
                category=article_data["category"],
                image_url=article_data["image_url"],
                thumb_url=article_data["thumb_url"],
                published_at=article_data["published_at"]
            )
            
            db.add(article)
            added_count += 1
            
            # הצג מידע
            title_short = article_data["title"][:60] + "..." if len(article_data["title"]) > 60 else article_data["title"]
            print(f"  ✅ {title_short}")
        
        db.commit()
        
        print(f"  📊 נוספו: {added_count} | דולגו (כפולים): {skipped_count}")
        
        return added_count
        
    except Exception as e:
        print(f"  ❌ שגיאה: {e}")
        db.rollback()
        return 0


def main():
    """פונקציה ראשית"""
    print("=" * 80)
    print("🌐 ייבוא מאמרים מ-News API")
    print("=" * 80)
    
    db = SessionLocal()
    total_added = 0
    
    try:
        # אופציה 1: ייבא מאמרים לפי קטגוריות
        categories = [
            ("technology", 10),
            ("business", 10),
            ("health", 10),
            ("science", 10),
            ("sports", 10)
        ]
        
        print("\n📂 מייבא מאמרים לפי קטגוריות:")
        for category, limit in categories:
            count = import_articles_from_category(db, category, limit)
            total_added += count
        
        # אופציה 2: ייבא מאמרים לפי נושאים ספציפיים (אופציונלי)
        # topics = [
        #     ("artificial intelligence", 5),
        #     ("climate change", 5),
        #     ("cryptocurrency", 5),
        # ]
        # 
        # print("\n\n🔍 מייבא מאמרים לפי נושאים:")
        # for topic, limit in topics:
        #     count = import_by_search(db, topic, days_back=7, limit=limit)
        #     total_added += count
        
        # סיכום
        print("\n" + "=" * 80)
        print(f"✅ הסתיים! סה\"כ נוספו {total_added} מאמרים חדשים")
        print("=" * 80)
        
        # הצג סטטיסטיקה כללית
        total_articles = db.query(Article).count()
        print(f"\n📊 סה\"כ מאמרים במערכת: {total_articles}")
        
        # הצג קטגוריות
        categories_in_db = db.query(Article.category).distinct().all()
        categories_list = [c[0] for c in categories_in_db if c[0]]
        print(f"📂 קטגוריות: {', '.join(categories_list)}")
        
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()