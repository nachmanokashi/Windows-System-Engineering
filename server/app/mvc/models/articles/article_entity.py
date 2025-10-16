import uuid
from sqlalchemy import Column, String, DateTime, Text, func, Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from app.core.db import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String(300), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    url = Column(String(500), nullable=False, unique=True)
    image_url = Column(String(500), nullable=True)  # ← תמונה למאמר
    published_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.getdate())
    
    category = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=True)
    
    # ← NEW: AI Analysis fields
    sentiment_score = Column(String(50), nullable=True)  # POSITIVE/NEGATIVE
    sentiment_confidence = Column(String(10), nullable=True)  # 0.95
    entities_json = Column(Text, nullable=True)  # JSON של NER entities