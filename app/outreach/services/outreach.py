import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import openai
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session
from twilio.rest import Client

from app.lead.models.lead import Lead
from app.outreach.models.outreach import (CommunicationPreference, Outreach,
                                          OutreachChannel,
                                          OutreachLog, OutreachStatus,
                                          OutreachTemplate)
from app.outreach.schemas.outreach import (CommunicationPreferenceCreate,
                                           CommunicationPreferenceUpdate,
                                           LeadUpload, OutreachCreate,
                                           OutreachFilter,
                                           OutreachTemplateCreate,
                                           OutreachTemplateFilter,
                                           OutreachTemplateUpdate,
                                           OutreachUpdate)
from app.shared.core.ai import AIService
from app.shared.core.audit import AuditLogger, AuditService
from app.shared.core.communication import (email_service, OutreachEngine,
                                           SMSService)
from app.shared.core.config import settings
from app.shared.core.exceptions import NotFoundException
from app.shared.core.logging import logger
from app.shared.models.customer import Customer
from app.shared.models.interaction import CallInteraction

logger = logging.getLogger(__name__)

class OutreachService:
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.customer = customer
        self.twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.openai = openai
        self.openai.api_key = settings.OPENAI_API_KEY
        self.ai_service = AIService()
        self.email_service = email_service
        self.sms_service = SMSService()
        self.communication_service = OutreachEngine(db)
        self.audit_logger = AuditLogger(db, customer)
        self.audit = AuditService(db)

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
                # Check communication preferences
                if lead.communication_preference == "call":
                    await self._make_call(lead, message)
                else:
                    await self._send_sms(lead, message)

            # Log outreach
            await self._log_outreach(lead, message)

            # Audit log
            await self.audit_logger.log(
                action="outreach_triggered",
                resource_type="lead",
                resource_id=lead.id,
                details={
                    "channels": ["email" if lead.email else "call" if lead.communication_preference == "call" else "sms"],
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
        Send email using EmailService with retry logic.
        """
        max_retries = settings.MAX_EMAIL_RETRIES
        retry_delay = settings.EMAIL_RETRY_DELAY

        try:
            # Split message into subject and body
            if "Subject:" in message and "Body:" in message:
                subject = message.split("Subject:")[1].split("Body:")[0].strip()
                body = message.split("Body:")[1].strip()
            else:
                subject = "Real Estate Opportunity"
                body = message

            await self.email_service.send_email(
                email_to=lead.email,
                subject=subject,
                template_name="outreach_generic",  # Use a generic outreach template
                template_data={"body": body, "lead": lead}
            )

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

    async def _make_call(self, lead: Lead, message: str, retry_count: int = 0) -> None:
        """
        Make a call using Twilio with text-to-speech and retry logic.
        """
        max_retries = settings.MAX_CALL_RETRIES
        retry_delay = settings.CALL_RETRY_DELAY

        try:
            # Generate call-specific message if needed
            call_message = await self._generate_call_message(lead, message)

            # Make the call
            call_result = await self.communication_service.make_call(
                to_phone=lead.phone,
                message=call_message,
                voice_id=settings.DEFAULT_VOICE_ID,
                record=True,
                status_callback=settings.full_call_status_callback_url
            )

            # Log the call
            await self._log_call(lead, call_result)

            await self.audit_logger.log(
                action="call_made",
                resource_type="lead",
                resource_id=lead.id,
                details={"retry_count": retry_count}
            )

        except Exception as e:
            logger.error(f"Error making call to lead {lead.id}: {str(e)}")
            
            if retry_count < max_retries:
                await asyncio.sleep(retry_delay)
                await self._make_call(lead, message, retry_count + 1)
            else:
                await self.audit_logger.log(
                    action="call_failed",
                    resource_type="lead",
                    resource_id=lead.id,
                    details={
                        "error": str(e),
                        "retry_count": retry_count
                    }
                )
                raise

    async def _generate_call_message(self, lead: Lead, base_message: str) -> str:
        """
        Generate a call-specific message from the base message.
        """
        try:
            # Use AI to convert the message to a more natural speaking style
            call_message = await self.ai_service.convert_to_speech(
                text=base_message,
                style="conversational",
                tone="friendly"
            )

            return call_message

        except Exception as e:
            logger.error(f"Error generating call message for lead {lead.id}: {str(e)}")
            # Fall back to base message if AI conversion fails
            return base_message

    async def _log_call(self, lead: Lead, call_result: Dict[str, Any]) -> None:
        """
        Log call details to the database.
        """
        try:
            call_interaction = CallInteraction(
                lead_id=lead.id,
                call_sid=call_result.get("call_sid"),
                duration=call_result.get("duration"),
                status=call_result.get("status"),
                recording_url=call_result.get("recording_url"),
                transcription=call_result.get("transcription")
            )
            self.db.add(call_interaction)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error logging call for lead {lead.id}: {str(e)}")
            # Don't raise the error as this is a non-critical operation

    async def _log_outreach(self, lead: Lead, message: str) -> None:
        """
        Log outreach details to the database.
        """
        try:
            outreach_log = OutreachLog(
                lead_id=lead.id,
                channel=OutreachChannel.EMAIL if lead.email else OutreachChannel.SMS,
                message=message,
                status=OutreachStatus.SENT
            )
            self.db.add(outreach_log)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error logging outreach for lead {lead.id}: {str(e)}")
            # Don't raise the error as this is a non-critical operation

    async def send_outreach(
        self,
        channel: OutreachChannel,
        leads: List[LeadUpload],
        retry_config: Optional[Dict] = None
    ) -> List[OutreachLog]:
        """
        Send outreach to multiple leads through a specific channel.
        """
        logs = []
        for lead_data in leads:
            try:
                lead = await self._get_or_create_lead(lead_data)
                message = await self._generate_message(lead)

                if channel == OutreachChannel.EMAIL:
                    await self._send_email(lead, message)
                elif channel == OutreachChannel.SMS:
                    await self._send_sms(lead, message)
                elif channel == OutreachChannel.CALL:
                    await self._make_call(lead, message)

                log = await self._log_outreach(lead, message)
                logs.append(log)

            except Exception as e:
                logger.error(f"Error sending outreach to lead {lead_data.get('email')}: {str(e)}")
                log = await self._log_outreach_error(lead_data, str(e))
                logs.append(log)

        return logs

    def get_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[OutreachLog]:
        """
        Get outreach logs with optional filtering.
        """
        query = self.db.query(OutreachLog)

        if filters:
            if filters.get("lead_id"):
                query = query.filter(OutreachLog.lead_id == filters["lead_id"])
            if filters.get("channel"):
                query = query.filter(OutreachLog.channel == filters["channel"])
            if filters.get("status"):
                query = query.filter(OutreachLog.status == filters["status"])
            if filters.get("start_date"):
                query = query.filter(OutreachLog.created_at >= filters["start_date"])
            if filters.get("end_date"):
                query = query.filter(OutreachLog.created_at <= filters["end_date"])

        return query.order_by(OutreachLog.created_at.desc()).offset(skip).limit(limit).all()

    def create_outreach(self, outreach: OutreachCreate) -> Outreach:
        """
        Create a new outreach campaign.
        """
        db_outreach = Outreach(
            name=outreach.name,
            description=outreach.description,
            channel=outreach.channel,
            template_id=outreach.template_id,
            status=OutreachStatus.DRAFT,
            customer_id=self.customer.id
        )
        self.db.add(db_outreach)
        self.db.commit()
        self.db.refresh(db_outreach)
        return db_outreach

    def get_outreach(self, outreach_id: uuid.UUID) -> Outreach:
        """
        Get an outreach campaign by ID.
        """
        outreach = self.db.query(Outreach).filter(Outreach.id == outreach_id).first()
        if not outreach:
            raise NotFoundException(f"Outreach campaign {outreach_id} not found")
        return outreach

    def update_outreach(self, outreach_id: uuid.UUID, outreach: OutreachUpdate) -> Outreach:
        """
        Update an outreach campaign.
        """
        db_outreach = self.get_outreach(outreach_id)
        
        for field, value in outreach.dict(exclude_unset=True).items():
            setattr(db_outreach, field, value)
        
        self.db.commit()
        self.db.refresh(db_outreach)
        return db_outreach

    def list_outreach(self, filter_params: OutreachFilter) -> List[Outreach]:
        """
        List outreach campaigns with filtering.
        """
        query = self.db.query(Outreach)

        if filter_params.channel:
            query = query.filter(Outreach.channel == filter_params.channel)
        if filter_params.status:
            query = query.filter(Outreach.status == filter_params.status)
        if filter_params.template_id:
            query = query.filter(Outreach.template_id == filter_params.template_id)

        return query.order_by(Outreach.created_at.desc()).all()

    def create_template(self, template: OutreachTemplateCreate) -> OutreachTemplate:
        """
        Create a new outreach template.
        """
        db_template = OutreachTemplate(
            name=template.name,
            description=template.description,
            content=template.content,
            channel=template.channel,
            customer_id=self.customer.id
        )
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def get_template(self, template_id: uuid.UUID) -> OutreachTemplate:
        """
        Get an outreach template by ID.
        """
        template = self.db.query(OutreachTemplate).filter(OutreachTemplate.id == template_id).first()
        if not template:
            raise NotFoundException(f"Template {template_id} not found")
        return template

    def update_template(self, template_id: uuid.UUID, template: OutreachTemplateUpdate) -> OutreachTemplate:
        """
        Update an outreach template.
        """
        db_template = self.get_template(template_id)
        
        for field, value in template.dict(exclude_unset=True).items():
            setattr(db_template, field, value)
        
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def list_templates(self, filter_params: OutreachTemplateFilter) -> List[OutreachTemplate]:
        """
        List outreach templates with filtering.
        """
        query = self.db.query(OutreachTemplate)

        if filter_params.channel:
            query = query.filter(OutreachTemplate.channel == filter_params.channel)
        if filter_params.name:
            query = query.filter(OutreachTemplate.name.ilike(f"%{filter_params.name}%"))

        return query.order_by(OutreachTemplate.created_at.desc()).all()

    def create_communication_preference(self, preference: CommunicationPreferenceCreate) -> CommunicationPreference:
        """
        Create communication preferences for a customer.
        """
        db_preference = CommunicationPreference(
            customer_id=self.customer.id,
            preferred_channel=preference.preferred_channel,
            email_enabled=preference.email_enabled,
            sms_enabled=preference.sms_enabled,
            call_enabled=preference.call_enabled,
            quiet_hours_start=preference.quiet_hours_start,
            quiet_hours_end=preference.quiet_hours_end
        )
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        return db_preference

    def get_communication_preference(self, customer_id: uuid.UUID) -> CommunicationPreference:
        """
        Get communication preferences for a customer.
        """
        preference = self.db.query(CommunicationPreference).filter(
            CommunicationPreference.customer_id == customer_id
        ).first()
        if not preference:
            raise NotFoundException(f"Communication preferences for customer {customer_id} not found")
        return preference

    def update_communication_preference(
        self, customer_id: uuid.UUID, preference: CommunicationPreferenceUpdate
    ) -> CommunicationPreference:
        """
        Update communication preferences for a customer.
        """
        db_preference = self.get_communication_preference(customer_id)
        
        for field, value in preference.dict(exclude_unset=True).items():
            setattr(db_preference, field, value)
        
        self.db.commit()
        self.db.refresh(db_preference)
        return db_preference

    def log_outreach(self, outreach_id: uuid.UUID, status: OutreachStatus, error_message: Optional[str] = None) -> OutreachLog:
        """
        Log an outreach attempt.
        """
        log = OutreachLog(
            outreach_id=outreach_id,
            status=status,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_outreach_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get outreach statistics for a date range.
        """
        query = self.db.query(OutreachLog)

        if start_date:
            query = query.filter(OutreachLog.created_at >= start_date)
        if end_date:
            query = query.filter(OutreachLog.created_at <= end_date)

        total = query.count()
        successful = query.filter(OutreachLog.status == OutreachStatus.SENT).count()
        failed = query.filter(OutreachLog.status == OutreachStatus.FAILED).count()

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0
        }

    def get_outreach_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get outreach analytics for the last N days.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get daily stats
        daily_stats = self.db.query(
            func.date(OutreachLog.created_at).label('date'),
            func.count().label('total'),
            func.sum(case((OutreachLog.status == OutreachStatus.SENT, 1), else_=0)).label('successful'),
            func.sum(case((OutreachLog.status == OutreachStatus.FAILED, 1), else_=0)).label('failed')
        ).filter(
            OutreachLog.created_at.between(start_date, end_date)
        ).group_by(
            func.date(OutreachLog.created_at)
        ).all()

        # Get channel stats
        channel_stats = self.db.query(
            OutreachLog.channel,
            func.count().label('total'),
            func.sum(case((OutreachLog.status == OutreachStatus.SENT, 1), else_=0)).label('successful')
        ).filter(
            OutreachLog.created_at.between(start_date, end_date)
        ).group_by(
            OutreachLog.channel
        ).all()

        return {
            "daily_stats": [
                {
                    "date": stat.date.isoformat(),
                    "total": stat.total,
                    "successful": stat.successful,
                    "failed": stat.failed,
                    "success_rate": (stat.successful / stat.total * 100) if stat.total > 0 else 0
                }
                for stat in daily_stats
            ],
            "channel_stats": [
                {
                    "channel": stat.channel,
                    "total": stat.total,
                    "successful": stat.successful,
                    "success_rate": (stat.successful / stat.total * 100) if stat.total > 0 else 0
                }
                for stat in channel_stats
            ]
        } 