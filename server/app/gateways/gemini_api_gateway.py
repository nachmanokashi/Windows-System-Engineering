import google.genai as genai

from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiAPIGateway:
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY לא מוגדר ב-.env")
        
        # הגדרת API Key
        genai.configure(api_key=self.api_key)
        
        # יצירת המודל
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # שמירת היסטוריית צ'אטים (session-based)
        self.chat_sessions = {}
        
        print("✅ Gemini Gateway initialized")
    
    def start_chat_session(self, session_id: str) -> None:
        """התחל session חדש של צ'אט"""
        self.chat_sessions[session_id] = self.model.start_chat(history=[])
        print(f"💬 Started new chat session: {session_id}")
    
    def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """שלח הודעה ב-session קיים"""
        try:
            # אם אין session - צור חדש
            if session_id not in self.chat_sessions:
                self.start_chat_session(session_id)
            
            chat = self.chat_sessions[session_id]
            
            # שלח הודעה
            response = chat.send_message(message)
            
            return {
                "session_id": session_id,
                "message": message,
                "response": response.text,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error in Gemini chat: {e}")
            return {
                "session_id": session_id,
                "message": message,
                "response": f"שגיאה: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        """קבל היסטוריית צ'אט"""
        if session_id not in self.chat_sessions:
            return []
        
        chat = self.chat_sessions[session_id]
        history = []
        
        for message in chat.history:
            history.append({
                "role": message.role,  # 'user' או 'model'
                "content": message.parts[0].text
            })
        
        return history
    
    def clear_chat_session(self, session_id: str) -> None:
        """נקה session"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
            print(f"🗑️ Cleared chat session: {session_id}")
    
    def ask_about_news(self, article_title: str, article_summary: str, question: str) -> str:
        """
        שאל שאלה על מאמר חדשות ספציפי
        """
        try:
            prompt = f"""
אתה עוזר AI מומחה לניתוח חדשות.

מאמר:
כותרת: {article_title}
תקציר: {article_summary}

שאלת המשתמש: {question}

אנא ענה על השאלה בצורה ברורה ותמציתית בעברית.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"שגיאה בשאלה על המאמר: {str(e)}"
    
    def analyze_news_sentiment(self, text: str) -> Dict[str, Any]:
        """
        נתח סנטימנט של חדשות
        """
        try:
            prompt = f"""
נתח את הסנטימנט של הטקסט הבא:

{text}

החזר תשובה במבנה הבא:
- סנטימנט כללי (חיובי/שלילי/ניטרלי)
- ציון (0-100)
- הסבר קצר

תשובה בעברית.
"""
            
            response = self.model.generate_content(prompt)
            return {
                "analysis": response.text,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis": f"שגיאה: {str(e)}",
                "success": False
            }


# Singleton instance
_gemini_gateway = None


def get_gemini_gateway() -> GeminiAPIGateway:
    """קבל instance יחיד של Gateway"""
    global _gemini_gateway
    if _gemini_gateway is None:
        _gemini_gateway = GeminiAPIGateway()
    return _gemini_gateway