from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.deps import get_current_active_user
from app.api.deps import get_db, get_current_customer
from app.models.models import User, Customer, Lead, InteractionLog
from app.analytics.schemas.analytics import (
    AnalyticsResponse,
    ConversionFunnelResponse,
    LeadScoreDistribution,
    LeadSourceStats,
    ChannelPerformance,
    TimeSeriesDataPoint,
    LeadStatusStats,
    PriceTrendResponse,
    TimeRange,
    LeadQualityResponse
)
from app.analytics.schemas.stats import LeadActivityStats, AgentPerformanceStats, InteractionStats
from app.analytics.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get analytics data for the current customer."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics(
        customer_id=current_customer.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/funnel", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get conversion funnel analytics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_conversion_funnel(current_customer.id)

@router.get("/sources", response_model=List[LeadSourceStats])
async def get_lead_sources(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get lead source statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_lead_sources(current_customer.id)

@router.get("/lead-status", response_model=List[LeadStatusStats])
async def get_lead_status_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get lead status statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_lead_status_stats(current_customer.id)

@router.get("/activity", response_model=List[LeadActivityStats])
async def get_lead_activity(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get lead activity statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_lead_activity(current_customer.id)

@router.get("/price-trends", response_model=PriceTrendResponse)
async def get_price_trends(
    time_range: TimeRange = TimeRange.LAST_30_DAYS,
    location: Optional[str] = None,
    property_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> PriceTrendResponse:
    """Get price trends for properties."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_price_trends(
        customer_id=current_customer.id,
        time_range=time_range,
        location=location,
        property_type=property_type
    )

@router.get("/lead-quality", response_model=LeadQualityResponse)
async def get_lead_quality(
    time_range: TimeRange = TimeRange.LAST_30_DAYS,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> LeadQualityResponse:
    """Get lead quality metrics including source distribution and conversion rates."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_lead_quality(
        customer_id=current_customer.id,
        time_range=time_range
    )

@router.get("/stats", response_model=AnalyticsResponse)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> AnalyticsResponse:
    """Get analytics data for the current customer."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics(current_customer.id)

@router.get("/lead-stats", response_model=LeadActivityStats)
async def get_lead_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> LeadActivityStats:
    """Get lead activity statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_lead_stats(current_customer.id)

@router.get("/agent-stats", response_model=List[AgentPerformanceStats])
async def get_agent_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> List[AgentPerformanceStats]:
    """Get agent performance statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_agent_stats(current_customer.id)

@router.get("/interaction-stats", response_model=InteractionStats)
async def get_interaction_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> InteractionStats:
    """Get interaction statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_interaction_stats(current_customer.id) 