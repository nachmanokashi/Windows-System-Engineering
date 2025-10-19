# server/scripts/test_news_api.py
"""
בדיקה שה-News API עובד
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.gateways.news_api_gateway import NewsAPIGateway

def test_api():
    """בדוק שה-API עובד"""
    print("=" * 70)
    print("🧪 בדיקת חיבור ל-News API")
    print("=" * 70)
    
    try:
        # צור gateway
        gateway = NewsAPIGateway()
        print(f"✅ Gateway נוצר בהצלחה")
        print(f"🔑 API Key: {gateway.api_key[:10]}..." if gateway.api_key else "❌ אין API Key")
        
        # נסה לשלוף מאמר אחד
        print("\n🌐 מנסה לשלוף מאמר אחד...")
        articles = gateway.get_top_headlines(category="technology", page_size=1)
        
        if articles:
            print(f"✅ הצלחה! התקבל מאמר:")
            print(f"   כותרת: {articles[0]['title'][:60]}...")
            print(f"   מקור: {articles[0]['source']}")
            print(f"   URL: {articles[0]['url'][:50]}...")
        else:
            print("⚠️  לא התקבלו מאמרים")
        
        print("\n" + "=" * 70)
        print("✅ ה-API עובד!")
        print("=" * 70)
        
    except ValueError as e:
        print(f"\n❌ שגיאה בהגדרות:")
        print(f"   {e}")
        print("\n💡 תבדוק ש-.env מכיל:")
        print("   NEWS_API_KEY=your_api_key_here")
        
    except Exception as e:
        print(f"\n❌ שגיאה:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()