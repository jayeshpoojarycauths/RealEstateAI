from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID
from app.models.models import ProjectStatus

# --- Enums ---
class ProjectType(str, Enum):
    """Types of real estate projects."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    LAND = "land"
    RENTAL = "rental"

# --- Create/Update Schemas ---
class ProjectBase(BaseModel):
    """Base fields required for all project operations."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ProjectType
    status: ProjectStatus = ProjectStatus.PLANNING
    location: str = Field(..., min_length=1, max_length=200)
    total_units: Optional[int] = Field(None, ge=0)
    price_range: Optional[str] = Field(None, max_length=100)
    amenities: Optional[List[str]] = Field(None)
    completion_date: Optional[datetime] = None
    total_value: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    customer_id: UUID

class ProjectUpdate(BaseModel):
    """Schema for updating an existing project. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    total_units: Optional[int] = Field(None, ge=0)
    price_range: Optional[str] = Field(None, max_length=100)
    amenities: Optional[List[str]] = None
    completion_date: Optional[datetime] = None
    total_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None

# --- Response/Read Schemas ---
class ProjectInDBBase(ProjectBase):
    """Base fields for a project as stored in the database."""
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    """Full project model for API responses."""
    pass

# --- Filtering Schemas ---
class ProjectFilter(BaseModel):
    """Schema for filtering projects in queries."""
    status: Optional[ProjectStatus] = None
    type: Optional[ProjectType] = None
    search: Optional[str] = None

# --- Analytics/Stats Schemas ---
class ProjectStats(BaseModel):
    """Key metrics for project performance."""
    total_projects: int
    active_projects: int
    completed_projects: int
    total_budget: float
    average_budget: float

class LeadTrend(BaseModel):
    """Time-series data for lead generation."""
    date: str
    count: int

class StatusDistribution(BaseModel):
    """Distribution of leads across different statuses."""
    status: str
    count: int

class ProjectAnalytics(BaseModel):
    """Comprehensive analytics data for a project."""
    projects_by_status: dict
    projects_by_month: dict
    budget_distribution: dict

class RealEstateProjectBase(BaseModel):
    name: str
    price: Optional[str] = None
    size: Optional[str] = None
    type: Optional[str] = None
    builder: Optional[str] = None
    location: Optional[str] = None
    completion_date: Optional[str] = None

class RealEstateProjectCreate(RealEstateProjectBase):
    customer_id: UUID

class RealEstateProjectUpdate(RealEstateProjectBase):
    pass

class RealEstateProjectInDBBase(RealEstateProjectBase):
    id: UUID
    customer_id: UUID

    class Config:
        from_attributes = True

class RealEstateProject(RealEstateProjectInDBBase):
    pass

class RealEstateProjectInDB(RealEstateProjectInDBBase):
    pass

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

class ProjectLeadCreate(BaseModel):
    lead_id: int
    project_id: int
    role: str
    notes: Optional[str] = None

class ProjectLeadResponse(BaseModel):
    id: int
    lead_id: int
    project_id: int
    role: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 