from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services.reporting import ReportingService
from app.api.deps import get_db, get_current_customer

router = APIRouter()

@router.get("/daily")
async def get_daily_report(
    report_date: Optional[date] = Query(None, description="Date for the report (defaults to yesterday)"),
    send_email: bool = Query(False, description="Whether to send email notification"),
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """Get daily report for the current customer."""
    reporting_service = ReportingService(db)
    
    if report_date is None:
        report_date = datetime.utcnow().date()
    
    # Check if report exists
    existing_report = reporting_service.get_report(
        current_customer.id,
        "daily",
        report_date
    )
    
    if existing_report:
        report_data = existing_report
    else:
        # Generate new report
        report_data = reporting_service.generate_daily_report(current_customer.id)
    
    # Send email notification if requested
    if send_email:
        reporting_service.send_report_notification(
            current_customer.id,
            "daily",
            report_data
        )
    
    return report_data

@router.get("/weekly")
async def get_weekly_report(
    week_start: Optional[date] = Query(None, description="Start date of the week (defaults to current week)"),
    send_email: bool = Query(False, description="Whether to send email notification"),
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """Get weekly report for the current customer."""
    reporting_service = ReportingService(db)
    
    if week_start is None:
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
    
    # Check if report exists
    existing_report = reporting_service.get_report(
        current_customer.id,
        "weekly",
        week_start
    )
    
    if existing_report:
        report_data = existing_report
    else:
        # Generate new report
        report_data = reporting_service.generate_weekly_report(current_customer.id)
    
    # Send email notification if requested
    if send_email:
        reporting_service.send_report_notification(
            current_customer.id,
            "weekly",
            report_data
        )
    
    return report_data

@router.get("/monthly")
async def get_monthly_report(
    month_start: Optional[date] = Query(None, description="Start date of the month (defaults to current month)"),
    send_email: bool = Query(False, description="Whether to send email notification"),
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """Get monthly report for the current customer."""
    reporting_service = ReportingService(db)
    
    if month_start is None:
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
    
    # Check if report exists
    existing_report = reporting_service.get_report(
        current_customer.id,
        "monthly",
        month_start
    )
    
    if existing_report:
        report_data = existing_report
    else:
        # Generate new report
        report_data = reporting_service.generate_monthly_report(current_customer.id)
    
    # Send email notification if requested
    if send_email:
        reporting_service.send_report_notification(
            current_customer.id,
            "monthly",
            report_data
        )
    
    return report_data

@router.get("/quarterly")
async def get_quarterly_report(
    quarter_start: Optional[date] = Query(None, description="Start date of the quarter (defaults to current quarter)"),
    send_email: bool = Query(False, description="Whether to send email notification"),
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """Get quarterly report for the current customer."""
    reporting_service = ReportingService(db)
    
    if quarter_start is None:
        today = datetime.utcnow().date()
        quarter_start = today.replace(month=((today.month-1)//3)*3+1, day=1)
    
    # Check if report exists
    existing_report = reporting_service.get_report(
        current_customer.id,
        "quarterly",
        quarter_start
    )
    
    if existing_report:
        report_data = existing_report
    else:
        # Generate new report
        report_data = reporting_service.generate_quarterly_report(current_customer.id)
    
    # Send email notification if requested
    if send_email:
        reporting_service.send_report_notification(
            current_customer.id,
            "quarterly",
            report_data
        )
    
    return report_data

@router.get("/visualizations/{visualization_type}")
async def get_visualization(
    visualization_type: str,
    report_date: date = Query(..., description="Date of the report"),
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """Get a specific visualization from a report."""
    reporting_service = ReportingService(db)
    
    # Map visualization types to filenames
    visualization_map = {
        "lead_scores": f"lead_scores_{current_customer.id}_{report_date.isoformat()}.html",
        "interactions": f"interactions_{current_customer.id}_{report_date.isoformat()}.html",
        "properties": f"properties_{current_customer.id}_{report_date.isoformat()}.html",
        "conversion_funnel": f"conversion_funnel_{current_customer.id}_{report_date.isoformat()}.html",
        "lead_quality": f"lead_quality_{current_customer.id}_{report_date.isoformat()}.html",
        "price_trend": f"price_trend_{current_customer.id}_{report_date.isoformat()}.html",
        "channel_effectiveness": f"channel_effectiveness_{current_customer.id}_{report_date.isoformat()}.html"
    }
    
    if visualization_type not in visualization_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid visualization type. Must be one of: {', '.join(visualization_map.keys())}"
        )
    
    filename = visualization_map[visualization_type]
    filepath = reporting_service.reports_dir / filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Visualization not found for date {report_date.isoformat()}"
        )
    
    with open(filepath, 'r') as f:
        return {"html_content": f.read()} 