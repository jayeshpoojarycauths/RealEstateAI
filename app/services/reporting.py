from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.models import Lead, LeadScore, InteractionLog, CallInteraction, MessageInteraction, RealEstateProject, Project, Customer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path
from app.core.email import send_email
from app.services.email import EmailService

class ReportingService:
    def __init__(self, db: Session):
        self.db = db
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.email_service = EmailService()

    def generate_daily_report(self, customer_id: int) -> Dict[str, Any]:
        """Generate a daily report for a customer."""
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        # Get lead statistics
        new_leads = self.db.query(Lead).filter(
            Lead.customer_id == customer_id,
            func.date(Lead.created_at) == yesterday
        ).count()

        active_leads = self.db.query(Lead).filter(
            Lead.customer_id == customer_id,
            Lead.status == 'active'
        ).count()

        # Get interaction statistics
        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.customer_id == customer_id,
            func.date(InteractionLog.created_at) == yesterday
        ).count()

        # Get project statistics
        active_projects = self.db.query(Project).filter(
            Project.customer_id == customer_id,
            Project.status == 'active'
        ).count()

        return {
            "date": yesterday,
            "new_leads": new_leads,
            "active_leads": active_leads,
            "interactions": interactions,
            "active_projects": active_projects,
            "generated_at": datetime.utcnow()
        }

    def _calculate_avg_property_price(self, customer_id: str) -> float:
        """Calculate average property price."""
        properties = self.db.query(RealEstateProject).filter(
            RealEstateProject.customer_id == customer_id
        ).all()
        
        prices = [float(p.price.replace('₹', '').replace(',', '')) for p in properties if p.price]
        return sum(prices) / len(prices) if prices else 0

    def _calculate_property_price_range(self, customer_id: str) -> Dict[str, float]:
        """Calculate property price range."""
        properties = self.db.query(RealEstateProject).filter(
            RealEstateProject.customer_id == customer_id
        ).all()
        
        prices = [float(p.price.replace('₹', '').replace(',', '')) for p in properties if p.price]
        return {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "median": sorted(prices)[len(prices)//2] if prices else 0
        }

    def _get_property_type_distribution(self, customer_id: str) -> Dict[str, int]:
        """Get distribution of property types."""
        properties = self.db.query(RealEstateProject).filter(
            RealEstateProject.customer_id == customer_id
        ).all()
        
        distribution = {}
        for prop in properties:
            distribution[prop.type] = distribution.get(prop.type, 0) + 1
        return distribution

    def _calculate_avg_interaction_duration(self, interactions: List[InteractionLog]) -> float:
        """Calculate average interaction duration."""
        durations = [i.duration for i in interactions if i.duration]
        return sum(durations) / len(durations) if durations else 0

    def _calculate_avg_response_time(self, customer_id: str) -> float:
        """Calculate average response time for messages."""
        message_interactions = self.db.query(MessageInteraction).join(
            InteractionLog
        ).filter(
            InteractionLog.customer_id == customer_id
        ).all()
        
        response_times = [i.response_time for i in message_interactions if i.response_time]
        return sum(response_times) / len(response_times) if response_times else 0

    def _calculate_channel_effectiveness(self, interactions: List[InteractionLog]) -> Dict[str, float]:
        """Calculate effectiveness of different communication channels."""
        channel_stats = {}
        for interaction in interactions:
            if interaction.interaction_type not in channel_stats:
                channel_stats[interaction.interaction_type] = {"total": 0, "successful": 0}
            
            channel_stats[interaction.interaction_type]["total"] += 1
            if interaction.status == "success":
                channel_stats[interaction.interaction_type]["successful"] += 1
        
        return {
            channel: (stats["successful"] / stats["total"] * 100)
            for channel, stats in channel_stats.items()
            if stats["total"] > 0
        }

    def _generate_conversion_funnel(self, customer_id: str, date: datetime.date):
        """Generate conversion funnel visualization."""
        leads = self.db.query(Lead).filter(
            Lead.customer_id == customer_id,
            func.date(Lead.created_at) == date
        ).all()
        
        funnel_data = {
            "New Leads": len(leads),
            "Interacted": sum(1 for lead in leads if lead.interactions),
            "Qualified": sum(1 for lead in leads if any(i.status == "success" for i in lead.interactions)),
            "Converted": sum(1 for lead in leads if lead.status == "converted")
        }
        
        fig = go.Figure(go.Funnel(
            y=list(funnel_data.keys()),
            x=list(funnel_data.values())
        ))
        
        filename = f"conversion_funnel_{customer_id}_{date.isoformat()}.html"
        fig.write_html(self.reports_dir / filename)

    def _generate_lead_quality_distribution(self, lead_scores: List[LeadScore], customer_id: str, date: datetime.date):
        """Generate lead quality distribution visualization."""
        quality_data = {
            "High Value": sum(1 for score in lead_scores if score.score >= 70),
            "Medium Value": sum(1 for score in lead_scores if 40 <= score.score < 70),
            "Low Value": sum(1 for score in lead_scores if score.score < 40)
        }
        
        fig = px.pie(
            values=list(quality_data.values()),
            names=list(quality_data.keys()),
            title="Lead Quality Distribution"
        )
        
        filename = f"lead_quality_{customer_id}_{date.isoformat()}.html"
        fig.write_html(self.reports_dir / filename)

    def _generate_property_price_trend(self, customer_id: str, date: datetime.date):
        """Generate property price trend visualization."""
        properties = self.db.query(RealEstateProject).filter(
            RealEstateProject.customer_id == customer_id
        ).order_by(RealEstateProject.created_at).all()
        
        df = pd.DataFrame([
            {
                "date": p.created_at.date(),
                "price": float(p.price.replace('₹', '').replace(',', '')) if p.price else 0,
                "type": p.type
            }
            for p in properties
        ])
        
        if not df.empty:
            fig = px.line(
                df,
                x="date",
                y="price",
                color="type",
                title="Property Price Trend"
            )
            
            filename = f"price_trend_{customer_id}_{date.isoformat()}.html"
            fig.write_html(self.reports_dir / filename)

    def _generate_channel_effectiveness(self, interactions: List[InteractionLog], customer_id: str, date: datetime.date):
        """Generate channel effectiveness visualization."""
        channel_stats = self._calculate_channel_effectiveness(interactions)
        
        fig = px.bar(
            x=list(channel_stats.keys()),
            y=list(channel_stats.values()),
            title="Channel Effectiveness",
            labels={"x": "Channel", "y": "Success Rate (%)"}
        )
        
        filename = f"channel_effectiveness_{customer_id}_{date.isoformat()}.html"
        fig.write_html(self.reports_dir / filename)

    def generate_weekly_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate weekly report for a customer."""
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Aggregate daily reports
        daily_reports = []
        current_date = week_start
        while current_date <= week_end:
            daily_report = self.generate_daily_report(customer_id)
            daily_reports.append(daily_report)
            current_date += timedelta(days=1)

        # Calculate weekly metrics
        weekly_metrics = {
            "period": {
                "start": week_start.isoformat(),
                "end": week_end.isoformat()
            },
            "leads": {
                "new": sum(r["new_leads"] for r in daily_reports),
                "total": daily_reports[-1]["active_leads"],
                "high_value": sum(1 for r in daily_reports if r["active_leads"] > 0),
                "average_score": sum(r["active_leads"] / r["interactions"] * 100 if r["interactions"] > 0 else 0 for r in daily_reports) / len(daily_reports)
            },
            "interactions": {
                "total": sum(r["interactions"] for r in daily_reports),
                "success_rate": sum(r["interactions"] / r["active_leads"] * 100 if r["active_leads"] > 0 else 0 for r in daily_reports) / len(daily_reports)
            },
            "properties": {
                "new": sum(r["active_projects"] for r in daily_reports),
                "total": daily_reports[-1]["active_projects"]
            }
        }

        # Save weekly report
        filename = f"weekly_report_{customer_id}_{week_start.isoformat()}.json"
        with open(self.reports_dir / filename, 'w') as f:
            json.dump(weekly_metrics, f, indent=2)

        return weekly_metrics

    def get_report(
        self,
        customer_id: int,
        report_type: str,
        report_date: date
    ) -> Optional[Dict[str, Any]]:
        """Get an existing report if it exists."""
        # Implementation would check a reports table
        return None

    def generate_monthly_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate monthly report for a customer."""
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Aggregate daily reports
        daily_reports = []
        current_date = month_start
        while current_date <= month_end:
            daily_report = self.generate_daily_report(customer_id)
            daily_reports.append(daily_report)
            current_date += timedelta(days=1)

        # Calculate monthly metrics
        monthly_metrics = {
            "period": {
                "start": month_start.isoformat(),
                "end": month_end.isoformat()
            },
            "leads": {
                "new": sum(r["new_leads"] for r in daily_reports),
                "total": daily_reports[-1]["active_leads"],
                "high_value": sum(1 for r in daily_reports if r["active_leads"] > 0),
                "average_score": sum(r["active_leads"] / r["interactions"] * 100 if r["interactions"] > 0 else 0 for r in daily_reports) / len(daily_reports),
                "quality_distribution": daily_reports[-1]["active_leads"] / daily_reports[-1]["interactions"] * 100 if daily_reports[-1]["interactions"] > 0 else 0
            },
            "interactions": {
                "total": sum(r["interactions"] for r in daily_reports),
                "success_rate": sum(r["interactions"] / r["active_leads"] * 100 if r["active_leads"] > 0 else 0 for r in daily_reports) / len(daily_reports),
                "quality_metrics": daily_reports[-1]["interactions"] / daily_reports[-1]["active_leads"] * 100 if daily_reports[-1]["active_leads"] > 0 else 0
            },
            "properties": {
                "new": sum(r["active_projects"] for r in daily_reports),
                "total": daily_reports[-1]["active_projects"]
            }
        }

        # Save monthly report
        filename = f"monthly_report_{customer_id}_{month_start.isoformat()}.json"
        with open(self.reports_dir / filename, 'w') as f:
            json.dump(monthly_metrics, f, indent=2)

        return monthly_metrics

    def generate_quarterly_report(self, customer_id: str) -> Dict[str, Any]:
        """Generate quarterly report for a customer."""
        today = datetime.utcnow().date()
        quarter_start = today.replace(month=((today.month-1)//3)*3+1, day=1)
        quarter_end = (quarter_start + timedelta(days=93)).replace(day=1) - timedelta(days=1)

        # Aggregate monthly reports
        monthly_reports = []
        current_date = quarter_start
        while current_date <= quarter_end:
            monthly_report = self.generate_monthly_report(customer_id)
            monthly_reports.append(monthly_report)
            current_date = (current_date + timedelta(days=32)).replace(day=1)

        # Calculate quarterly metrics
        quarterly_metrics = {
            "period": {
                "start": quarter_start.isoformat(),
                "end": quarter_end.isoformat()
            },
            "leads": {
                "new": sum(r["leads"]["new"] for r in monthly_reports),
                "total": monthly_reports[-1]["leads"]["total"],
                "high_value": monthly_reports[-1]["leads"]["high_value"],
                "average_score": sum(r["leads"]["average_score"] for r in monthly_reports) / len(monthly_reports),
                "quality_distribution": monthly_reports[-1]["leads"]["quality_distribution"]
            },
            "interactions": {
                "total": sum(r["interactions"]["total"] for r in monthly_reports),
                "success_rate": sum(r["interactions"]["success_rate"] for r in monthly_reports) / len(monthly_reports),
                "quality_metrics": monthly_reports[-1]["interactions"]["quality_metrics"]
            },
            "properties": {
                "new": sum(r["properties"]["new"] for r in monthly_reports),
                "total": monthly_reports[-1]["properties"]["total"],
                "metrics": monthly_reports[-1]["properties"]["metrics"]
            }
        }

        # Save quarterly report
        filename = f"quarterly_report_{customer_id}_{quarter_start.isoformat()}.json"
        with open(self.reports_dir / filename, 'w') as f:
            json.dump(quarterly_metrics, f, indent=2)

        return quarterly_metrics

    async def send_report_notification(
        self,
        customer_id: int,
        report_type: str,
        report_data: Dict[str, Any]
    ) -> None:
        """Send report notification via email."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer or not customer.email:
            return

        subject = f"Daily Report - {report_data['date']}"
        message = f"""
        Daily Report Summary:
        - New Leads: {report_data['new_leads']}
        - Active Leads: {report_data['active_leads']}
        - Interactions: {report_data['interactions']}
        - Active Projects: {report_data['active_projects']}
        """

        await self.email_service.send_email(
            to_email=customer.email,
            subject=subject,
            message=message
        ) 