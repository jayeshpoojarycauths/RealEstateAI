from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from enum import Enum
from app.outreach.models.outreach import OutreachChannel, OutreachStatus

class OutreachChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"
    WHATSAPP = "whatsapp"

class OutreachStatus(str, Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class OutreachCreate(BaseModel):
    channel: OutreachChannel
    message: str = Field(..., min_length=1, max_length=1000)
    subject: Optional[str] = Field(None, max_length=200)
    template_id: Optional[str] = None
    variables: Optional[dict] = None

    @validator('message')
    def validate_message_length(cls, v, values):
        if values.get('channel') == OutreachChannel.SMS and len(v) > 160:
            raise ValueError('SMS messages must be 160 characters or less')
        return v

class OutreachResponse(OutreachCreate):
    id: int
    lead_id: int
    customer_id: int
    status: OutreachStatus
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class OutreachFilter(BaseModel):
    channel: Optional[OutreachChannel] = None
    status: Optional[OutreachStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    lead_id: Optional[int] = None
    customer_id: Optional[int] = None
    has_error: Optional[bool] = None
    retry_count: Optional[int] = None

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class OutreachStats(BaseModel):
    total_outreach: int
    successful_outreach: int
    failed_outreach: int
    channel_distribution: Dict[str, int]
    average_response_time: Optional[float] = None
    success_rate_by_channel: Dict[str, float]
    retry_rate: float
    error_distribution: Dict[str, int]

class OutreachTrend(BaseModel):
    date: str
    count: int
    channel: OutreachChannel
    status: OutreachStatus

class ChannelStats(BaseModel):
    channel: OutreachChannel
    total: int
    successful: int
    failed: int
    response_rate: float
    average_response_time: Optional[float]
    error_distribution: Dict[str, int]

class OutreachAnalytics(BaseModel):
    daily_outreach_volume: Dict[str, int]
    channel_success_rate: Dict[str, float]
    trends: List[OutreachTrend]
    channel_stats: List[ChannelStats]
    response_time_distribution: List[dict]
    status_distribution: List[dict]
    error_analysis: Dict[str, int]
    retry_analysis: Dict[str, int]

class LeadUpload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    source: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    property_preferences: Optional[str] = Field(None, max_length=200)
    budget_range: Optional[str] = Field(None, max_length=100)

    @validator('phone', 'email')
    def validate_contact_info(cls, v, values):
        if not v and not values.get('email') and not values.get('phone'):
            raise ValueError('At least one contact method (email or phone) is required')
        return v

class OutreachRequest(BaseModel):
    channel: OutreachChannel
    leads: List[LeadUpload] = Field(..., min_items=1)
    template_id: Optional[str] = None
    variables: Optional[dict] = None
    retry_config: Optional[dict] = None

    @validator('leads')
    def validate_leads_for_channel(cls, v, values):
        channel = values.get('channel')
        if channel == OutreachChannel.EMAIL:
            if not all(lead.email for lead in v):
                raise ValueError('All leads must have email addresses for email outreach')
        elif channel == OutreachChannel.SMS:
            if not all(lead.phone for lead in v):
                raise ValueError('All leads must have phone numbers for SMS outreach')
        return v

class OutreachLogResponse(BaseModel):
    id: int
    lead_id: int
    channel: OutreachChannel
    status: OutreachStatus
    message: str
    sent_at: Optional[datetime] = None
    created_at: datetime
    error_message: Optional[str] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InteractionLogBase(BaseModel):
    lead_id: int
    interaction_type: str
    status: str
    details: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None
    duration: Optional[float] = None

class InteractionLogCreate(InteractionLogBase):
    customer_id: int
    user_id: int

class InteractionLogUpdate(BaseModel):
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None
    duration: Optional[float] = None

class InteractionLog(InteractionLogBase):
    id: int
    customer_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InteractionLogResponse(InteractionLog):
    pass 