import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.shared.core.config import settings
from app.shared.core.exceptions import ExternalServiceError
from app.shared.core.communication.messages import MessageCode, Messages
from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr
import jinja2
import aiofiles
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.shared.models.user import User
from app.shared.models.customer import Customer

logger = logging.getLogger(__name__)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.PROJECT_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'email-templates'
)

# Initialize FastMail
fastmail = FastMail(conf)

# Initialize Jinja2
template_loader = jinja2.FileSystemLoader(searchpath=str(conf.TEMPLATE_FOLDER))
template_env = jinja2.Environment(loader=template_loader)

async def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> None:
    """Send an email using a template."""
    try:
        # Load and render template
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**template_data)
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )
        
        # Send email
        await fastmail.send_message(message)
        
    except Exception as e:
        # Log error but don't raise to prevent API disruption
        logger.error(f"Error sending email: {str(e)}")

async def send_verification_email(
    email_to: str,
    token: str,
    user_name: str
) -> None:
    """Send verification email."""
    subject = f"{settings.PROJECT_NAME} - Verify your email"
    template_data = {
        "project_name": settings.PROJECT_NAME,
        "user_name": user_name,
        "verification_url": f"{settings.SERVER_HOST}/verify-email?token={token}"
    }
    await send_email(email_to, subject, "verification", template_data)

async def send_password_reset_email(
    email_to: str,
    token: str,
    user_name: str
) -> None:
    """Send password reset email."""
    subject = f"{settings.PROJECT_NAME} - Password Reset"
    template_data = {
        "project_name": settings.PROJECT_NAME,
        "user_name": user_name,
        "reset_url": f"{settings.SERVER_HOST}/reset-password?token={token}"
    }
    await send_email(email_to, subject, "password_reset", template_data)

async def send_mfa_code_email(
    email_to: str,
    code: str,
    user_name: str
) -> None:
    """Send MFA code email."""
    subject = f"{settings.PROJECT_NAME} - Your MFA Code"
    template_data = {
        "project_name": settings.PROJECT_NAME,
        "user_name": user_name,
        "mfa_code": code
    }
    await send_email(email_to, subject, "mfa_code", template_data)

__all__ = ['send_email'] 