from pydantic import BaseModel
from datetime import datetime

class ArticleOut(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    published_at: datetime
