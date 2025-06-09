from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.analytics.schemas.analytics import (AnalyticsResponse,
                                             ConversionFunnelResponse,
                                             LeadActivityStats,
                                             LeadQualityResponse,
                                             LeadSourceStats, LeadStatusStats,
                                             PriceTrendDataPoint,
                                             PriceTrendResponse, TimeRange)
from app.lead.models.lead import Lead
from app.shared.models.interaction import InteractionLog
from app.shared.models.interaction import InteractionLog
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func
from datetime import timedelta
from app.shared.models.interaction import InteractionLog
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func
from datetime import timedelta


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def _get_date_range(self, time_range: TimeRange) -> tuple[datetime, datetime]:
        """Get start and end dates for the given time range."""
        now = datetime.utcnow()
        if time_range == TimeRange.TODAY:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_range == TimeRange.YESTERDAY:
            start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == TimeRange.LAST_7_DAYS:
            start_date = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_range == TimeRange.LAST_30_DAYS:
            start_date = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_range == TimeRange.THIS_MONTH:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_range == TimeRange.LAST_MONTH:
            last_month = now.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError(f"Unsupported time range: {time_range}")
        return start_date, end_date

    async def get_analytics(
        self,
        customer_id: str,
        time_range: TimeRange = TimeRange.get_default()
    ) -> AnalyticsResponse:
        """Get comprehensive analytics data."""
        start_date, end_date = self._get_date_range(time_range)
        
        # Mock implementation - replace with actual database queries
        return AnalyticsResponse(
            total_leads=100,
            active_leads=50,
            conversion_rate=0.25,
            average_lead_score=0.75,
            lead_sources=[],
            score_distribution=[],
            channel_performance=[],
            leads_over_time=[],
            conversions_over_time=[],
            conversion_funnel=None,
            average_response_time=2.5,
            total_value=1000000.0,
            top_performing_channels=["website", "referral"],
            time_period=time_range.value,
            total_interactions=500,
            total_projects=20,
            active_projects=15,
            period_start=start_date,
            period_end=end_date,
            new_leads=30,
            qualified_leads=40,
            converted_leads=25,
            average_conversion_rate=0.25,
            source_distribution={},
            lead_stats=None,
            agent_stats=None,
            interaction_stats=None,
            timestamp=datetime.utcnow()
        )

    async def get_conversion_funnel(
        self,
        customer_id: int
    ) -> ConversionFunnelResponse:
        """Get conversion funnel analytics."""
        # Get counts for each stage
        new_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.customer_id == customer_id,
            Lead.status == 'new'
        ).scalar()

        qualified_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.customer_id == customer_id,
            Lead.status == 'qualified'
        ).scalar()

        converted_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.customer_id == customer_id,
            Lead.status == 'converted'
        ).scalar()

        return ConversionFunnelResponse(
            new_leads=new_leads,
            qualified_leads=qualified_leads,
            converted_leads=converted_leads,
            conversion_rate=converted_leads / new_leads if new_leads > 0 else 0
        )

    async def get_lead_sources(
        self,
        customer_id: int
    ) -> List[LeadSourceStats]:
        """Get lead source statistics."""
        sources = self.db.query(
            Lead.source,
            func.count(Lead.id).label('count'),
            func.avg(Lead.score).label('avg_score')
        ).filter(
            Lead.customer_id == customer_id
        ).group_by(Lead.source).all()

        return [
            LeadSourceStats(
                source=source,
                count=count,
                avg_score=float(avg_score) if avg_score else 0.0
            )
            for source, count, avg_score in sources
        ]

    async def get_lead_status_stats(
        self,
        customer_id: int
    ) -> List[LeadStatusStats]:
        """Get lead status statistics."""
        statuses = self.db.query(
            Lead.status,
            func.count(Lead.id).label('count'),
            func.avg(Lead.score).label('avg_score')
        ).filter(
            Lead.customer_id == customer_id
        ).group_by(Lead.status).all()

        return [
            LeadStatusStats(
                status=status,
                count=count,
                avg_score=float(avg_score) if avg_score else 0.0
            )
            for status, count, avg_score in statuses
        ]

    async def get_lead_activity(
        self,
        customer_id: int
    ) -> List[LeadActivityStats]:
        """Get lead activity statistics."""
        activities = self.db.query(
            InteractionLog.interaction_type,
            func.count(InteractionLog.id).label('count'),
            func.avg(InteractionLog.duration).label('avg_duration')
        ).filter(
            InteractionLog.customer_id == customer_id
        ).group_by(InteractionLog.interaction_type).all()

        return [
            LeadActivityStats(
                activity_type=activity_type,
                count=count,
                avg_duration=float(avg_duration) if avg_duration else 0.0
            )
            for activity_type, count, avg_duration in activities
        ]

    async def get_price_trends(
        self,
        customer_id: str,
        time_range: TimeRange = TimeRange.get_default(),
        location: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> PriceTrendResponse:
        """Get price trends for properties."""
        start_date, end_date = self._get_date_range(time_range)
        
        # Mock implementation - replace with actual database queries
        return PriceTrendResponse(
            data_points=[
                PriceTrendDataPoint(
                    date=start_date + timedelta(days=i),
                    average_price=500000.0 + (i * 1000),
                    median_price=450000.0 + (i * 1000),
                    min_price=300000.0 + (i * 1000),
                    max_price=800000.0 + (i * 1000),
                    volume=10 + i,
                    location=location or "All Locations",
                    property_type=property_type or "All Types"
                )
                for i in range((end_date - start_date).days + 1)
            ],
            time_range=time_range,
            location=location,
            property_type=property_type,
            generated_at=datetime.utcnow()
        )

    async def get_lead_quality(
        self,
        customer_id: str,
        time_range: TimeRange = TimeRange.get_default()
    ) -> LeadQualityResponse:
        """Get lead quality metrics."""
        start_date, end_date = self._get_date_range(time_range)
        
        # Mock implementation - replace with actual database queries
        return LeadQualityResponse(
            source_distribution={
                "website": 100,
                "referral": 50,
                "social": 30
            },
            conversion_rates={
                "website": 0.15,
                "referral": 0.25,
                "social": 0.10
            },
            average_response_time=2.5,
            engagement_score=0.75,
            time_range=time_range,
            generated_at=datetime.utcnow()
        ) 