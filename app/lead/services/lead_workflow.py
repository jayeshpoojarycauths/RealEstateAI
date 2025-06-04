from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import json
from fastapi import Depends

from app.models.models import Lead, User, Customer, LeadActivity, ActivityType
from app.lead.schemas.lead import LeadResponse
from app.lead.schemas.lead_activity import LeadActivityResponse
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole
from app.shared.core.audit import AuditService, get_audit_service
from app.shared.core.exceptions import NotFoundException, ValidationException
from app.shared.core.email import send_email
from app.shared.core.sms import send_sms

class LeadWorkflowService:
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.customer = customer
        self.audit_logger = AuditLogger(db, customer)

    async def create_lead_activity(
        self,
        lead_id: int,
        activity_type: ActivityType,
        description: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> LeadActivity:
        """Create a new lead activity."""
        activity = LeadActivity(
            lead_id=lead_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        await self.audit_logger.log_action(
            action="create",
            entity_type="lead_activity",
            entity_id=activity.id,
            user_id=str(user_id) if user_id else None,
            details={
                "lead_id": lead_id,
                "activity_type": activity_type.value,
                "description": description
            }
        )
        
        return activity

    async def get_lead_activities(
        self,
        lead_id: int,
        activity_type: Optional[ActivityType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[LeadActivity]:
        """Get activities for a lead with optional filtering."""
        query = self.db.query(LeadActivity).filter(LeadActivity.lead_id == lead_id)
        
        if activity_type:
            query = query.filter(LeadActivity.activity_type == activity_type)
        if start_date:
            query = query.filter(LeadActivity.created_at >= start_date)
        if end_date:
            query = query.filter(LeadActivity.created_at <= end_date)
            
        return query.order_by(LeadActivity.created_at.desc()).all()

    async def update_lead_status(
        self,
        lead_id: int,
        new_status: str,
        user_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Lead:
        """Update lead status and create activity."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        old_status = lead.status
        lead.status = new_status
        lead.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(lead)
        
        # Create activity for status change
        await self.create_lead_activity(
            lead_id=lead_id,
            activity_type=ActivityType.STATUS_CHANGE,
            description=f"Status changed from {old_status} to {new_status}. {notes or ''}",
            user_id=user_id
        )
        
        await self.audit_logger.log_action(
            action="update",
            entity_type="lead",
            entity_id=lead_id,
            user_id=str(user_id) if user_id else None,
            details={
                "old_status": old_status,
                "new_status": new_status,
                "notes": notes
            }
        )
        
        return lead

    async def assign_lead(
        self,
        lead_id: int,
        user_id: int,
        assigned_by: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Lead:
        """Assign lead to a user and create activity."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        old_assignee = lead.assigned_to
        lead.assigned_to = user_id
        lead.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(lead)
        
        # Create activity for assignment
        await self.create_lead_activity(
            lead_id=lead_id,
            activity_type=ActivityType.ASSIGNMENT,
            description=f"Lead assigned to user {user_id}. {notes or ''}",
            user_id=assigned_by
        )
        
        await self.audit_logger.log_action(
            action="assign",
            entity_type="lead",
            entity_id=lead_id,
            user_id=str(assigned_by) if assigned_by else None,
            details={
                "old_assignee": old_assignee,
                "new_assignee": user_id,
                "notes": notes
            }
        )
        
        return lead

# ... existing code ... 