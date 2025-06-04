import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.shared.core.security import create_access_token, UserRole
from app.shared.core.exceptions import NotFoundException
from app.shared.core.pagination import PaginationParams
from app.project.models import Project
from app.project.schemas import ProjectType, ProjectStatus

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token():
    return create_access_token(
        data={"sub": "admin@example.com", "roles": [UserRole.ADMIN]}
    )

@pytest.fixture
def manager_token():
    return create_access_token(
        data={"sub": "manager@example.com", "roles": [UserRole.MANAGER]}
    )

@pytest.fixture
def agent_token():
    return create_access_token(
        data={"sub": "agent@example.com", "roles": [UserRole.AGENT]}
    )

@pytest.fixture
def viewer_token():
    return create_access_token(
        data={"sub": "viewer@example.com", "roles": [UserRole.VIEWER]}
    )

@pytest.fixture
def test_project(db_session: Session, test_customer):
    project = Project(
        name="Test Project",
        description="Test Description",
        type=ProjectType.RESIDENTIAL,
        status=ProjectStatus.PLANNING,
        location="Test Location",
        total_units=100,
        price_range="10L-50L",
        amenities=["Pool", "Gym"],
        customer_id=test_customer.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

class TestProjectEndpoints:
    def test_list_projects(self, client, viewer_token, test_project):
        response = client.get(
            "/api/v1/projects/",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == test_project.name

    def test_create_project(self, client, manager_token):
        project_data = {
            "name": "New Project",
            "description": "New Description",
            "type": "residential",
            "status": "planning",
            "location": "New Location",
            "total_units": 50,
            "price_range": "50L-1Cr",
            "amenities": ["Parking", "Security"]
        }
        response = client.post(
            "/api/v1/projects/",
            json=project_data,
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]

    def test_get_project(self, client, viewer_token, test_project):
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_project.name

    def test_update_project(self, client, manager_token, test_project):
        update_data = {
            "name": "Updated Project",
            "status": "in_progress"
        }
        response = client.put(
            f"/api/v1/projects/{test_project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["status"] == update_data["status"]

    def test_delete_project(self, client, admin_token, test_project):
        response = client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

    def test_get_project_stats(self, client, viewer_token, test_project):
        response = client.get(
            f"/api/v1/projects/{test_project.id}/stats",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert "conversion_rate" in data

    def test_get_project_analytics(self, client, viewer_token, test_project):
        response = client.get(
            f"/api/v1/projects/{test_project.id}/analytics",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "lead_trends" in data
        assert "status_distribution" in data

    def test_assign_lead_to_project(self, client, agent_token, test_project, test_lead):
        response = client.post(
            f"/api/v1/projects/{test_project.id}/leads/{test_lead.id}",
            headers={"Authorization": f"Bearer {agent_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Lead assigned successfully"

    def test_remove_lead_from_project(self, client, agent_token, test_project, test_lead):
        response = client.delete(
            f"/api/v1/projects/{test_project.id}/leads/{test_lead.id}",
            headers={"Authorization": f"Bearer {agent_token}"}
        )
        assert response.status_code == 204

    def test_unauthorized_access(self, client, test_project):
        # Test without token
        response = client.get(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == 401

        # Test with insufficient permissions
        response = client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 403

    def test_invalid_project_id(self, client, viewer_token):
        response = client.get(
            "/api/v1/projects/999999",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 404

    def test_invalid_request_data(self, client, manager_token):
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "type": "invalid_type"  # Invalid project type
        }
        response = client.post(
            "/api/v1/projects/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 422 