from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.user import User


def get_users(db: Session, search: Optional[str] = None, is_active: Optional[bool] = None):
    query = db.query(User)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_filter),
                User.email.ilike(search_filter)
            )
        )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()
