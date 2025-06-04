from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.models.audit import AuditLog
from app.shared.core.tenant import get_customer_id
import json
from fastapi import Depends, Request
from app.shared.db.session import get_db
from app.shared.core.security import get_current_user

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
    ) -> AuditLog:
        """Log an audit action in the system."""
        if not customer_id:
            customer_id = self.customer.id

        audit_log = AuditLog(
            action=action,
            resource_type=entity_type,
            resource_id=str(entity_id),
            user_id=user_id,
            customer_id=customer_id,
            details=details or {},
            timestamp=datetime.utcnow()
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    async def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Retrieve audit logs with optional filtering."""
        query = self.db.query(AuditLog)

        if entity_type:
            query = query.filter(AuditLog.resource_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.resource_id == entity_id)
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

        return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

class AuditService:
    """Service for handling audit logging."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit action.
        
        Args:
            action: The action performed
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            user_id: Optional ID of user performing action
            details: Optional additional details
            ip_address: Optional IP address
            user_agent: Optional user agent
            
        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log

    def log_auth_event(
        self,
        user: Optional[User],
        action: str,
        metadata: Dict[str, Any],
        customer_id: Optional[str] = None
    ) -> None:
        """Log authentication event."""
        log = AuditLog(
            user_id=user.id if user else None,
            action=action,
            resource_type="auth",
            resource_id="system",
            details=metadata,
            customer_id=customer_id,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

    def log_login_success(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
    ) -> None:
        """Log successful login attempt."""
        self.log_auth_event(
            user=user,
            action="login_success",
            metadata={
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )

    def log_login_failure(
        self,
        email: str,
        ip_address: str,
        user_agent: str,
        reason: str,
        customer_id: Optional[str] = None
    ) -> None:
        """Log failed login attempt."""
        self.log_auth_event(
            user=None,
            action="login_failure",
            metadata={
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "reason": reason
            },
            customer_id=customer_id
        )

    def log_logout(
        self,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> None:
        """Log user logout."""
        self.log_auth_event(
            user=user,
            action="logout",
            metadata={
                "ip_address": ip_address,
                "user_agent": user_agent
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
            metadata={
                "method": method,
                "ip_address": ip_address,
                "user_agent": user_agent
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
            metadata={
                "method": method,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
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
            metadata={
                "session_id": session_id,
                "ip_address": ip_address,
                "user_agent": user_agent
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
            metadata={
                "session_id": session_id,
                "reason": reason,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )

def get_audit_service(
    db: Session = Depends(get_db)
) -> AuditService:
    """Get audit service instance."""
    return AuditService(db)

async def log_audit(
    request: Request,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> AuditLog:
    """
    Log an audit action with request context.
    
    Args:
        request: FastAPI request object
        action: The action performed
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        details: Optional additional details
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created AuditLog instance
    """
    audit_service = AuditService(db)
    
    return audit_service.log_action(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=current_user.id if current_user else None,
        details=details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

__all__ = ['AuditService', 'get_audit_service', 'log_audit'] 