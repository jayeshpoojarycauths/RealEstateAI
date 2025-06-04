import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.models import User, Customer, Lead
from app.shared.core.security.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def test_customer(db: Session) -> Customer:
    customer = Customer(
        name="Test Customer",
        domain="test.com"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@pytest.fixture
def test_user(db: Session, test_customer: Customer) -> User:
    user = User(
        email="test@test.com",
        password_hash="hashed_password",
        customer_id=test_customer.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user: User):
    access_token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def test_leads(db: Session, test_customer: Customer):
    leads = []
    for i in range(5):
        score = i * 20
        lead = Lead(
            name=f"Lead {i}",
            email=f"lead{i}@test.com",
            score=score,
            customer_id=test_customer.id
        )
        db.add(lead)
        leads.append(lead)
    db.commit()
    return leads

class TestAnalyticsEndpoint:
    def test_lead_score_distribution(self, db: Session, test_customer: Customer, auth_headers, test_leads):
        response = client.get("/api/v1/analytics/lead-scores/distribution", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "distribution" in data
        assert len(data["distribution"]) == 5

    def test_customer_isolation(self, db: Session, test_customer: Customer, auth_headers):
        # Create another customer with leads
        other_customer = Customer(name="Other Customer", domain="other.com")
        db.add(other_customer)
        db.commit()

        # Create leads for other customer
        for i in range(3):
            lead = Lead(
                name=f"Other Lead {i}",
                email=f"other{i}@test.com",
                score=50,
                customer_id=other_customer.id
            )
            db.add(lead)
        db.commit()

        # Get distribution for first customer
        response = client.get("/api/v1/analytics/lead-scores/distribution", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_leads"] == 0  # No leads in first customer

    def test_unauthorized_access(self, db: Session):
        response = client.get("/api/v1/analytics/lead-scores/distribution")
        assert response.status_code == 401

    def test_empty_distribution(self, db: Session, test_customer: Customer, auth_headers):
        response = client.get("/api/v1/analytics/lead-scores/distribution", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "distribution" in data
        assert len(data["distribution"]) == 0 