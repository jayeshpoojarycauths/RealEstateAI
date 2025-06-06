from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from enum import Enum
from uuid import UUID
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
    RESPONDED = "responded"

# --- Base Schemas ---
class OutreachBase(BaseModel):
    """Base fields required for all outreach operations."""
    channel: OutreachChannel
    message: str = Field(..., min_length=1, max_length=1000)
    subject: Optional[str] = Field(None, max_length=200)
    template_id: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

    @validator('message')
    def validate_message_length(cls, v, values):
        if values.get('channel') == OutreachChannel.SMS and len(v) > 160:
            raise ValueError('SMS messages must be 160 characters or less')
        return v

class OutreachCreate(OutreachBase):
    """Schema for creating a new outreach."""
    lead_id: UUID

class OutreachUpdate(BaseModel):
    """Schema for updating an existing outreach."""
    status: Optional[OutreachStatus] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    last_retry_at: Optional[datetime] = None

# --- Template Schemas ---
class OutreachTemplateBase(BaseModel):
    """Base fields for outreach templates."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    channel: OutreachChannel
    subject: Optional[str] = Field(None, max_length=200)
    body: str = Field(..., min_length=1)
    variables: Optional[Dict[str, Any]] = None
    is_active: bool = True

class OutreachTemplateCreate(OutreachTemplateBase):
    """Schema for creating a new template."""
    pass

class OutreachTemplateUpdate(OutreachTemplateBase):
    """Schema for updating an existing template."""
    pass

class OutreachTemplate(OutreachTemplateBase):
    """Schema for template responses."""
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Communication Preference Schemas ---
class CommunicationPreferenceBase(BaseModel):
    """Base fields for communication preferences."""
    default_channel: OutreachChannel
    email_template: Optional[str] = None
    sms_template: Optional[str] = None
    whatsapp_template: Optional[str] = None
    working_hours_start: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    working_hours_end: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    max_daily_outreach: int = Field(default=100, ge=1, le=1000)

class CommunicationPreferenceCreate(CommunicationPreferenceBase):
    """Schema for creating communication preferences."""
    pass

class CommunicationPreferenceUpdate(CommunicationPreferenceBase):
    """Schema for updating communication preferences."""
    pass

class CommunicationPreference(CommunicationPreferenceBase):
    """Schema for communication preference responses."""
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Response Schemas ---
class Outreach(OutreachBase):
    """Schema for outreach responses."""
    id: UUID
    lead_id: UUID
    customer_id: UUID
    status: OutreachStatus
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class OutreachLog(BaseModel):
    """Schema for outreach log responses."""
    id: UUID
    lead_id: UUID
    customer_id: UUID
    channel: OutreachChannel
    status: OutreachStatus
    message: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class OutreachLogResponse(BaseModel):
    id: UUID
    lead_id: UUID
    customer_id: UUID
    channel: OutreachChannel
    status: OutreachStatus
    message: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- List Schemas ---
class OutreachList(BaseModel):
    """Schema for paginated outreach list responses."""
    items: List[Outreach]
    total: int

class OutreachTemplateList(BaseModel):
    """Schema for paginated template list responses."""
    items: List[OutreachTemplate]
    total: int

# --- Filter Schemas ---
class OutreachFilter(BaseModel):
    """Schema for filtering outreach attempts."""
    channel: Optional[OutreachChannel] = None
    status: Optional[OutreachStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None

class OutreachTemplateFilter(BaseModel):
    """Filter parameters for outreach templates."""
    channel: Optional[OutreachChannel] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

# --- Stats Schemas ---
class OutreachStats(BaseModel):
    """Schema for outreach statistics."""
    total_outreach: int
    successful_outreach: int
    failed_outreach: int
    channel_distribution: Dict[str, int]
    average_response_time: Optional[float] = None
    success_rate_by_channel: Dict[str, float]
    retry_rate: float
    error_distribution: Dict[str, int]

# --- Analytics Schemas ---
class OutreachTrend(BaseModel):
    """Schema for outreach trend data."""
    date: str
    count: int
    channel: OutreachChannel
    status: OutreachStatus

class OutreachAnalytics(BaseModel):
    """Schema for outreach analytics."""
    trends: List[OutreachTrend]
    channel_performance: Dict[str, Dict[str, Any]]
    time_distribution: Dict[str, int]
    success_metrics: Dict[str, float]
    error_analysis: Dict[str, int]

class ChannelStats(BaseModel):
    channel: OutreachChannel
    total: int
    successful: int
    failed: int
    response_rate: float
    average_response_time: Optional[float]
    error_distribution: Dict[str, int]

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