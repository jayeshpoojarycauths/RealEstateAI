from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_mfa: Optional[bool] = False

class TokenData(BaseModel):
    user_id: Optional[str] = None
    customer_id: Optional[str] = None

class MFASettings(BaseModel):
    is_enabled: bool
    preferred_method: str
    phone_number: Optional[str] = None
    email: Optional[str] = None

class MFASetupResponse(BaseModel):
    secret_key: str
    qr_code: str
    backup_codes: List[str]

class MFAVerify(BaseModel):
    code: str

class MFABackupCode(BaseModel):
    code: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class UserSession(BaseModel):
    id: str
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class LoginAttempt(BaseModel):
    id: str
    email: str
    ip_address: str
    user_agent: Optional[str] = None
    success: bool
    attempt_time: datetime
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True 