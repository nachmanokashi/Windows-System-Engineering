# app/mvc/models/users/user_schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# === User Base ===
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """קלט ליצירת משתמש"""
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """קלט להתחברות"""
    username: str
    password: str

class UserRead(UserBase):
    """פלט למשתמש"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """עדכון פרטי משתמש"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

# === Token Schemas ===
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None