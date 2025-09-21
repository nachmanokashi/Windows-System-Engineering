from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Article:
    id: str
    title: str
    summary: str
    source: str
    published_at: datetime
    category: str