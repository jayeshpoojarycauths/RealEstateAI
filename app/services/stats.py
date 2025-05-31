from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.models import (
    Lead, Project, InteractionLog, Customer, ProjectStatus
)
from app.schemas.stats import (
    StatsResponse,
    LeadStats,
    ProjectStats,
    ActivityStats,
    PriceTrendResponse,
    LeadQualityResponse
)

class StatsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_stats(
        self,
        customer_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> StatsResponse:
        """Get comprehensive statistics for a customer."""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get lead statistics
        lead_stats = await self.get_lead_stats(customer_id, start_date, end_date)
        
        # Get project statistics
        project_stats = await self.get_project_stats(customer_id, start_date, end_date)
        
        # Get activity statistics
        activity_stats = await self.get_activity_stats(customer_id, start_date, end_date)

        return StatsResponse(
            lead_stats=lead_stats,
            project_stats=project_stats,
            activity_stats=activity_stats,
            generated_at=datetime.utcnow()
        )

    async def get_lead_stats(
        self,
        customer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> LeadStats:
        """Get lead-related statistics."""
        total_leads = self.db.query(Lead).filter(
            Lead.customer_id == customer_id
        ).count()

        active_leads = self.db.query(Lead).filter(
            Lead.customer_id == customer_id,
            Lead.status == 'active'
        ).count()

        converted_leads = self.db.query(Lead).filter(
            Lead.customer_id == customer_id,
            Lead.status == 'converted'
        ).count()

        # Get leads by source
        leads_by_source = {}
        source_counts = self.db.query(
            Lead.source,
            func.count(Lead.id)
        ).filter(
            Lead.customer_id == customer_id
        ).group_by(Lead.source).all()

        for source, count in source_counts:
            # Convert None sources to 'unknown'
            source_key = str(source) if source is not None else 'unknown'
            leads_by_source[source_key] = count

        # Get leads by status
        leads_by_status = {}
        status_counts = self.db.query(
            Lead.status,
            func.count(Lead.id)
        ).filter(
            Lead.customer_id == customer_id
        ).group_by(Lead.status).all()

        for status, count in status_counts:
            # Convert None statuses to 'unknown'
            status_key = str(status) if status is not None else 'unknown'
            leads_by_status[status_key] = count

        # Calculate conversion rate
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0

        # Calculate average response time
        avg_response_time = self.db.query(
            func.avg(InteractionLog.response_time)
        ).filter(
            InteractionLog.customer_id == customer_id,
            InteractionLog.created_at.between(start_date, end_date)
        ).scalar() or 0

        return LeadStats(
            total_leads=total_leads,
            active_leads=active_leads,
            converted_leads=converted_leads,
            leads_by_source=leads_by_source,
            leads_by_status=leads_by_status,
            conversion_rate=conversion_rate,
            average_response_time=avg_response_time,
            last_updated=datetime.utcnow()
        )

    async def get_project_stats(
        self,
        customer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> ProjectStats:
        """Get project-related statistics."""
        total_projects = self.db.query(Project).filter(
            Project.customer_id == customer_id
        ).count()

        active_projects = self.db.query(Project).filter(
            Project.customer_id == customer_id,
            Project.status == ProjectStatus.IN_PROGRESS
        ).count()

        completed_projects = self.db.query(Project).filter(
            Project.customer_id == customer_id,
            Project.status == ProjectStatus.COMPLETED
        ).count()

        # Calculate project value
        total_value = 0  # Project model does not have total_value column

        return ProjectStats(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_value=total_value,
            last_updated=datetime.utcnow()
        )

    async def get_activity_stats(
        self,
        customer_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> ActivityStats:
        """Get activity-related statistics."""
        # Get total interactions
        total_interactions = self.db.query(InteractionLog).filter(
            InteractionLog.customer_id == customer_id,
            InteractionLog.created_at.between(start_date, end_date)
        ).count()

        # Get interactions by type
        interactions_by_type = {}
        type_counts = self.db.query(
            InteractionLog.interaction_type,
            func.count(InteractionLog.id)
        ).filter(
            InteractionLog.customer_id == customer_id,
            InteractionLog.created_at.between(start_date, end_date)
        ).group_by(InteractionLog.interaction_type).all()

        for interaction_type, count in type_counts:
            interactions_by_type[interaction_type] = count

        # Calculate success rate
        successful_interactions = self.db.query(InteractionLog).filter(
            InteractionLog.customer_id == customer_id,
            InteractionLog.status == 'success',
            InteractionLog.created_at.between(start_date, end_date)
        ).count()

        success_rate = (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0

        return ActivityStats(
            total_interactions=total_interactions,
            interactions_by_type=interactions_by_type,
            success_rate=success_rate,
            last_updated=datetime.utcnow()
        ) 