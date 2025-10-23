from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.mvc.models.users.user_repository import UserRepository
from app.mvc.models.users.user_entity import User
from app.core.auth_utils import get_password_hash, verify_password, create_access_token

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """רישום משתמש חדש"""
        # בדיקה אם שם המשתמש קיים
        if self.repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # בדיקה אם האימייל קיים
        if self.repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # יצירת hash לסיסמה
        hashed_password = get_password_hash(password)
        
        # יצירת המשתמש
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_admin": False
        }
        
        return self.repo.create(user_data)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """אימות משתמש"""
        user = self.repo.get_by_username(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # עדכון זמן התחברות
        self.repo.update_last_login(user.id)
        
        return user

    def login(self, username: str, password: str) -> dict:
        """התחברות וקבלת טוקן"""
        user = self.authenticate(username, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # יצירת טוקן
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """קבלת משתמש לפי ID"""
        return self.repo.get_by_id(user_id)

    def update_user(self, user_id: int, email: Optional[str] = None, 
                   full_name: Optional[str] = None, password: Optional[str] = None) -> Optional[User]:
        """עדכון פרטי משתמש"""
        update_data = {}
        
        if email:
            # בדיקה שהאימייל לא בשימוש
            existing = self.repo.get_by_email(email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            update_data["email"] = email
        
        if full_name is not None:
            update_data["full_name"] = full_name
        
        if password:
            update_data["hashed_password"] = get_password_hash(password)
        
        if not update_data:
            return self.repo.get_by_id(user_id)
        
        return self.repo.update(user_id, update_data)