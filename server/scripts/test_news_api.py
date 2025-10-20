# server/scripts/test_news_api.py
"""
בדיקה שה-NewsAPI.ai (Event Registry) עובד
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.gateways.news_api_gateway import NewsAPIGateway

def test_api():
    """בדוק שה-API עובד"""
    print("=" * 70)
    print("🧪 בדיקת חיבור ל-NewsAPI.ai (Event Registry)")
    print("=" * 70)
    
    try:
        # צור gateway
        gateway = NewsAPIGateway()
        print(f"✅ Gateway נוצר בהצלחה")
        print(f"🔑 API Key: {gateway.api_key[:10]}..." if gateway.api_key else "❌ אין API Key")
        print(f"🌐 Base URL: {gateway.base_url}")
        
        # בדיקה 1: חפש מאמרים לפי מילת חיפוש
        print("\n" + "=" * 70)
        print("📰 בדיקה 1: חיפוש מאמרים על 'technology'")
        print("=" * 70)
        articles = gateway.get_articles_by_keyword("technology", max_items=3)
        
        if articles:
            print(f"✅ הצלחה! התקבלו {len(articles)} מאמרים:")
            for i, article in enumerate(articles, 1):
                print(f"\n   {i}. כותרת: {article['title'][:60]}...")
                print(f"      מקור: {article['source']}")
                print(f"      שפה: {article['language']}")
                if article.get('published_at'):
                    print(f"      תאריך: {article['published_at'][:10]}")
        else:
            print("⚠️  לא התקבלו מאמרים")
        
        # בדיקה 2: קבל כותרות עיקריות בקטגוריה
        print("\n" + "=" * 70)
        print("📰 בדיקה 2: כותרות עיקריות - טכנולוגיה")
        print("=" * 70)
        headlines = gateway.get_top_headlines(category="technology", page_size=2)
        
        if headlines:
            print(f"✅ הצלחה! התקבלו {len(headlines)} כותרות:")
            for i, article in enumerate(headlines, 1):
                print(f"\n   {i}. כותרת: {article['title'][:60]}...")
                print(f"      מקור: {article['source']}")
                print(f"      URL: {article['url'][:50]}...")
        else:
            print("⚠️  לא התקבלו כותרות")
        
        # בדיקה 3: חיפוש עם טווח תאריכים
        print("\n" + "=" * 70)
        print("📰 בדיקה 3: חיפוש מאמרים על 'climate' מ-7 ימים אחורה")
        print("=" * 70)
        recent_articles = gateway.get_articles_by_topic("climate", days_back=7, page_size=2)
        
        if recent_articles:
            print(f"✅ הצלחה! התקבלו {len(recent_articles)} מאמרים:")
            for i, article in enumerate(recent_articles, 1):
                print(f"\n   {i}. כותרת: {article['title'][:60]}...")
                print(f"      מקור: {article['source']}")
                if article.get('categories'):
                    print(f"      קטגוריות: {', '.join(article['categories'][:3])}")
        else:
            print("⚠️  לא התקבלו מאמרים")
        
        print("\n" + "=" * 70)
        print("✅ כל הבדיקות הצליחו! ה-API עובד תקין!")
        print("=" * 70)
        
    except ValueError as e:
        print(f"\n❌ שגיאה בהגדרות:")
        print(f"   {e}")
        print("\n💡 תבדוק ש-.env מכיל:")
        print("   NEWS_API_KEY=f4fbf935-a453-4875-97d4-08c41b1dbfd8")
        
    except Exception as e:
        print(f"\n❌ שגיאה:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()