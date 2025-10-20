# desktop/newsdesk/components/chat/chat_presenter.py
"""
Chat Presenter - לוגיקה לצ'אט AI
"""

from PySide6.QtCore import QObject


class ChatPresenter(QObject):
    """Presenter לצ'אט"""
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.view = None
        self.session_id = "default"
    
    def set_view(self, view):
        """קבע את ה-View"""
        self.view = view
    
    def send_message(self, message: str):
        """שלח הודעה ל-AI"""
        print(f"💬 Sending message to Gemini: {message}")
        
        try:
            # שלח ל-API
            response = self.api_client.post("/api/v1/gemini/chat", json={
                "message": message,
                "session_id": self.session_id
            })
            
            # בדוק תשובה
            if hasattr(response, 'status_code'):
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("ai_response", "")
                    print(f"✅ AI Response: {ai_response[:50]}...")
                    
                    if self.view:
                        self.view.show_ai_response(ai_response)
                else:
                    error = f"Server error {response.status_code}"
                    print(f"❌ {error}")
                    if self.view:
                        self.view.show_error(error)
            else:
                # זה כבר dict
                if 'ai_response' in response:
                    ai_response = response["ai_response"]
                    print(f"✅ AI Response: {ai_response[:50]}...")
                    
                    if self.view:
                        self.view.show_ai_response(ai_response)
                elif 'error' in response:
                    print(f"❌ {response['error']}")
                    if self.view:
                        self.view.show_error(response['error'])
                        
        except Exception as e:
            error = str(e)
            print(f"❌ Error sending message: {error}")
            if self.view:
                self.view.show_error(error)
    
    def clear_chat(self):
        """נקה את ה-session"""
        print(f"🗑️ Clearing chat session: {self.session_id}")
        
        try:
            self.api_client.delete(f"/api/v1/gemini/session/{self.session_id}")
            print("✅ Chat session cleared")
        except Exception as e:
            print(f"⚠️ Failed to clear session: {e}")
    
    def load_history(self):
        """טען היסטוריה (אופציונלי)"""
        try:
            response = self.api_client.get(f"/api/v1/gemini/history/{self.session_id}")
            
            if hasattr(response, 'status_code'):
                if response.status_code == 200:
                    data = response.json()
                    history = data.get("history", [])
                    
                    # הצג בממשק
                    if self.view:
                        for msg in history:
                            is_user = msg["role"] == "user"
                            self.view.add_message(msg["content"], is_user)
                            
        except Exception as e:
            print(f"⚠️ Failed to load history: {e}")