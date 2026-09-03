from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str
    full_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(BaseModel):
    message: str
    data: UserResponse


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
