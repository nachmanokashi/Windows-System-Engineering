from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from app.gateways.gemini_api_gateway import get_gemini_gateway, GeminiAPIGateway
from app.core.auth_utils import get_current_active_user
from app.mvc.models.users.user_entity import User

router = APIRouter(tags=["gemini"])


# === Schemas ===

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: str = Field(default="default")


class ChatMessageResponse(BaseModel):
    session_id: str
    user_message: str
    ai_response: str
    success: bool


class ChatHistoryResponse(BaseModel):
    session_id: str
    history: List[Dict[str, str]]


class NewsQuestionRequest(BaseModel):
    article_title: str
    article_summary: str
    question: str


class NewsQuestionResponse(BaseModel):
    answer: str
    success: bool


# === Endpoints ===

@router.post("/gemini/chat", response_model=ChatMessageResponse)
def chat_with_gemini(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user),
    gemini: GeminiAPIGateway = Depends(get_gemini_gateway)
):
    """
    צ'אט עם Gemini AI
    """
    try:
        # שלח הודעה
        result = gemini.send_message(
            session_id=f"{current_user.id}_{payload.session_id}",
            message=payload.message
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Chat failed"))
        
        return {
            "session_id": payload.session_id,
            "user_message": payload.message,
            "ai_response": result["response"],
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/gemini/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str = "default",
    current_user: User = Depends(get_current_active_user),
    gemini: GeminiAPIGateway = Depends(get_gemini_gateway)
):
    """
    קבל היסטוריית צ'אט
    """
    try:
        full_session_id = f"{current_user.id}_{session_id}"
        history = gemini.get_chat_history(full_session_id)
        
        return {
            "session_id": session_id,
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.delete("/gemini/session/{session_id}")
def clear_chat_session(
    session_id: str = "default",
    current_user: User = Depends(get_current_active_user),
    gemini: GeminiAPIGateway = Depends(get_gemini_gateway)
):
    """
    נקה session של צ'אט
    """
    try:
        full_session_id = f"{current_user.id}_{session_id}"
        gemini.clear_chat_session(full_session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} cleared"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")


@router.post("/gemini/ask-about-article", response_model=NewsQuestionResponse)
def ask_about_article(
    payload: NewsQuestionRequest,
    current_user: User = Depends(get_current_active_user),
    gemini: GeminiAPIGateway = Depends(get_gemini_gateway)
):
    """
    שאל שאלה על מאמר חדשות ספציפי
    """
    try:
        answer = gemini.ask_about_news(
            article_title=payload.article_title,
            article_summary=payload.article_summary,
            question=payload.question
        )
        
        return {
            "answer": answer,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question failed: {str(e)}")