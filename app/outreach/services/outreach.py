from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Lead, OutreachLog, OutreachChannel, OutreachStatus, Customer
from app.shared.core.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import openai
from datetime import datetime
import asyncio
import logging
from app.outreach.schemas.outreach import LeadUpload
from app.services.ai import AIService
from app.services.email import EmailService
from app.services.sms import SMSService
from app.core.audit import AuditLogger
from app.outreach.models.outreach import *
import uuid

logger = logging.getLogger(__name__)

class OutreachService:
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.customer = customer
        self.twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.openai = openai
        self.openai.api_key = settings.OPENAI_API_KEY
        self.ai_service = AIService()
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.audit_logger = AuditLogger(db, customer)

    async def trigger_outreach(self, lead: Lead) -> None:
        """
        Trigger outreach to a lead through configured channels.
        """
        try:
            # Generate personalized message
            message = await self._generate_message(lead)

            # Send through configured channels
            if lead.email:
                await self._send_email(lead, message)
            
            if lead.phone:
                await self._send_sms(lead, message)

            # Log outreach
            await self._log_outreach(lead, message)

            # Audit log
            await self.audit_logger.log(
                action="outreach_triggered",
                resource_type="lead",
                resource_id=lead.id,
                details={
                    "channels": ["email" if lead.email else "sms"],
                    "message_length": len(message)
                }
            )

        except Exception as e:
            logger.error(f"Error triggering outreach for lead {lead.id}: {str(e)}")
            await self.audit_logger.log(
                action="outreach_failed",
                resource_type="lead",
                resource_id=lead.id,
                details={"error": str(e)}
            )
            raise

    async def _generate_message(self, lead: Lead) -> str:
        """
        Generate personalized message using GPT.
        """
        try:
            message = await self.ai_service.generate_outreach_message(
                lead_name=lead.name,
                lead_source=lead.source,
                channel=OutreachChannel.EMAIL if lead.email else OutreachChannel.SMS,
                property_preferences=lead.property_preferences,
                budget_range=lead.budget_range,
                notes=lead.notes
            )

            await self.audit_logger.log(
                action="message_generated",
                resource_type="lead",
                resource_id=lead.id,
                details={"message_length": len(message)}
            )

            return message

        except Exception as e:
            logger.error(f"Error generating message for lead {lead.id}: {str(e)}")
            await self.audit_logger.log(
                action="message_generation_failed",
                resource_type="lead",
                resource_id=lead.id,
                details={"error": str(e)}
            )
            raise

    async def _send_email(self, lead: Lead, message: str, retry_count: int = 0) -> None:
        """
        Send email using SendGrid with retry logic.
        """
        max_retries = settings.MAX_EMAIL_RETRIES
        retry_delay = settings.EMAIL_RETRY_DELAY

        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            # Split message into subject and body
            if "Subject:" in message and "Body:" in message:
                subject = message.split("Subject:")[1].split("Body:")[0].strip()
                body = message.split("Body:")[1].strip()
            else:
                subject = "Real Estate Opportunity"
                body = message

            email = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=lead.email,
                subject=subject,
                plain_text_content=body
            )
            sg.send(email)

            await self.audit_logger.log(
                action="email_sent",
                resource_type="lead",
                resource_id=lead.id,
                details={"retry_count": retry_count}
            )

        except Exception as e:
            logger.error(f"Error sending email to lead {lead.id}: {str(e)}")
            
            if retry_count < max_retries:
                await asyncio.sleep(retry_delay)
                await self._send_email(lead, message, retry_count + 1)
            else:
                await self.audit_logger.log(
                    action="email_failed",
                    resource_type="lead",
                    resource_id=lead.id,
                    details={
                        "error": str(e),
                        "retry_count": retry_count
                    }
                )
                raise

    async def _send_sms(self, lead: Lead, message: str, retry_count: int = 0) -> None:
        """
        Send SMS using Twilio with retry logic.
        """
        max_retries = settings.MAX_SMS_RETRIES
        retry_delay = settings.SMS_RETRY_DELAY

        try:
            self.twilio.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=lead.phone
            )

            await self.audit_logger.log(
                action="sms_sent",
                resource_type="lead",
                resource_id=lead.id,
                details={"retry_count": retry_count}
            )

        except Exception as e:
            logger.error(f"Error sending SMS to lead {lead.id}: {str(e)}")
            
            if retry_count < max_retries:
                await asyncio.sleep(retry_delay)
                await self._send_sms(lead, message, retry_count + 1)
            else:
                await self.audit_logger.log(
                    action="sms_failed",
                    resource_type="lead",
                    resource_id=lead.id,
                    details={
                        "error": str(e),
                        "retry_count": retry_count
                    }
                )
                raise

    async def _log_outreach(self, lead: Lead, message: str) -> None:
        """
        Log outreach attempt.
        """
        log = OutreachLog(
            lead_id=lead.id,
            customer_id=self.customer.id,
            channel="email" if lead.email else "sms",
            message=message,
            status="sent",
            retry_count=0
        )
        self.db.add(log)
        self.db.commit()

    async def send_outreach(
        self,
        channel: OutreachChannel,
        leads: List[LeadUpload],
        retry_config: Optional[Dict] = None
    ) -> List[OutreachLog]:
        """
        Send outreach messages to leads via the specified channel.
        """
        outreach_logs = []
        
        for lead in leads:
            try:
                # Generate AI message
                message = await self.ai_service.generate_outreach_message(
                    lead_name=lead.name,
                    lead_source=lead.source,
                    channel=channel,
                    property_preferences=lead.property_preferences,
                    budget_range=lead.budget_range,
                    notes=lead.notes
                )
                
                # Create outreach log
                outreach_log = OutreachLog(
                    customer_id=self.customer.id,
                    lead_id=lead.id,
                    channel=channel,
                    status=OutreachStatus.PENDING,
                    message=message,
                    retry_count=0
                )
                self.db.add(outreach_log)
                self.db.flush()
                
                # Send message based on channel
                if channel == OutreachChannel.EMAIL:
                    # Split message into subject and body
                    if "Subject:" in message and "Body:" in message:
                        subject = message.split("Subject:")[1].split("Body:")[0].strip()
                        body = message.split("Body:")[1].strip()
                    else:
                        subject = "Real Estate Opportunity"
                        body = message

                    await self.email_service.send_email(
                        to_email=lead.email,
                        subject=subject,
                        message=body
                    )
                else:  # SMS
                    await self.sms_service.send_sms(
                        to_phone=lead.phone,
                        message=message
                    )
                
                # Update log status
                outreach_log.status = OutreachStatus.SENT
                outreach_log.sent_at = datetime.utcnow()
                
                await self.audit_logger.log(
                    action="outreach_sent",
                    resource_type="lead",
                    resource_id=lead.id,
                    details={
                        "channel": channel.value,
                        "message_length": len(message)
                    }
                )
            
            except Exception as e:
                logger.error(f"Error sending outreach to lead {lead.id}: {str(e)}")
                outreach_log.status = OutreachStatus.FAILED
                outreach_log.error_message = str(e)
                
                # Apply retry logic if configured
                if retry_config and retry_config.get('max_retries', 0) > outreach_log.retry_count:
                    outreach_log.retry_count += 1
                    outreach_log.last_retry_at = datetime.utcnow()
                    outreach_log.status = OutreachStatus.PENDING
                
                await self.audit_logger.log(
                    action="outreach_failed",
                    resource_type="lead",
                    resource_id=lead.id,
                    details={
                        "error": str(e),
                        "retry_count": outreach_log.retry_count
                    }
                )
            
            outreach_logs.append(outreach_log)
        
        self.db.commit()
        return outreach_logs

    def get_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[OutreachLog]:
        """
        Get outreach logs for the current customer with filtering.
        """
        query = (
            self.db.query(OutreachLog)
            .filter(OutreachLog.customer_id == self.customer.id)
        )

        if filters:
            if filters.get('channel'):
                query = query.filter(OutreachLog.channel == filters['channel'])
            if filters.get('status'):
                query = query.filter(OutreachLog.status == filters['status'])
            if filters.get('start_date'):
                query = query.filter(OutreachLog.created_at >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(OutreachLog.created_at <= filters['end_date'])
            if filters.get('lead_id'):
                query = query.filter(OutreachLog.lead_id == filters['lead_id'])
            if filters.get('has_error'):
                query = query.filter(OutreachLog.error_message.isnot(None))
            if filters.get('retry_count'):
                query = query.filter(OutreachLog.retry_count >= filters['retry_count'])

        return (
            query.order_by(OutreachLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def create_outreach(
        self,
        lead_id: str,
        channel: OutreachChannel,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OutreachLog:
        """
        Create a new outreach record.
        """
        outreach = OutreachLog(
            lead_id=lead_id,
            channel=channel,
            message=message,
            status=OutreachStatus.PENDING,
            customer_id=self.customer.id,
            outreach_metadata=metadata or {}
        )
        
        self.db.add(outreach)
        self.db.commit()
        self.db.refresh(outreach)
        
        await self.audit_logger.log_action(
            action="create",
            entity_type="outreach",
            entity_id=outreach.id,
            details={
                "lead_id": lead_id,
                "channel": channel,
                "status": OutreachStatus.PENDING
            }
        )
        
        return outreach

    async def get_outreach_logs(
        self,
        lead_id: Optional[str] = None,
        channel: Optional[OutreachChannel] = None,
        status: Optional[OutreachStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OutreachLog]:
        """
        Get outreach logs for the current customer with filtering.
        """
        query = self.db.query(OutreachLog).filter(
            OutreachLog.customer_id == self.customer.id
        )

        if lead_id:
            query = query.filter(OutreachLog.lead_id == lead_id)
        if channel:
            query = query.filter(OutreachLog.channel == channel)
        if status:
            query = query.filter(OutreachLog.status == status)
        if start_date:
            query = query.filter(OutreachLog.created_at >= start_date)
        if end_date:
            query = query.filter(OutreachLog.created_at <= end_date)

        return query.order_by(OutreachLog.created_at.desc()).all() 