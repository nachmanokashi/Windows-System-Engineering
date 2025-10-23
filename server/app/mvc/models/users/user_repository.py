from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.mvc.models.users.user_entity import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> User:
        """יצירת משתמש חדש"""
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """קבלת משתמש לפי ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """קבלת משתמש לפי שם משתמש"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """קבלת משתמש לפי אימייל"""
        return self.db.query(User).filter(User.email == email).first()

    def update(self, user_id: int, data: dict) -> Optional[User]:
        """עדכון פרטי משתמש"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user_id: int) -> None:
        """עדכון זמן התחברות אחרון"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = func.getdate()
            self.db.commit()

    def delete(self, user_id: int) -> bool:
        """מחיקת משתמש"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True

    def deactivate(self, user_id: int) -> Optional[User]:
        """השבתת משתמש"""
        return self.update(user_id, {"is_active": False})

    def activate(self, user_id: int) -> Optional[User]:
        """הפעלת משתמש"""
        return self.update(user_id, {"is_active": True})