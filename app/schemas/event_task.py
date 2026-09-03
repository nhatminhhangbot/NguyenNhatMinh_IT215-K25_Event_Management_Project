from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.user import UserResponse


class EventTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class EventTaskCreate(EventTaskBase):
    pass


class EventTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    status: str
    created_at: datetime
    assignee: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedTaskResponse(BaseModel):
    items: List[EventTaskResponse]
    total: int
    page: int
    size: int
    total_pages: int
