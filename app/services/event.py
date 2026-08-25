from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from app.models.user import User
from app.models.event import Event, EventStaff
from app.schemas.event import EventCreate, EventUpdate, EventStaffCreate


def is_admin(current_user: User):
    return current_user.role == "ADMIN"


def create_event(db: Session, event_data: EventCreate, current_user: User):
    existing_event = db.query(Event).filter(
        Event.name.ilike(event_data.name.strip())).first()
    if existing_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sự kiện đã tồn tại trong hệ thống"
        )

    db_event = Event(
        name=event_data.name,
        description=event_data.description,
        owner_id=current_user.id
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    owner_member = EventStaff(
        event_id=db_event.id,
        user_id=current_user.id,
        role="OWNER"
    )
    db.add(owner_member)
    db.commit()

    return db_event


def get_user_events(db: Session, current_user: User, search: Optional[str] = None):
    if is_admin(current_user):
        query = db.query(Event)
    else:
        query = db.query(Event).filter(
            or_(
                Event.owner_id == current_user.id,
                Event.staffs.any(EventStaff.user_id == current_user.id)
            )
        )

    if search:
        query = query.filter(Event.name.ilike(f"%{search}%"))

    return query.all()


def get_event_by_id(db: Session, event_id: int, current_user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if is_admin(current_user) or event.owner_id == current_user.id:
        return event

    is_member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id, EventStaff.user_id == current_user.id).first()
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ thành viên sự kiện mới có quyền xem chi tiết"
        )

    return event


def update_event(db: Session, event_id: int, event_data: EventUpdate, current_user: User, is_partial: bool = False):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if not is_admin(current_user) and event.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ ADMIN hoặc OWNER mới có quyền cập nhật sự kiện"
        )

    update_dict = event_data.model_dump(exclude_unset=is_partial)
    updated_result = {}
    for key, value in update_dict.items():
        if key == "name" and isinstance(value, str):
            value = value.strip()
        setattr(event, key, value)
        updated_result[key] = value

    db.commit()
    db.refresh(event)
    if is_partial:
        return {
            "message": "Cập nhật một phần sự kiện thành công",
            "updated_data": updated_result
        }
    else:
        return {
            "message": "Cập nhật toàn bộ sự kiện thành công",
            "updated_data": {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "owner_id": event.owner_id,
                "created_at": event.created_at
            }
        }


def delete_event(db: Session, event_id: int, current_user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if not is_admin(current_user) and event.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ ADMIN hoặc OWNER mới có quyền xóa sự kiện"
        )

    db.delete(event)
    db.commit()
    return None


def add_event_member(db: Session, event_id: int, member_data: EventStaffCreate, current_user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if not is_admin(current_user) and event.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ ADMIN hoặc OWNER mới có quyền thêm thành viên"
        )

    target_user = db.query(User).filter(User.id == member_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng cần thêm"
        )

    existing_member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id, EventStaff.user_id == member_data.user_id).first()
    if existing_member or member_data.user_id == event.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã là thành viên của sự kiện này"
        )

    new_member = EventStaff(
        event_id=event_id,
        user_id=member_data.user_id,
        role=member_data.role
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


def remove_event_member(db: Session, event_id: int, user_id: int, current_user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if not is_admin(current_user) and event.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ ADMIN hoặc OWNER mới có quyền xóa thành viên"
        )

    if user_id == event.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa OWNER ra khỏi sự kiện"
        )

    existing_member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thành viên không tồn tại trong sự kiện này"
        )

    db.delete(existing_member)
    db.commit()
    return None


def get_event_members(db: Session, event_id: int, current_user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if not is_admin(current_user) and event.owner_id != current_user.id:
        is_member = db.query(EventStaff).filter(
            EventStaff.event_id == event_id, EventStaff.user_id == current_user.id).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ thành viên sự kiện mới có quyền xem chi tiết"
            )

    member_list = db.query(EventStaff).filter(
        EventStaff.event_id == event_id).all()

    has_owner = any(member.user_id == event.owner_id for member in member_list)
    if not has_owner:
        owner_user = db.query(User).filter(User.id == event.owner_id).first()
        if owner_user:
            owner_member = EventStaff(
                event_id=event.id,
                user_id=owner_user.id,
                role="OWNER",
                joined_at=datetime.now(),
                user=owner_user
            )
            member_list.insert(0, owner_member)

    return member_list
