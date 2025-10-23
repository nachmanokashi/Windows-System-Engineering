from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from app.mvc.models.base import Base


# טען את הקובץ .env
load_dotenv()

# קבל את ה-DATABASE_URL (תמיכה גם ב-DB_URL)
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")

print(f"🔍 DEBUG: DATABASE_URL = {DATABASE_URL[:50]}..." if DATABASE_URL else "None")

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL או DB_URL לא מוגדר!\n"
        "צור קובץ .env בתיקייה server/ עם:\n"
        "DATABASE_URL=your_connection_string_here"
    )

# SQL Server + pyodbc תמיד משתמשים ב-Unicode, אין צורך בפרמטר encoding
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,  
)

# הוסף event listener כדי להבטיח UTF-8 בכל חיבור
@event.listens_for(engine, "connect")
def set_unicode(dbapi_conn, connection_record):
    """הבטח שהחיבור תומך ב-Unicode"""
    cursor = dbapi_conn.cursor()
    try:
        # הגדר text size מקסימלי
        cursor.execute("SET TEXTSIZE 2147483647")
        cursor.close()
    except:
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()