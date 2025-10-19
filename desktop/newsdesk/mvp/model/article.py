# desktop/newsdesk/mvp/model/article.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Article:
    id: str
    title: str
    summary: str
    source: str
    published_at: Optional[datetime] # Allow None if parsing fails
    category: str
    image_url: str
    thumb_url: str
    # Ensure content field exists and defaults if missing from API
    content: Optional[str] = field(default="")