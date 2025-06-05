 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app/outreach/services/outreach.py b/app/outreach/services/outreach.py
index 68b5f4603e2a4f877aadba9b6088c29058a23897..fd8bc16f04b9d394d94d5ca7a9f09dc5f752b96b 100644
--- a/app/outreach/services/outreach.py
+++ b/app/outreach/services/outreach.py
@@ -1,210 +1,178 @@
 from typing import Optional, List, Dict, Any
 from sqlalchemy.orm import Session
 
 from app.shared.core.config import settings
-from sendgrid import SendGridAPIClient
-from sendgrid.helpers.mail import Mail
-from twilio.rest import Client
-import openai
 from datetime import datetime, timedelta
 import asyncio
 import logging
-from app.outreach.schemas.outreach import LeadUpload, OutreachCreate, OutreachUpdate, OutreachTemplateCreate, OutreachTemplateUpdate, CommunicationPreferenceCreate, CommunicationPreferenceUpdate, OutreachFilter, OutreachTemplateFilter
-from app.shared.core.ai import AIService
-from app.shared.core.communication import EmailService
-from app.shared.core.communication import SMSService
+from app.outreach.schemas.outreach import (
+    LeadUpload,
+    OutreachCreate,
+    OutreachUpdate,
+    OutreachTemplateCreate,
+    OutreachTemplateUpdate,
+    CommunicationPreferenceCreate,
+    CommunicationPreferenceUpdate,
+    OutreachFilter,
+    OutreachTemplateFilter,
+)
+from .message_service import MessageService
+from .channel_service import EmailClient, SMSClient
 from app.shared.core.audit import AuditLogger
 from app.outreach.models.outreach import Outreach, OutreachTemplate, CommunicationPreference
 from app.shared.core.exceptions import NotFoundError, ValidationError
 from app.shared.core.audit import AuditService
 import uuid
 from sqlalchemy import func, and_, or_, case
-from fastapi import Depends
-from app.shared.db.session import get_db
-from app.shared.models.outreach import OutreachCampaign, OutreachTemplate
-from app.shared.models.contact import Contact
-from app.shared.models.user import User
-from app.shared.core.audit import get_audit_service
-from app.shared.core.security import get_current_user
-from app.shared.core.tenant import get_customer_id
-from app.shared.core.exceptions import NotFoundException, ValidationException
-from app.shared.core.communication.email import send_email
-from app.shared.core.communication.sms import send_sms
+from app.shared.models.outreach import OutreachTemplate
 from app.lead.models.lead import Lead
 from app.shared.models.customer import Customer
 
 logger = logging.getLogger(__name__)
 
 class OutreachService:
     def __init__(self, db: Session, customer: Customer):
         self.db = db
         self.customer = customer
-        self.twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
-        self.openai = openai
-        self.openai.api_key = settings.OPENAI_API_KEY
-        self.ai_service = AIService()
-        self.email_service = EmailService()
-        self.sms_service = SMSService()
+        self.message_service = MessageService()
+        self.email_client = EmailClient()
+        self.sms_client = SMSClient()
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
-        """
-        Generate personalized message using GPT.
-        """
+        """Generate personalized message using the message service."""
         try:
-            message = await self.ai_service.generate_outreach_message(
-                lead_name=lead.name,
-                lead_source=lead.source,
-                channel=OutreachChannel.EMAIL if lead.email else OutreachChannel.SMS,
-                property_preferences=lead.property_preferences,
-                budget_range=lead.budget_range,
-                notes=lead.notes
-            )
+            channel = OutreachChannel.EMAIL if lead.email else OutreachChannel.SMS
+            message = await self.message_service.generate(lead, channel)
 
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
-        """
-        Send email using SendGrid with retry logic.
-        """
+        """Send email using the email client with retry logic."""
         max_retries = settings.MAX_EMAIL_RETRIES
         retry_delay = settings.EMAIL_RETRY_DELAY
 
         try:
-            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
-            # Split message into subject and body
             if "Subject:" in message and "Body:" in message:
                 subject = message.split("Subject:")[1].split("Body:")[0].strip()
                 body = message.split("Body:")[1].strip()
             else:
                 subject = "Real Estate Opportunity"
                 body = message
 
-            email = Mail(
-                from_email=settings.FROM_EMAIL,
-                to_emails=lead.email,
-                subject=subject,
-                plain_text_content=body
-            )
-            sg.send(email)
+            await self.email_client.send(lead.email, subject, body)
 
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
-        """
-        Send SMS using Twilio with retry logic.
-        """
+        """Send SMS using the SMS client with retry logic."""
         max_retries = settings.MAX_SMS_RETRIES
         retry_delay = settings.SMS_RETRY_DELAY
 
         try:
-            self.twilio.messages.create(
-                body=message,
-                from_=settings.TWILIO_PHONE_NUMBER,
-                to=lead.phone
-            )
+            await self.sms_client.send(lead.phone, message)
 
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
diff --git a/app/outreach/services/outreach.py b/app/outreach/services/outreach.py
index 68b5f4603e2a4f877aadba9b6088c29058a23897..fd8bc16f04b9d394d94d5ca7a9f09dc5f752b96b 100644
--- a/app/outreach/services/outreach.py
+++ b/app/outreach/services/outreach.py
@@ -227,91 +195,77 @@ class OutreachService:
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
-                message = await self.ai_service.generate_outreach_message(
-                    lead_name=lead.name,
-                    lead_source=lead.source,
-                    channel=channel,
-                    property_preferences=lead.property_preferences,
-                    budget_range=lead.budget_range,
-                    notes=lead.notes
-                )
+                message = await self.message_service.generate(lead, channel)
                 
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
 
-                    await self.email_service.send_email(
-                        to_email=lead.email,
-                        subject=subject,
-                        message=body
-                    )
+                    await self.email_client.send(lead.email, subject, body)
                 else:  # SMS
-                    await self.sms_service.send_sms(
-                        to_phone=lead.phone,
-                        message=message
-                    )
+                    await self.sms_client.send(lead.phone, message)
                 
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
 
EOF
)