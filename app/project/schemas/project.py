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
    """Schema for creating a new project."""
    customer_id: UUID

class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    total_units: Optional[int] = Field(None, ge=0)
    price_range: Optional[str] = Field(None, max_length=100)
    amenities: Optional[List[str]] = None
    completion_date: Optional[datetime] = None
    total_value: Optional[float] = Field(None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    
    # Location fields
    address: Optional[str] = Field(None, min_length=1, max_length=200)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    zip_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# --- Feature Schemas ---
class ProjectFeatureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None

class ProjectFeatureCreate(ProjectFeatureBase):
    project_id: UUID

class ProjectFeatureUpdate(ProjectFeatureBase):
    pass

class ProjectFeature(ProjectFeatureBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Image Schemas ---
class ProjectImageBase(BaseModel):
    url: str = Field(..., min_length=1, max_length=500)
    caption: Optional[str] = Field(None, max_length=200)
    is_primary: bool = False
    order: int = 0

class ProjectImageCreate(ProjectImageBase):
    project_id: UUID

class ProjectImageUpdate(ProjectImageBase):
    pass

class ProjectImage(ProjectImageBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Amenity Schemas ---
class ProjectAmenityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=100)

class ProjectAmenityCreate(ProjectAmenityBase):
    project_id: UUID

class ProjectAmenityUpdate(ProjectAmenityBase):
    pass

class ProjectAmenity(ProjectAmenityBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Lead Assignment Schemas ---
class ProjectLeadBase(BaseModel):
    """Base schema for project lead assignments."""
    notes: Optional[str] = None

class ProjectLeadCreate(ProjectLeadBase):
    """Schema for creating a new project lead assignment."""
    project_id: UUID
    lead_id: UUID

class ProjectLeadUpdate(ProjectLeadBase):
    """Schema for updating a project lead assignment."""
    pass

class ProjectLeadResponse(ProjectLeadBase):
    """Schema for project lead assignment response."""
    project_id: UUID
    lead_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Response Schemas ---
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

class ProjectList(BaseModel):
    """Schema for list of projects."""
    items: List[Project]
    total: int

# --- Filter Schemas ---
class ProjectFilter(BaseModel):
    type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    city: Optional[str] = None
    state: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    amenities: Optional[List[str]] = None

# --- Stats Schemas ---
class ProjectStats(BaseModel):
    total_projects: int
    projects_by_type: Dict[str, int]
    projects_by_status: Dict[str, int]
    projects_by_city: Dict[str, int]
    total_value: float
    average_project_value: float
    total_leads: int
    conversion_rate: float

# --- Analytics Schemas ---
class ProjectAnalytics(BaseModel):
    lead_trends: List[Dict[str, Any]]
    status_distribution: List[Dict[str, Any]]
    value_distribution: List[Dict[str, Any]]
    location_distribution: List[Dict[str, Any]]
    amenity_popularity: List[Dict[str, Any]]

class ProjectResponse(ProjectBase):
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_leads: int = 0
    converted_leads: int = 0
    conversion_rate: float = 0.0

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    skip: int
    limit: int

# TODO: Implement RealEstateProject schemas when needed 