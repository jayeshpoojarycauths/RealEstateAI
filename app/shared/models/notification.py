"""
Notification models for the Real Estate AI platform.

This module defines the Notification and NotificationPreference models for managing user notifications.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.shared.db.base_class import Base

if TYPE_CHECKING:
    from app.shared.models.user import User

class Notification(Base):
    """
    Notification model for storing user notifications.
    
    Attributes:
        id (str): Unique identifier for the notification
        user_id (str): ID of the user who owns this notification
        customer_id (str): ID of the customer associated with this notification
        title (str): Notification title
        message (str): Notification message
        type (str): Type of notification (e.g., 'info', 'warning', 'error')
        is_read (bool): Whether the notification has been read
        created_at (datetime): When the notification was created
        read_at (datetime): When the notification was read (if read)
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
    customer = relationship("Customer", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.title}>"

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()

class NotificationPreference(Base):
    """
    NotificationPreference model for storing user notification preferences.
    
    Attributes:
        id (str): Unique identifier for the preference
        user_id (str): ID of the user who owns these preferences
        customer_id (str): ID of the customer associated with these preferences
        email_enabled (bool): Whether email notifications are enabled
        push_enabled (bool): Whether push notifications are enabled
        sms_enabled (bool): Whether SMS notifications are enabled
        created_at (datetime): When the preferences were created
        updated_at (datetime): When the preferences were last updated
    """
    __tablename__ = "notification_preferences"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notification_preferences")
    customer = relationship("Customer", back_populates="notification_preferences")

    def __repr__(self):
        return f"<NotificationPreference {self.user_id}>"

    def update_preferences(
        self,
        email_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None,
        sms_enabled: Optional[bool] = None
    ):
        """Update notification preferences."""
        if email_enabled is not None:
            self.email_enabled = email_enabled
        if push_enabled is not None:
            self.push_enabled = push_enabled
        if sms_enabled is not None:
            self.sms_enabled = sms_enabled
        self.updated_at = datetime.utcnow()

__all__ = ["Notification", "NotificationPreference"] 