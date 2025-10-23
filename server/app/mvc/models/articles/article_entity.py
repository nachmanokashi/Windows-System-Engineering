from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.mvc.models.base import Base  


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text)
    content = Column(Text)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(200))
    category = Column(String(100), index=True)
    image_url = Column(String(1000))
    thumb_url = Column(String(1000))
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...')>"