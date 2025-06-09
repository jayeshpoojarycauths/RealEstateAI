import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.lead.models.lead import Lead
from app.lead.schemas.lead import LeadUpdate
from app.shared.core.communication import OutreachEngine
from app.shared.models.customer import Customer
from app.shared.models.user import User
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from app.shared.core.logging import logger
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from app.shared.core.logging import logger

logger = logging.getLogger(__name__)

class LeadNotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.communication_service = OutreachEngine(db)

    async def notify_new_lead(self, lead: Lead, customer_id: int) -> None:
        """Send notifications for a new lead"""
        try:
            # Get customer's notification preferences
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                logger.error(f"Customer {customer_id} not found")
                return

            # Get assigned agent if any
            agent = None
            if lead.assigned_to:
                agent = self.db.query(User).filter(User.id == lead.assigned_to).first()

            # Prepare notification data
            notification_data = {
                "lead_id": lead.id,
                "lead_name": lead.name,
                "lead_email": lead.email,
                "lead_phone": lead.phone,
                "customer_id": customer_id,
                "customer_name": customer.name,
                "agent_name": agent.name if agent else "Unassigned",
                "created_at": datetime.utcnow().isoformat()
            }

            # Send notifications based on preferences
            if customer.notification_preferences.get("email", True):
                await self.communication_service.send_email(
                    to_email=customer.email,
                    subject=f"New Lead: {lead.name}",
                    template_name="new_lead_notification",
                    template_data=notification_data
                )

            if customer.notification_preferences.get("sms", False):
                await self.communication_service.send_sms(
                    to_phone=customer.phone,
                    message=f"New lead received: {lead.name}. Check your dashboard for details."
                )

            # Log the notification
            logger.info(f"Notifications sent for new lead {lead.id}")

        except Exception as e:
            logger.error(f"Error sending lead notifications: {str(e)}")
            raise

    async def notify_lead_update(self, lead: Lead, update_data: LeadUpdate, customer_id: int) -> None:
        """Send notifications for lead updates"""
        try:
            # Get customer's notification preferences
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                logger.error(f"Customer {customer_id} not found")
                return

            # Get assigned agent if any
            agent = None
            if lead.assigned_to:
                agent = self.db.query(User).filter(User.id == lead.assigned_to).first()

            # Prepare notification data
            notification_data = {
                "lead_id": lead.id,
                "lead_name": lead.name,
                "lead_email": lead.email,
                "lead_phone": lead.phone,
                "customer_id": customer_id,
                "customer_name": customer.name,
                "agent_name": agent.name if agent else "Unassigned",
                "updated_at": datetime.utcnow().isoformat(),
                "changes": update_data.dict(exclude_unset=True)
            }

            # Send notifications based on preferences
            if customer.notification_preferences.get("email", True):
                await self.communication_service.send_email(
                    to_email=customer.email,
                    subject=f"Lead Update: {lead.name}",
                    template_name="lead_update_notification",
                    template_data=notification_data
                )

            if customer.notification_preferences.get("sms", False):
                await self.communication_service.send_sms(
                    to_phone=customer.phone,
                    message=f"Lead {lead.name} has been updated. Check your dashboard for details."
                )

            # Log the notification
            logger.info(f"Notifications sent for lead update {lead.id}")

        except Exception as e:
            logger.error(f"Error sending lead update notifications: {str(e)}")
            raise 