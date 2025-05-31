import pandas as pd
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from fastapi import UploadFile, HTTPException
from datetime import datetime, timedelta
import json

from app.models.models import Lead, User, Customer
from app.lead.models.lead_activity import LeadActivity
from app.lead.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadFilter,
    LeadStats,
    LeadActivityCreate,
    LeadActivityResponse
)
from app.lead.services.lead_audit import LeadAuditService
from app.lead.services.lead_validation import LeadValidationService
from app.lead.services.lead_notification import LeadNotificationService
from app.lead.services.lead_import import LeadImportService
from app.lead.services.lead_export import LeadExportService
from app.lead.services.lead_analytics import LeadAnalyticsService
from app.lead.services.lead_workflow import LeadWorkflowService
from app.outreach.services.outreach import OutreachService
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole
from app.shared.core.pagination import PaginationParams
from app.services.ai import AIService
import logging

logger = logging.getLogger(__name__)

class LeadService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    # --- Consolidated Upload Logic ---
    def validate_lead_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate lead data and return list of errors if any."""
        errors = []
        required_fields = ['name', 'phone', 'email', 'location']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        if data.get('email') and '@' not in data['email']:
            errors.append("Invalid email format")
        if data.get('phone') and not str(data['phone']).isdigit():
            errors.append("Phone number should contain only digits")
        if data.get('budget') and not isinstance(data['budget'], (int, float, str)):
            errors.append("Budget should be a number or string")
        return errors

    def process_upload(self, file_path: str, customer_id: int) -> Dict[str, Any]:
        """Process uploaded file and create leads (sync version for batch jobs)."""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            total_leads = len(df)
            successful_leads = 0
            failed_leads = 0
            errors = []
            for index, row in df.iterrows():
                lead_data = row.to_dict()
                lead_data['customer_id'] = customer_id
                validation_errors = self.validate_lead_data(lead_data)
                if validation_errors:
                    failed_leads += 1
                    errors.append(f"Row {index + 2}: {', '.join(validation_errors)}")
                    continue
                try:
                    lead = Lead(
                        name=lead_data['name'],
                        phone=lead_data['phone'],
                        email=lead_data['email'],
                        location=lead_data['location'],
                        budget=lead_data.get('budget'),
                        property_type=lead_data.get('property_type'),
                        customer_id=customer_id,
                        created_at=datetime.utcnow()
                    )
                    self.db.add(lead)
                    successful_leads += 1
                except Exception as e:
                    failed_leads += 1
                    errors.append(f"Row {index + 2}: {str(e)}")
            self.db.commit()
            return {
                "total_leads": total_leads,
                "successful_leads": successful_leads,
                "failed_leads": failed_leads,
                "errors": errors
            }
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            raise

    def get_upload_template(self) -> pd.DataFrame:
        """Return a template DataFrame for lead uploads."""
        template_data = {
            'name': ['John Doe'],
            'phone': ['1234567890'],
            'email': ['john@example.com'],
            'location': ['Mumbai'],
            'budget': [5000000],
            'property_type': ['Apartment'],
            'notes': ['Interested in 2BHK']
        }
        return pd.DataFrame(template_data)

    async def upload_leads(self, file: UploadFile, customer_id: int) -> List[Lead]:
        """
        Upload and process leads from CSV/Excel file (async version for API).
        """
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
        leads = []
        for _, row in df.iterrows():
            lead_data = LeadCreate(
                name=row.get('name'),
                email=row.get('email'),
                phone=row.get('phone'),
                source=row.get('source', 'csv_upload'),
                status=row.get('status', 'new'),
                notes=row.get('notes', ''),
                customer_id=customer_id
            )
            lead = await self.create_lead(lead_data, customer_id)
            enriched_data = await self.ai_service.enrich_lead(lead)
            if enriched_data:
                lead = await self.update_lead(lead.id, enriched_data, customer_id)
            await self.outreach_service.trigger_outreach(lead)
            leads.append(lead)
        return leads

    # --- Existing CRUD and Query Logic (unchanged) ---
    async def list_leads(
        self,
        customer_id: int,
        pagination: PaginationParams,
        filters: LeadFilter
    ) -> List[Lead]:
        query = self.db.query(Lead).filter(Lead.customer_id == customer_id)
        if filters.status:
            query = query.filter(Lead.status == filters.status)
        if filters.source:
            query = query.filter(Lead.source == filters.source)
        if filters.search:
            search = f"%{filters.search}%"
            query = query.filter(
                (Lead.name.ilike(search)) |
                (Lead.email.ilike(search)) |
                (Lead.phone.ilike(search))
            )
        query = query.offset(pagination.offset).limit(pagination.limit)
        return query.all()

    async def create_lead(self, lead: LeadCreate, customer_id: int) -> Lead:
        # Check for duplicate email for this customer
        if lead.email:
            existing = self.db.query(Lead).filter(Lead.email == lead.email, Lead.customer_id == customer_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="A lead with this email already exists.")
        db_lead = Lead(**lead.dict(), customer_id=customer_id)
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    async def get_lead(self, lead_id: int, customer_id: int) -> Optional[Lead]:
        return self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.customer_id == customer_id
        ).first()

    async def update_lead(
        self,
        lead_id: int,
        lead: LeadUpdate,
        customer_id: int
    ) -> Optional[Lead]:
        db_lead = await self.get_lead(lead_id, customer_id)
        if not db_lead:
            return None
        for key, value in lead.dict(exclude_unset=True).items():
            setattr(db_lead, key, value)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    async def delete_lead(self, lead_id: int, customer_id: int) -> bool:
        db_lead = await self.get_lead(lead_id, customer_id)
        if not db_lead:
            return False
        self.db.delete(db_lead)
        self.db.commit()
        return True

    def bulk_upload_leads(self, df, customer_id, db):
        """
        Bulk upload leads from a DataFrame. Matches by email: updates if found, creates if not.
        Sets customer_id and created_at/updated_at as appropriate.
        """
        created, updated, errors = 0, 0, []
        
        for idx, row in df.iterrows():
            try:
                email = str(row.get("email", "")).strip().lower()
                name = str(row.get("name", "")).strip()
                
                if not name:
                    errors.append(f"Row {idx+2}: Missing name.")
                    continue
                    
                # Split name into first and last name
                name_parts = name.split()
                first_name = name_parts[0] if name_parts else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                lead = db.query(Lead).filter(
                    Lead.email == email,
                    Lead.customer_id == customer_id
                ).first()
                
                now = datetime.utcnow()
                
                if lead:
                    # Update existing lead
                    for col in df.columns:
                        if hasattr(lead, col) and col in row:
                            setattr(lead, col, row[col])
                    lead.updated_at = now
                    lead.first_name = first_name
                    lead.last_name = last_name
                    updated += 1
                else:
                    # Create new lead
                    lead_data = {
                        "name": name,
                        "email": email,
                        "customer_id": customer_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "created_at": now,
                        "updated_at": now
                    }
                    # Add other fields if present
                    for col in df.columns:
                        if col not in ["name", "email", "customer_id"] and hasattr(Lead, col):
                            lead_data[col] = row[col]
                    
                    lead = Lead(**lead_data)
                    db.add(lead)
                    created += 1
                    
                db.commit()
                
            except Exception as e:
                db.rollback()
                errors.append(f"Row {idx+2}: {str(e)}")
                
        return {
            "created": created,
            "updated": updated,
            "errors": errors
        } 