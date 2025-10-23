from typing import Dict, Any, List, Optional
from app.core.gateway import get_gateway
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class HuggingFaceService:
    """שירות לעבודה עם Hugging Face Models"""
    
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    # Models שנשתמש בהם
    MODELS = {
        "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
        "summarization": "facebook/bart-large-cnn",
        "translation_en_he": "Helsinki-NLP/opus-mt-en-he",
        "translation_he_en": "Helsinki-NLP/opus-mt-he-en",
        "zero_shot": "facebook/bart-large-mnli",
    }
    
    def __init__(self):
        self.gateway = get_gateway()
        self.api_key = settings.HUGGINGFACE_API_KEY
        
    def _get_headers(self) -> Dict[str, str]:
        """Headers for Hugging Face API"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _query_model(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """שאילתה למודל ב-Hugging Face"""
        url = f"{self.BASE_URL}/{model_name}"
        
        try:
            result = self.gateway.post(
                url=url,
                service_name="huggingface",
                headers=self._get_headers(),
                json=payload,
                timeout=60,
                cache_ttl=3600,  # Cache for 1 hour
                rate_limit=50    # 50 requests per minute
            )
            return result
        except Exception as e:
            logger.error(f"Error querying Hugging Face model {model_name}: {e}")
            raise Exception(f"Failed to query Hugging Face: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        ניתוח סנטימנט של טקסט
        
        Returns:
            {
                "label": "POSITIVE" or "NEGATIVE",
                "score": 0.99
            }
        """
        try:
            result = self._query_model(
                self.MODELS["sentiment"],
                {"inputs": text}
            )
            
            if isinstance(result, list) and len(result) > 0:
                # הmodel מחזיר רשימה של תוצאות
                top_result = max(result[0], key=lambda x: x['score'])
                return {
                    "label": top_result["label"],
                    "score": top_result["score"],
                    "all_scores": result[0]
                }
            
            return {"label": "UNKNOWN", "score": 0.0}
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "ERROR", "score": 0.0, "error": str(e)}
    
    def summarize_text(self, text: str, max_length: int = 130, min_length: int = 30) -> Dict[str, Any]:
        """
        סיכום טקסט
        
        Returns:
            {
                "summary": "...",
                "original_length": 1000,
                "summary_length": 100
            }
        """
        try:
            result = self._query_model(
                self.MODELS["summarization"],
                {
                    "inputs": text,
                    "parameters": {
                        "max_length": max_length,
                        "min_length": min_length,
                        "do_sample": False
                    }
                }
            )
            
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get("summary_text", "")
                return {
                    "summary": summary,
                    "original_length": len(text),
                    "summary_length": len(summary)
                }
            
            return {"summary": "", "error": "No summary generated"}
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {"summary": "", "error": str(e)}
    
    def translate_text(self, text: str, direction: str = "en_to_he") -> Dict[str, Any]:
        """
        תרגום טקסט
        
        Args:
            text: הטקסט לתרגום
            direction: "en_to_he" או "he_to_en"
        
        Returns:
            {
                "translated_text": "...",
                "direction": "en_to_he"
            }
        """
        try:
            model_key = f"translation_{direction}"
            if model_key not in self.MODELS:
                return {"translated_text": "", "error": "Invalid direction"}
            
            result = self._query_model(
                self.MODELS[model_key],
                {"inputs": text}
            )
            
            if isinstance(result, list) and len(result) > 0:
                translated = result[0].get("translation_text", "")
                return {
                    "translated_text": translated,
                    "direction": direction,
                    "original_text": text
                }
            
            return {"translated_text": "", "error": "Translation failed"}
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {"translated_text": "", "error": str(e)}
    
    def classify_text(self, text: str, categories: List[str]) -> Dict[str, Any]:
        """
        סיווג טקסט לקטגוריות
        
        Args:
            text: הטקסט לסיווג
            categories: רשימת קטגוריות אפשריות
        
        Returns:
            {
                "category": "Technology",
                "scores": {"Technology": 0.95, "Politics": 0.05}
            }
        """
        try:
            result = self._query_model(
                self.MODELS["zero_shot"],
                {
                    "inputs": text,
                    "parameters": {
                        "candidate_labels": categories
                    }
                }
            )
            
            if "labels" in result and "scores" in result:
                scores = dict(zip(result["labels"], result["scores"]))
                top_category = result["labels"][0]
                
                return {
                    "category": top_category,
                    "confidence": result["scores"][0],
                    "all_scores": scores
                }
            
            return {"category": "UNKNOWN", "confidence": 0.0}
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {"category": "ERROR", "confidence": 0.0, "error": str(e)}
    
    def analyze_article(self, title: str, summary: str) -> Dict[str, Any]:
        """
        ניתוח מקיף של מאמר
        משלב: sentiment, classification
        """
        text = f"{title}. {summary}"
        
        return {
            "sentiment": self.analyze_sentiment(text),
            "category": self.classify_text(text, [
                "Technology", "Politics", "Sports", "Entertainment",
                "Business", "Health", "Science", "World"
            ])
        }


# Singleton
_hf_service: Optional[HuggingFaceService] = None

def get_huggingface_service() -> HuggingFaceService:
    """קבלת instance של HuggingFaceService"""
    global _hf_service
    if _hf_service is None:
        _hf_service = HuggingFaceService()
    return _hf_service