# app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# engine יציב ל-MSSQL/pyodbc
engine = create_engine(
    settings.DB_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"timeout": 15},  # נסה 15–30
    future=True,
)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
