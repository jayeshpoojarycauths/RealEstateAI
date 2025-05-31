from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Customer
from app.shared.core.tenant import get_customer_id

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