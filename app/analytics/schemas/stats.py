from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ActivityMetric(BaseModel):
    """Base class for activity metrics."""
    count: int = 0
    trend: float = 0.0  # Percentage change
    last_activity: Optional[datetime] = None

class LeadActivityStats(BaseModel):
    """Lead activity statistics."""
    total_leads: int = 0
    active_leads: int = 0
    new_leads_today: int = 0
    new_leads_week: int = 0
    new_leads_month: int = 0
    conversion_rate: float = 0.0
    average_response_time: float = 0.0  # in minutes
    engagement_rate: float = 0.0
    status_distribution: Dict[str, int] = Field(default_factory=dict)
    source_distribution: Dict[str, int] = Field(default_factory=dict)
    activity_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    top_performing_agents: List[Dict[str, Any]] = Field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        from_attributes = True

class AgentPerformanceStats(BaseModel):
    """Agent performance statistics."""
    agent_id: int
    name: str
    total_leads: int = 0
    active_leads: int = 0
    converted_leads: int = 0
    conversion_rate: float = 0.0
    average_response_time: float = 0.0
    total_interactions: int = 0
    successful_interactions: int = 0
    success_rate: float = 0.0

    class Config:
        from_attributes = True

class InteractionStats(BaseModel):
    """Interaction statistics."""
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    average_duration: float = 0.0
    channel_distribution: Dict[str, int] = Field(default_factory=dict)
    time_distribution: Dict[str, int] = Field(default_factory=dict)
    outcome_distribution: Dict[str, int] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    """Complete analytics response."""
    lead_stats: LeadActivityStats
    agent_stats: List[AgentPerformanceStats]
    interaction_stats: InteractionStats
    generated_at: datetime

    class Config:
        from_attributes = True 