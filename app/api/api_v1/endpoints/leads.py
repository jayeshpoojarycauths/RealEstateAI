from fastapi import Response, Query
import csv
from io import StringIO
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import deps
from app.models.lead import Lead

router = APIRouter()

@router.get("/leads/export")
def export_leads(
    status: str = Query(None),
    assigned_to: str = Query(None),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    query = db.query(Lead).filter(Lead.customer_id == current_user.customer_id)
    if status:
        query = query.filter(Lead.status == status)
    if assigned_to:
        query = query.filter(Lead.assigned_to == assigned_to)
    leads = query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "phone", "status", "assigned_to", "created_at"])
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.name,
            lead.email,
            lead.phone,
            lead.status,
            lead.assigned_to,
            lead.created_at
        ])
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    ) 