# server/scripts/add_articles.py
"""
סקריפט להוספת מאמרים למערכת
אפשרויות:
1. הוספה ידנית של מאמרים
2. שליפה אוטומטית מ-News API
3. יצירת מאמרים דמה לבדיקות
"""

import sys
import os
from datetime import datetime, timedelta
import random

# הוסף את תיקיית ה-server ל-path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.mvc.models.articles.article_entity import Article


# ============================================
# מאמרים לדוגמה בתחומים שונים
# ============================================

SAMPLE_ARTICLES = [
    {
        "title": "פריצת דרך בטכנולוגיית AI: מודל חדש מבין הקשר כמו בני אדם",
        "summary": "חוקרים פיתחו מודל בינה מלאכותית חדש שמסוגל להבין הקשר ורגשות בשיחות כמעט כמו בני אדם",
        "content": """
        במעבדות המחקר של אוניברסיטת סטנפורד פותח מודל AI חדשני שמסוגל להבין הקשר רגשי בשיחות.
        המודל, שנקרא "ContextPro", משתמש בארכיטקטורת Transformer משופרת המאפשרת לו לזהות 
        גוונים רגשיים עדינים בטקסט ודיבור.
        
        המודל עבר אימון על מיליוני שיחות אנושיות ומסוגל כעת לזהות:
        - סרקזם ואירוניה
        - רגשות נסתרים
        - כוונות מרומזות
        - הקשר תרבותי
        
        החוקרים מדווחים על דיוק של 94% בזיהוי רגשות, לעומת 87% במודלים קודמים.
        הטכנולוגיה עשויה לשנות את תחום שירות הלקוחות, טיפול נפשי דיגיטלי, וממשקי שיחה.
        """,
        "url": "https://example.com/ai-breakthrough",
        "source": "Tech News",
        "category": "Technology",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"
    },
    {
        "title": "מחקר חדש: תזונה ים-תיכונית מפחיתה סיכון למחלות לב ב-40%",
        "summary": "מחקר ענק שנערך על 10,000 משתתפים מצא קשר ברור בין תזונה ים-תיכונית לבריאות הלב",
        "content": """
        מחקר חדש שפורסם בכתב העת JAMA הרפואי מגלה כי תזונה ים-תיכונית מפחיתה באופן 
        משמעותי את הסיכון למחלות לב וכלי דם.
        
        המחקר, שנמשך 12 שנים ועקב אחר 10,000 משתתפים מ-23 מדינות, מצא כי:
        
        - ירידה של 40% בסיכון לאוטם שריר הלב
        - ירידה של 35% בסיכון לשבץ מוחי
        - שיפור ברמות הכולסטרול ב-28%
        - הפחתת לחץ דם ב-15%
        
        עקרונות התזונה כוללים:
        • שמן זית כשומן עיקרי
        • דגים 2-3 פעמים בשבוע
        • ירקות ופירות טריים
        • קטניות ודגנים מלאים
        • מעט בשר אדום
        
        החוקרים ממליצים לאמץ את התזונה בהדרגה לתוצאות מיטביות.
        """,
        "url": "https://example.com/mediterranean-diet",
        "source": "Health Magazine",
        "category": "Health",
        "image_url": "https://images.unsplash.com/photo-1505253758473-96b7015fcd40?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1505253758473-96b7015fcd40?w=400"
    },
    {
        "title": "SpaceX משיקה טלסקופ חלל חדש לחיפוש חיים מחוץ לכדור הארץ",
        "summary": "טלסקופ ExoLife החדש ישוגר השבוע ויסרוק כוכבי לכת מרוחקים לחיפוש סימני חיים",
        "content": """
        SpaceX מתכוננת לשגר את טלסקופ החלל ExoLife, הטלסקופ המתקדם ביותר שנבנה אי פעם 
        לחיפוש חיים מחוץ לכדור הארץ.
        
        יכולות הטלסקופ:
        - ניתוח ספקטרוסקופי של אטמוספרות כוכבי לכת
        - זיהוי מולקולות אורגניות מרחוק של מיליוני שנות אור
        - מעקב אחר 10,000 כוכבי לכת במקביל
        - רגישות פי 100 מטלסקופ ג'יימס ווב
        
        המדענים יחפשו "ביו-סיגנטורות" כמו:
        • חמצן וחנקן באטמוספרה
        • מתאן ביולוגי
        • כלורופיל מצמחייה
        • אותות רדיו מלאכותיים
        
        השיגור מתוכנן לשבוע הבא ותוצאות ראשונות צפויות תוך 6 חודשים.
        פרויקט זה עשוי לענות על השאלה העתיקה: האם אנחנו לבד ביקום?
        """,
        "url": "https://example.com/exolife-telescope",
        "source": "Space Daily",
        "category": "Science",
        "image_url": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400"
    },
    {
        "title": "המהפכה הירוקה: ישראל מובילה בטכנולוגיות אנרגיה מתחדשת",
        "summary": "סטארט-אפים ישראלים מפתחים טכנולוגיות פורצות דרך באנרגיה סולארית ואחסון אנרגיה",
        "content": """
        ישראל ממשיכה להוביל את המהפכה הירוקה עם פריצות דרך בתחום האנרגיה המתחדשת.
        
        חידושים מרכזיים:
        
        **פאנלים סולאריים דו-צדדיים:**
        חברת SolarEdge פיתחה פאנלים שסופגים אור משני הצדדים, מה שמגדיל את היעילות ב-35%.
        
        **סוללות נוזליות:**
        סטארט-אפ ישראלי פיתח סוללות flow battery שיכולות לאחסן אנרגיה לשבועות שלמים.
        
        **AI לניהול רשת:**
        מערכת חכמה שמנבאת צריכת חשמל ומייעלת את הפצת האנרגיה בזמן אמת.
        
        השפעה כלכלית:
        • חיסכון של 2 מיליארד ש"ח לשנה
        • יצירת 15,000 מקומות עבודה
        • הפחתת פליטות CO2 ב-25%
        
        המטרה: 100% אנרגיה מתחדשת עד 2040.
        """,
        "url": "https://example.com/green-tech-israel",
        "source": "Innovation Daily",
        "category": "Environment",
        "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400"
    },
    {
        "title": "האקדמיה המלכותית לכדורגל: כך מאמנים את כוכבי העתיד",
        "summary": "מבט מאחורי הקלעים לאקדמיה היוקרתית שמגדלת את שחקני הכדורגל המובילים בעולם",
        "content": """
        האקדמיה המלכותית של ריאל מדריד נחשבת לטובה בעולם בהכשרת כדורגלנים צעירים.
        
        תוכנית האימונים כוללת:
        
        **אימוני כדורגל מתקדמים:**
        - 6 ימים בשבוע, 3 שעות ליום
        - דגש על טכניקה אישית
        - משחק קבוצתי ואסטרטגיה
        
        **פיתוח גופני:**
        - אימוני כוח וסיבולת
        - תזונה מדעית מותאמת אישית
        - מעקב רפואי שוטף
        
        **פיתוח מנטלי:**
        - עבודה עם פסיכולוגים ספורט
        - ניהול לחץ והתמודדות עם כישלון
        - בניית אופי ומנהיגות
        
        **חינוך:**
        - לימודים מלאים במקביל
        - שפות (אנגלית + ספרדית)
        - הכנה לקריירה אחרי הספורט
        
        סטטיסטיקה מרשימה:
        • 80% מהבוגרים משחקים במקצועני
        • 35 בוגרים בנבחרות לאומיות
        • 5 זוכי גלובוס הזהב יצאו מהאקדמיה
        
        האקדמיה מקבלת רק 2% מהמועמדים - הכי תחרותי בעולם.
        """,
        "url": "https://example.com/real-madrid-academy",
        "source": "Sports Weekly",
        "category": "Sports",
        "image_url": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400"
    },
    {
        "title": "כלכלת ההייטק: למה סטארט-אפים מעבירים משרדים לתל אביב?",
        "summary": "גל חדש של חברות טכנולוגיה בינלאומיות פותח משרדי פיתוח בישראל",
        "content": """
        תל אביב הופכת למגנט עולמי לחברות הייטק, עם עשרות חברות בינלאומיות שפותחות 
        מרכזי פיתוח בעיר.
        
        הסיבות למעבר:
        
        **כישרונות איכותיים:**
        • מהנדסים עם רקע צבאי ייחודי (8200, תלפיות)
        • תרבות של innovation וחשיבה out-of-the-box
        • שליטה ב-3-4 שפות תכנות בממוצע
        
        **אקוסיסטם תומך:**
        • קירבה למשקיעי Venture Capital
        • רשת של חברות סטארט-אפ לשיתופי פעולה
        • אירועי networking שבועיים
        
        **עלויות תחרוטיות:**
        • זול ב-40% מסן פרנסיסקו
        • זול ב-25% מלונדון
        • מענקי ממשלה לחברות זרות
        
        **איכות חיים:**
        • אקלים ים תיכוני
        • תרבות ואומנות משגשגת
        • קרבה לים ולטבע
        
        חברות שכבר כאן:
        Google, Microsoft, Apple, Amazon, Meta, Nvidia, Intel
        
        צפי: 50 אלף מקומות עבודה חדשים עד 2027.
        """,
        "url": "https://example.com/tel-aviv-tech",
        "source": "Business Today",
        "category": "Business",
        "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400"
    }
]


def add_sample_articles(db: Session, days_offset: int = 0):
    """הוסף מאמרים לדוגמה למסד הנתונים"""
    added_count = 0
    
    for article_data in SAMPLE_ARTICLES:
        # בדוק אם המאמר כבר קיים
        existing = db.query(Article).filter(Article.url == article_data["url"]).first()
        if existing:
            print(f"⚠️  מאמר כבר קיים: {article_data['title'][:50]}...")
            continue
        
        # צור תאריך פרסום אקראי בימים האחרונים
        days_ago = random.randint(0, days_offset) if days_offset > 0 else random.randint(0, 30)
        published_at = datetime.utcnow() - timedelta(days=days_ago)
        
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
            published_at=published_at
        )
        
        db.add(article)
        added_count += 1
        print(f"✅ נוסף: {article_data['title'][:60]}...")
    
    db.commit()
    return added_count


def main():
    """פונקציה ראשית"""
    print("=" * 70)
    print("🚀 הוספת מאמרים למערכת")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # הוסף מאמרים לדוגמה
        count = add_sample_articles(db, days_offset=60)
        
        print("\n" + "=" * 70)
        print(f"✅ הסתיים בהצלחה! נוספו {count} מאמרים חדשים")
        print("=" * 70)
        
        # הצג סטטיסטיקה
        total = db.query(Article).count()
        print(f"\n📊 סה\"כ מאמרים במערכת: {total}")
        
        # הצג קטגוריות
        categories = db.query(Article.category).distinct().all()
        print(f"📂 קטגוריות: {', '.join([c[0] for c in categories if c[0]])}")
        
    except Exception as e:
        print(f"\n❌ שגיאה: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()