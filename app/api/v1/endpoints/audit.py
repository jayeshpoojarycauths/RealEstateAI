from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.core.deps import get_current_active_user
from app.core.audit import AuditLogger
from app.schemas.audit import AuditLogResponse, AuditLogFilter, AuditLogCreate
from app.models.models import Customer, AuditLog, User
from app.core.pagination import PaginationParams, get_pagination_params

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Get audit logs for the current customer."""
    logs = db.query(AuditLog).filter(
        AuditLog.customer_id == current_customer.id
    ).offset(pagination.skip).limit(pagination.limit).all()
    return logs

@router.post("/", response_model=AuditLogResponse)
async def create_audit_log(
    *,
    db: Session = Depends(deps.get_db),
    log_in: AuditLogCreate,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Create a new audit log entry."""
    log = AuditLog(
        **log_in.dict(),
        customer_id=current_customer.id,
        user_id=current_user.id
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/logs/", response_model=List[AuditLogResponse])
async def get_audit_logs_filtered(
    *,
    db: Session = Depends(deps.get_db),
    current_tenant: Customer = Depends(deps.get_current_customer),
    filter: AuditLogFilter = Depends()
) -> List[AuditLogResponse]:
    """
    Retrieve audit logs with filtering.
    Only accessible by superusers.
    """
    if not deps.get_current_active_superuser():
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    audit_logger = AuditLogger(db, current_tenant)
    logs = await audit_logger.get_logs(
        resource_type=filter.resource_type,
        resource_id=filter.resource_id,
        action=filter.action,
        start_date=filter.start_date,
        end_date=filter.end_date,
        user_id=filter.user_id,
        skip=filter.skip,
        limit=filter.limit
    )
    return logs 