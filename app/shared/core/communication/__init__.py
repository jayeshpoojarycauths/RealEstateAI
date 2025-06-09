"""
Communication module.
"""

from app.shared.core.communication.email import email_service
from app.shared.core.communication.messages import (MessageCode, Messages,
                                                    MessageType, get_message)
from app.shared.core.communication.outreach import (MockOutreachEngine,
                                                    OutreachEngine)
from app.shared.core.communication.sms import (SMSService,
                                               send_password_reset_sms,
                                               send_sms, send_verification_sms)

# Re-export commonly used functions
__all__ = [
    'email_service',
    'MessageCode',
    'Messages',
    'MessageType',
    'get_message',
    'MockOutreachEngine',
    'OutreachEngine',
    'SMSService',
    'send_password_reset_sms',
    'send_sms',
    'send_verification_sms'
] 