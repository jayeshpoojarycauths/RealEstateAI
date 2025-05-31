from typing import Optional
from app.shared.core.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_reset_password_email(to_email: str, reset_link: str):
    # Placeholder for sending reset password email
    print(f"Send reset password email to {to_email} with link: {reset_link}")

def send_mfa_code_email(to_email: str, mfa_code: str):
    """Send MFA code via email using SendGrid."""
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        mail = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=to_email,
            subject="Your MFA Code",
            html_content=f"Your MFA code is: {mfa_code}"
        )
        response = sg.send(mail)
        return {"status": "success", "message_id": response.headers['X-Message-Id']}
    except Exception as e:
        print(f"Error sending MFA code email: {str(e)}")
        raise 