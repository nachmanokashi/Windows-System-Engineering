from typing import Dict, Any, List
from app.services.uggingface_service import get_huggingface_service
import json

class AIAnalysisService:
    """שירות ניתוח AI מתקדם"""
    
    def __init__(self):
        self.hf_service = get_huggingface_service()
    
    def analyze_article_full(self, title: str, summary: str, body: str = "") -> Dict[str, Any]:
        """
        ניתוח מלא של מאמר:
        1. Sentiment Analysis
        2. NER (Named Entity Recognition)
        3. Key Topics
        """
        # טקסט מלא לניתוח
        full_text = f"{title}. {summary}"
        if body:
            full_text += f" {body[:500]}"  
        
        # 1. Sentiment Analysis
        sentiment = self.hf_service.analyze_sentiment(full_text)
        
        # 2. NER - זיהוי ישויות
        entities = self.extract_entities(full_text)
        
        # 3. Key Topics/Classification
        classification = self.hf_service.classify_text(full_text, [
            "Politics", "Economy", "Technology", "Sports",
            "Health", "Entertainment", "Science", "World"
        ])
        
        return {
            "sentiment": {
                "label": sentiment.get("label", "UNKNOWN"),
                "score": sentiment.get("score", 0.0)
            },
            "entities": entities,
            "suggested_category": classification.get("category", "General"),
            "category_confidence": classification.get("confidence", 0.0)
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        זיהוי ישויות (NER) - שמות, ארגונים, מקומות וכו'
        
        משתמש במודל Hugging Face NER
        """
        try:
            from app.core.gateway import get_gateway
            gateway = get_gateway()
            
            # Hugging Face NER model
            result = gateway.post(
                url="https://api-inference.huggingface.co/models/dslim/bert-base-NER",
                service_name="huggingface_ner",
                json={"inputs": text},
                headers={"Content-Type": "application/json"},
                timeout=30,
                cache_ttl=3600
            )
            
            if isinstance(result, list):
                entities = []
                for entity in result:
                    if entity.get("score", 0) > 0.7: 
                        entities.append({
                            "text": entity.get("word", ""),
                            "type": entity.get("entity_group", entity.get("entity", "UNKNOWN")),
                            "score": round(entity.get("score", 0), 2),
                            "start": entity.get("start", 0),
                            "end": entity.get("end", 0)
                        })
                
                return entities
            
            return []
            
        except Exception as e:
            print(f"NER extraction failed: {e}")
            return []
    
    def get_sentiment_emoji(self, sentiment_label: str) -> str:
        """המרת sentiment ל-emoji"""
        emoji_map = {
            "POSITIVE": "😊",
            "NEGATIVE": "😞",
            "NEUTRAL": "😐"
        }
        return emoji_map.get(sentiment_label, "🤔")
    
    def format_entities_for_display(self, entities: List[Dict]) -> str:
        """עיצוב entities לתצוגה"""
        if not entities:
            return "No entities found"
        
        # קיבוץ לפי סוג
        grouped = {}
        for entity in entities:
            entity_type = entity["type"]
            if entity_type not in grouped:
                grouped[entity_type] = []
            grouped[entity_type].append(entity["text"])
        
        # בניית מחרוזת תצוגה
        result = []
        type_labels = {
            "PER": "👤 People",
            "ORG": "🏢 Organizations",
            "LOC": "📍 Locations",
            "MISC": "🔖 Others"
        }
        
        for entity_type, names in grouped.items():
            label = type_labels.get(entity_type, entity_type)
            unique_names = list(set(names))[:5]  # רק 5 הראשונים
            result.append(f"{label}: {', '.join(unique_names)}")
        
        return "\n".join(result)


# Singleton
_ai_analysis_service: Any = None

def get_ai_analysis_service() -> AIAnalysisService:
    global _ai_analysis_service
    if _ai_analysis_service is None:
        _ai_analysis_service = AIAnalysisService()
    return _ai_analysis_service