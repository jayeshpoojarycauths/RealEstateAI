from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.core.rbac import Role

class TokenPayload(BaseModel):
    sub: str  # Subject (user ID)
    exp: datetime  # Expiration time
    type: str = "access"  # Token type (access or refresh)
    customer_id: Optional[str] = None  # Customer ID for multi-tenant support

class Token(BaseModel):
    access_token: str
    token_type: str
    csrf_token: str

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: constr(min_length=1, max_length=50)
    last_name: constr(min_length=1, max_length=50)
    role: Role

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: constr(min_length=8, max_length=100)
    customer_id: UUID

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    first_name: Optional[constr(min_length=1, max_length=50)] = None
    last_name: Optional[constr(min_length=1, max_length=50)] = None
    password: Optional[constr(min_length=8, max_length=100)] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: UUID
    customer_id: UUID

    class Config:
        from_attributes = True

class UserInDB(UserBase):
    password_hash: str

class MFASettingsBase(BaseModel):
    is_enabled: bool = False
    preferred_method: str = "totp"
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class MFASettingsCreate(MFASettingsBase):
    pass

class MFASettingsUpdate(MFASettingsBase):
    pass

class MFASettings(MFASettingsBase):
    id: UUID
    user_id: UUID
    last_used: Optional[datetime] = None

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: constr(min_length=8, max_length=100)

class MFASetupResponse(BaseModel):
    secret_key: str
    qr_code_url: str
    backup_codes: List[str]

class MFAVerify(BaseModel):
    code: str

class MFABackupCode(BaseModel):
    code: str

class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True 