from enum import Enum




class OutreachChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"

class OutreachStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"

class OutreachType(Enum):
    CALL = "call"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

# Remove the OutreachTemplate class definition from this file. 