import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.lead.models import LeadActivity
from app.lead.models.lead import Lead
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from sqlalchemy import func
from datetime import timedelta
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from sqlalchemy import func
from datetime import timedelta

logger = logging.getLogger(__name__)

class LeadAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_lead_conversion_rate(self, customer_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """Calculate lead conversion rate for a customer."""
        try:
            query = self.db.query(Lead).filter(Lead.customer_id == customer_id)
            
            if start_date:
                query = query.filter(Lead.created_at >= start_date)
            if end_date:
                query = query.filter(Lead.created_at <= end_date)
            
            total_leads = query.count()
            converted_leads = query.filter(Lead.status == 'converted').count()
            
            return (converted_leads / total_leads * 100) if total_leads > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating lead conversion rate: {str(e)}")
            raise

    def get_lead_source_distribution(self, customer_id: int) -> Dict[str, int]:
        """Get distribution of leads by source."""
        try:
            results = self.db.query(
                Lead.source,
                func.count(Lead.id).label('count')
            ).filter(
                Lead.customer_id == customer_id
            ).group_by(
                Lead.source
            ).all()
            
            return {source: count for source, count in results}
            
        except Exception as e:
            logger.error(f"Error getting lead source distribution: {str(e)}")
            raise

    def get_lead_activity_metrics(self, customer_id: int, days: int = 30) -> Dict[str, Any]:
        """Get lead activity metrics for the specified period."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get total activities
            total_activities = self.db.query(LeadActivity).join(
                Lead
            ).filter(
                Lead.customer_id == customer_id,
                LeadActivity.created_at >= start_date
            ).count()
            
            # Get activities by type
            activities_by_type = self.db.query(
                LeadActivity.activity_type,
                func.count(LeadActivity.id).label('count')
            ).join(
                Lead
            ).filter(
                Lead.customer_id == customer_id,
                LeadActivity.created_at >= start_date
            ).group_by(
                LeadActivity.activity_type
            ).all()
            
            # Get average response time
            response_times = self.db.query(
                func.avg(
                    func.extract('epoch', LeadActivity.created_at) -
                    func.extract('epoch', Lead.created_at)
                ).label('avg_response_time')
            ).join(
                Lead
            ).filter(
                Lead.customer_id == customer_id,
                LeadActivity.created_at >= start_date
            ).scalar()
            
            return {
                'total_activities': total_activities,
                'activities_by_type': {t: c for t, c in activities_by_type},
                'avg_response_time_seconds': response_times or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting lead activity metrics: {str(e)}")
            raise

    def get_lead_trends(self, customer_id: int, days: int = 30) -> Dict[str, List[Any]]:
        """Get lead trends over time."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get daily lead counts
            daily_leads = self.db.query(
                func.date(Lead.created_at).label('date'),
                func.count(Lead.id).label('count')
            ).filter(
                Lead.customer_id == customer_id,
                Lead.created_at >= start_date
            ).group_by(
                func.date(Lead.created_at)
            ).all()
            
            # Get daily conversion counts
            daily_conversions = self.db.query(
                func.date(Lead.updated_at).label('date'),
                func.count(Lead.id).label('count')
            ).filter(
                Lead.customer_id == customer_id,
                Lead.status == 'converted',
                Lead.updated_at >= start_date
            ).group_by(
                func.date(Lead.updated_at)
            ).all()
            
            return {
                'dates': [str(d.date) for d in daily_leads],
                'lead_counts': [d.count for d in daily_leads],
                'conversion_counts': [d.count for d in daily_conversions]
            }
            
        except Exception as e:
            logger.error(f"Error getting lead trends: {str(e)}")
            raise 