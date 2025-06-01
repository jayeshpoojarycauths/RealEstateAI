from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Customer, AuditLog, User
from app.shared.core.tenant import get_customer_id
import json

class AuditLogger:
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.customer = customer

    async def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: Any,
        user_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an audit action in the system.
        
        Args:
            action: The action performed (e.g., 'create', 'update', 'delete')
            entity_type: The type of entity affected (e.g., 'lead', 'project')
            entity_id: The ID of the affected entity
            user_id: The ID of the user performing the action
            customer_id: The ID of the customer context
            details: Additional details about the action
        """
        from app.models.models import AuditLog  # Import here to avoid circular imports
        
        if not customer_id:
            customer_id = self.customer.id

        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            user_id=user_id,
            customer_id=customer_id,
            details=details or {},
            timestamp=datetime.utcnow()
        )

        self.db.add(audit_log)
        self.db.commit()

    async def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list:
        """
        Retrieve audit logs with optional filtering.
        """
        from app.models.models import AuditLog  # Import here to avoid circular imports
        
        query = self.db.query(AuditLog)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if customer_id:
            query = query.filter(AuditLog.customer_id == customer_id)
        else:
            query = query.filter(AuditLog.customer_id == self.customer.id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        return query.order_by(AuditLog.timestamp.desc()).all()

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_auth_event(
        self,
        user: Optional[User],
        action: str,
        ip_address: str,
        user_agent: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """Log an authentication-related event."""
        audit_log = AuditLog(
            user_id=user.id if user else None,
            customer_id=user.customer_id if user else None,
            action=action,
            entity_type="auth",
            entity_id=user.id if user else None,
            details={
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
                **(details or {})
            }
        )
        self.db.add(audit_log)
        self.db.commit()

    def log_login_success(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        method: str = "password",
        mfa_used: bool = False
    ) -> None:
        """Log successful login."""
        self.log_auth_event(
            user=user,
            action="login_success",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "method": method,
                "mfa_used": mfa_used
            }
        )

    def log_login_failure(
        self,
        email: str,
        ip_address: str,
        user_agent: str,
    def log_login_failure(..., reason: str, customer_id: Optional[str] = None) -> None:
         ...
        self.log_auth_event(
             user=None,
             action="login_failure",
             ip_address=ip_address,
             user_agent=user_agent,
             details={
                 "email": email,
                 "reason": reason
            },
             success=False,
            customer_id=customer_id
         )
        )

    def log_logout(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        session_id: Optional[str] = None
    ) -> None:
        """Log user logout."""
        self.log_auth_event(
            user=user,
            action="logout",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "session_id": session_id
            }
        )

    def log_password_change(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        method: str = "user_initiated"
    ) -> None:
        """Log password change."""
        self.log_auth_event(
            user=user,
            action="password_change",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "method": method
            }
        )

    def log_mfa_verification(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        method: str,
        success: bool
    ) -> None:
        """Log MFA verification attempt."""
        self.log_auth_event(
            user=user,
            action="mfa_verification",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "method": method
            },
            success=success
        )

    def log_session_creation(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> None:
        """Log new session creation."""
        self.log_auth_event(
            user=user,
            action="session_creation",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "session_id": session_id
            }
        )

    def log_session_invalidation(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        session_id: str,
        reason: str
    ) -> None:
        """Log session invalidation."""
        self.log_auth_event(
            user=user,
            action="session_invalidation",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "session_id": session_id,
                "reason": reason
            }
        ) 