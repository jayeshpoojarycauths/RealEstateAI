from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScrapingConfigBase(BaseModel):
    """Base schema for scraping configuration."""
    sources: List[str] = Field(..., description="List of property sources to scrape")
    locations: List[str] = Field(..., description="List of locations to scrape")
    property_types: List[str] = Field(..., description="List of property types to scrape")
    price_range: Dict[str, float] = Field(..., description="Price range for properties")
    max_pages: int = Field(default=10, description="Maximum number of pages to scrape per source")
    interval_hours: int = Field(default=24, description="Interval between scraping runs in hours")

class ScrapingConfigCreate(ScrapingConfigBase):
    """Schema for creating scraping configuration."""
    pass

class ScrapingConfigUpdate(BaseModel):
    """Schema for updating scraping configuration."""
    sources: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    property_types: Optional[List[str]] = None
    price_range: Optional[Dict[str, float]] = None
    max_pages: Optional[int] = None
    interval_hours: Optional[int] = None

class ScrapingConfigResponse(ScrapingConfigBase):
    """Schema for scraping configuration response."""
    id: str
    customer_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PropertyData(BaseModel):
    """Schema for property data."""
    source: str
    source_id: str
    title: str
    description: str
    price: float
    currency: str
    location: str
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    amenities: List[str] = []
    images: List[str] = []
    url: str
    posted_date: Optional[datetime] = None
    raw_data: Dict[str, Any] = {}

class ScrapedLead(BaseModel):
    id: str
    customer_id: str
    lead_type: str
    data: Dict[str, Any]
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScrapingResult(BaseModel):
    """Schema for scraping result."""
    source: str
    timestamp: datetime
    total_properties: int
    properties: List[PropertyData]
    status: str
    error: Optional[str] = None
    lead_type: Optional[str] = None

class ScrapingStats(BaseModel):
    """Schema for scraping statistics."""
    total_properties: int
    properties_by_source: Dict[str, int]
    properties_by_type: Dict[str, int]
    properties_by_location: Dict[str, int]
    average_price: float
    price_range: Dict[str, float]
    last_updated: datetime 