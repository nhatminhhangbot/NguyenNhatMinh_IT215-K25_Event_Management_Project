from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.dependencies import get_current_user, require_admin
from app.services.user import get_users

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/me", response_model=UserResponse)
def get_my_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UserResponse])
def handle_get_users(
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc email"),
    is_active: Optional[bool] = Query(
        None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_users(db=db, search=search, is_active=is_active)
