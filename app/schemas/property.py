from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class PropertyFeature(BaseModel):
    """Property feature model."""
    name: str
    value: str
    unit: Optional[str] = None

class PropertyImage(BaseModel):
    """Property image model."""
    url: str
    caption: Optional[str] = None
    is_primary: bool = False
    order: int = 0

class PropertyLocation(BaseModel):
    """Property location model."""
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyAmenity(BaseModel):
    """Property amenity model."""
    name: str
    description: Optional[str] = None
    category: str
    icon: Optional[str] = None

class RealEstateProjectBase(BaseModel):
    """Base model for real estate projects."""
    name: str
    description: Optional[str] = None
    type: str
    status: str
    price: Optional[float] = None
    size: Optional[float] = None
    location: PropertyLocation
    features: List[PropertyFeature] = Field(default_factory=list)
    amenities: List[PropertyAmenity] = Field(default_factory=list)
    images: List[PropertyImage] = Field(default_factory=list)
    builder: Optional[str] = None
    completion_date: Optional[datetime] = None
    total_units: Optional[int] = None
    available_units: Optional[int] = None
    price_range: Optional[str] = None

class RealEstateProjectCreate(RealEstateProjectBase):
    """Schema for creating a real estate project."""
    customer_id: UUID

class RealEstateProjectUpdate(BaseModel):
    """Schema for updating a real estate project."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None
    size: Optional[float] = None
    location: Optional[PropertyLocation] = None
    features: Optional[List[PropertyFeature]] = None
    amenities: Optional[List[PropertyAmenity]] = None
    images: Optional[List[PropertyImage]] = None
    builder: Optional[str] = None
    completion_date: Optional[datetime] = None
    total_units: Optional[int] = None
    available_units: Optional[int] = None
    price_range: Optional[str] = None

class RealEstateProject(RealEstateProjectBase):
    """Full real estate project model."""
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    assigned_agents: List[Dict[str, Any]] = Field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    view_count: int = 0
    favorite_count: int = 0
    inquiry_count: int = 0

    class Config:
        from_attributes = True

class RealEstateProjectList(BaseModel):
    """List of real estate projects with pagination."""
    items: List[RealEstateProject]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True 