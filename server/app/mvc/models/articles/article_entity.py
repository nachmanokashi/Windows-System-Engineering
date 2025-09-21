from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Category(str, Enum):
    sports = "sports"
    economy = "economy"
    politics = "politics"

@dataclass(frozen=True)
class Article:
    id: str
    title: str
    summary: str
    source: str
    published_at: datetime
    category: Category  # ← חדש
