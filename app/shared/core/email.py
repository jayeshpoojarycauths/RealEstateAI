import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import func

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Environment, FileSystemLoader
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.shared.core.config import settings
from app.shared.core.exceptions import ServiceUnavailableException
from app.shared.core.logging import logger

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / "templates" / "email"
)

# Initialize Jinja2 environment
template_dir = Path(__file__).parent.parent.parent / "templates" / "email"
env = Environment(loader=FileSystemLoader(template_dir))

def send_email_smtp(
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

async def send_email_fastmail(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> None:
    """
    Send an email using FastMail and templates.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        template_name: Name of the template file (without extension)
        template_data: Data to render in the template
    """
    try:
        # Render template
        template = env.get_template(f"{template_name}.html")
        html_content = template.render(**template_data)
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )
        
        # Send email
        fm = FastMail(conf)
        await fm.send_message(message)
        
        logger.info(f"Email sent to {email_to}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise ServiceUnavailableException(
            detail=f"Failed to send email: {str(e)}"
        )

async def send_email_sendgrid(
    to_email: str,
    subject: str,
    html_content: str
) -> Dict[str, str]:
    """
    Send an email using SendGrid.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content
        
    Returns:
        Dict containing status and message ID
    """
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        mail = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        response = sg.send(mail)
        return {"status": "success", "message_id": response.headers['X-Message-Id']}
    except Exception as e:
        logger.error(f"Error sending email via SendGrid: {str(e)}")
        raise ServiceUnavailableException(
            detail=f"Error sending email via SendGrid: {str(e)}"
        )

async def send_verification_email(
    email_to: str,
    token: str,
    user_name: str
) -> None:
    """
    Send email verification email.
    
    Args:
        email_to: Recipient email address
        token: Verification token
        user_name: Name of the user
    """
    verification_url = f"{settings.SERVER_HOST}/verify-email?token={token}"
    
    await send_email_fastmail(
        email_to=email_to,
        subject="Verify your email address",
        template_name="verify_email",
        template_data={
            "user_name": user_name,
            "verification_url": verification_url
        }
    )

async def send_password_reset_email(
    email_to: str,
    token: str,
    user_name: str
) -> None:
    """
    Send password reset email.
    
    Args:
        email_to: Recipient email address
        token: Password reset token
        user_name: Name of the user
    """
    reset_url = f"{settings.SERVER_HOST}/reset-password?token={token}"
    
    await send_email_fastmail(
        email_to=email_to,
        subject="Reset your password",
        template_name="reset_password",
        template_data={
            "user_name": user_name,
            "reset_url": reset_url
        }
    )

async def send_mfa_code_email(
    email_to: str,
    code: str,
    user_name: str
) -> None:
    """
    Send MFA code email.
    
    Args:
        email_to: Recipient email address
        code: MFA code
        user_name: Name of the user
    """
    if settings.USE_SENDGRID:
        await send_email_sendgrid(
            to_email=email_to,
            subject="Your MFA Code",
            html_content=f"<p>Hello {user_name},</p><p>Your MFA code is: <strong>{code}</strong></p>"
        )
    else:
        await send_email_fastmail(
            email_to=email_to,
            subject="Your MFA code",
            template_name="mfa_code",
            template_data={
                "user_name": user_name,
                "code": code
            }
        )

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_content: Optional[str] = None,
    template_name: Optional[str] = None,
    template_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Generic email sending function that uses the appropriate email service based on configuration.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_content: Optional HTML email content
        template_name: Optional template name to use
        template_data: Optional data for template rendering
    """
    if settings.USE_SENDGRID:
        await send_email_sendgrid(
            to_email=to_email,
            subject=subject,
            html_content=html_content or body
        )
    elif template_name and template_data:
        await send_email_fastmail(
            email_to=to_email,
            subject=subject,
            template_name=template_name,
            template_data=template_data
        )
    else:
        send_email_smtp(
            to_emails=[to_email],
            subject=subject,
            body=body,
            html_body=html_content
        )

__all__ = [
    'send_email_smtp',
    'send_email_fastmail',
    'send_email_sendgrid',
    'send_verification_email',
    'send_password_reset_email',
    'send_mfa_code_email',
    'send_email'
] 