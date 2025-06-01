from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum
import re

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_mfa: Optional[bool] = False

class TokenData(BaseModel):
    user_id: Optional[str] = None
    customer_id: Optional[str] = None

class MFAMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"

class MFASettings(BaseModel):
    is_enabled: bool
    preferred_method: MFAMethod
    phone_number: Optional[str] = None
    email: Optional[str] = None

    @validator('phone_number')
    def validate_phone_for_sms(cls, v, values):
        if values.get('preferred_method') == 'sms' and not v:
            raise ValueError('Phone number required for SMS MFA')
        return v

    @validator('email')
    def validate_email_for_email_mfa(cls, v, values):
        if values.get('preferred_method') == 'email' and not v:
            raise ValueError('Email required for email MFA')
        return v

class MFASetupResponse(BaseModel):
    secret_key: str
    qr_code: str
    backup_codes: List[str]

class MFAVerify(BaseModel):
    code: str = Field(..., min_length=6, max_length=8, regex=r'^\d+$', description="6-8 digit MFA code")

class MFABackupCode(BaseModel):
    code: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, description="New password")

    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

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