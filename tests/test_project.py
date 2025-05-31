import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import Project, ProjectLead, Lead
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectType, ProjectStatus
from app.services.project import ProjectService
from app.core.pagination import PaginationParams

@pytest.fixture
def project_service(db_session: Session):
    return ProjectService(db_session)

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

@pytest.fixture
def test_lead(db_session: Session, test_customer):
    lead = Lead(
        name="Test Lead",
        email="test@example.com",
        phone="1234567890",
        source="website",
        status="active",
        customer_id=test_customer.id
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead

class TestProjectService:
    async def test_create_project(self, project_service: ProjectService, test_customer):
        project_data = ProjectCreate(
            name="New Project",
            description="New Description",
            type=ProjectType.COMMERCIAL,
            status=ProjectStatus.PLANNING,
            location="New Location",
            total_units=50,
            price_range="50L-1Cr",
            amenities=["Parking", "Security"]
        )
        
        project = await project_service.create_project(project_data, test_customer.id)
        
        assert project.name == project_data.name
        assert project.type == project_data.type
        assert project.customer_id == test_customer.id

    async def test_get_project(self, project_service: ProjectService, test_project, test_customer):
        project = await project_service.get_project(test_project.id, test_customer.id)
        
        assert project is not None
        assert project.id == test_project.id
        assert project.name == test_project.name

    async def test_update_project(self, project_service: ProjectService, test_project, test_customer):
        update_data = ProjectUpdate(
            name="Updated Project",
            status=ProjectStatus.IN_PROGRESS
        )
        
        updated_project = await project_service.update_project(
            test_project.id, update_data, test_customer.id
        )
        
        assert updated_project.name == update_data.name
        assert updated_project.status == update_data.status

    async def test_delete_project(self, project_service: ProjectService, test_project, test_customer):
        success = await project_service.delete_project(test_project.id, test_customer.id)
        
        assert success is True
        deleted_project = await project_service.get_project(test_project.id, test_customer.id)
        assert deleted_project is None

    async def test_list_projects(self, project_service: ProjectService, test_project, test_customer):
        pagination = PaginationParams(page=1, limit=10)
        filters = {"status": ProjectStatus.PLANNING}
        
        projects = await project_service.list_projects(
            test_customer.id, pagination, filters
        )
        
        assert len(projects) > 0
        assert projects[0].id == test_project.id

    async def test_get_project_stats(self, project_service: ProjectService, test_project, test_lead, test_customer):
        # Assign lead to project
        project_lead = ProjectLead(project_id=test_project.id, lead_id=test_lead.id)
        project_service.db.add(project_lead)
        project_service.db.commit()
        
        stats = await project_service.get_project_stats(test_project.id, test_customer.id)
        
        assert stats is not None
        assert stats.total_leads == 1
        assert stats.active_leads == 1

    async def test_get_project_analytics(self, project_service: ProjectService, test_project, test_lead, test_customer):
        # Assign lead to project
        project_lead = ProjectLead(project_id=test_project.id, lead_id=test_lead.id)
        project_service.db.add(project_lead)
        project_service.db.commit()
        
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        analytics = await project_service.get_project_analytics(
            test_project.id, test_customer.id, start_date, end_date
        )
        
        assert analytics is not None
        assert len(analytics.lead_trends) > 0
        assert len(analytics.status_distribution) > 0

    async def test_assign_lead(self, project_service: ProjectService, test_project, test_lead, test_customer):
        success = await project_service.assign_lead(
            test_project.id, test_lead.id, test_customer.id
        )
        
        assert success is True
        
        # Verify assignment
        project_lead = project_service.db.query(ProjectLead).filter(
            ProjectLead.project_id == test_project.id,
            ProjectLead.lead_id == test_lead.id
        ).first()
        
        assert project_lead is not None

    async def test_remove_lead(self, project_service: ProjectService, test_project, test_lead, test_customer):
        # First assign the lead
        await project_service.assign_lead(test_project.id, test_lead.id, test_customer.id)
        
        # Then remove it
        success = await project_service.remove_lead(
            test_project.id, test_lead.id, test_customer.id
        )
        
        assert success is True
        
        # Verify removal
        project_lead = project_service.db.query(ProjectLead).filter(
            ProjectLead.project_id == test_project.id,
            ProjectLead.lead_id == test_lead.id
        ).first()
        
        assert project_lead is None 