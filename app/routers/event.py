from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.dependencies.dependencies import get_current_user
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventStaffCreate, EventStaffResponse
from app.services.event import create_event, get_user_events, get_event_by_id, update_event, delete_event, add_event_member, remove_event_member, get_event_members

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def handle_create_event(event_in: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_event(db=db, event_data=event_in, current_user=current_user)


@router.get("/", response_model=List[EventResponse])
def handle_get_user_events(
    search: Optional[str] = Query(
        None, description="Tìm kiếm theo tên sự kiện"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_events(db=db, current_user=current_user, search=search)


@router.get("/{event_id}", response_model=EventResponse)
def handle_get_event_by_id(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_event_by_id(db=db, event_id=event_id, current_user=current_user)


@router.put("/{event_id}")
def handle_update_full_event(event_id: int, event_in: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_event(db=db, event_id=event_id, event_data=event_in, current_user=current_user, is_partial=False)


@router.patch("/{event_id}")
def handle_update_partial_event(event_id: int, event_in: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_event(db=db, event_id=event_id, event_data=event_in, current_user=current_user, is_partial=True)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def handle_delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_event(db=db, event_id=event_id, current_user=current_user)


@router.post("/{event_id}/members", response_model=EventStaffResponse, status_code=status.HTTP_201_CREATED)
def handle_add_event_member(event_id: int, member_in: EventStaffCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return add_event_member(db=db, event_id=event_id, member_data=member_in, current_user=current_user)


@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def handle_remove_event_member(event_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return remove_event_member(db=db, event_id=event_id,
                               user_id=user_id, current_user=current_user)


@router.get("/{event_id}/members", response_model=List[EventStaffResponse])
def handle_get_event_members(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_event_members(db=db, event_id=event_id, current_user=current_user)
