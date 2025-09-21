from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import get_settings

settings = get_settings()

# Engine (SQLite קובץ מקומי)
engine = create_engine(settings.DB_URL, future=True, echo=False)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base לכל המודלים ה־ORMיים
class Base(DeclarativeBase):
    pass

# תלות ל-FastAPI (Session לכל בקשה)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
