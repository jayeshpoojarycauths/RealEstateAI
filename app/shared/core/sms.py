"""
SMS and WhatsApp service module using Twilio.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from ratelimit import limits, sleep_and_retry
from sqlalchemy.orm import Session
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.shared.core.exceptions import (CommunicationException,
                                        RateLimitException)
from app.shared.core.infrastructure.logger_config import logger

async def send_mfa_code_sms(
    phone_number: str,
    code: str,
    customer_id: Optional[int] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Standalone function to send MFA verification code via SMS.
    
    Args:
        phone_number: Recipient phone number
        code: MFA verification code
        customer_id: Optional customer ID for tracking
        db: Optional database session
        
    Returns:
        Dict containing message details and status
    """
    sms_service = SMSService()
    return await sms_service.send_mfa_code_sms(phone_number, code, customer_id)

class SMSService:
    """
    Service for sending SMS and WhatsApp messages using Twilio.
    """
    
    def __init__(self):
        """
        Initialize Twilio service.
        """
        self.client = None
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not fully configured. SMS/WhatsApp service will not be available.")
            return
            
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio service: {str(e)}")
            raise CommunicationException("Failed to initialize Twilio service")
        
    def send_sms(
        self,
        to_number: str,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> bool:
        """
        Send an SMS message using Twilio.
        
        Args:
            to_number: Recipient's phone number
            message: Message content
            media_urls: Optional list of media URLs to attach
        """
        if not self.client:
            raise CommunicationException("Twilio service is not configured")
            
        try:
            message_params = {
                "from_": self.from_number,
                "body": message,
                "to": to_number
            }
            
            if media_urls:
                message_params["media_url"] = media_urls
                
            message = self.client.messages.create(**message_params)
            logger.info(f"SMS sent to {to_number}, SID: {message.sid}")
            return True
        except TwilioRestException as e:
            logger.error(f"Twilio error: {str(e)}")
            raise CommunicationException(f"Failed to send SMS: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            raise CommunicationException(f"Failed to send SMS: {str(e)}")
            
    def send_whatsapp(
        self,
        to_number: str,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> bool:
        """
        Send a WhatsApp message using Twilio.
        
        Args:
            to_number: Recipient's WhatsApp number
            message: Message content
            media_urls: Optional list of media URLs to attach
        """
        if not self.client or not self.whatsapp_number:
            raise CommunicationException("WhatsApp service is not configured")
            
        try:
            # Format numbers for WhatsApp
            from_whatsapp = f"whatsapp:{self.whatsapp_number}"
            to_whatsapp = f"whatsapp:{to_number}"
            
            message_params = {
                "from_": from_whatsapp,
                "body": message,
                "to": to_whatsapp
            }
            
            if media_urls:
                message_params["media_url"] = media_urls
                
            message = self.client.messages.create(**message_params)
            logger.info(f"WhatsApp message sent to {to_number}, SID: {message.sid}")
            return True
        except TwilioRestException as e:
            logger.error(f"Twilio error: {str(e)}")
            raise CommunicationException(f"Failed to send WhatsApp message: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            raise CommunicationException(f"Failed to send WhatsApp message: {str(e)}")
            
    def send_verification_code(self, phone_number: str, code: str, use_whatsapp: bool = False) -> bool:
        """
        Send verification code via SMS or WhatsApp.
        """
        message = f"Your verification code is: {code}"
        if use_whatsapp:
            return self.send_whatsapp(phone_number, message)
        return self.send_sms(phone_number, message)
        
    def send_notification(
        self,
        phone_number: str,
        notification_type: str,
        data: Dict[str, Any],
        use_whatsapp: bool = False,
        media_urls: Optional[List[str]] = None
    ) -> bool:
        """
        Send notification via SMS or WhatsApp.
        """
        message = f"Notification: {notification_type}\n"
        for key, value in data.items():
            message += f"{key}: {value}\n"
            
        if use_whatsapp:
            return self.send_whatsapp(phone_number, message, media_urls)
        return self.send_sms(phone_number, message, media_urls)

    async def send_mfa_code_sms(
        self,
        phone_number: str,
        code: str,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send MFA verification code via SMS.
        
        Args:
            phone_number: Recipient phone number
            code: MFA verification code
            customer_id: Optional customer ID for tracking
            
        Returns:
            Dict containing message details and status
        """
        message = f"Your verification code is: {code}. This code will expire in 10 minutes."
        # Pass only supported params or delegate to `send_sms_with_rate_limit`
        return await self.send_sms_with_rate_limit(phone_number, message, customer_id=customer_id)

    @sleep_and_retry
    @limits(calls=100, period=60)  # 100 calls per minute
    async def send_sms_with_rate_limit(
        self,
        to_number: str,
        message: str,
        customer_id: Optional[int] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Send an SMS message using Twilio with rate limiting and retries.
        
        Args:
            to_number: The recipient's phone number
            message: The message content
            customer_id: Optional customer ID for tracking
            retry_count: Number of retry attempts
            
        Returns:
            Dict containing message details and status
            
        Raises:
            CommunicationException: If message sending fails
            RateLimitException: If rate limit is exceeded
        """
        try:
            logger.info(f"Sending SMS to {to_number} for customer {customer_id}")
            
            # Validate phone number format
            if not self._validate_phone_number(to_number):
                raise CommunicationException(f"Invalid phone number format: {to_number}")

            # Check message length
            if len(message) > 1600:  # Twilio's limit
                raise CommunicationException("Message exceeds maximum length of 1600 characters")

            loop = asyncio.get_running_loop()
            twilio_msg = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=to_number
                )
            )
            
            logger.info(f"SMS sent successfully. Message SID: {twilio_msg.sid}")
            
            return {
                "status": "success",
                "message_id": twilio_msg.sid,
                "to": to_number,
                "customer_id": customer_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {str(e)}")
            
            # Handle specific Twilio error codes
            if e.code == 21211:  # Invalid phone number
                raise CommunicationException(f"Invalid phone number: {to_number}")
            elif e.code == 21608:  # Rate limit exceeded
                raise RateLimitException("SMS rate limit exceeded")
            elif e.code == 21614:  # Unreachable number
                raise CommunicationException(f"Phone number {to_number} is unreachable")
            
            # Retry on certain error codes
            if retry_count < 3 and e.code in [20003, 20008, 20012]:  # Retryable errors
                logger.warning(f"Retrying SMS send. Attempt {retry_count + 1}")
                return await self.send_sms_with_rate_limit(to_number, message, customer_id, retry_count + 1)
            
            raise CommunicationException(f"Failed to send SMS: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            raise CommunicationException(f"Failed to send SMS: {str(e)}")

    async def send_bulk_sms(
        self,
        numbers: List[str],
        message: str,
        customer_id: Optional[int] = None,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Send SMS messages to multiple recipients with batching and error handling.
        
        Args:
            numbers: List of recipient phone numbers
            message: The message content
            customer_id: Optional customer ID for tracking
            batch_size: Number of messages to send in each batch
            
        Returns:
            Dict containing results for each message
        """
        results = []
        errors = []
        start_time = datetime.utcnow()
        
        logger.info(f"Starting bulk SMS send to {len(numbers)} recipients")
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(numbers), batch_size):
            batch = numbers[i:i + batch_size]
            batch_results = []
            
            for number in batch:
                try:
                    result = await self.send_sms_with_rate_limit(number, message, customer_id)
                    batch_results.append(result)
                except (CommunicationException, RateLimitException) as e:
                    logger.error(f"Error sending SMS to {number}: {str(e)}")
                    errors.append({
                        "number": number,
                        "error": str(e)
                    })
                    batch_results.append({
                        "status": "error",
                        "to": number,
                        "error": str(e)
                    })
            
            results.extend(batch_results)
            
            # Add delay between batches to respect rate limits
            if i + batch_size < len(numbers):
                await asyncio.sleep(1)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "completed",
            "total_messages": len(numbers),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "errors": errors,
            "duration_seconds": duration,
            "results": results
        }

    def _validate_phone_number(self, number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            number: Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, number))
        
        # Basic validation (can be enhanced based on requirements)
        return len(digits) >= 10 and len(digits) <= 15 

# Create a singleton instance
sms_service = SMSService()

__all__ = ["sms_service"] 