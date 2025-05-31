from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.shared.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        """Initialize SMS service with Twilio client."""
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER

    async def send_sms(
        self,
        to_number: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message using Twilio.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            metadata: Optional metadata to store with the message
            
        Returns:
            Dict containing message details and status
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                "status": "sent",
                "message_id": message.sid,
                "to": to_number,
                "from": self.from_number,
                "metadata": metadata
            }
            
        except TwilioRestException as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "to": to_number,
                "from": self.from_number,
                "metadata": metadata
            }
            
    async def send_bulk_sms(
        self,
        messages: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Send multiple SMS messages.
        
        Args:
            messages: List of dicts containing to_number, message, and optional metadata
            
        Returns:
            List of message results
        """
        results = []
        for msg in messages:
            result = await self.send_sms(
                to_number=msg["to_number"],
                message=msg["message"],
                metadata=msg.get("metadata")
            )
            results.append(result)
        return results

    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get status of a sent message.
        
        Args:
            message_id: Twilio message SID
            
        Returns:
            Dict containing message status and details
        """
        try:
            message = self.client.messages(message_id).fetch()
            return {
                "status": message.status,
                "message_id": message.sid,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
        except TwilioRestException as e:
            logger.error(f"Failed to get message status: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 