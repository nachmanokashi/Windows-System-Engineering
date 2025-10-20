# server/scripts/interactive_import.py
"""
ייבוא אינטראקטיבי של מאמרים - בחר קטגוריות ומספר מאמרים
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.mvc.models.articles.article_entity import Article
from app.gateways.news_api_gateway import NewsAPIGateway
from datetime import datetime


# 📚 רשימת קטגוריות פופולריות
POPULAR_CATEGORIES = {
    "1": {"name": "Technology", "keywords": ["technology", "AI", "software"]},
    "2": {"name": "Business", "keywords": ["business", "economy", "finance"]},
    "3": {"name": "Sports", "keywords": ["sports", "football", "basketball"]},
    "4": {"name": "Health", "keywords": ["health", "medicine", "wellness"]},
    "5": {"name": "Science", "keywords": ["science", "research", "space"]},
    "6": {"name": "Entertainment", "keywords": ["entertainment", "movies", "music"]},
    "7": {"name": "Politics", "keywords": ["politics", "election", "government"]},
    "8": {"name": "Environment", "keywords": ["climate", "environment", "sustainability"]},
    "9": {"name": "Education", "keywords": ["education", "university", "learning"]},
    "10": {"name": "Travel", "keywords": ["travel", "tourism", "vacation"]},
}


def import_by_keyword(db: Session, keyword: str, category: str, count: int) -> int:
    """ייבא מאמרים לפי מילת מפתח"""
    gateway = NewsAPIGateway()
    
    try:
        print(f"\n🔍 מחפש מאמרים על '{keyword}'...")
        articles = gateway.get_articles_by_keyword(keyword, max_items=count)
        
        if not articles:
            print(f"  ⚠️  לא נמצאו מאמרים")
            return 0
        
        added = 0
        skipped = 0
        
        for article_data in articles:
            # בדוק אם קיים
            existing = db.query(Article).filter(Article.url == article_data["url"]).first()
            if existing:
                skipped += 1
                continue
            
            # המר תאריך
            published_at = None
            if article_data.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(article_data["published_at"].replace("Z", "+00:00"))
                except:
                    pass
            
            # צור מאמר
            article = Article(
                title=article_data["title"],
                summary=article_data.get("description") or article_data["title"][:200],
                content=article_data.get("content") or article_data.get("description"),
                url=article_data["url"],
                source=article_data["source"],
                category=category,
                image_url=article_data.get("image_url"),
                thumb_url=article_data.get("image_url"),
                published_at=published_at
            )
            
            db.add(article)
            added += 1
            print(f"  ✅ {article.title[:55]}...")
        
        db.commit()
        
        if added > 0:
            print(f"\n  ✨ נוספו {added} מאמרים חדשים לקטגוריה '{category}'")
        if skipped > 0:
            print(f"  ⏭️  דולגו על {skipped} מאמרים קיימים")
        
        return added
        
    except Exception as e:
        print(f"  ❌ שגיאה: {e}")
        db.rollback()
        return 0


def show_menu():
    """הצג תפריט קטגוריות"""
    print("\n" + "=" * 70)
    print("📰 בחר קטגוריות לייבוא:")
    print("=" * 70)
    
    for key, cat in POPULAR_CATEGORIES.items():
        keywords_str = ", ".join(cat["keywords"][:2])
        print(f"  {key}. {cat['name']:<15} (מילות מפתח: {keywords_str})")
    
    print(f"\n  0. ❌ סיים וצא")
    print(f"  all. 🌟 ייבא הכל (מומלץ!)")
    print(f"  custom. ✏️  הזן מילת מפתח מותאמת אישית")
    print("=" * 70)


def import_all_categories(db: Session, count_per_category: int = 10):
    """ייבא מכל הקטגוריות"""
    total = 0
    
    print(f"\n🚀 מייבא {count_per_category} מאמרים מכל קטגוריה...")
    
    for cat_data in POPULAR_CATEGORIES.values():
        print(f"\n{'='*70}")
        print(f"📂 קטגוריה: {cat_data['name']}")
        print(f"{'='*70}")
        
        # נסה עם כל מילת מפתח עד שמצליחים
        for keyword in cat_data['keywords']:
            added = import_by_keyword(db, keyword, cat_data['name'], count_per_category)
            if added > 0:
                total += added
                break  # מצאנו מאמרים, עובר לקטגוריה הבאה
    
    return total


def import_custom_keyword(db: Session, keyword: str, category: str, count: int):
    """ייבא עם מילת מפתח מותאמת אישית"""
    print(f"\n🎨 ייבוא מותאם אישית:")
    print(f"  מילת מפתח: {keyword}")
    print(f"  קטגוריה: {category}")
    print(f"  כמות: {count}")
    
    return import_by_keyword(db, keyword, category, count)


def main():
    """תפריט ראשי"""
    print("\n" + "🎉" * 35)
    print("  ברוך הבא למערכת ייבוא המאמרים האינטראקטיבית!")
    print("🎉" * 35)
    
    db = SessionLocal()
    total_imported = 0
    
    try:
        while True:
            show_menu()
            choice = input("\n👉 בחר אפשרות: ").strip().lower()
            
            if choice == "0":
                print("\n👋 יציאה...")
                break
            
            elif choice == "all":
                print("\n📊 כמה מאמרים לייבא מכל קטגוריה?")
                count = input("   הזן מספר (ברירת מחדל: 10): ").strip()
                count = int(count) if count.isdigit() else 10
                
                imported = import_all_categories(db, count)
                total_imported += imported
            
            elif choice == "custom":
                keyword = input("\n✏️  הזן מילת מפתח לחיפוש: ").strip()
                if not keyword:
                    print("❌ חייב להזין מילת מפתח!")
                    continue
                
                category = input("   הזן שם קטגוריה (או Enter לברירת מחדל): ").strip()
                category = category if category else keyword.capitalize()
                
                count_str = input("   כמה מאמרים? (ברירת מחדל: 10): ").strip()
                count = int(count_str) if count_str.isdigit() else 10
                
                imported = import_custom_keyword(db, keyword, category, count)
                total_imported += imported
            
            elif choice in POPULAR_CATEGORIES:
                cat_data = POPULAR_CATEGORIES[choice]
                
                print(f"\n📂 קטגוריה נבחרה: {cat_data['name']}")
                print(f"   מילות מפתח זמינות: {', '.join(cat_data['keywords'])}")
                
                keyword_choice = input(f"   בחר מילת מפתח (Enter לראשונה): ").strip()
                keyword = keyword_choice if keyword_choice else cat_data['keywords'][0]
                
                count_str = input("   כמה מאמרים? (ברירת מחדל: 15): ").strip()
                count = int(count_str) if count_str.isdigit() else 15
                
                imported = import_by_keyword(db, keyword, cat_data['name'], count)
                total_imported += imported
            
            else:
                print("❌ בחירה לא חוקית!")
            
            # הצג סטטיסטיקה
            print(f"\n📊 סה\"כ יובאו עד כה: {total_imported} מאמרים")
            
            # שאל אם להמשיך
            continue_choice = input("\n🔄 לייבא עוד קטגוריות? (y/n): ").strip().lower()
            if continue_choice != 'y':
                break
        
        # סיכום
        print("\n" + "=" * 70)
        print(f"🎊 סיום! סה\"כ יובאו {total_imported} מאמרים חדשים")
        print("=" * 70)
        print("\n💡 עכשיו הפעל מחדש את השרת כדי לראות את המאמרים החדשים!")
        print("   python -m uvicorn app.main:app --reload")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  פעולה בוטלה על ידי המשתמש")
    except Exception as e:
        print(f"\n❌ שגיאה לא צפויה: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()