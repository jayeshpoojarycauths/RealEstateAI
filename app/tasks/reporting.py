from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.shared.db.session import SessionLocal
from app.shared.models.customer import Customer
from app.shared.core.reporting import ReportingService
from app.shared.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def generate_reports(
    db: Session,
    report_type: str,
    start_date: datetime,
    end_date: datetime
) -> None:
    """
    Generate reports for all customers based on the specified type and date range.
    
    Args:
        db: Database session
        report_type: Type of report ('daily', 'weekly', 'monthly', 'quarterly')
        start_date: Start date for the report period
        end_date: End date for the report period
    """
    try:
        # Get all customers
        customers = db.query(Customer).all()
        if not customers:
            logger.warning("No customers found for report generation")
            return

        # Initialize reporting service
        reporting_service = ReportingService(db)
        
        # Generate reports for each customer
        for customer in customers:
            try:
                if report_type == 'daily':
                    await reporting_service.generate_daily_report(customer.id, start_date)
                elif report_type == 'weekly':
                    await reporting_service.generate_weekly_report(customer.id, start_date)
                elif report_type == 'monthly':
                    await reporting_service.generate_monthly_report(customer.id, start_date)
                elif report_type == 'quarterly':
                    await reporting_service.generate_quarterly_report(customer.id, start_date)
                else:
                    raise ValueError(f"Invalid report type: {report_type}")
                
                logger.info(f"Generated {report_type} report for customer {customer.id}")
            except Exception as e:
                logger.error(f"Error generating {report_type} report for customer {customer.id}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error in generate_reports: {str(e)}")
        raise

async def generate_daily_reports(db: Session) -> None:
    """Generate daily reports for all customers."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)
    await generate_reports(db, 'daily', start_date, end_date)

async def generate_weekly_reports(db: Session) -> None:
    """Generate weekly reports for all customers."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(weeks=1)
    await generate_reports(db, 'weekly', start_date, end_date)

async def generate_monthly_reports(db: Session) -> None:
    """Generate monthly reports for all customers."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    await generate_reports(db, 'monthly', start_date, end_date)

async def generate_quarterly_reports(db: Session) -> None:
    """Generate quarterly reports for all customers."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)
    await generate_reports(db, 'quarterly', start_date, end_date)

def cleanup_old_reports():
    """Clean up reports older than 30 days."""
    db = SessionLocal()
    try:
        reporting_service = ReportingService(db)
        cutoff_date = datetime.utcnow().date() - timedelta(days=30)
        
        for report_file in reporting_service.reports_dir.glob("*"):
            try:
                # Extract date from filename
                date_str = report_file.stem.split("_")[-1]
                report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                if report_date < cutoff_date:
                    report_file.unlink()
                    logger.info(f"Deleted old report: {report_file}")
            except Exception as e:
                logger.error(f"Error cleaning up report {report_file}: {str(e)}")
    finally:
        db.close() 