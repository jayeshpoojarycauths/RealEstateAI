from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.shared.models.customer import Customer
from app.shared.core.communication.email import send_email
import logging

logger = logging.getLogger(__name__)

class ReportingService:
    """Service for generating and managing reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_daily_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate daily report for a customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Get date range
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        # Generate report data
        report_data = {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "report_date": today.isoformat(),
            "report_type": "daily",
            "metrics": self._get_daily_metrics(customer_id, yesterday, today)
        }

        # Save report
        filename = f"daily_report_{customer_id}_{today.isoformat()}.json"
        self._save_report(filename, report_data)

        return report_data

    def generate_weekly_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate weekly report for a customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Get date range
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())

        # Generate report data
        report_data = {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "report_date": today.isoformat(),
            "report_type": "weekly",
            "week_start": week_start.isoformat(),
            "metrics": self._get_weekly_metrics(customer_id, week_start, today)
        }

        # Save report
        filename = f"weekly_report_{customer_id}_{today.isoformat()}.json"
        self._save_report(filename, report_data)

        return report_data

    def generate_monthly_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate monthly report for a customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Get date range
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        # Generate report data
        report_data = {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "report_date": today.isoformat(),
            "report_type": "monthly",
            "month_start": month_start.isoformat(),
            "metrics": self._get_monthly_metrics(customer_id, month_start, today)
        }

        # Save report
        filename = f"monthly_report_{customer_id}_{today.isoformat()}.json"
        self._save_report(filename, report_data)

        return report_data

    def generate_quarterly_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate quarterly report for a customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Get date range
        today = datetime.utcnow().date()
        quarter_start = today.replace(month=((today.month-1)//3)*3+1, day=1)

        # Generate report data
        report_data = {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "report_date": today.isoformat(),
            "report_type": "quarterly",
            "quarter_start": quarter_start.isoformat(),
            "metrics": self._get_quarterly_metrics(customer_id, quarter_start, today)
        }

        # Save report
        filename = f"quarterly_report_{customer_id}_{today.isoformat()}.json"
        self._save_report(filename, report_data)

        return report_data

    def send_report_notification(self, customer_id: str, report_type: str, report_data: Dict[str, Any]) -> None:
        """Send email notification with report."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        subject = f"Your {report_type.capitalize()} Report - {datetime.utcnow().date()}"
        template = self._get_report_template(report_type)
        
        # Send email
        send_email(
            to_email=customer.email,
            subject=subject,
            template=template,
            data=report_data
        )

    def _get_daily_metrics(self, customer_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get daily metrics for reporting."""
        # Implement your daily metrics collection logic here
        return {
            "total_leads": 0,
            "new_leads": 0,
            "conversions": 0,
            "revenue": 0
        }

    def _get_weekly_metrics(self, customer_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get weekly metrics for reporting."""
        # Implement your weekly metrics collection logic here
        return {
            "total_leads": 0,
            "new_leads": 0,
            "conversions": 0,
            "revenue": 0,
            "daily_breakdown": {}
        }

    def _get_monthly_metrics(self, customer_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get monthly metrics for reporting."""
        # Implement your monthly metrics collection logic here
        return {
            "total_leads": 0,
            "new_leads": 0,
            "conversions": 0,
            "revenue": 0,
            "weekly_breakdown": {}
        }

    def _get_quarterly_metrics(self, customer_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get quarterly metrics for reporting."""
        # Implement your quarterly metrics collection logic here
        return {
            "total_leads": 0,
            "new_leads": 0,
            "conversions": 0,
            "revenue": 0,
            "monthly_breakdown": {}
        }

    def _get_report_template(self, report_type: str) -> str:
        """Get email template for report type."""
        templates = {
            "daily": "daily_report_template.html",
            "weekly": "weekly_report_template.html",
            "monthly": "monthly_report_template.html",
            "quarterly": "quarterly_report_template.html"
        }
        return templates.get(report_type, "default_report_template.html")

    def _save_report(self, filename: str, report_data: Dict[str, Any]) -> None:
        """Save report to file."""
        import json
        filepath = self.reports_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2) 