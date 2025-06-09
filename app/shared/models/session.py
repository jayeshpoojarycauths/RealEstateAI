from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, String, Text)
from sqlalchemy.orm import relationship

from app.shared.db.base_class import Base

class UserSession(Base):
    """User session model for tracking user sessions."""
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 addresses can be up to 45 chars
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession {self.id}>"

__all__ = ["UserSession"] 