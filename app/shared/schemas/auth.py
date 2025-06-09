from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.shared.models.user import User
from sqlalchemy.orm import Session
from app.shared.models.user import User


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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