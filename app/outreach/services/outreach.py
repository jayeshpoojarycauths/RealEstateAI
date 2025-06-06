from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import openai
from datetime import datetime, timedelta
import asyncio
import logging
from app.outreach.schemas.outreach import LeadUpload, OutreachCreate, OutreachUpdate, OutreachTemplateCreate, OutreachTemplateUpdate, CommunicationPreferenceCreate, CommunicationPreferenceUpdate, OutreachFilter, OutreachTemplateFilter
from app.shared.core.ai import AIService
from app.shared.core.communication import EmailService
from app.shared.core.communication import SMSService
from app.shared.core.audit import AuditLogger
from app.outreach.models.outreach import Outreach, OutreachTemplate, CommunicationPreference, OutreachChannel, OutreachLog, OutreachStatus
from app.shared.core.exceptions import NotFoundException, ValidationException
from app.shared.core.audit import AuditService
import uuid
from sqlalchemy import func, and_, or_, case
from fastapi import Depends
from app.shared.db.session import get_db
from app.outreach.models.outreach import OutreachCampaign, OutreachTemplate
from app.shared.models.user import User
from app.shared.core.audit import get_audit_service
from app.shared.core.security.auth import get_current_user
from app.shared.core.tenant import get_customer_id
from app.shared.core.communication.email import send_email
from app.shared.core.communication.sms import send_sms
from app.lead.models.lead import Lead
from app.shared.models.customer import Customer
from app.shared.core.communication import OutreachEngine

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
                details={
                    "call_sid": call_result["call_sid"],
                    "retry_count": retry_count
                }
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
        Generate a call-specific message using GPT.
        """
        try:
            call_message = await self.ai_service.generate_call_message(
                lead_name=lead.name,
                base_message=base_message,
                lead_source=lead.source,
                property_preferences=lead.property_preferences,
                budget_range=lead.budget_range,
                notes=lead.notes
            )

            await self.audit_logger.log(
                action="call_message_generated",
                resource_type="lead",
                resource_id=lead.id,
                details={"message_length": len(call_message)}
            )

            return call_message

        except Exception as e:
            logger.error(f"Error generating call message for lead {lead.id}: {str(e)}")
            await self.audit_logger.log(
                action="call_message_generation_failed",
                resource_type="lead",
                resource_id=lead.id,
                details={"error": str(e)}
            )
            return base_message  # Fallback to base message

    async def _log_call(self, lead: Lead, call_result: Dict[str, Any]) -> None:
        """
        Log call details in the database.
        """
        try:
            call_interaction = CallInteraction(
                interaction_id=str(uuid.uuid4()),
                call_sid=call_result["call_sid"],
                recording_url=call_result.get("recording_url"),
                call_quality_metrics={},  # To be updated when call completes
                model_metadata={
                    "voice_id": settings.DEFAULT_VOICE_ID,
                    "audio_url": call_result["audio_url"]
                }
            )
            
            self.db.add(call_interaction)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error logging call for lead {lead.id}: {str(e)}")
            self.db.rollback()

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
                # Pre-allocate log so it exists even if message generation fails
                outreach_log = OutreachLog(
                    customer_id=self.customer.id,
                    lead_id=lead.id,
                    channel=channel,
                    status=OutreachStatus.PENDING,
                    retry_count=0
                )
                self.db.add(outreach_log)
                self.db.flush()

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

    def create_outreach(self, outreach: OutreachCreate) -> Outreach:
        """Create a new outreach attempt."""
        db_outreach = Outreach(
            lead_id=outreach.lead_id,
            channel=outreach.channel,
            message=outreach.message,
            subject=outreach.subject,
            template_id=outreach.template_id,
            variables=outreach.variables,
            status=OutreachStatus.PENDING
        )
        self.db.add(db_outreach)
        self.db.commit()
        self.db.refresh(db_outreach)
        
        self.audit.log_activity(
            entity_type="outreach",
            entity_id=str(db_outreach.id),
            action="create",
            details={"channel": outreach.channel.value}
        )
        
        return db_outreach

    def get_outreach(self, outreach_id: uuid.UUID) -> Outreach:
        """Get an outreach attempt by ID."""
        outreach = self.db.query(Outreach).filter(Outreach.id == outreach_id).first()
        if not outreach:
            raise NotFoundException(f"Outreach with ID {outreach_id} not found")
        return outreach

    def update_outreach(self, outreach_id: uuid.UUID, outreach: OutreachUpdate) -> Outreach:
        """Update an outreach attempt."""
        db_outreach = self.get_outreach(outreach_id)
        
        for field, value in outreach.dict(exclude_unset=True).items():
            setattr(db_outreach, field, value)
        
        self.db.commit()
        self.db.refresh(db_outreach)
        
        self.audit.log_activity(
            entity_type="outreach",
            entity_id=str(outreach_id),
            action="update",
            details={"status": outreach.status.value if outreach.status else None}
        )
        
        return db_outreach

    def list_outreach(self, filter_params: OutreachFilter) -> List[Outreach]:
        """List outreach attempts with filtering."""
        query = (self.db.query(Outreach)
                 .filter(Outreach.customer_id == self.customer.id))
        
        if filter_params.channel:
            query = query.filter(Outreach.channel == filter_params.channel)
        if filter_params.status:
            query = query.filter(Outreach.status == filter_params.status)
        if filter_params.start_date:
            query = query.filter(Outreach.created_at >= filter_params.start_date)
        if filter_params.end_date:
            query = query.filter(Outreach.created_at <= filter_params.end_date)
        if filter_params.search:
            search = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    Outreach.message.ilike(search),
                    Outreach.subject.ilike(search)
                )
            )
        
        return query.order_by(Outreach.created_at.desc()).all()

    def create_template(self, template: OutreachTemplateCreate) -> OutreachTemplate:
        """Create a new outreach template."""
        db_template = OutreachTemplate(**template.dict())
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        self.audit.log_activity(
            entity_type="outreach_template",
            entity_id=str(db_template.id),
            action="create",
            details={"channel": template.channel.value}
        )
        
        return db_template

    def get_template(self, template_id: uuid.UUID) -> OutreachTemplate:
        """Get a template by ID."""
        template = self.db.query(OutreachTemplate).filter(OutreachTemplate.id == template_id).first()
        if not template:
            raise NotFoundException(f"Template with ID {template_id} not found")
        return template

    def update_template(self, template_id: uuid.UUID, template: OutreachTemplateUpdate) -> OutreachTemplate:
        """Update a template."""
        db_template = self.get_template(template_id)
        
        for field, value in template.dict(exclude_unset=True).items():
            setattr(db_template, field, value)
        
        self.db.commit()
        self.db.refresh(db_template)
        
        self.audit.log_activity(
            entity_type="outreach_template",
            entity_id=str(template_id),
            action="update"
        )
        
        return db_template

    def list_templates(self, filter_params: OutreachTemplateFilter) -> List[OutreachTemplate]:
        """List templates with filtering."""
        query = self.db.query(OutreachTemplate)
        
        if filter_params.channel:
            query = query.filter(OutreachTemplate.channel == filter_params.channel)
        if filter_params.is_active is not None:
            query = query.filter(OutreachTemplate.is_active == filter_params.is_active)
        if filter_params.search:
            search = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    OutreachTemplate.name.ilike(search),
                    OutreachTemplate.description.ilike(search),
                    OutreachTemplate.body.ilike(search)
                )
            )
        
        return query.order_by(OutreachTemplate.created_at.desc()).all()

    def create_communication_preference(self, preference: CommunicationPreferenceCreate) -> CommunicationPreference:
        """Create communication preferences for a customer."""
        db_preference = CommunicationPreference(**preference.dict())
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        
        self.audit.log_activity(
            entity_type="communication_preference",
            entity_id=str(db_preference.id),
            action="create",
            details={"default_channel": preference.default_channel.value}
        )
        
        return db_preference

    def get_communication_preference(self, customer_id: uuid.UUID) -> CommunicationPreference:
        """Get communication preferences for a customer."""
        preference = self.db.query(CommunicationPreference).filter(
            CommunicationPreference.customer_id == customer_id
        ).first()
        if not preference:
            raise NotFoundException(f"Communication preferences for customer {customer_id} not found")
        return preference

    def update_communication_preference(
        self, customer_id: uuid.UUID, preference: CommunicationPreferenceUpdate
    ) -> CommunicationPreference:
        """Update communication preferences for a customer."""
        db_preference = self.get_communication_preference(customer_id)
        
        for field, value in preference.dict(exclude_unset=True).items():
            setattr(db_preference, field, value)
        
        self.db.commit()
        self.db.refresh(db_preference)
        
        self.audit.log_activity(
            entity_type="communication_preference",
            entity_id=str(db_preference.id),
            action="update",
            details={"default_channel": preference.default_channel.value}
        )
        
        return db_preference

    def log_outreach(self, outreach_id: uuid.UUID, status: OutreachStatus, error_message: Optional[str] = None) -> OutreachLog:
        """Log an outreach attempt."""
        outreach = self.get_outreach(outreach_id)
        
        log = OutreachLog(
            lead_id=outreach.lead_id,
            customer_id=outreach.customer_id,
            channel=outreach.channel,
            status=status,
            message=outreach.message,
            error_message=error_message
        )
        
        if status == OutreachStatus.SENT:
            log.sent_at = datetime.utcnow()
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log

    def get_outreach_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get outreach statistics."""
        query = self.db.query(Outreach)
        
        if start_date:
            query = query.filter(Outreach.created_at >= start_date)
        if end_date:
            query = query.filter(Outreach.created_at <= end_date)
        
        total = query.count()
        successful = query.filter(Outreach.status == OutreachStatus.SENT).count()
        failed = query.filter(Outreach.status == OutreachStatus.FAILED).count()
        
        channel_distribution = {}
        for channel in OutreachChannel:
            count = query.filter(Outreach.channel == channel).count()
            channel_distribution[channel.value] = count
        
        success_rate_by_channel = {}
        for channel in OutreachChannel:
            channel_total = query.filter(Outreach.channel == channel).count()
            if channel_total > 0:
                channel_success = query.filter(
                    and_(
                        Outreach.channel == channel,
                        Outreach.status == OutreachStatus.SENT
                    )
                ).count()
                success_rate_by_channel[channel.value] = channel_success / channel_total
            else:
                success_rate_by_channel[channel.value] = 0.0
        
        retry_rate = query.filter(Outreach.retry_count > 0).count() / total if total > 0 else 0
        
        error_distribution = {}
        error_query = self.db.query(
            Outreach.error_message,
            func.count(Outreach.id).label('count')
        ).filter(
            Outreach.error_message.isnot(None)
        ).group_by(Outreach.error_message)
        
        for error, count in error_query.all():
            error_distribution[error] = count
        
        return {
            "total_outreach": total,
            "successful_outreach": successful,
            "failed_outreach": failed,
            "channel_distribution": channel_distribution,
            "success_rate_by_channel": success_rate_by_channel,
            "retry_rate": retry_rate,
            "error_distribution": error_distribution
        }

    def get_outreach_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed outreach analytics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get trends
        trends = []
        for channel in OutreachChannel:
            for status in OutreachStatus:
                daily_counts = self.db.query(
                    func.date(Outreach.created_at).label('date'),
                    func.count(Outreach.id).label('count')
                ).filter(
                    and_(
                        Outreach.created_at >= start_date,
                        Outreach.created_at <= end_date,
                        Outreach.channel == channel,
                        Outreach.status == status
                    )
                ).group_by(
                    func.date(Outreach.created_at)
                ).all()
                
                for date, count in daily_counts:
                    trends.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "count": count,
                        "channel": channel,
                        "status": status
                    })
        
        # Get channel performance
        channel_performance = {}
        for channel in OutreachChannel:
            channel_stats = self.db.query(
                func.count(Outreach.id).label('total'),
                func.avg(
                    func.extract('epoch', Outreach.sent_at - Outreach.created_at)
                ).label('avg_response_time'),
                func.count(
                    case([(Outreach.status == OutreachStatus.SENT, 1)])
                ).label('successful')
            ).filter(
                and_(
                    Outreach.created_at >= start_date,
                    Outreach.created_at <= end_date,
                    Outreach.channel == channel
                )
            ).first()
            
            channel_performance[channel.value] = {
                "total": channel_stats.total,
                "success_rate": channel_stats.successful / channel_stats.total if channel_stats.total > 0 else 0,
                "avg_response_time": channel_stats.avg_response_time
            }
        
        # Get time distribution
        time_distribution = {}
        for hour in range(24):
            count = self.db.query(Outreach).filter(
                and_(
                    Outreach.created_at >= start_date,
                    Outreach.created_at <= end_date,
                    func.extract('hour', Outreach.created_at) == hour
                )
            ).count()
            time_distribution[f"{hour:02d}:00"] = count
        
        # Get success metrics
        success_metrics = {
            "overall_success_rate": self.db.query(Outreach).filter(
                and_(
                    Outreach.created_at >= start_date,
                    Outreach.created_at <= end_date,
                    Outreach.status == OutreachStatus.SENT
                )
            ).count() / self.db.query(Outreach).filter(
                and_(
                    Outreach.created_at >= start_date,
                    Outreach.created_at <= end_date
                )
            ).count(),
            "avg_retry_count": self.db.query(
                func.avg(Outreach.retry_count)
            ).filter(
                and_(
                    Outreach.created_at >= start_date,
                    Outreach.created_at <= end_date
                )
            ).scalar() or 0
        }
        
        # Get error analysis
        error_analysis = {}
        error_query = self.db.query(
            Outreach.error_message,
            func.count(Outreach.id).label('count')
        ).filter(
            and_(
                Outreach.created_at >= start_date,
                Outreach.created_at <= end_date,
                Outreach.error_message.isnot(None)
            )
        ).group_by(Outreach.error_message)
        
        for error, count in error_query.all():
            error_analysis[error] = count
        
        return {
            "trends": trends,
            "channel_performance": channel_performance,
            "time_distribution": time_distribution,
            "success_metrics": success_metrics,
            "error_analysis": error_analysis
        } 