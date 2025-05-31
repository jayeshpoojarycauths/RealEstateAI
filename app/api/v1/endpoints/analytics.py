from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import User, Customer
from app.analytics.schemas.analytics import (
    AnalyticsResponse,
    LeadQualityResponse,
    PriceTrendResponse,
    TimeRange
)
from app.analytics.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    time_range: TimeRange = Query(default=TimeRange.get_default()),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
) -> AnalyticsResponse:
    """Get comprehensive analytics data."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_analytics(
        customer_id=current_customer.id,
        time_range=time_range
    )

@router.get("/lead-quality", response_model=LeadQualityResponse)
async def get_lead_quality(
    time_range: TimeRange = Query(default=TimeRange.get_default()),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
) -> LeadQualityResponse:
    """Get lead quality metrics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_lead_quality(
        customer_id=current_customer.id,
        time_range=time_range
    )

@router.get("/price-trends", response_model=PriceTrendResponse)
async def get_price_trends(
    time_range: TimeRange = Query(default=TimeRange.get_default()),
    location: Optional[str] = None,
    property_type: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
) -> PriceTrendResponse:
    """Get price trends for properties."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_price_trends(
        customer_id=current_customer.id,
        time_range=time_range,
        location=location,
        property_type=property_type
    ) 