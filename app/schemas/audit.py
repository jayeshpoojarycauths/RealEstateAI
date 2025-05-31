from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AuditLogBase(BaseModel):
    action: str = Field(..., description="The action performed (e.g., 'create', 'update', 'delete')")
    resource_type: str = Field(..., description="The type of resource affected (e.g., 'lead', 'project')")
    resource_id: int = Field(..., description="The ID of the affected resource")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the action")
    user_id: Optional[int] = Field(None, description="ID of the user who performed the action")

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    tenant_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class AuditLogFilter(BaseModel):
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    skip: int = 0
    limit: int = 100 