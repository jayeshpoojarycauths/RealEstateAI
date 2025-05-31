from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
from app.core.deps import get_current_active_user
from app.api import deps
from app.models.models import RealEstateProject, Lead, Customer, User, InteractionLog
from app.schemas.stats import (
    PriceTrendResponse,
    LeadQualityResponse,
    PriceTrendPoint,
    LeadQualityMetric,
    StatsResponse,
    LeadStats,
    ProjectStats,
    ActivityStats
)
from app.schemas.analytics import (
    LeadScoreDistribution,
    ScoreBucket,
    ConversionFunnelResponse,
    ConversionFunnelStage
)
from app.services.stats import StatsService

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    current_customer = Depends(deps.get_current_customer)
):
    """Get comprehensive statistics for the current customer."""
    stats_service = StatsService(db)
    return await stats_service.get_stats(
        customer_id=current_customer.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/stats/price-trends/{property_type}", response_model=PriceTrendResponse)
async def get_price_trends(
    property_type: str,
    location: str,
    db: Session = Depends(deps.get_db),
    current_customer = Depends(deps.get_current_customer)
):
    """Get price trends for a specific property type and location."""
    # TODO: Implement price trend analysis
    raise HTTPException(status_code=501, detail="Price trend analysis not implemented yet")

@router.get("/stats/lead-quality/{lead_id}", response_model=LeadQualityResponse)
async def get_lead_quality(
    lead_id: int,
    db: Session = Depends(deps.get_db),
    current_customer = Depends(deps.get_current_customer)
):
    """Get quality analysis for a specific lead."""
    # TODO: Implement lead quality analysis
    raise HTTPException(status_code=501, detail="Lead quality analysis not implemented yet")

@router.get("/leads", response_model=LeadStats)
async def get_lead_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Get lead-related statistics."""
    stats_service = StatsService(db)
    return await stats_service.get_lead_stats(current_customer.id)

@router.get("/projects", response_model=ProjectStats)
async def get_project_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Get project-related statistics."""
    stats_service = StatsService(db)
    return await stats_service.get_project_stats(current_customer.id)

@router.get("/activity", response_model=ActivityStats)
async def get_activity_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Get activity-related statistics."""
    stats_service = StatsService(db)
    return await stats_service.get_activity_stats(current_customer.id)

@router.get("/price-trends", response_model=PriceTrendResponse)
async def get_price_trends(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Get price trends for the current customer."""
    stats_service = StatsService(db)
    return await stats_service.get_price_trends(
        customer_id=current_customer.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/lead-quality/", response_model=LeadQualityResponse)
async def get_lead_quality(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """
    Get lead quality metrics including source distribution and conversion rates.
    """
    try:
        # Parse dates
        end = datetime.utcnow() if not end_date else datetime.fromisoformat(end_date)
        start = end - timedelta(days=30) if not start_date else datetime.fromisoformat(start_date)
        
        # Get total leads
        total_leads = db.query(func.count(Lead.id)).filter(
            Lead.tenant_id == current_customer.id,
            Lead.created_at.between(start, end)
        ).scalar()
        
        # Get source distribution
        source_distribution = db.query(
            Lead.source,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.tenant_id == current_customer.id,
            Lead.created_at.between(start, end)
        ).group_by(Lead.source).all()
        
        # Get conversion rates
        conversion_rates = db.query(
            Lead.source,
            func.count(Lead.id).filter(Lead.status == 'converted').label('converted'),
            func.count(Lead.id).label('total')
        ).filter(
            Lead.tenant_id == current_customer.id,
            Lead.created_at.between(start, end)
        ).group_by(Lead.source).all()
        
        # Format response
        return LeadQualityResponse(
            total_leads=total_leads,
            source_distribution=[
                LeadQualityMetric(name=source, value=count)
                for source, count in source_distribution
            ],
            conversion_rates=[
                LeadQualityMetric(
                    name=source,
                    value=float(converted) / total if total > 0 else 0
                )
                for source, converted, total in conversion_rates
            ]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lead-score/", response_model=LeadScoreDistribution)
async def get_lead_score_distribution(
    db: Session = Depends(deps.get_db),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """
    Get distribution of leads by score buckets.
    """
    try:
        # Define score buckets
        score_buckets = [
            (0, 25, "0-25"),
            (26, 50, "26-50"),
            (51, 75, "51-75"),
            (76, 100, "76-100")
        ]

        # Build the case statement for bucketing
        bucket_case = case(
            *[
                (
                    (Lead.score >= min_score) & (Lead.score <= max_score),
                    bucket_name
                )
                for min_score, max_score, bucket_name in score_buckets
            ],
            else_="Unknown"
        )

        # Query to get counts per bucket
        bucket_counts = (
            db.query(
                bucket_case.label("bucket"),
                func.count(Lead.id).label("count")
            )
            .filter(Lead.tenant_id == current_customer.id)
            .group_by(bucket_case)
            .all()
        )

        # Get total lead count
        total_leads = (
            db.query(func.count(Lead.id))
            .filter(Lead.tenant_id == current_customer.id)
            .scalar()
        )

        # Format response
        return LeadScoreDistribution(
            total_leads=total_leads,
            buckets=[
                ScoreBucket(
                    range=bucket_name,
                    count=next((count for bucket, count in bucket_counts if bucket == bucket_name), 0)
                )
                for _, _, bucket_name in score_buckets
            ]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversion-funnel/", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    db: Session = Depends(deps.get_db),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """
    Get lead conversion funnel data showing distribution across stages.
    """
    try:
        # Define stages in order
        stages = ["new", "contacted", "qualified", "converted"]
        
        # Get total leads count
        total_leads = (
            db.query(func.count(Lead.id))
            .filter(Lead.tenant_id == current_customer.id)
            .scalar()
        )
        
        if total_leads == 0:
            return ConversionFunnelResponse(
                total_leads=0,
                stages=[
                    ConversionFunnelStage(stage=stage, count=0, percentage=0.0)
                    for stage in stages
                ]
            )
        
        # Get count for each stage
        stage_counts = (
            db.query(
                Lead.status,
                func.count(Lead.id).label('count')
            )
            .filter(Lead.tenant_id == current_customer.id)
            .group_by(Lead.status)
            .all()
        )
        
        # Convert to dictionary for easy lookup
        stage_count_dict = {status: count for status, count in stage_counts}
        
        # Format response
        funnel_stages = []
        for stage in stages:
            count = stage_count_dict.get(stage, 0)
            percentage = (count / total_leads) * 100 if total_leads > 0 else 0
            funnel_stages.append(
                ConversionFunnelStage(
                    stage=stage,
                    count=count,
                    percentage=percentage
                )
            )
        
        return ConversionFunnelResponse(
            total_leads=total_leads,
            stages=funnel_stages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 