from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class MetricValue(BaseModel):
    """Schema for a metric value."""
    value: float
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"

class TimeRangeStats(BaseModel):
    """Schema for statistics over a time range."""
    start_date: datetime
    end_date: datetime
    total_leads: int
    active_leads: int
    conversion_rate: float
    average_lead_score: float
    total_value: float

class ChannelStats(BaseModel):
    """Schema for channel-specific statistics."""
    channel: str
    total_interactions: int
    success_rate: float
    average_response_time: float
    conversion_rate: float
    total_value: float

class SourceStats(BaseModel):
    """Schema for source-specific statistics."""
    source: str
    total_leads: int
    conversion_rate: float
    average_score: float
    total_value: float

class PriceTrendPoint(BaseModel):
    """Data point for price trend."""
    date: datetime
    price: float
    volume: Optional[int] = None
    location: Optional[str] = None
    property_type: Optional[str] = None

class PriceTrendResponse(BaseModel):
    """Response for price trend data."""
    time_period: str
    data_points: List[PriceTrendPoint]
    average_price: float
    price_change: float
    volume_change: Optional[float] = None
    location: Optional[str] = None
    property_type: Optional[str] = None

class LeadQualityMetric(BaseModel):
    """Metric for lead quality."""
    name: str
    value: float

class LeadQualityResponse(BaseModel):
    """Response for lead quality data."""
    total_leads: int
    source_distribution: List[LeadQualityMetric]
    conversion_rates: List[LeadQualityMetric]
    avg_response_time: Optional[float] = None
    avg_lead_score: Optional[float] = None

class StatsResponse(BaseModel):
    """Complete statistics response."""
    lead_stats: Dict[str, int]
    project_stats: Dict[str, int]
    activity_stats: Dict[str, int]
    price_trends: Optional[PriceTrendResponse] = None
    lead_quality: Optional[LeadQualityResponse] = None
    additional_metrics: Optional[Dict[str, float]] = None
    
    # Overall metrics
    total_leads: MetricValue
    active_leads: MetricValue
    conversion_rate: MetricValue
    average_lead_score: MetricValue
    total_value: MetricValue
    
    # Time-based metrics
    current_period: TimeRangeStats
    previous_period: TimeRangeStats
    
    # Channel metrics
    channel_stats: List[ChannelStats]
    
    # Source metrics
    source_stats: List[SourceStats]
    
    # Top performers
    top_performing_channels: List[str]
    top_performing_sources: List[str]
    
    # Additional metrics
    average_response_time: float
    lead_velocity: float  # Rate of new leads over time
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_period: str
    filters: Optional[Dict[str, Any]] = None

class LeadStats(BaseModel):
    total_leads: int
    active_leads: int
    converted_leads: int
    leads_by_source: Dict[str, int]
    leads_by_status: Dict[str, int]
    conversion_rate: float
    average_response_time: float
    last_updated: datetime

    class Config:
        from_attributes = True

class ProjectStats(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    total_value: float
    last_updated: datetime

    class Config:
        from_attributes = True

class ActivityStats(BaseModel):
    total_interactions: int
    interactions_by_type: Dict[str, int]
    success_rate: float
    last_updated: datetime

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    lead_stats: LeadStats
    project_stats: ProjectStats
    activity_stats: ActivityStats
    generated_at: datetime

    class Config:
        from_attributes = True

class PriceTrendResponse(BaseModel):
    property_type: str
    location: str
    price_trend: Dict[str, float]  # date -> price
    average_price: float
    price_change_percentage: float
    last_updated: datetime

    class Config:
        from_attributes = True

class LeadQualityResponse(BaseModel):
    lead_id: int
    quality_score: float
    engagement_score: float
    conversion_probability: float
    recommended_actions: list[str]
    last_updated: datetime

    class Config:
        from_attributes = True 