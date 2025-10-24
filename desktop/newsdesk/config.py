import os
from typing import Optional


class ClientConfig:
    """הגדרות Client"""
    
    # API Settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
    API_TIMEOUT: int = 10
    
    # App Settings
    APP_NAME: str = "NewsDesk Client"
    APP_VERSION: str = "1.0.0"
    
    # UI Settings
    WINDOW_MIN_WIDTH: int = 800
    WINDOW_MIN_HEIGHT: int = 600
    
    # Cache Settings
    ENABLE_CACHE: bool = True
    CACHE_DURATION_SECONDS: int = 300  
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_api_url(cls) -> str:
        """קבל URL של ה-API"""
        return cls.API_BASE_URL
    
    @classmethod
    def is_production(cls) -> bool:
        """בדוק אם זה סביבת ייצור"""
        return "localhost" not in cls.API_BASE_URL and "127.0.0.1" not in cls.API_BASE_URL


# Instance יחיד
_config = ClientConfig()


def get_config() -> ClientConfig:
    """קבל את התצורה"""
    return _config
