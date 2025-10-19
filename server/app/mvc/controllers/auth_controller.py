# app/mvc/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.auth_utils import get_current_user, get_current_active_user
from app.mvc.models.users.user_service import UserService
from app.mvc.models.users.user_repository import UserRepository
from app.mvc.models.users.user_schemas import (
    UserCreate, UserRead, UserLogin, Token, UserUpdate
)
from app.mvc.models.users.user_entity import User

# Event Sourcing Imports
from app.event_sourcing.event_store import get_event_store
from app.event_sourcing.events import (
    UserRegisteredEvent,
    UserLoggedInEvent
)

router = APIRouter(tags=["auth"])


# ============================================
# Register - עם Event Sourcing
# ============================================

@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    full_name: str = None,
    db: Session = Depends(get_db)
):
    """
    רישום משתמש חדש - עם Event Sourcing!
    """
    repo = UserRepository(db)
    event_store = get_event_store(db)
    
    # בדוק אם המשתמש כבר קיים
    if repo.get_by_username(username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if repo.get_by_email(email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    try:
        # Hash את הסיסמה
        from app.core.auth_utils import get_password_hash
        hashed_pwd = get_password_hash(password)
        
        # צור משתמש חדש
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_pwd,
            "full_name": full_name,
            "is_active": True,
            "is_admin": False
        }
        
        user = repo.create(user_data)
        
        # שמור Event
        event = UserRegisteredEvent(
            user_id=user.id,
            username=username,
            email=email,
            full_name=full_name
        )
        
        event_id = event_store.save_event(event)
        
        print(f"✅ User registered with ID: {user.id}, Event ID: {event_id}")
        
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "event_id": event_id
        }
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


# ============================================
# Login - עם Event Sourcing
# ============================================

@router.post("/auth/login", response_model=Token)
def login(
    payload: UserLogin, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    התחברות למערכת - עם Event Sourcing!
    """
    try:
        service = UserService(db)
        event_store = get_event_store(db)
        
        # התחבר
        result = service.login(payload.username, payload.password)
        
        # קבל את פרטי המשתמש
        repo = UserRepository(db)
        user = repo.get_by_username(payload.username)
        
        if user:
            # שמור Event
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
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/auth/login/form", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    התחברות דרך OAuth2 form (לשימוש עם Swagger UI) - עם Event Sourcing!
    """
    try:
        service = UserService(db)
        event_store = get_event_store(db)
        
        # התחבר
        result = service.login(form_data.username, form_data.password)
        
        # קבל את פרטי המשתמש
        repo = UserRepository(db)
        user = repo.get_by_username(form_data.username)
        
        if user:
            # שמור Event
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
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user: {str(e)}"
        )