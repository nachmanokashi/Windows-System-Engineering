from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Article:
    id: str
    title: str
    summary: str
    source: str
    published_at: Optional[datetime] 
    category: str
    image_url: str
    thumb_url: str
    content: Optional[str] = field(default="")