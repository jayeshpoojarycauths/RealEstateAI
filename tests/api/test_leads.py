import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any
import pandas as pd
from io import BytesIO
import time
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.shared.models.lead import Lead
from app.shared.core.security import create_access_token
from app.shared.core.pagination import PaginationParams
from app.shared.core.exceptions import NotFoundException
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.ai import AIService

client = TestClient(app)

@pytest.fixture
def test_customer(db: Session) -> Customer:
    customer = Customer(
        name="Test Customer",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@pytest.fixture
def test_user(db: Session, test_customer: Customer) -> User:
    user = User(
        email="test@test.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        customer_id=test_customer.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_lead(db: Session, test_customer: Customer) -> Lead:
    lead = Lead(
        name="Test Lead",
        email="lead@test.com",
        phone="+1234567890",
        source="test",
        status="new",
        customer_id=test_customer.id,
        created_at=datetime.utcnow()
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    access_token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(autouse=True)
def cleanup_leads(db: Session):
    """Cleanup leads after each test"""
    yield
    db.query(Lead).delete()
    db.commit()

class TestLeadsEndpoint:
    def test_list_leads_pagination(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        # Create multiple leads
        leads = []
        for i in range(15):
            lead = Lead(
                name=f"Lead {i}",
                email=f"lead{i}@test.com",
                phone=f"+123456789{i}",
                source="test",
                status="new",
                customer_id=test_customer.id
            )
            leads.append(lead)
        db.add_all(leads)
        db.commit()

        # Test first page
        response = client.get("/api/leads/", headers=auth_headers, params={"page": 1, "limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

        # Test second page
        response = client.get("/api/leads/", headers=auth_headers, params={"page": 2, "limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_leads_filtering(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        # Create leads with different statuses and sources
        leads = [
            Lead(name="Lead 1", email="lead1@test.com", status="new", source="website", customer_id=test_customer.id),
            Lead(name="Lead 2", email="lead2@test.com", status="contacted", source="referral", customer_id=test_customer.id),
            Lead(name="Lead 3", email="lead3@test.com", status="qualified", source="website", customer_id=test_customer.id)
        ]
        db.add_all(leads)
        db.commit()

        # Test status filter
        response = client.get("/api/leads/", headers=auth_headers, params={"status": "new"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "new"

        # Test source filter
        response = client.get("/api/leads/", headers=auth_headers, params={"source": "website"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Test search filter
        response = client.get("/api/leads/", headers=auth_headers, params={"search": "Lead 1"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Lead 1"

    def test_create_lead(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        lead_data = {
            "name": "New Lead",
            "email": "new@test.com",
            "phone": "+1234567890",
            "source": "website",
            "status": "new"
        }

        response = client.post("/api/leads/", headers=auth_headers, json=lead_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == lead_data["name"]
        assert data["email"] == lead_data["email"]
        assert data["customer_id"] == test_customer.id

    def test_update_lead(self, db: Session, test_lead: Lead, auth_headers: Dict[str, str]):
        update_data = {
            "name": "Updated Lead",
            "status": "contacted"
        }

        response = client.put(f"/api/leads/{test_lead.id}", headers=auth_headers, json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["status"] == update_data["status"]

    def test_delete_lead(self, db: Session, test_lead: Lead, auth_headers: Dict[str, str]):
        response = client.delete(f"/api/leads/{test_lead.id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify lead is deleted
        lead = db.query(Lead).filter(Lead.id == test_lead.id).first()
        assert lead is None

    def test_customer_isolation(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        # Create another customer and lead
        other_customer = Customer(name="Other Customer")
        db.add(other_customer)
        db.commit()

        other_lead = Lead(
            name="Other Lead",
            email="other@test.com",
            customer_id=other_customer.id
        )
        db.add(other_lead)
        db.commit()

        # Try to access other customer's lead
        response = client.get(f"/api/leads/{other_lead.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_upload_leads(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        # Create test CSV file
        df = pd.DataFrame({
            'name': ['Lead 1', 'Lead 2'],
            'email': ['lead1@test.com', 'lead2@test.com'],
            'phone': ['+1234567890', '+1234567891'],
            'source': ['website', 'referral']
        })
        csv_file = BytesIO()
        df.to_csv(csv_file, index=False)
        csv_file.seek(0)

        response = client.post(
            "/api/leads/upload",
            headers=auth_headers,
            files={"file": ("leads.csv", csv_file, "text/csv")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success_count"] == 2
        assert data["error_count"] == 0

    def test_lead_scoring(self, db: Session, test_lead: Lead, auth_headers: Dict[str, str]):
        response = client.get(f"/api/leads/{test_lead.id}/score", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "scoring_factors" in data

    def test_unauthorized_access(self, db: Session, test_lead: Lead):
        # Test without auth headers
        response = client.get("/api/leads/")
        assert response.status_code == 401

        response = client.get(f"/api/leads/{test_lead.id}")
        assert response.status_code == 401

    def test_forbidden_access(self, db: Session, test_customer: Customer):
        # Create non-superuser user
        user = User(
            email="regular@test.com",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
            customer_id=test_customer.id
        )
        db.add(user)
        db.commit()

        # Create auth token for non-superuser
        access_token = create_access_token(user.id)
        headers = {"Authorization": f"Bearer {access_token}"}

        # Test restricted endpoints
        response = client.get("/api/leads/upload", headers=headers)
        assert response.status_code == 403

    def test_invalid_lead_data(self, db: Session, auth_headers: Dict[str, str]):
        # Test with invalid email
        invalid_data = {
            "name": "Invalid Lead",
            "email": "invalid-email",
            "phone": "+1234567890",
            "source": "website"
        }

        response = client.post("/api/leads/", headers=auth_headers, json=invalid_data)
        assert response.status_code == 422

    def test_lead_interactions(self, db: Session, test_lead: Lead, auth_headers: Dict[str, str]):
        # Test getting interactions
        response = client.get(f"/api/leads/{test_lead.id}/interactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Test creating interaction
        interaction_data = {
            "interaction_type": "call",
            "status": "success",
            "user_input": {"duration": 300}
        }

        response = client.post(
            f"/api/leads/{test_lead.id}/interactions",
            headers=auth_headers,
            json=interaction_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["interaction_type"] == "call"
        assert data["status"] == "success"

    def test_large_dataset_performance(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        """Test performance with large dataset"""
        # Create 500+ leads
        leads = []
        for i in range(550):
            lead = Lead(
                name=f"Lead {i}",
                email=f"lead{i}@test.com",
                phone=f"+123456789{i}",
                source="test",
                status="new",
                customer_id=test_customer.id
            )
            leads.append(lead)
        db.add_all(leads)
        db.commit()

        # Test pagination performance
        start_time = time.time()
        response = client.get("/api/leads/", headers=auth_headers, params={"page": 1, "limit": 100})
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 100
        
        # Assert response time is under 1 second
        assert end_time - start_time < 1.0

        # Test filtering performance
        start_time = time.time()
        response = client.get("/api/leads/", headers=auth_headers, params={"search": "Lead 1"})
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 1.0

    @patch('app.services.lead.LeadService.list_leads')
    def test_db_failure_handling(self, mock_list_leads, db: Session, auth_headers: Dict[str, str]):
        """Test handling of database failures"""
        # Simulate database error
        mock_list_leads.side_effect = SQLAlchemyError("Database connection failed")
        
        response = client.get("/api/leads/", headers=auth_headers)
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]

    def test_malformed_upload_file(self, db: Session, auth_headers: Dict[str, str]):
        """Test handling of malformed upload files"""
        # Create malformed CSV
        malformed_csv = BytesIO(b"invalid,csv,data\n1,2,3")
        
        response = client.post(
            "/api/leads/upload",
            headers=auth_headers,
            files={"file": ("leads.csv", malformed_csv, "text/csv")}
        )
        assert response.status_code == 400
        assert "Invalid file format" in response.json()["detail"]

    @patch('app.services.ai.AIService.score_lead')
    def test_ai_scoring_failure(self, mock_score_lead, db: Session, test_lead: Lead, auth_headers: Dict[str, str]):
        """Test handling of AI scoring failures"""
        # Simulate AI service failure
        mock_score_lead.side_effect = Exception("AI service unavailable")
        
        response = client.get(f"/api/leads/{test_lead.id}/score", headers=auth_headers)
        assert response.status_code == 500
        assert "AI service error" in response.json()["detail"]

    def test_upload_timeout(self, db: Session, auth_headers: Dict[str, str]):
        """Test handling of upload timeouts"""
        # Create large CSV file
        df = pd.DataFrame({
            'name': ['Lead ' + str(i) for i in range(1000)],
            'email': ['lead' + str(i) + '@test.com' for i in range(1000)],
            'phone': ['+123456789' + str(i) for i in range(1000)],
            'source': ['website'] * 1000
        })
        csv_file = BytesIO()
        df.to_csv(csv_file, index=False)
        csv_file.seek(0)

        with patch('app.services.lead.LeadService.process_upload', side_effect=TimeoutError("Upload timeout")):
            response = client.post(
                "/api/leads/upload",
                headers=auth_headers,
                files={"file": ("leads.csv", csv_file, "text/csv")}
            )
            assert response.status_code == 504
            assert "Upload timeout" in response.json()["detail"]

    def test_concurrent_lead_creation(self, db: Session, test_customer: Customer, auth_headers: Dict[str, str]):
        """Test concurrent lead creation handling"""
        import threading
        
        def create_lead():
            lead_data = {
                "name": f"Concurrent Lead {threading.get_ident()}",
                "email": f"concurrent{threading.get_ident()}@test.com",
                "phone": f"+123456789{threading.get_ident()}",
                "source": "test",
                "status": "new"
            }
            response = client.post("/api/leads/", headers=auth_headers, json=lead_data)
            assert response.status_code == 200

        # Create 10 threads to create leads concurrently
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_lead)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all leads were created
        leads = db.query(Lead).filter(Lead.customer_id == test_customer.id).all()
        assert len(leads) >= 10

    def test_lead_validation_edge_cases(self, db: Session, auth_headers: Dict[str, str]):
        """Test edge cases in lead validation"""
        test_cases = [
            {
                "data": {
                    "name": "A" * 256,  # Exceeds max length
                    "email": "valid@test.com",
                    "phone": "+1234567890"
                },
                "expected_status": 422
            },
            {
                "data": {
                    "name": "Test Lead",
                    "email": "test@test.com",
                    "phone": "invalid-phone"  # Invalid phone format
                },
                "expected_status": 422
            },
            {
                "data": {
                    "name": "Test Lead",
                    "email": "test@test.com",
                    "phone": "+1234567890",
                    "status": "invalid_status"  # Invalid status
                },
                "expected_status": 422
            }
        ]

        for test_case in test_cases:
            response = client.post("/api/leads/", headers=auth_headers, json=test_case["data"])
            assert response.status_code == test_case["expected_status"]

    def test_lead_update_conflicts(self, db: Session, test_lead: Lead, auth_headers: Dict[str, str]):
        """Test handling of concurrent lead updates"""
        # Simulate concurrent update
        update_data1 = {"name": "Update 1", "status": "contacted"}
        update_data2 = {"name": "Update 2", "status": "qualified"}

        # First update
        response1 = client.put(f"/api/leads/{test_lead.id}", headers=auth_headers, json=update_data1)
        assert response1.status_code == 200

        # Second update
        response2 = client.put(f"/api/leads/{test_lead.id}", headers=auth_headers, json=update_data2)
        assert response2.status_code == 200

        # Verify final state
        response = client.get(f"/api/leads/{test_lead.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data2["name"]
        assert data["status"] == update_data2["status"] 