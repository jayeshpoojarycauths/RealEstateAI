from datetime import datetime
from typing import Optional, Any, Dict, List
from sqlalchemy.orm import Session
from app.models.models import Customer, AuditLog
from app.shared.core.tenant import get_customer_id

class AuditLogger:
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.customer = customer

    async def get_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get filtered audit logs."""
        query = self.db.query(AuditLog).filter(
            AuditLog.customer_id == self.customer.id
        )

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    async def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log an audit action."""
        log = AuditLog(
            customer_id=self.customer.id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            created_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

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
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        return query.order_by(AuditLog.timestamp.desc()).all() 