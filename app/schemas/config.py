from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID

class SMSSettings(BaseModel):
    """SMS service configuration settings."""
    provider: str = "twilio"
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: Optional[str] = None
    enabled: bool = True

class EmailSettings(BaseModel):
    """Email service configuration settings."""
    provider: str = "sendgrid"
    api_key: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    enabled: bool = True

class WhatsAppSettings(BaseModel):
    """WhatsApp service configuration settings."""
    provider: str = "twilio"
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    phone_number: Optional[str] = None
    enabled: bool = True

class TelegramSettings(BaseModel):
    """Telegram service configuration settings."""
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    enabled: bool = True

class VoiceSettings(BaseModel):
    """Voice call service configuration settings."""
    provider: str = "twilio"
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: Optional[str] = None
    enabled: bool = True

class CommunicationSettings(BaseModel):
    """Communication service configuration settings."""
    sms: SMSSettings = Field(default_factory=SMSSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    whatsapp: WhatsAppSettings = Field(default_factory=WhatsAppSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)

class SystemConfig(BaseModel):
    """System-wide configuration settings."""
    customer_id: UUID
    communication_settings: CommunicationSettings = Field(default_factory=CommunicationSettings)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SystemConfigCreate(BaseModel):
    """Schema for creating system configuration."""
    customer_id: UUID
    communication_settings: Optional[CommunicationSettings] = None

class SystemConfigUpdate(BaseModel):
    """Schema for updating system configuration."""
    communication_settings: Optional[CommunicationSettings] = None

class SystemConfigResponse(SystemConfig):
    """Response schema for system configuration."""
    pass

class ConfigUpdate(BaseModel):
    """Schema for updating configuration settings."""
    sms_settings: Optional[SMSSettings] = None
    email_settings: Optional[EmailSettings] = None
    whatsapp_settings: Optional[WhatsAppSettings] = None
    telegram_settings: Optional[TelegramSettings] = None
    voice_settings: Optional[VoiceSettings] = None

class ConfigResponse(BaseModel):
    """Response schema for configuration settings."""
    customer_id: UUID
    communication_settings: CommunicationSettings
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 