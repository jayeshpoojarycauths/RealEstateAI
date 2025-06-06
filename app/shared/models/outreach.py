from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.shared.db.base_class import Base
from sqlalchemy.orm import relationship

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