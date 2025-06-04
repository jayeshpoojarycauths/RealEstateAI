from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum
from app.shared.models.interaction import InteractionType

class InteractionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    NO_RESPONSE = "no_response"

class LeadScoreBase(BaseModel):
    score: float = Field(..., ge=0, le=100)
    scoring_factors: Dict[str, Any]

class LeadScoreCreate(LeadScoreBase):
    lead_id: UUID

class LeadScoreUpdate(LeadScoreBase):
    pass

class LeadScoreInDBBase(LeadScoreBase):
    id: UUID
    lead_id: UUID
    last_updated: datetime

    class Config:
        orm_mode = True

class LeadScore(LeadScoreInDBBase):
    pass

class InteractionLogBase(BaseModel):
    lead_id: UUID
    customer_id: UUID
    interaction_type: InteractionType
    status: InteractionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    user_input: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None  # Average response time in seconds

class InteractionLogCreate(InteractionLogBase):
    pass

class InteractionLogUpdate(BaseModel):
    status: Optional[InteractionStatus] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    user_input: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None  # Average response time in seconds

class InteractionLogInDBBase(InteractionLogBase):
    id: UUID

    class Config:
        orm_mode = True

class InteractionLog(InteractionLogInDBBase):
    pass

class CallInteractionBase(BaseModel):
    call_sid: str
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    keypad_inputs: Optional[Dict[str, Any]] = None
    menu_selections: Optional[Dict[str, Any]] = None
    call_quality_metrics: Optional[Dict[str, Any]] = None

class CallInteractionCreate(CallInteractionBase):
    interaction_id: UUID

class CallInteractionUpdate(CallInteractionBase):
    pass

class CallInteractionInDBBase(CallInteractionBase):
    id: UUID
    interaction_id: UUID

    class Config:
        orm_mode = True

class CallInteraction(CallInteractionInDBBase):
    pass

class MessageInteractionBase(BaseModel):
    message_id: str
    content: str
    response_content: Optional[str] = None
    response_time: Optional[int] = None
    delivery_status: Optional[str] = None

class MessageInteractionCreate(MessageInteractionBase):
    interaction_id: UUID

class MessageInteractionUpdate(MessageInteractionBase):
    pass

class MessageInteractionInDBBase(MessageInteractionBase):
    id: UUID
    interaction_id: UUID

    class Config:
        orm_mode = True

class MessageInteraction(MessageInteractionInDBBase):
    pass 