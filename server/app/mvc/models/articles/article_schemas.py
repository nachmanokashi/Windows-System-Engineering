from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

# === יחידת בסיס למאמר ===
class ArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None         
    category: Optional[str] = None
    image_url: Optional[str] = None       
    thumb_url: Optional[str] = None       
    published_at: Optional[datetime] = None
    source: Optional[str] = None
    url: Optional[str] = None

class ArticleCreate(ArticleBase):
    """קלט ליצירה/עדכון"""

class ArticleRead(ArticleBase):
    """פלט לאפליקציה/לקוח"""
    id: int

# === רשימה פשוטה ===
class ArticlesList(BaseModel):
    items: List[ArticleRead]

# === עמוד מדפדף (אם תרצה להשתמש בהמשך) ===
class PageMeta(BaseModel):
    page: int = 1
    size: int = 20
    total: int

class ArticlesPage(BaseModel):
    meta: PageMeta
    items: List[ArticleRead]

__all__ = [
    "ArticleBase",
    "ArticleCreate",
    "ArticleRead",
    "ArticlesList",
    "PageMeta",
    "ArticlesPage",
]
