from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, RegisterResponse, LoginRequest, TokenResponse
from app.services.auth import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def handle_register(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_user(db=db, user_in=user_in)


@router.post("/login", response_model=TokenResponse)
def handle_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db=db, login_data=login_data)
