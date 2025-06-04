from typing import Optional
from app.shared.core.config import settings
from app.shared.models.outreach import OutreachChannel

class CommunicationBaseService:
    """Base class for communication services."""
    
    def __init__(self, preferences: dict):
        self.preferences = preferences
        self.default_channel = preferences.get("default_channel", OutreachChannel.EMAIL)

    async def send_message(
        self,
        to: str,
        message: str,
        channel: Optional[OutreachChannel] = None,
        subject: Optional[str] = None
    ) -> bool:
        """Send a message through the specified channel."""
        channel = channel or self.default_channel
        
        if channel == OutreachChannel.EMAIL:
            return await self.send_email(to, message, subject)
        elif channel == OutreachChannel.SMS:
            return await self.send_sms(to, message)
        elif channel == OutreachChannel.WHATSAPP:
            return await self.send_whatsapp(to, message)
        else:
            raise ValueError(f"Unsupported channel: {channel}")

    async def send_email(self, to: str, message: str, subject: Optional[str] = None) -> bool:
        """Send an email message."""
        raise NotImplementedError

    async def send_sms(self, to: str, message: str) -> bool:
        """Send an SMS message."""
        raise NotImplementedError

    async def send_whatsapp(self, to: str, message: str) -> bool:
        """Send a WhatsApp message."""
        raise NotImplementedError 