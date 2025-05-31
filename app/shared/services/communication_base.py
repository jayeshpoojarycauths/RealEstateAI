from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
from app.shared.core.config import settings

logger = logging.getLogger(__name__)

class CommunicationBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email using SendGrid."""
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            mail = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=message or ""
            )
            
            response = sg.send(mail)
            return {"status": "success", "message_id": response.headers['X-Message-Id']}
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise

    async def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Dict[str, Any]:
        """Send SMS using Twilio."""
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )
            
            return {"status": "success", "message_sid": message.sid}
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise 