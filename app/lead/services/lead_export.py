from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import logging
import pandas as pd
import json

from app.lead.models.lead import Lead
from app.lead.schemas.lead import LeadFilter, LeadCreate, LeadUpdate
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole

logger = logging.getLogger(__name__)

class LeadExportService:
    def __init__(self, db: Session):
        self.db = db

    def export_leads_to_csv(self, leads: List[Lead], file_path: str) -> None:
        """Export leads to a CSV file."""
        try:
            # Convert leads to DataFrame
            data = []
            for lead in leads:
                data.append({
                    'name': lead.name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'source': lead.source,
                    'status': lead.status,
                    'notes': lead.notes,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None,
                    'updated_at': lead.updated_at.isoformat() if lead.updated_at else None
                })
            
            df = pd.DataFrame(data)
            
            # Export to CSV
            df.to_csv(file_path, index=False)
            logger.info(f"Exported {len(leads)} leads to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting leads to CSV: {str(e)}")
            raise

    def export_leads_to_json(self, leads: List[Lead], file_path: str) -> None:
        """Export leads to a JSON file."""
        try:
            # Convert leads to list of dictionaries
            data = []
            for lead in leads:
                data.append({
                    'name': lead.name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'source': lead.source,
                    'status': lead.status,
                    'notes': lead.notes,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None,
                    'updated_at': lead.updated_at.isoformat() if lead.updated_at else None
                })
            
            # Export to JSON
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported {len(leads)} leads to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting leads to JSON: {str(e)}")
            raise 