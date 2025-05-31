from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import ScrapedLead
from datetime import datetime
import uuid

def get_scraped_leads(db: Session, customer_id: str, lead_type: Optional[str] = None) -> List[ScrapedLead]:
    q = db.query(ScrapedLead).filter(ScrapedLead.customer_id == customer_id)
    if lead_type:
        q = q.filter(ScrapedLead.lead_type == lead_type)
    return q.order_by(ScrapedLead.created_at.desc()).all()

def get_scraped_lead(db: Session, customer_id: str, id: str) -> Optional[ScrapedLead]:
    return db.query(ScrapedLead).filter(ScrapedLead.customer_id == customer_id, ScrapedLead.id == id).first()

def create_scraped_lead(db: Session, customer_id: str, lead_type: str, data: Dict[str, Any], source: str) -> ScrapedLead:
    db_lead = ScrapedLead(
        id=uuid.uuid4(),
        customer_id=customer_id,
        lead_type=lead_type,
        data=data,
        source=source,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def update_scraped_lead(db: Session, customer_id: str, id: str, update_data: Dict[str, Any]) -> Optional[ScrapedLead]:
    db_lead = get_scraped_lead(db, customer_id, id)
    if not db_lead:
        return None
    for field, value in update_data.items():
        setattr(db_lead, field, value)
    db_lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_lead)
    return db_lead

def delete_scraped_lead(db: Session, customer_id: str, id: str) -> bool:
    db_lead = get_scraped_lead(db, customer_id, id)
    if not db_lead:
        return False
    db.delete(db_lead)
    db.commit()
    return True

def save_scraped_leads(db: Session, customer_id: str, lead_type: str, source: str, leads: List[Dict[str, Any]]):
    for lead in leads:
        db_lead = ScrapedLead(
            id=uuid.uuid4(),
            customer_id=customer_id,
            lead_type=lead_type,
            data=lead,
            source=source,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_lead)
    db.commit() 