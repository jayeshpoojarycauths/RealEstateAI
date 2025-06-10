from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr, validator
from sqlalchemy.orm import Session
from app.shared.models.user import User
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
import re


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserInDB(UserBase):
    id: int
    password_hash: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    model_metadata: Optional[dict] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    model_metadata: Optional[dict] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotUsernameRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class MFAVerify(BaseModel):
    user_id: int
    code: str = Field(..., min_length=6, max_length=6)

class MFASetup(BaseModel):
    user_id: int
    code: str = Field(..., min_length=6, max_length=6)

class MFABackupCodes(BaseModel):
    codes: list[str]

class SessionCreate(BaseModel):
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: str
    last_activity: str
    expires_at: str
    is_active: bool

class SessionList(BaseModel):
    items: list[SessionResponse]
    total: int 