import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import Lead, Customer
from app.models.lead import Lead as LeadModel

def test_get_lead_score_distribution(
    client: TestClient,
    db: Session,
    test_customer: Customer,
    test_token_headers: dict
):
    """Test getting lead score distribution."""
    # Create test leads with different scores
    leads = [
        LeadModel(
            name=f"Lead {i}",
            email=f"lead{i}@test.com",
            score=score,
            customer_id=test_customer.id
        )
        for i, score in enumerate([10, 30, 45, 60, 80, 90])
    ]
    db.add_all(leads)
    db.commit()

    response = client.get(
        "/api/v1/stats/lead-score",
        headers=test_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    
    # Check total leads
    assert data["total_leads"] == 6
    
    # Check bucket counts
    buckets = {bucket["range"]: bucket["count"] for bucket in data["buckets"]}
    assert buckets["0-25"] == 1  # Score 10
    assert buckets["26-50"] == 2  # Scores 30, 45
    assert buckets["51-75"] == 1  # Score 60
    assert buckets["76-100"] == 2  # Scores 80, 90

def test_get_lead_score_distribution_no_leads(
    client: TestClient,
    test_token_headers: dict
):
    """Test getting lead score distribution with no leads."""
    response = client.get(
        "/api/v1/stats/lead-score",
        headers=test_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["total_leads"] == 0
    assert all(bucket["count"] == 0 for bucket in data["buckets"])

def test_get_lead_score_distribution_unauthorized(
    client: TestClient
):
    """Test getting lead score distribution without authentication."""
    response = client.get("/api/v1/stats/lead-score")
    assert response.status_code == 401

def test_get_conversion_funnel(
    client: TestClient,
    db: Session,
    test_customer: Customer,
    test_token_headers: dict
):
    """Test getting conversion funnel data."""
    # Create test leads with different statuses
    leads = [
        LeadModel(
            name=f"Lead {i}",
            email=f"lead{i}@test.com",
            status=status,
            customer_id=test_customer.id
        )
        for i, status in enumerate([
            "new", "new", "contacted", "contacted",
            "qualified", "converted", "converted"
        ])
    ]
    db.add_all(leads)
    db.commit()

    response = client.get(
        "/api/v1/stats/conversion-funnel",
        headers=test_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    
    # Check total leads
    assert data["total_leads"] == 7
    
    # Check stage counts and percentages
    stages = {stage["stage"]: stage for stage in data["stages"]}
    
    assert stages["new"]["count"] == 2
    assert stages["new"]["percentage"] == pytest.approx(28.57, 0.01)
    
    assert stages["contacted"]["count"] == 2
    assert stages["contacted"]["percentage"] == pytest.approx(28.57, 0.01)
    
    assert stages["qualified"]["count"] == 1
    assert stages["qualified"]["percentage"] == pytest.approx(14.29, 0.01)
    
    assert stages["converted"]["count"] == 2
    assert stages["converted"]["percentage"] == pytest.approx(28.57, 0.01)

def test_get_conversion_funnel_no_leads(
    client: TestClient,
    test_token_headers: dict
):
    """Test getting conversion funnel data with no leads."""
    response = client.get(
        "/api/v1/stats/conversion-funnel",
        headers=test_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["total_leads"] == 0
    assert len(data["stages"]) == 4  # All stages should be present
    assert all(stage["count"] == 0 and stage["percentage"] == 0.0 
              for stage in data["stages"])

def test_get_conversion_funnel_unauthorized(
    client: TestClient
):
    """Test getting conversion funnel data without authentication."""
    response = client.get("/api/v1/stats/conversion-funnel")
    assert response.status_code == 401 