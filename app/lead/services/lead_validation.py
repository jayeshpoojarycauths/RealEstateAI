from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError

from app.models.models import Lead, User, Customer
from app.lead.schemas.lead import LeadCreate, LeadUpdate
from app.shared.core.tenant import get_customer_id
from app.shared.core.security import UserRole

class LeadValidationService:
    def __init__(self, db: Session):
        self.db = db

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        try:
            # Remove any non-digit characters
            phone = re.sub(r'\D', '', phone)
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone, None)
            # Check if it's a valid number
            return phonenumbers.is_valid_number(parsed_number)
        except Exception:
            return False

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    def validate_lead_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate lead data and return list of errors"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")

        # Phone validation
        if data.get('phone') and not self.validate_phone(data['phone']):
            errors.append("Invalid phone number format")

        # Email validation
        if data.get('email') and not self.validate_email(data['email']):
            errors.append("Invalid email format")

        # Budget validation
        if data.get('budget'):
            try:
                budget = float(data['budget'])
                if budget < 0:
                    errors.append("Budget cannot be negative")
            except ValueError:
                errors.append("Invalid budget format")

        return errors

    def validate_lead_update(self, lead: Lead, update_data: LeadUpdate) -> List[str]:
        """Validate lead update data"""
        errors = []
        
        # Phone validation
        if update_data.phone and not self.validate_phone(update_data.phone):
            errors.append("Invalid phone number format")

        # Email validation
        if update_data.email and not self.validate_email(update_data.email):
            errors.append("Invalid email format")

        # Budget validation
        if update_data.budget is not None:
            try:
                budget = float(update_data.budget)
                if budget < 0:
                    errors.append("Budget cannot be negative")
            except ValueError:
                errors.append("Invalid budget format")

        return errors

    def validate_lead_import(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of leads for import"""
        results = {
            "valid": [],
            "invalid": [],
            "errors": []
        }

        for index, lead_data in enumerate(leads, 1):
            errors = self.validate_lead_data(lead_data)
            if errors:
                results["invalid"].append(lead_data)
                results["errors"].append(f"Row {index}: {', '.join(errors)}")
            else:
                results["valid"].append(lead_data)

        return results

# ... existing code ... 