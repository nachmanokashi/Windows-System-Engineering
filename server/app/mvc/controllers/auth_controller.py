# app/mvc/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.auth_utils import get_current_user, get_current_active_user
from app.mvc.models.users.user_service import UserService
from app.mvc.models.users.user_schemas import (
    UserCreate, UserRead, UserLogin, Token, UserUpdate
)
from app.mvc.models.users.user_entity import User

router = APIRouter(tags=["auth"])

@router.post("/auth/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """רישום משתמש חדש"""
    try:
        service = UserService(db)
        user = service.register(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error registering user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register user: {str(e)}"
        )

@router.post("/auth/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """התחברות למערכת"""
    try:
        service = UserService(db)
        result = service.login(payload.username, payload.password)
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
    db: Session = Depends(get_db)
):
    """התחברות דרך OAuth2 form (לשימוש עם Swagger UI)"""
    try:
        service = UserService(db)
        result = service.login(form_data.username, form_data.password)
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