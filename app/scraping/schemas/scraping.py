from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from app.scraping.models.scraping import ScrapingSource, ScrapingStatus

# --- Base Schemas ---
class ScrapingConfigBase(BaseModel):
    """Base schema for scraping configuration."""
    enabled_sources: List[ScrapingSource] = Field(..., description="List of enabled scraping sources")
    locations: List[str] = Field(..., description="List of locations to scrape")
    property_types: List[str] = Field(..., description="List of property types to scrape")
    price_range_min: Optional[float] = Field(None, description="Minimum price range")
    price_range_max: Optional[float] = Field(None, description="Maximum price range")
    max_pages_per_source: int = Field(default=5, ge=1, le=100, description="Maximum pages to scrape per source")
    scraping_delay: int = Field(default=2, ge=1, le=60, description="Delay between requests in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum number of retries per request")
    proxy_enabled: bool = Field(default=False, description="Whether to use proxy")
    proxy_url: Optional[str] = Field(None, description="Proxy URL if enabled")
    user_agent: Optional[str] = Field(None, description="Custom user agent")
    auto_scrape_enabled: bool = Field(default=False, description="Whether to enable automatic scraping")
    auto_scrape_interval: int = Field(default=24, ge=1, le=168, description="Interval between automatic scrapes in hours")

    @validator('price_range_max')
    def validate_price_range(cls, v, values):
        if v is not None and values.get('price_range_min') is not None:
            if v <= values['price_range_min']:
                raise ValueError('Maximum price must be greater than minimum price')
        return v

class ScrapingConfigCreate(ScrapingConfigBase):
    """Schema for creating a new scraping configuration."""
    pass

class ScrapingConfigUpdate(ScrapingConfigBase):
    """Schema for updating an existing scraping configuration."""
    enabled_sources: Optional[List[ScrapingSource]] = None
    locations: Optional[List[str]] = None
    property_types: Optional[List[str]] = None

class ScrapingConfig(ScrapingConfigBase):
    """Schema for scraping configuration responses."""
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Job Schemas ---
class ScrapingJobBase(BaseModel):
    """Base schema for scraping jobs."""
    source: ScrapingSource
    location: Optional[str] = None
    property_type: Optional[str] = None

class ScrapingJobCreate(ScrapingJobBase):
    """Schema for creating a new scraping job."""
    pass

class ScrapingJobUpdate(BaseModel):
    """Schema for updating a scraping job."""
    status: Optional[ScrapingStatus] = None
    items_scraped: Optional[int] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ScrapingJob(ScrapingJobBase):
    """Schema for scraping job responses."""
    id: UUID
    config_id: UUID
    status: ScrapingStatus
    items_scraped: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Result Schemas ---
class ScrapingResultBase(BaseModel):
    """Base schema for scraping results."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    images: Optional[List[str]] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ScrapingResultCreate(ScrapingResultBase):
    """Schema for creating a new scraping result."""
    job_id: UUID

class ScrapingResult(ScrapingResultBase):
    """Schema for scraping result responses."""
    id: UUID
    job_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- List Schemas ---
class ScrapingConfigList(BaseModel):
    """Schema for paginated scraping configuration list responses."""
    items: List[ScrapingConfig]
    total: int

class ScrapingJobList(BaseModel):
    """Schema for paginated scraping job list responses."""
    items: List[ScrapingJob]
    total: int

class ScrapingResultList(BaseModel):
    """Schema for paginated scraping result list responses."""
    items: List[ScrapingResult]
    total: int

# --- Filter Schemas ---
class ScrapingJobFilter(BaseModel):
    """Schema for filtering scraping jobs."""
    source: Optional[ScrapingSource] = None
    status: Optional[ScrapingStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    property_type: Optional[str] = None

class ScrapingResultFilter(BaseModel):
    """Schema for filtering scraping results."""
    job_id: Optional[UUID] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None

# --- Stats Schemas ---
class ScrapingStats(BaseModel):
    """Schema for scraping statistics."""
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    total_items_scraped: int
    source_distribution: Dict[str, int]
    average_items_per_job: float
    success_rate: float
    error_distribution: Dict[str, int]

# --- Analytics Schemas ---
class ScrapingTrend(BaseModel):
    """Schema for scraping trend data."""
    date: str
    count: int
    source: ScrapingSource
    status: ScrapingStatus

class ScrapingAnalytics(BaseModel):
    """Schema for scraping analytics."""
    trends: List[ScrapingTrend]
    source_performance: Dict[str, Dict[str, Any]]
    time_distribution: Dict[str, int]
    success_metrics: Dict[str, float]
    error_analysis: Dict[str, int] 