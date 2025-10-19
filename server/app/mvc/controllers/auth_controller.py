# app/mvc/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field # <-- הוספנו ייבוא
from typing import Optional # <-- הוספנו ייבוא

from app.core.db import get_db
from app.core.auth_utils import get_current_user, get_current_active_user
from app.mvc.models.users.user_service import UserService
from app.mvc.models.users.user_repository import UserRepository
from app.mvc.models.users.user_schemas import (
    UserRead, UserLogin, Token, UserUpdate
)
from app.mvc.models.users.user_entity import User

# Event Sourcing Imports
from app.event_sourcing.event_store import get_event_store
from app.event_sourcing.events import (
    UserRegisteredEvent,
    UserLoggedInEvent
)

router = APIRouter(tags=["auth"])

# --- הוספנו מודל קלט חדש עבור רישום ---
class UserRegisterPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

# ============================================
# Register - עכשיו מקבל JSON Body
# ============================================

@router.post("/auth/register")
# --- שינינו את החתימה כאן ---
def register(
    payload: UserRegisterPayload, # מקבלים את הנתונים כמודל מגוף הבקשה
    db: Session = Depends(get_db)
):
    """
    רישום משתמש חדש - עם Event Sourcing!
    """
    repo = UserRepository(db)
    event_store = get_event_store(db)

    # --- משתמשים בנתונים מה-payload ---
    if repo.get_by_username(payload.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    if repo.get_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    try:
        from app.core.auth_utils import get_password_hash
        hashed_pwd = get_password_hash(payload.password)

        user_data = {
            "username": payload.username,
            "email": payload.email,
            "hashed_password": hashed_pwd,
            "full_name": payload.full_name,
            "is_active": True,
            "is_admin": False
        }

        user = repo.create(user_data)

        event = UserRegisteredEvent(
            user_id=user.id,
            username=payload.username, # שימוש בנתוני payload
            email=payload.email,       # שימוש בנתוני payload
            full_name=payload.full_name # שימוש בנתוני payload
        )
        event_id = event_store.save_event(event)

        print(f"✅ User registered with ID: {user.id}, Event ID: {event_id}")

        # מחזירים תגובה מעט שונה, רק את הנתונים הבסיסיים
        return UserRead.model_validate(user) # המרה למודל קריאה

    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


# ============================================
# Login (ללא שינוי מהותי בקוד הפנימי, רק בחתימה של login)
# ============================================

@router.post("/auth/login", response_model=Token)
def login(
    payload: UserLogin, # כבר היה מוגדר נכון
    request: Request,
    db: Session = Depends(get_db)
):
    """
    התחברות למערכת - עם Event Sourcing!
    """
    try:
        service = UserService(db)
        event_store = get_event_store(db)
        result = service.login(payload.username, payload.password) # שימוש בנתוני payload
        repo = UserRepository(db)
        user = repo.get_by_username(payload.username) # שימוש בנתוני payload

        if user:
            event = UserLoggedInEvent(
                user_id=user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
            event_id = event_store.save_event(event)
            print(f"✅ Login event saved with ID: {event_id}")

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/auth/login/form", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    התחברות דרך OAuth2 form (לשימוש עם Swagger UI) - עם Event Sourcing!
    """
    # קוד זה נשאר זהה כי הוא מקבל Form Data ולא JSON
    try:
        service = UserService(db)
        event_store = get_event_store(db)
        result = service.login(form_data.username, form_data.password)
        repo = UserRepository(db)
        user = repo.get_by_username(form_data.username)

        if user:
            event = UserLoggedInEvent(
                user_id=user.id,
                ip_address=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
            event_id = event_store.save_event(event)
            print(f"✅ Login event saved with ID: {event_id}")

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during form login: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


# ============================================
# User Info & Update (ללא שינוי)
# ============================================

@router.get("/auth/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """קבלת פרטי המשתמש המחובר"""
    return current_user


@router.put("/auth/me", response_model=UserRead)
def update_current_user(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """עדכון פרטי המשתמש המחובר"""
    try:
        service = UserService(db)
        updated_user = service.update_user(
            user_id=current_user.id,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")