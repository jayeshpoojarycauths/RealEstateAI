from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[datetime] = None
    customer_id: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserRegister(UserBase):
    company_name: str
    password: constr(min_length=8)
    captcha_token: Optional[str] = None

class UserResponse(UserBase):
    id: int
    customer_id: int
    is_active: bool
    requires_verification: bool

    class Config:
        from_attributes = True

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