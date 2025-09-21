from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "NewsDesk API"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    DB_URL: str = "sqlite:///./newsdesk.db"  # ← חדש

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
