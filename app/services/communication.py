from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import logging
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
import json
from app.shared.core.config import settings
from fastapi import HTTPException
from app.lead.services.lead import LeadService
from app.outreach.services.outreach import OutreachService
import uuid
from twilio.twiml.voice_response import VoiceResponse
from app.services.text_to_speech import tts_service
import os
from pathlib import Path
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole
from app.shared.services.communication_base import CommunicationBaseService
from app.models.models import User, Customer, UserCommunicationPreference, CommunicationPreferences, Lead, CommunicationChannel

logger = logging.getLogger(__name__)

class CommunicationService:
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.base_service = CommunicationBaseService(db)
        self.lead_service = LeadService(db)
        self.outreach_service = OutreachService(db, customer)
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def get_communication_preferences(self, customer_id: int) -> CommunicationPreferences:
        """Get communication preferences for a customer."""
        prefs = self.db.query(CommunicationPreferences).filter(
            CommunicationPreferences.customer_id == customer_id
        ).first()
        
        if not prefs:
            raise ValueError(f"No communication preferences found for customer {customer_id}")
        
        return prefs

    def send_sms(self, lead: Lead, message: str, prefs: CommunicationPreferences) -> Dict[str, Any]:
        """Send SMS using Twilio."""
        try:
            # Debug logging for lead object
            logger.info(f"Lead object: {lead}")
            
            # Extract phone number from lead object
            if not hasattr(lead, 'phone'):
                raise ValueError(f"Lead object has no phone attribute: {lead}")
            
            phone_number = getattr(lead, 'phone', None)
            logger.info(f"Extracted phone number: {phone_number}")
            
            if not phone_number:
                raise ValueError(f"No phone number found for lead {lead.id}")

            # Ensure phone number is a string and in E.164 format
            phone_number = str(phone_number).strip()
            if not phone_number.startswith('+'):
                phone_number = f"+91{phone_number}"  # Add India country code if not present
            logger.info(f"Formatted phone number: {phone_number}")

            # Validate phone number using Twilio Lookup API
            try:
                lookup = self.client.lookups.v2.phone_numbers(phone_number).fetch()
                if not lookup.valid:
                    raise ValueError(f"Invalid phone number format for lead {lead.id}: {lookup.validation_errors}")
                # Use the validated E.164 format phone number
                validated_phone = lookup.phone_number
                logger.info(f"Validated phone number: {validated_phone}")
            except Exception as lookup_error:
                logger.error(f"Error validating phone number: {str(lookup_error)}")
                raise ValueError(f"Failed to validate phone number for lead {lead.id}")

            client = Client(
                prefs.sms_settings['twilio_account_sid'],
                prefs.sms_settings['twilio_auth_token']
            )
            
            message = client.messages.create(
                body=message,
                from_=prefs.sms_settings['twilio_phone_number'],
                to=validated_phone  # Use the validated phone number
            )
            
            # Log interaction
            interaction = MessageInteraction(
                lead_id=lead.id,
                customer_id=lead.customer_id,
                interaction_type="sms",
                status="success",
                message_id=message.sid,
                content=message,
                delivery_status="delivered"
            )
            self.db.add(interaction)
            self.db.commit()
            
            return {"status": "success", "message_sid": message.sid}
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise

    def send_email(self, lead: Lead, subject: str, message: str, prefs: CommunicationPreferences) -> Dict[str, Any]:
        """Send email using SendGrid."""
        try:
            sg = SendGridAPIClient(prefs.email_settings['sendgrid_api_key'])
            mail = Mail(
                from_email=prefs.email_settings['from_email'],
                to_emails=lead.email,
                subject=subject,
                html_content=message
            )
            
            response = sg.send(mail)
            
            # Log interaction
            interaction = MessageInteraction(
                lead_id=lead.id,
                customer_id=lead.customer_id,
                interaction_type="email",
                status="success",
                message_id=str(response.headers['X-Message-Id']),
                content=message,
                delivery_status="delivered"
            )
            self.db.add(interaction)
            self.db.commit()
            
            return {"status": "success", "message_id": response.headers['X-Message-Id']}
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise

    def send_whatsapp(self, lead: Lead, message: str, prefs: CommunicationPreferences) -> Dict[str, Any]:
        """Send WhatsApp message using WhatsApp Business API."""
        try:
            headers = {
                'Authorization': f'Bearer {prefs.whatsapp_settings["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': lead.phone,
                'type': 'text',
                'text': {'body': message}
            }
            
            response = requests.post(
                'https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages',
                headers=headers,
                json=data
            )
            
            response_data = response.json()
            
            # Log interaction
            interaction = MessageInteraction(
                lead_id=lead.id,
                customer_id=lead.customer_id,
                interaction_type="whatsapp",
                status="success",
                message_id=response_data['messages'][0]['id'],
                content=message,
                delivery_status="delivered"
            )
            self.db.add(interaction)
            self.db.commit()
            
            return {"status": "success", "message_id": response_data['messages'][0]['id']}
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise

    def send_telegram(self, lead: Lead, message: str, prefs: CommunicationPreferences) -> Dict[str, Any]:
        """Send Telegram message using Telegram Bot API."""
        try:
            url = f"https://api.telegram.org/bot{prefs.telegram_settings['bot_token']}/sendMessage"
            data = {
                'chat_id': prefs.telegram_settings['chat_id'],
                'text': message
            }
            
            response = requests.post(url, json=data)
            response_data = response.json()
            
            # Log interaction
            interaction = MessageInteraction(
                lead_id=lead.id,
                customer_id=lead.customer_id,
                interaction_type="telegram",
                status="success",
                message_id=str(response_data['result']['message_id']),
                content=message,
                delivery_status="delivered"
            )
            self.db.add(interaction)
            self.db.commit()
            
            return {"status": "success", "message_id": response_data['result']['message_id']}
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            raise

    def make_voice_call(self, lead: Lead, message: str, prefs: CommunicationPreferences) -> str:
        """
        Make a voice call using TTS and Twilio.
        
        Args:
            lead: Lead to call
            message: Message to speak
            prefs: Communication preferences
            
        Returns:
            Call SID
        """
        try:
            # Generate TTS audio
            audio_path = tts_service.generate_temp_audio(
                text=message,
                voice_id=prefs.voice_settings.get('voice_id', 'default_voice_id'),
                use_cache=True
            )
            
            # Upload audio to Twilio
            audio_url = self._upload_to_twilio(audio_path)
            
            # Create TwiML response
            response = VoiceResponse()
            response.play(audio_url)
            
            # Make the call
            call = self.client.calls.create(
                twiml=str(response),
                to=lead.phone,
                from_=self.from_number
            )
            
            # Clean up temporary audio file
            try:
                os.remove(audio_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary audio file: {e}")
            
            return call.sid
            
        except Exception as e:
            logger.error(f"Error making voice call: {str(e)}", exc_info=True)
            # Fallback to basic TTS if audio generation fails
            response = VoiceResponse()
            response.say(message)
            
            call = self.client.calls.create(
                twiml=str(response),
                to=lead.phone,
                from_=self.from_number
            )
            return call.sid

    def _upload_to_twilio(self, audio_path: Union[str, Path]) -> str:
        """
        Upload audio file to Twilio and return the URL.
        """
        try:
            # Generate a unique filename
            filename = f"tts_{uuid.uuid4()}.mp3"
            
            # Upload to Twilio
            with open(audio_path, 'rb') as audio_file:
                media = self.client.messages.create(
                    media_url=[f"file://{filename}"],
                    from_=self.from_number,
                    to=self.from_number  # Send to self to get media URL
                )
            
            # Get the media URL
            media_url = media.media_list[0].uri
            
            return media_url
            
        except Exception as e:
            logger.error(f"Error uploading audio to Twilio: {str(e)}", exc_info=True)
            raise

    def send_message(self, lead: Lead, message: str, channel: CommunicationChannel) -> Dict[str, Any]:
        """Send message through specified channel."""
        prefs = self.get_communication_preferences(lead.customer_id)
        
        if channel == CommunicationChannel.SMS and prefs.sms_enabled:
            # Extract phone number from lead
            phone_number = str(lead.phone).strip()
            if not phone_number.startswith('+'):
                phone_number = f"+91{phone_number}"  # Add India country code if not present
            logger.info(f"Sending SMS to phone number: {phone_number}")
            return self.send_sms(phone_number, message, prefs)
        elif channel == CommunicationChannel.EMAIL and prefs.email_enabled:
            return self.send_email(lead, "Property Update", message, prefs)
        elif channel == CommunicationChannel.WHATSAPP and prefs.whatsapp_enabled:
            return self.send_whatsapp(lead, message, prefs)
        elif channel == CommunicationChannel.TELEGRAM and prefs.telegram_enabled:
            return self.send_telegram(lead, message, prefs)
        elif channel == CommunicationChannel.VOICE and prefs.voice_enabled:
            return self.make_voice_call(lead, message, prefs)
        else:
            raise ValueError(f"Channel {channel} is not enabled for this customer")

    def format_message(self, template: str, lead: Lead, **kwargs) -> str:
        """Format message template with lead data and additional parameters."""
        template_data = {
            'name': lead.name,
            'property_name': kwargs.get('property_name', ''),
            'datetime': kwargs.get('datetime', ''),
            **kwargs
        }
        return template.format(**template_data)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        from_email: Optional[str] = None
    ) -> None:
        """Send an email using the base service"""
        await self.base_service.send_email(
            to_email=to_email,
            subject=subject,
            template_name=template_name,
            template_data=template_data,
            from_email=from_email
        )

    async def send_sms(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> None:
        """Send an SMS using the base service"""
        await self.base_service.send_sms(
            to_phone=to_phone,
            message=message
        )

    async def send_voice_call(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> None:
        """Send a voice call using text-to-speech"""
        try:
            # Convert text to speech
            audio_content = await tts_service.text_to_speech(message)
            
            # Send voice call using outreach service
            await self.outreach_service.send_voice_call(
                to_phone=to_phone,
                audio_content=audio_content,
                from_phone=from_phone
            )
            
            logger.info(f"Voice call sent to {to_phone}")
            
        except Exception as e:
            logger.error(f"Error sending voice call: {str(e)}")
            raise

    async def send_notification(
        self,
        user_id: int,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a notification to a user based on their preferences"""
        try:
            # Get user's communication preferences
            preferences = self.db.query(UserCommunicationPreference).filter(
                UserCommunicationPreference.user_id == user_id
            ).first()
            
            if not preferences:
                logger.warning(f"No communication preferences found for user {user_id}")
                return
                
            # Get user details
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return
                
            # Send notification based on preferences
            if preferences.email_enabled:
                await self.send_email(
                    to_email=user.email,
                    subject=f"Notification: {notification_type}",
                    template_name="notification",
                    template_data={
                        "message": message,
                        "data": data or {},
                        "user_name": user.name,
                        "notification_type": notification_type
                    }
                )
                
            if preferences.sms_enabled and user.phone:
                await self.send_sms(
                    to_phone=user.phone,
                    message=f"{notification_type}: {message}"
                )
                
            if preferences.voice_enabled and user.phone:
                await self.send_voice_call(
                    to_phone=user.phone,
                    message=f"{notification_type}: {message}"
                )
                
            logger.info(f"Notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

# Create singleton instance
# communication_service = CommunicationService() 