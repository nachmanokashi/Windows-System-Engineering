from sqlalchemy import Column, String, DateTime, Boolean, Integer, func
from app.core.db import Base
from app.mvc.models.base import Base  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.getdate())
    last_login = Column(DateTime, nullable=True)