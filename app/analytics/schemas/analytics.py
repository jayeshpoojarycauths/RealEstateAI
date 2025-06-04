from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Lead Score Distribution Schemas
class ScoreBucket(BaseModel):
    range: str
    count: int

class LeadScoreDistribution(BaseModel):
    score_range: str
    count: int
    percentage: float

# Conversion Funnel Schemas
class ConversionFunnelStage(BaseModel):
    """Schema for a stage in the conversion funnel."""
    stage: str
    count: int
    percentage: float
    drop_off: Optional[float] = None

class TimeRange(str, Enum):
    """Time range options for analytics queries."""
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"

    @classmethod
    def get_default(cls) -> "TimeRange":
        """Get the default time range."""
        return cls.LAST_30_DAYS

class ConversionFunnelResponse(BaseModel):
    """Schema for conversion funnel analytics."""
    stages: List[ConversionFunnelStage]
    total_leads: int
    conversion_rate: float
    average_time_to_convert: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Price Trend Schemas
class PriceTrendPoint(BaseModel):
    date: str
    avg_price: float
    count: int

class PriceTrendDataPoint(BaseModel):
    """Data point for price trends."""
    date: datetime
    average_price: float
    median_price: float
    min_price: float
    max_price: float
    volume: int
    location: str
    property_type: str

class PriceTrendResponse(BaseModel):
    """Response model for price trends."""
    data_points: List[PriceTrendDataPoint]
    time_range: TimeRange
    location: Optional[str] = None
    property_type: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

# Lead Quality Schemas
class LeadQualityMetric(BaseModel):
    name: str
    value: float

class LeadQualityResponse(BaseModel):
    """Response model for lead quality metrics."""
    source_distribution: Dict[str, int]
    conversion_rates: Dict[str, float]
    average_response_time: float
    engagement_score: float
    time_range: TimeRange
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

# Lead Source Metrics
class LeadSourceMetrics(BaseModel):
    """Schema for lead source metrics."""
    source: str
    total_leads: int
    conversion_rate: float
    average_score: float
    total_value: float

class ChannelPerformance(BaseModel):
    """Schema for channel performance metrics."""
    channel: str
    total_interactions: int
    success_rate: float
    average_response_time: float
    conversion_rate: float

class TimeSeriesDataPoint(BaseModel):
    """Schema for a time series data point."""
    timestamp: datetime
    value: float
    label: Optional[str] = None

class LeadSourceStats(BaseModel):
    """Statistics for a lead source."""
    source: str
    total_leads: int
    active_leads: int
    conversion_rate: float
    avg_response_time: Optional[float] = None
    avg_lead_score: Optional[float] = None

class ActivityMetric(BaseModel):
    count: int
    trend: float
    last_activity: Optional[datetime] = None

class LeadActivityStats(BaseModel):
    """Lead activity statistics schema."""
    total_leads: int
    active_leads: int
    new_leads_today: int
    new_leads_this_week: int
    new_leads_this_month: int
    leads_by_status: Dict[str, int]
    leads_by_source: Dict[str, int]
    average_response_time: float
    last_activity: Optional[datetime] = None

class AgentPerformanceStats(BaseModel):
    total_leads: int
    conversion_rate: float
    avg_response_time: float
    interactions_per_lead: float
    success_rate: float
    status_distribution: Dict[str, int]

class InteractionStats(BaseModel):
    total_interactions: int
    success_rate: float
    avg_response_time: float
    channel_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    timeline: List[Dict[str, Any]]

class AnalyticsResponse(BaseModel):
    """Analytics response schema."""
    total_leads: int
    active_leads: int
    conversion_rate: float
    average_response_time: float
    lead_quality_score: float
    lead_status_distribution: Dict[str, int]
    lead_activity_stats: 'LeadActivityStats'
    lead_status_stats: List['LeadStatusStats']

    # Source metrics
    lead_sources: List[LeadSourceMetrics]
    
    # Score distribution
    score_distribution: List[LeadScoreDistribution]
    
    # Channel performance
    channel_performance: List[ChannelPerformance]
    
    # Time series data
    leads_over_time: List[TimeSeriesDataPoint]
    conversions_over_time: List[TimeSeriesDataPoint]
    
    # Funnel data
    conversion_funnel: ConversionFunnelResponse
    
    # Additional metrics
    total_value: float
    top_performing_channels: List[str]
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_period: str
    filters: Optional[Dict[str, Any]] = None

    # New fields from the code block
    source_metrics: List[LeadSourceStats]
    additional_metrics: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, str]] = None

    # New fields from the code block
    total_interactions: int
    total_projects: int
    active_projects: int
    period_start: datetime
    period_end: datetime

    # New fields from the code block
    new_leads: int
    qualified_leads: int
    converted_leads: int
    average_conversion_rate: float

    # New fields from the code block
    source_distribution: Dict[str, Dict[str, Any]]

    timestamp: datetime

class LeadStatusStats(BaseModel):
    """Lead status statistics schema."""
    status: str
    count: int
    percentage: float
    trend: float  # Percentage change from previous period
    timestamp: datetime

    # New fields from the code block
    total_leads: int
    active_leads: int
    conversion_rate: float
    engagement_rate: float
    new_leads_today: int
    new_leads_this_week: int
    new_leads_this_month: int
    leads_by_status: Dict[str, int]
    leads_by_source: Dict[str, int]
    average_response_time: float
    last_activity: Optional[datetime] = None

    # New fields from the code block
    source_metrics: List[LeadSourceStats]
    additional_metrics: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, str]] = None

    # New fields from the code block
    total_interactions: int
    total_projects: int
    active_projects: int
    period_start: datetime
    period_end: datetime

    # New fields from the code block
    new_leads: int
    qualified_leads: int
    converted_leads: int
    average_conversion_rate: float

    # New fields from the code block
    source_distribution: Dict[str, Dict[str, Any]]

    lead_stats: LeadActivityStats
    agent_stats: AgentPerformanceStats
    interaction_stats: InteractionStats
    timestamp: datetime 