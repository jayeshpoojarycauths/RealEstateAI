from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.project.models.project import ProjectStatus, ProjectType, project_leads

# --- Base Schemas ---
class ProjectBase(BaseModel):
    """Base fields for project operations."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ProjectType
    status: str = Field(..., min_length=1, max_length=50)
    customer_id: UUID
    owner_id: UUID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Location fields
    address: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zip_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None

class ProjectFeatureBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectFeatureCreate(ProjectFeatureBase):
    pass

class ProjectFeature(ProjectFeatureBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True

class ProjectImageBase(BaseModel):
    url: str
    caption: Optional[str] = None

class ProjectImageCreate(ProjectImageBase):
    pass

class ProjectImage(ProjectImageBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True

class ProjectAmenityBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectAmenityCreate(ProjectAmenityBase):
    pass

class ProjectAmenity(ProjectAmenityBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True

class ProjectLeadBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    status: str = "new"

class ProjectLeadCreate(ProjectLeadBase):
    pass

class ProjectLead(ProjectLeadBase):
    id: int
    project_id: int
    assigned_to_id: Optional[int] = None

    class Config:
        orm_mode = True

class Project(ProjectBase):
    """Schema for project response."""
    id: UUID
    customer_id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    features: List[ProjectFeature] = []
    images: List[ProjectImage] = []
    amenities_list: List[ProjectAmenity] = []
    leads: List[UUID] = []  # List of lead IDs instead of ProjectLead objects

    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    project: Project

class ProjectList(BaseModel):
    items: List[Project]
    total: int
    page: int
    size: int
    pages: int

class ProjectFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    created_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None

class ProjectStats(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    total_leads: int
    active_leads: int
    converted_leads: int

class ProjectAnalytics(BaseModel):
    project_type_distribution: dict
    lead_status_distribution: dict
    monthly_project_creation: dict
    monthly_lead_conversion: dict

class ProjectLeadResponse:
    """Placeholder for ProjectLeadResponse schema."""
    pass

class ProjectListResponse:
    """Placeholder for ProjectListResponse schema."""
    pass 