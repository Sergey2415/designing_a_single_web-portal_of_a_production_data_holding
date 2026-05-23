from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, AuthCheckResponse, UserResponse
from app.auth import verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password):
        return LoginResponse(
            success=False,
            message="Неверный логин или пароль"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        success=True,
        token=access_token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            role=user.role
        )
    )


@router.get("/check", response_model=AuthCheckResponse)
def check_auth(current_user: User = Depends(get_current_user)):
    return AuthCheckResponse(
        success=True,
        user=UserResponse(
            id=current_user.id,
            name=current_user.name,
            role=current_user.role
        )
    )








