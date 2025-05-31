from typing import List, Optional, Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.shared.core.config import settings

class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fastmail = FastMail(self.config)

    async def send_email(
        self,
        to_email: EmailStr,
        subject: str,
        message: str,
        cc: Optional[List[EmailStr]] = None,
        bcc: Optional[List[EmailStr]] = None
    ) -> None:
        """Send an email using FastMail."""
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=message,
            cc=cc or [],
            bcc=bcc or []
        )
        
        await self.fastmail.send_message(message)

    async def send_bulk_email(
        self,
        recipients: List[EmailStr],
        subject: str,
        message: str,
        cc: Optional[List[EmailStr]] = None,
        bcc: Optional[List[EmailStr]] = None
    ) -> None:
        """Send bulk emails using FastMail."""
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=message,
            cc=cc or [],
            bcc=bcc or []
        )
        
        await self.fastmail.send_message(message)

    async def send_templated_email(
        self,
        email_to: List[EmailStr],
        template_id: str,
        template_data: Dict[str, Any],
        subject: Optional[str] = None
    ) -> bool:
        """
        Send a templated email using a predefined template.
        
        Args:
            email_to: List of recipient email addresses
            template_id: ID of the template to use
            template_data: Data to populate the template
            subject: Optional subject override
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Here you would typically:
        # 1. Load the template
        # 2. Render it with the template_data
        # 3. Send the email
        
        # For now, we'll just use a simple template
        body = f"Template {template_id} with data: {template_data}"
        return await self.send_email(
            email_to=email_to,
            subject=subject or f"Message from {settings.PROJECT_NAME}",
            message=body
        )

# Create a singleton instance
email_service = EmailService() 