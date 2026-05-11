from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

from ..utils.enums import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserNewStatus(BaseModel):
    is_active: bool


class UserNewRole(BaseModel):
    role: UserRole


class UserOutBasic(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserOutAdmin(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
