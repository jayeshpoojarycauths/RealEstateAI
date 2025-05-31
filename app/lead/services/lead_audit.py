from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta

from app.models.models import Lead, User, Customer
from app.lead.models.lead_activity import LeadActivity
from app.lead.schemas.lead_audit import (
    LeadAuditLog,
    LeadAuditLogResponse,
    LeadAuditStats,
    LeadAuditStatsResponse
)
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole

class LeadAuditService:
    def __init__(self, db: Session):
        self.db = db

    async def log_activity(
        self,
        lead_id: int,
        user_id: int,
        action: str,
        details: Optional[str] = None
    ) -> LeadAuditLog:
        """Log a lead activity"""
        activity = LeadActivity(
            lead_id=lead_id,
            user_id=user_id,
            activity_type=action,
            description=details,
            created_at=datetime.utcnow()
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    async def get_lead_activities(
        self,
        lead_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> LeadAuditLogResponse:
        """Get activities for a specific lead"""
        query = self.db.query(LeadActivity).filter(LeadActivity.lead_id == lead_id)
        total = query.count()
        activities = query.order_by(desc(LeadActivity.created_at)).offset(skip).limit(limit).all()
        
        return LeadAuditLogResponse(
            logs=[LeadAuditLog.from_orm(activity) for activity in activities],
            total=total
        )

    async def get_audit_stats(
        self,
        customer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> LeadAuditStatsResponse:
        """Get audit statistics for a customer"""
        query = self.db.query(LeadActivity).join(Lead).filter(
            Lead.customer_id == customer_id,
            LeadActivity.created_at.between(start_date, end_date)
        )

        # Get total activities
        total_activities = query.count()

        # Get activities by type
        activities_by_type = dict(
            query.with_entities(
                LeadActivity.activity_type,
                func.count(LeadActivity.id)
            ).group_by(LeadActivity.activity_type).all()
        )

        # Get activities by user
        activities_by_user = dict(
            query.with_entities(
                LeadActivity.user_id,
                func.count(LeadActivity.id)
            ).group_by(LeadActivity.user_id).all()
        )

        # Get activities by date
        activities_by_date = dict(
            query.with_entities(
                func.date(LeadActivity.created_at),
                func.count(LeadActivity.id)
            ).group_by(func.date(LeadActivity.created_at)).all()
        )

        stats = LeadAuditStats(
            total_activities=total_activities,
            activities_by_type=activities_by_type,
            activities_by_user=activities_by_user,
            activities_by_date=activities_by_date
        )

        return LeadAuditStatsResponse(
            stats=stats,
            period_start=start_date,
            period_end=end_date
        ) 