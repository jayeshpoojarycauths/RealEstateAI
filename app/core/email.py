import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from pathlib import Path
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email(
    to_emails: List[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    from_email: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
        from_email: Optional sender email address (defaults to SMTP_USER)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get SMTP settings from environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_server, smtp_user, smtp_password]):
            logger.error("Missing SMTP configuration")
            return False
            
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email or smtp_user
        msg['To'] = ", ".join(to_emails)
        
        # Attach plain text body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach HTML body if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
            
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_emails}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False 

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.PROJECT_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='./templates/email'
)

async def send_verification_email(email_to: str, token: str):
    """
    Send email verification link to user.
    """
    try:
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{token}"
        
        message = MessageSchema(
            subject=f"Verify your email - {settings.PROJECT_NAME}",
            recipients=[email_to],
            body=f"""
            <html>
                <body>
                    <h1>Welcome to {settings.PROJECT_NAME}!</h1>
                    <p>Please verify your email address by clicking the link below:</p>
                    <p><a href="{verification_link}">Verify Email</a></p>
                    <p>If you did not create an account, please ignore this email.</p>
                </body>
            </html>
            """,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Verification email sent to {email_to}")
        
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        raise 