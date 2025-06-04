from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.shared.db.session import SessionLocal
from app.shared.models.customer import Customer
from app.shared.core.reporting import ReportingService
import logging

logger = logging.getLogger(__name__)

def generate_daily_reports():
    """Generate daily reports for all customers."""
    db = SessionLocal()
    try:
        reporting_service = ReportingService(db)
        customers = db.query(Customer).all()
        
        for customer in customers:
            try:
                report = reporting_service.generate_daily_report(customer.id)
                # Send email notification
                reporting_service.send_report_notification(
                    customer.id,
                    "daily",
                    report
                )
                logger.info(f"Generated daily report for customer {customer.id} on {datetime.utcnow().date()}")
            except Exception as e:
                logger.error(f"Error generating daily report for customer {customer.id}: {str(e)}")
    finally:
        db.close()

def generate_weekly_reports():
    """Generate weekly reports for all customers."""
    db = SessionLocal()
    try:
        reporting_service = ReportingService(db)
        customers = db.query(Customer).all()
        
        for customer in customers:
            try:
                report = reporting_service.generate_weekly_report(customer.id)
                # Send email notification
                reporting_service.send_report_notification(
                    customer.id,
                    "weekly",
                    report
                )
                logger.info(f"Generated weekly report for customer {customer.id} for week starting {datetime.utcnow().date()}")
            except Exception as e:
                logger.error(f"Error generating weekly report for customer {customer.id}: {str(e)}")
    finally:
        db.close()

def generate_monthly_reports():
    """Generate monthly reports for all customers."""
    db = SessionLocal()
    try:
        reporting_service = ReportingService(db)
        customers = db.query(Customer).all()
        
        for customer in customers:
            try:
                report = reporting_service.generate_monthly_report(customer.id)
                # Send email notification
                reporting_service.send_report_notification(
                    customer.id,
                    "monthly",
                    report
                )
                logger.info(f"Generated monthly report for customer {customer.id} for month starting {datetime.utcnow().date()}")
            except Exception as e:
                logger.error(f"Error generating monthly report for customer {customer.id}: {str(e)}")
    finally:
        db.close()

def generate_quarterly_reports():
    """Generate quarterly reports for all customers."""
    db = SessionLocal()
    try:
        reporting_service = ReportingService(db)
        customers = db.query(Customer).all()
        
        for customer in customers:
            try:
                report = reporting_service.generate_quarterly_report(customer.id)
                # Send email notification
                reporting_service.send_report_notification(
                    customer.id,
                    "quarterly",
                    report
                )
                logger.info(f"Generated quarterly report for customer {customer.id} for quarter starting {datetime.utcnow().date()}")
            except Exception as e:
                logger.error(f"Error generating quarterly report for customer {customer.id}: {str(e)}")
    finally:
        db.close()

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