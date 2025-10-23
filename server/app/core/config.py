from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="allow"
    )
    
    # App Settings
    APP_NAME: str = "NewsDesk API"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    
    # Database
    DB_URL: str = Field(default="sqlite:///./news.db")
    RUN_CREATE_ALL: bool = False
    
    # JWT Settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production-min-32-chars-long",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Hugging Face 
    HUGGINGFACE_API_KEY: str = Field(default="", description="Hugging Face API Key")
    
    # External APIs 
    NEWS_API_KEY: str = Field(default="", description="News API Key")

    GUARDIAN_API_KEY: str = Field(default="", description="Guardian API Key")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()