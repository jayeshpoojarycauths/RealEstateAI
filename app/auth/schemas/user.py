from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class MFABackupCode(BaseModel):
    """Schema for MFA backup code."""
    code: str
    is_used: bool = False
    created_at: datetime
    used_at: Optional[datetime] = None

class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str
    requires_mfa: bool = False

class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None

class UserBase(BaseModel):
    """Base schema for user data."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    """Schema for updating a user."""
    password: Optional[str] = None

class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """Schema for user response."""
    pass

class UserInDB(UserInDBBase):
    """Schema for user in database with hashed password."""
    hashed_password: str

class MFASettings(BaseModel):
    """Schema for MFA settings."""
    is_enabled: bool = False
    method: Optional[str] = None
    secret_key: Optional[str] = None
    backup_codes: Optional[List[MFABackupCode]] = None

class MFAVerify(BaseModel):
    """Schema for MFA verification."""
    code: str
    method: str = "totp"

class MFASetupResponse(BaseModel):
    """Schema for MFA setup response."""
    secret_key: str
    qr_code: str
    backup_codes: List[str]

class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for password reset."""
    token: str
    new_password: str 