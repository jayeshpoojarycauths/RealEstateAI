from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    status: str = "active"

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
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    assigned_to_id: Optional[int] = None
    features: List[ProjectFeature] = []
    images: List[ProjectImage] = []
    amenities: List[ProjectAmenity] = []
    leads: List[ProjectLead] = []

    class Config:
        orm_mode = True

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