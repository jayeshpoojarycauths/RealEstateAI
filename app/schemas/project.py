from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID

class PropertyType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    LAND = "land"
    INDUSTRIAL = "industrial"

class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    PENDING = "pending"
    OFF_MARKET = "off_market"

class PropertyFeature(BaseModel):
    name: str
    value: str

class PropertyImage(BaseModel):
    url: str
    caption: Optional[str] = None
    is_primary: bool = False

class PropertyLocation(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyAmenity(BaseModel):
    name: str
    description: Optional[str] = None
    category: str

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.AVAILABLE
    price: float
    location: PropertyLocation
    features: List[PropertyFeature] = []
    images: List[PropertyImage] = []
    amenities: List[PropertyAmenity] = []
    total_area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    year_built: Optional[int] = None
    is_featured: bool = False

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    price: Optional[float] = None
    location: Optional[PropertyLocation] = None
    features: Optional[List[PropertyFeature]] = None
    images: Optional[List[PropertyImage]] = None
    amenities: Optional[List[PropertyAmenity]] = None
    total_area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    year_built: Optional[int] = None
    is_featured: Optional[bool] = None

class Project(ProjectBase):
    id: str
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    class Config:
        from_attributes = True

class ProjectList(BaseModel):
    items: List[Project]
    total: int
    page: int
    size: int
    pages: int

class ProjectStats(BaseModel):
    total_projects: int
    active_projects: int
    total_value: float
    average_price: float
    status_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    location_distribution: Dict[str, int]
    timeline: List[Dict[str, Any]] 