from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum
from uuid import UUID

class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL = "social"
    DIRECT = "direct"
    OTHER = "other"

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    LOST = "lost"
    CONVERTED = "converted"

class LeadPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class LeadBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = LeadStatus.NEW
    notes: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    updated_by: Optional[UUID] = None

class LeadInDBBase(LeadBase):
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Lead(LeadInDBBase):
    pass

class LeadInDB(LeadInDBBase):
    pass

class LeadList(BaseModel):
    items: List[Lead]
    total: int
    page: int
    size: int
    pages: int

class LeadStats(BaseModel):
    total_leads: int
    active_leads: int
    conversion_rate: float
    average_score: float
    status_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    timeline: List[Dict[str, Any]] 