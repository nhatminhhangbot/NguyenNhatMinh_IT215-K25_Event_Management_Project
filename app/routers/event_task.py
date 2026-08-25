from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.dependencies.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate, EventTaskResponse, PaginatedTaskResponse
from app.services.event_task import create_event_task, get_event_tasks, get_event_task_detail, update_event_task, delete_event_task

router = APIRouter(tags=["Event Tasks"])


@router.post("/events/{event_id}/event-tasks", response_model=EventTaskResponse, status_code=status.HTTP_201_CREATED)
def handle_create_event_task(event_id: int, task_data: EventTaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_event_task(db=db, event_id=event_id, task_data=task_data, current_user=current_user)


@router.get("/events/{event_id}/event-tasks", response_model=PaginatedTaskResponse)
def handle_get_event_tasks(
    event_id: int,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=10),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return get_event_tasks(
        db=db,
        event_id=event_id,
        current_user=current_user,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/event-tasks/{task_id}", response_model=EventTaskResponse)
def handle_get_event_task_detail(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_event_task_detail(db=db, task_id=task_id, current_user=current_user)


@router.patch("/event-tasks/{task_id}")
def handle_update_event_task(task_id: int, task_data: EventTaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_event_task(db=db, task_id=task_id, task_data=task_data, current_user=current_user)


@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def handle_delete_event_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_event_task(db=db, task_id=task_id, current_user=current_user)
