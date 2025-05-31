from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
from app.models.models import Lead, User, Customer
from app.lead.schemas.lead import LeadCreate, LeadUpdate
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole

logger = logging.getLogger(__name__)

class LeadImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_leads_from_csv(self, file_path: str, customer_id: int) -> List[Lead]:
        """Import leads from a CSV file."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['name', 'email', 'phone']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Clean and validate data
            df = self._clean_data(df)
            
            # Import leads
            leads = []
            for _, row in df.iterrows():
                lead_data = LeadCreate(
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    source=row.get('source', 'csv_import'),
                    status=row.get('status', 'new'),
                    notes=row.get('notes', ''),
                    customer_id=customer_id
                )
                
                lead = Lead(**lead_data.dict())
                self.db.add(lead)
                leads.append(lead)
            
            self.db.commit()
            return leads
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing leads from CSV: {str(e)}")
            raise

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate lead data."""
        # Remove duplicates
        df = df.drop_duplicates(subset=['email', 'phone'])
        
        # Clean phone numbers
        df['phone'] = df['phone'].apply(self._clean_phone)
        
        # Clean email addresses
        df['email'] = df['email'].str.lower().str.strip()
        
        # Fill missing values
        df = df.fillna({
            'source': 'csv_import',
            'status': 'new',
            'notes': ''
        })
        
        return df

    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number."""
        if pd.isna(phone):
            return None
            
        # Remove non-numeric characters
        phone = ''.join(filter(str.isdigit, str(phone)))
        
        # Add country code if missing
        if len(phone) == 10:
            phone = '1' + phone
            
        return phone 