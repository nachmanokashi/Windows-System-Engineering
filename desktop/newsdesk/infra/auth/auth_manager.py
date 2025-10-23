from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

class AuthManager:
    """מנהל אימות - JWT Tokens"""
    
    def __init__(self):
        self._access_token: Optional[str] = None
        self._user_data: Optional[Dict[str, Any]] = None
        self._token_expires_at: Optional[datetime] = None
    
    def login(self, access_token: str, user_data: Optional[Dict[str, Any]] = None) -> None:
        """שמירת טוקן והתחברות"""
        self._access_token = access_token
        self._user_data = user_data
        self._token_expires_at = datetime.now() + timedelta(hours=24)
    
    def logout(self) -> None:
        """התנתקות"""
        self._access_token = None
        self._user_data = None
        self._token_expires_at = None
    
    @property
    def is_authenticated(self) -> bool:
        """האם המשתמש מחובר"""
        if not self._access_token:
            return False
        if self._token_expires_at and datetime.now() > self._token_expires_at:
            self.logout()
            return False
        return True
    
    @property
    def access_token(self) -> Optional[str]:
        """קבלת הטוקן"""
        return self._access_token if self.is_authenticated else None
    
    @property
    def user_data(self) -> Optional[Dict[str, Any]]:
        """נתוני המשתמש"""
        return self._user_data
    
    def get_auth_header(self) -> Dict[str, str]:
        """קבלת header לשליחה ב-HTTP requests"""
        if self.is_authenticated and self._access_token:
            return {"Authorization": f"Bearer {self._access_token}"}
        return {}
    
    @property
    def username(self) -> Optional[str]:
        """שם המשתמש"""
        return self._user_data.get("username") if self._user_data else None

    @property
    def is_admin(self) -> bool:
            """האם המשתמש הוא מנהל (Admin)"""
            return self._user_data.get("is_admin", False) if self._user_data else False

# Singleton instance
_auth_manager: Optional[AuthManager] = None

def get_auth_manager() -> AuthManager:
    """קבלת instance יחיד של AuthManager"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager