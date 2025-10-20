# server/scripts/test_classification.py
"""
בדיקה מהירה של Classification Service
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.classification_service import ClassificationService

def test_classification():
    """בדוק שה-Classification עובד"""
    print("=" * 70)
    print("🧪 בדיקת Classification Service")
    print("=" * 70)
    
    service = ClassificationService()
    
    # בדוק שיש API Key
    if not service.api_key:
        print("\n❌ שגיאה: HUGGINGFACE_API_KEY לא מוגדר ב-.env!")
        print("💡 הוסף את השורה הזו ל-.env:")
        print("   HUGGINGFACE_API_KEY=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")
        return
    
    print(f"\n✅ API Key נמצא: {service.api_key[:10]}...")
    
    # מאמרים לבדיקה
    test_articles = [
        {
            "title": "Tesla announces new AI-powered autopilot system",
            "content": "Elon Musk revealed Tesla's latest breakthrough in autonomous driving technology using advanced neural networks."
        },
        {
            "title": "Lakers win NBA Championship in dramatic finals",
            "content": "LeBron James led the Los Angeles Lakers to victory in game 7 of the NBA Finals."
        },
        {
            "title": "President announces new economic stimulus package",
            "content": "The administration revealed plans for a $2 trillion economic recovery program."
        },
        {
            "title": "New study shows benefits of Mediterranean diet",
            "content": "Researchers found that a Mediterranean diet can reduce risk of heart disease by 30%."
        }
    ]
    
    print("\n" + "=" * 70)
    print("🔬 מריץ בדיקות...")
    print("=" * 70)
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n📄 Test {i}: {article['title'][:50]}...")
        
        result = service.classify_article(
            title=article["title"],
            content=article["content"]
        )
        
        if "error" in result:
            print(f"   ❌ שגיאה: {result['error']}")
        else:
            print(f"   ✅ קטגוריה: {result['category']}")
            print(f"   📊 ביטחון: {result['confidence']:.1%}")
            
            if "suggestions" in result:
                print(f"   💡 הצעות נוספות:")
                for sug in result["suggestions"][:3]:
                    print(f"      - {sug['category']}: {sug['confidence']:.1%}")
    
    print("\n" + "=" * 70)
    print("✅ בדיקות הושלמו!")
    print("=" * 70)
    print("\n💡 אם הכל עבד - אפשר להמשיך לבנות את ה-Admin Panel!")
    print("   אם היו שגיאות - תבדוק:")
    print("   1. שה-API Key נכון ב-.env")
    print("   2. שיש חיבור אינטרנט")
    print("   3. שמותקן: pip install transformers requests")

if __name__ == "__main__":
    test_classification()