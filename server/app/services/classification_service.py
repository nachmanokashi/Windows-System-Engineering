
from typing import Dict, List, Any
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class ClassificationService:
    """שירות סיווג מאמרים באמצעות Hugging Face"""
    
    # הקטגוריות האפשריות
    CATEGORIES = [
        "Technology",
        "Business", 
        "Politics",
        "Sports",
        "Health",
        "Entertainment",
        "Science",
        "Environment",
        "Education",
        "Travel"
    ]
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        
        if not self.api_key:
            print("⚠️  Warning: HUGGINGFACE_API_KEY not set!")
    
    def classify_article(self, title: str, content: str = "", summary: str = "") -> Dict[str, Any]:
        """
        סווג מאמר לקטגוריה
        
        Args:
            title: כותרת המאמר
            content: תוכן המאמר (אופציונלי)
            summary: סיכום (אופציונלי)
        
        Returns:
            {
                "category": "Technology",
                "confidence": 0.95,
                "all_scores": {"Technology": 0.95, "Business": 0.82, ...}
            }
        """
        try:
            # בנה טקסט לניתוח (עד 512 תווים)
            text = f"{title}. "
            if summary:
                text += f"{summary[:200]}. "
            if content:
                text += content[:300]
            
            text = text.strip()[:512]  # הגבלת אורך
            
            print(f"🤖 Classifying: '{text[:60]}...'")
            
            # שלח ל-Hugging Face
            result = self._query_huggingface(text, self.CATEGORIES)
            
            if "error" in result:
                print(f"❌ Classification error: {result['error']}")
                return {
                    "category": "General",
                    "confidence": 0.0,
                    "error": result["error"]
                }
            
            # חלץ תוצאות
            top_category = result["labels"][0]
            top_score = result["scores"][0]
            
            all_scores = {
                label: score 
                for label, score in zip(result["labels"], result["scores"])
            }
            
            print(f"✅ Classified as: {top_category} ({top_score:.2%})")
            
            return {
                "category": top_category,
                "confidence": top_score,
                "all_scores": all_scores,
                "suggestions": [
                    {"category": label, "confidence": score}
                    for label, score in list(zip(result["labels"], result["scores"]))[:3]
                ]
            }
            
        except Exception as e:
            print(f"❌ Classification failed: {e}")
            return {
                "category": "General",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _query_huggingface(self, text: str, candidate_labels: List[str]) -> Dict[str, Any]:
        """שאילתה ל-Hugging Face API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": candidate_labels,
                "multi_label": False
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API returned {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Request timeout - model might be loading"}
        except Exception as e:
            return {"error": str(e)}
    
    def classify_batch(self, articles: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        סווג מספר מאמרים בבת אחת
        
        Args:
            articles: רשימת מאמרים [{"title": "...", "content": "..."}, ...]
        
        Returns:
            רשימת תוצאות סיווג
        """
        results = []
        
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Classifying article {i}/{len(articles)}...")
            
            result = self.classify_article(
                title=article.get("title", ""),
                content=article.get("content", ""),
                summary=article.get("summary", "")
            )
            
            results.append({
                "article_id": article.get("id"),
                "title": article.get("title"),
                "classification": result
            })
        
        return results
    
    def get_available_categories(self) -> List[str]:
        """החזר רשימת קטגוריות זמינות"""
        return self.CATEGORIES.copy()


# Singleton instance
_classification_service = None

def get_classification_service() -> ClassificationService:
    """קבל instance של Classification Service"""
    global _classification_service
    if _classification_service is None:
        _classification_service = ClassificationService()
    return _classification_service


# ============================================
# בדיקה מהירה
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Classification Service")
    print("=" * 70)
    
    service = ClassificationService()
    
    # בדיקה 1
    print("\n📝 Test 1: Technology article")
    result = service.classify_article(
        title="Tesla announces new AI-powered self-driving system",
        content="Elon Musk revealed Tesla's latest breakthrough in autonomous driving technology..."
    )
    print(f"Result: {result}")
    
    # בדיקה 2
    print("\n📝 Test 2: Sports article")
    result = service.classify_article(
        title="Lakers win NBA championship",
        content="LeBron James led the Los Angeles Lakers to victory..."
    )
    print(f"Result: {result}")
    
    # בדיקה 3
    print("\n📝 Test 3: Politics article")
    result = service.classify_article(
        title="President announces new economic policy",
        content="The administration revealed plans for economic reform..."
    )
    print(f"Result: {result}")
    
    print("\n" + "=" * 70)
    print("✅ Testing complete!")
    print("=" * 70)