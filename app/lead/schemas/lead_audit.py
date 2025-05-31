from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class LeadAuditLog(BaseModel):
    """Schema for lead audit log entry"""
    id: int
    lead_id: int
    user_id: int
    action: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LeadAuditLogResponse(BaseModel):
    """Schema for lead audit log response"""
    logs: List[LeadAuditLog]
    total: int

class LeadAuditStats(BaseModel):
    """Schema for lead audit statistics"""
    total_activities: int
    activities_by_type: dict
    activities_by_user: dict
    activities_by_date: dict

class LeadAuditStatsResponse(BaseModel):
    """Schema for lead audit statistics response"""
    stats: LeadAuditStats
    period_start: datetime
    period_end: datetime 