from typing import Dict, Any
from newsdesk.infra.http.news_api_client import NewsApiClient

class HttpAuthService:
    
    def __init__(self, api: NewsApiClient) -> None:
        self._api = api
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        התחברות למערכת
        
        Returns:
            {
                "access_token": "...",
                "token_type": "bearer"
            }
        """
        response = self._api.post("/auth/login", {
            "username": username,
            "password": password
        })
        return response
    
    def register(self, username: str, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """
        רישום משתמש חדש
        
        Returns:
            User data
        """
        response = self._api.post("/auth/register", {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name
        })
        return response
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        קבלת פרטי המשתמש המחובר
        """
        response = self._api.get("/auth/me")
        return response