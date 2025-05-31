from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AnalyticsTimeRange(BaseModel):
    start_date: datetime
    end_date: datetime

class LeadAnalytics(BaseModel):
    total_leads: int
    new_leads: int
    converted_leads: int
    conversion_rate: float
    lead_sources: Dict[str, int]
    lead_status_distribution: Dict[str, int]
    average_response_time: float
    top_performing_agents: List[Dict[str, Any]]

class ProjectAnalytics(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    project_status_distribution: Dict[str, int]
    average_project_duration: float
    project_type_distribution: Dict[str, int]

class CustomerAnalytics(BaseModel):
    total_customers: int
    new_customers: int
    customer_satisfaction_score: float
    customer_retention_rate: float
    top_customer_segments: List[Dict[str, Any]]

class AnalyticsResponse(BaseModel):
    lead_analytics: LeadAnalytics
    project_analytics: ProjectAnalytics
    customer_analytics: CustomerAnalytics
    time_range: AnalyticsTimeRange
    generated_at: datetime

class LeadScoreDistribution(BaseModel):
    score_range: str
    count: int
    percentage: float

class LeadSourceDistribution(BaseModel):
    source: str
    count: int
    percentage: float

class LeadStatusDistribution(BaseModel):
    status: str
    count: int
    percentage: float

class LeadActivityMetrics(BaseModel):
    total_activities: int
    activities_by_type: Dict[str, int]
    average_response_time: float
    most_active_users: List[Dict[str, Any]]

class LeadConversionMetrics(BaseModel):
    total_leads: int
    converted_leads: int
    conversion_rate: float
    average_conversion_time: float
    conversion_by_source: Dict[str, float]

class OutreachMetrics(BaseModel):
    total_outreach: int
    successful_outreach: int
    success_rate: float
    outreach_by_channel: Dict[str, int]
    response_rate: float

class ProjectMetrics(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    projects_by_status: Dict[str, int]
    average_completion_time: float

class AnalyticsResponse(BaseModel):
    lead_scores: List[LeadScoreDistribution]
    lead_sources: List[LeadSourceDistribution]
    lead_statuses: List[LeadStatusDistribution]
    lead_activities: LeadActivityMetrics
    lead_conversions: LeadConversionMetrics
    outreach_metrics: OutreachMetrics
    project_metrics: ProjectMetrics
    generated_at: datetime

class ScoreBucket(BaseModel):
    min_score: float
    max_score: float
    count: int
    percentage: float
    leads: List[Dict[str, Any]]

class ConversionFunnelStage(BaseModel):
    stage: str
    count: int
    percentage: float
    drop_off: float

class ConversionFunnelResponse(BaseModel):
    stages: List[ConversionFunnelStage]
    total_leads: int
    conversion_rate: float
    average_time_to_convert: float
    generated_at: datetime

class LeadStatusStats(BaseModel):
    status: str
    count: int
    percentage: float
    trend: Optional[str] = None  # "up", "down", "stable"
    last_updated: datetime

    class Config:
        from_attributes = True

class LeadScoreDistribution(BaseModel):
    total_leads: int
    buckets: List[Dict[str, int]]
    last_updated: datetime

    class Config:
        from_attributes = True

class ConversionFunnelStage(BaseModel):
    stage: str
    count: int
    percentage: float
    last_updated: datetime

    class Config:
        from_attributes = True

class ConversionFunnelResponse(BaseModel):
    total_leads: int
    stages: List[ConversionFunnelStage]
    last_updated: datetime

    class Config:
        from_attributes = True 