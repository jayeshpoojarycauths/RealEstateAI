import re
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, validator
from app.shared.models.user import User
from app.shared.models.user import User


class PasswordValidation(BaseModel):
    password: constr(min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

# class UserCreateValidation(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    is_active: Optional[bool] = None

class LeadCreate(BaseModel):
    name: constr(min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ProjectCreate(BaseModel):
    name: constr(min_length=1, max_length=255)
    description: Optional[str] = None
    location: constr(min_length=1, max_length=255)
    price_range: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)] = None
    description: Optional[str] = None
    location: Optional[constr(min_length=1, max_length=255)] = None
    price_range: Optional[str] = None
    status: Optional[str] = None

class OutreachCreate(BaseModel):
    lead_id: str
    channel: str
    message: constr(min_length=1)
    outreach_metadata: Optional[dict] = None

class CommunicationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    telegram_enabled: Optional[bool] = None
    email_frequency: Optional[str] = None
    sms_frequency: Optional[str] = None
    push_frequency: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

    @validator('email_frequency', 'sms_frequency', 'push_frequency')
    def validate_frequency(cls, v):
        if v and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('Frequency must be daily, weekly, or monthly')
        return v

    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v and not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Time must be in 24-hour format (HH:MM)')
        return v 