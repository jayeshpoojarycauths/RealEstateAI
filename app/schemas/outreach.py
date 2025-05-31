from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from uuid import UUID

class OutreachStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class OutreachChannel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    VOICE = "voice"

class OutreachBase(BaseModel):
    lead_id: str
    channel: OutreachChannel
    message: str
    status: OutreachStatus = OutreachStatus.PENDING
    metadata: Optional[Dict] = None

class OutreachCreate(OutreachBase):
    customer_id: UUID

class OutreachUpdate(BaseModel):
    status: Optional[OutreachStatus] = None
    metadata: Optional[Dict] = None

class OutreachInDB(OutreachBase):
    id: str
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Outreach(OutreachInDB):
    pass 