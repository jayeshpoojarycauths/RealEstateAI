from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

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
class LeadBase(BaseModel):
    """Base fields for a lead."""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[str] = None
    property_type: Optional[str] = None
    notes: Optional[str] = None

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
    id: UUID
    lead_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LeadResponse(LeadBase):
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    activities: List[LeadActivityResponse] = []

    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    items: List[LeadResponse]
    total: int

class LeadFilter(BaseModel):
    status: Optional[str] = None
    source: Optional[str] = None
    search: Optional[str] = None

class LeadStats(BaseModel):
    total_leads: int
    active_leads: int
    converted_leads: int
    leads_by_source: dict
    leads_by_status: dict

# --- Response/Read Schemas ---
class LeadInDBBase(LeadBase):
    """Base fields for a lead as stored in the database."""
    id: UUID
    customer_id: UUID

    class Config:
        from_attributes = True

class Lead(LeadInDBBase):
    """Full lead model for API responses."""
    pass

# --- Filtering Schemas (if any, add here) ---
# (No explicit filter schema in original, but LeadFilter is imported elsewhere)

# --- Scoring/Interaction Schemas ---
# (These are defined in app/schemas/interaction.py and not duplicated here) 