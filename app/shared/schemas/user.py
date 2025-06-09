from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.shared.core.security.roles import Role
from app.shared.models.user import User
from datetime import datetime
from app.shared.models.user import User
from datetime import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    role: Role = Role.GUEST

class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserResponse(BaseModel):
    user: User

class UserList(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int
    pages: int

class UserFilter(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None

class UserStats(BaseModel):
    total_users: int
    active_users: int
    users_by_role: dict
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int 