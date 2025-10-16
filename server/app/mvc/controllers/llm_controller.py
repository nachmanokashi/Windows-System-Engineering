# app/mvc/controllers/llm_controller.py
"""
LLM Controller - endpoints לעבודה עם AI/LLM
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from pydantic import BaseModel, Field
from app.services.uggingface_service import get_huggingface_service, HuggingFaceService
from app.core.auth_utils import get_current_active_user
from app.mvc.models.users.user_entity import User

router = APIRouter(tags=["llm"])

# === Schemas ===

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class SentimentResponse(BaseModel):
    label: str
    score: float
    text: str

class SummarizationRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=10000)
    max_length: int = Field(130, ge=30, le=500)
    min_length: int = Field(30, ge=10, le=100)

class SummarizationResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int

class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    direction: str = Field("en_to_he", pattern="^(en_to_he|he_to_en)$")

class TranslationResponse(BaseModel):
    translated_text: str
    original_text: str
    direction: str

class ClassificationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    categories: List[str] = Field(
        default=["Technology", "Politics", "Sports", "Entertainment", "Business", "Health", "Science", "World"]
    )

class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    all_scores: dict

class ArticleAnalysisRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    summary: str = Field(..., min_length=1, max_length=2000)

# === Endpoints ===

@router.post("/llm/sentiment", response_model=SentimentResponse)
def analyze_sentiment(
    payload: SentimentRequest,
    current_user: User = Depends(get_current_active_user),
    hf_service: HuggingFaceService = Depends(get_huggingface_service)
):
    """
    ניתוח סנטימנט של טקסט
    מזהה אם הטקסט חיובי או שלילי
    """
    try:
        result = hf_service.analyze_sentiment(payload.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "label": result["label"],
            "score": result["score"],
            "text": payload.text[:100] + "..." if len(payload.text) > 100 else payload.text
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/llm/summarize", response_model=SummarizationResponse)
def summarize_text(
    payload: SummarizationRequest,
    current_user: User = Depends(get_current_active_user),
    hf_service: HuggingFaceService = Depends(get_huggingface_service)
):
    """
    סיכום טקסט ארוך לטקסט קצר
    שימושי לסיכום מאמרים ארוכים
    """
    try:
        result = hf_service.summarize_text(
            payload.text,
            max_length=payload.max_length,
            min_length=payload.min_length
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.post("/llm/translate", response_model=TranslationResponse)
def translate_text(
    payload: TranslationRequest,
    current_user: User = Depends(get_current_active_user),
    hf_service: HuggingFaceService = Depends(get_huggingface_service)
):
    """
    תרגום טקסט
    תומך ב: אנגלית <-> עברית
    """
    try:
        result = hf_service.translate_text(payload.text, payload.direction)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/llm/classify", response_model=ClassificationResponse)
def classify_text(
    payload: ClassificationRequest,
    current_user: User = Depends(get_current_active_user),
    hf_service: HuggingFaceService = Depends(get_huggingface_service)
):
    """
    סיווג טקסט לקטגוריה
    מזהה את הנושא המרכזי של הטקסט
    """
    try:
        result = hf_service.classify_text(payload.text, payload.categories)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/llm/analyze-article")
def analyze_article(
    payload: ArticleAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    hf_service: HuggingFaceService = Depends(get_huggingface_service)
):
    """
    ניתוח מקיף של מאמר
    משלב sentiment + classification
    """
    try:
        result = hf_service.analyze_article(payload.title, payload.summary)
        return {
            "title": payload.title,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Article analysis failed: {str(e)}")

@router.get("/llm/models")
def list_models(current_user: User = Depends(get_current_active_user)):
    """רשימת המודלים הזמינים"""
    return {
        "models": {
            "sentiment": "Sentiment Analysis (Positive/Negative)",
            "summarization": "Text Summarization",
            "translation": "Translation (EN <-> HE)",
            "classification": "Text Classification"
        },
        "usage": {
            "rate_limit": "50 requests per minute",
            "cache": "Results cached for 1 hour"
        }
    }