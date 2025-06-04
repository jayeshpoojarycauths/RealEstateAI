from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.shared.models.activity import ActivityType

class LeadActivityBase(BaseModel):
    lead_id: int
    activity_type: ActivityType
    description: Optional[str] = None

class LeadActivityCreate(LeadActivityBase):
    pass

class LeadActivityUpdate(LeadActivityBase):
    pass

class LeadActivityResponse(LeadActivityBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 