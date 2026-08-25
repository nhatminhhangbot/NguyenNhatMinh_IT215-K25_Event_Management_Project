from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate
from app.utils.pagination import paginate

VALID_STATUSES = {"TODO", "IN_PROGRESS", "DONE"}
VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}


def is_admin(current_user: User):
    return current_user.role == "ADMIN"


def check_user_in_event(db: Session, event_id: int, current_user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện"
        )

    if is_admin(current_user) or event.owner_id == current_user.id:
        return event

    existing_member = db.query(EventStaff).filter(
        EventStaff.event_id == event_id, EventStaff.user_id == current_user.id).first()
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Người dùng không phải thành viên của sự kiện này"
        )

    return event


def check_assignee_in_event(db: Session, event_id: int, assignee_id: Optional[int] = None):
    if assignee_id is None:
        return

    event = db.query(Event).filter(Event.id == event_id).first()
    if event and event.owner_id == assignee_id:
        return

    assignee_in_event = db.query(EventStaff).filter(
        EventStaff.event_id == event_id, EventStaff.user_id == assignee_id).first()
    if not assignee_in_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người được giao việc không phải thành viên của sự kiện này"
        )


def validate_task_status(status_value: Optional[str] = None):
    if status_value is not None and status_value not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trạng thái phải là TODO, IN_PROGRESS hoặc DONE"
        )


def validate_task_priority(priority_value: Optional[str] = None):
    if priority_value is not None and priority_value not in VALID_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Độ ưu tiên phải là LOW, MEDIUM hoặc HIGH"
        )


def create_event_task(db: Session, event_id: int, task_data: EventTaskCreate, current_user: User):
    check_user_in_event(db, event_id, current_user)
    validate_task_priority(task_data.priority)

    if task_data.assignee_id:
        check_assignee_in_event(db, event_id, task_data.assignee_id)

    db_task = EventTask(
        event_id=event_id,
        title=task_data.title.strip(),
        description=task_data.description,
        status="TODO",
        priority=task_data.priority,
        assignee_id=task_data.assignee_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_event_tasks(
    db: Session,
    event_id: int,
    current_user: User,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    check_user_in_event(db, event_id, current_user)

    query = db.query(EventTask).filter(EventTask.event_id == event_id)
    if status:
        query = query.filter(EventTask.status == status)
    if priority:
        query = query.filter(EventTask.priority == priority)
    if assignee_id is not None:
        query = query.filter(EventTask.assignee_id == assignee_id)
    if search:
        query = query.filter(EventTask.title.ilike(f"%{search}%"))

    if sort_by == "due_date":
        sort_column = EventTask.due_date
    else:
        sort_column = EventTask.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return paginate(query=query, page=page, size=size)


def get_event_task_detail(db: Session, task_id: int, current_user: User):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc"
        )

    check_user_in_event(db, task.event_id, current_user)
    return task


def update_event_task(db: Session, task_id: int, task_data: EventTaskUpdate, current_user: User):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc"
        )

    event = check_user_in_event(db, task.event_id, current_user)

    is_owner = event.owner_id == current_user.id
    is_assignee = task.assignee_id == current_user.id
    if not is_admin(current_user) and not is_owner and not is_assignee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ ADMIN, OWNER sự kiện hoặc người phụ trách công việc mới có quyền cập nhật"
        )

    validate_task_status(task_data.status)
    validate_task_priority(task_data.priority)

    if task_data.assignee_id is not None:
        if not is_admin(current_user) and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ ADMIN hoặc OWNER mới có quyền thay đổi người phụ trách công việc"
            )
        check_assignee_in_event(db, task.event_id, task_data.assignee_id)

    update_dict = task_data.model_dump(exclude_unset=True)
    updated_result = {}
    for key, value in update_dict.items():
        if key == "title" and value:
            value = value.strip()
        setattr(task, key, value)
        updated_result[key] = value

    db.commit()
    db.refresh(task)
    return {
        "message": "Cập nhật công việc thành công",
        "updated_data": updated_result
    }


def delete_event_task(db: Session, task_id: int, current_user: User):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc"
        )

    event = check_user_in_event(db, task.event_id, current_user)
    if not is_admin(current_user) and event.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ ADMIN hoặc OWNER sự kiện mới có quyền xóa công việc"
        )

    db.delete(task)
    db.commit()
    return None
