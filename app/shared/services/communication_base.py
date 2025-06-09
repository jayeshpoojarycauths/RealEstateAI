import logging
from typing import Any, Dict, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session
from twilio.rest import Client

from app.shared.core.config import settings
from app.shared.core.text_to_speech import TextToSpeechService

logger = logging.getLogger(__name__)

class CommunicationBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
        self.tts_service = TextToSpeechService()

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

    async def make_call(
        self,
        to_phone: str,
        message: str,
        voice_id: str = "default",
        record: bool = True,
        status_callback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make an outbound call using Twilio with text-to-speech.
        
        Args:
            to_phone: The phone number to call
            message: The text message to convert to speech
            voice_id: The ElevenLabs voice ID to use
            record: Whether to record the call
            status_callback: URL to receive call status updates
            
        Returns:
            Dict containing call details and status
        """
        try:
            # Generate audio from text using ElevenLabs
            audio_url = await self.tts_service.generate_audio(message, voice_id)
            
            # Make the call using Twilio
            call = self.client.calls.create(
                to=to_phone,
                from_=self.from_number,
                twiml=f'<Response><Play>{audio_url}</Play></Response>',
                record=record,
                status_callback=status_callback,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            return {
                "status": "success",
                "call_sid": call.sid,
                "audio_url": audio_url
            }
            
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            raise

    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """
        Get the status of a call using its SID.
        
        Args:
            call_sid: The Twilio Call SID
            
        Returns:
            Dict containing call status and details
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "recording_url": call.recordings.list()[0].uri if call.recordings.list() else None
            }
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise 