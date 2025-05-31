from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from uuid import UUID

class CommunicationChannel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    VOICE = "voice"

class ChannelSettings(BaseModel):
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    api_key: Optional[str] = None
    phone_number: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None

class MessageTemplates(BaseModel):
    welcome: str = "Welcome {name}! Thank you for your interest in our properties."
    follow_up: str = "Hi {name}, I wanted to follow up on your interest in {property_name}."
    appointment: str = "Hi {name}, your appointment for {property_name} is scheduled for {datetime}."
    thank_you: str = "Thank you {name} for visiting our property. We look forward to assisting you further."

class CommunicationPreferenceBase(BaseModel):
    channel: CommunicationChannel
    is_enabled: bool = True
    preferred_time: Optional[str] = None
    do_not_disturb: bool = False

class CommunicationPreferenceCreate(CommunicationPreferenceBase):
    pass

class CommunicationPreferenceUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    preferred_time: Optional[str] = None
    do_not_disturb: Optional[bool] = None

class CommunicationPreference(CommunicationPreferenceBase):
    id: int
    customer_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommunicationPreferencesBase(BaseModel):
    customer_id: UUID
    default_channel: CommunicationChannel = CommunicationChannel.EMAIL
    preferences: List[CommunicationPreference]

class CommunicationPreferencesCreate(CommunicationPreferencesBase):
    pass

class CommunicationPreferencesUpdate(BaseModel):
    default_channel: Optional[CommunicationChannel] = None
    preferences: Optional[List[CommunicationPreferenceUpdate]] = None

class CommunicationPreferences(CommunicationPreferencesBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommunicationPreferencesResponse(CommunicationPreferences):
    pass 