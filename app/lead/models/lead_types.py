import enum

class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    SMS = "sms"
    MEETING = "meeting"
    NOTE = "note"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    OTHER = "other"
