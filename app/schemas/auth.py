from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    customer_id: Optional[str] = None

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[str] = None
    customer_id: Optional[str] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class MFABackupCode(BaseModel):
    code: str
    used: bool = False

class MFASettings(BaseModel):
    is_enabled: bool = False
    method: Optional[str] = None
    secret_key: Optional[str] = None
    backup_codes: Optional[List[MFABackupCode]] = None

class MFAVerify(BaseModel):
    code: str
    method: str = "totp"

class MFASetupResponse(BaseModel):
    secret_key: str
    qr_code: str
    backup_codes: List[str] 