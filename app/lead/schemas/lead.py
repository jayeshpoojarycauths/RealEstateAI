from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from enum import Enum

# --- Upload Schemas ---
class LeadUploadResponse(BaseModel):
    """Response returned after uploading leads in bulk."""
    total_leads: int
    successful_uploads: int
    failed_uploads: int
    errors: Optional[List[str]] = None

class LeadBulkCreate(BaseModel):
    """Request schema for bulk creation of leads."""
    leads: List['LeadCreate']

# --- Create/Update Schemas ---
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
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"
    LOST = "lost"

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
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    customer_id: UUID

class LeadUpdate(LeadBase):
    """Schema for updating an existing lead."""
    name: Optional[str] = None

class LeadActivityBase(BaseModel):
    activity_type: str
    description: Optional[str] = None

class LeadActivityCreate(LeadActivityBase):
    lead_id: UUID

class LeadActivityResponse(LeadActivityBase):
    id: int
    lead_id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class LeadResponse(LeadBase):
    id: int
    customer_id: str
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    activities: List[LeadActivityResponse] = []
    score: Optional[float] = None

    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    items: List[LeadResponse]
    total: int

class LeadFilter(BaseModel):
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    assigned_to: Optional[str] = None

class LeadStats(BaseModel):
    total_leads: int
    leads_by_status: Dict[str, int]
    leads_by_source: Dict[str, int]
    leads_by_priority: Dict[str, int]
    average_score: float
    conversion_rate: float

# --- Response/Read Schemas ---
class LeadInDBBase(LeadBase):
    """Base fields for a lead as stored in the database."""
    id: int
    customer_id: str
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Lead(LeadInDBBase):
    """Full lead model for API responses."""
    pass

# --- Filtering Schemas (if any, add here) ---
# (No explicit filter schema in original, but LeadFilter is imported elsewhere)

# --- Scoring/Interaction Schemas ---
# (These are defined in app/schemas/interaction.py and not duplicated here) 