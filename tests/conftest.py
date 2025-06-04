import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.shared.db.base import Base
from app.shared.core.config import Settings
from app.models.models import User, Customer, Role, Permission, ScrapingConfig
from datetime import datetime
import uuid
from app.shared.core.config import settings
from app.db.session import get_db
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from app.main import app
from app.shared.db.session import SessionLocal
from app.shared.core.security import create_access_token
from app.shared.models.user import User
from app.shared.models.customer import Customer

# Create test settings instance
test_settings = Settings(
    _env_file=".env.test",  # Use test environment file
    POSTGRES_DB="test_db",  # Override database name for tests
    DB_ECHO=False  # Disable SQL echo during tests
)

# Create test database engine
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create a test client with a database session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_customer(db):
    customer = Customer(
        id=str(uuid.uuid4()),
        name="Test Company",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(customer)
    db.commit()
    return customer

@pytest.fixture
def test_user(db, test_customer):
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        customer_id=test_customer.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def test_role(db, test_customer):
    role = Role(
        id=str(uuid.uuid4()),
        name="Test Role",
        description="Test Role Description",
        customer_id=test_customer.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(role)
    db.commit()
    return role

@pytest.fixture
def test_permission(db):
    permission = Permission(
        id=str(uuid.uuid4()),
        name="test_permission",
        description="Test Permission",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(permission)
    db.commit()
    return permission

@pytest.fixture
def test_scraping_config(db, test_customer):
    config = ScrapingConfig(
        id=str(uuid.uuid4()),
        customer_id=test_customer.id,
        enabled_sources=["magicbricks", "housing", "proptiger", "commonfloor"],
        locations=["Mumbai", "Delhi"],
        property_types=["Apartment", "Villa"],
        max_pages_per_source=2,
        scraping_delay=1,
        rate_limit=10,
        retry_count=3,
        timeout=30,
        proxy_enabled=False,
        proxy_url=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(config)
    db.commit()
    return config

@pytest.fixture
def test_mfa_settings(db, test_user):
    from app.auth.models.auth import MFASettings
    mfa_settings = MFASettings(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        is_enabled=True,
        secret_key="test_secret_key",
        backup_codes=["code1", "code2"],
        preferred_method="totp",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(mfa_settings)
    db.commit()
    return mfa_settings

@pytest.fixture
def test_outreach(db, test_user, test_customer):
    from app.outreach.models.outreach import Outreach
    outreach = Outreach(
        id=str(uuid.uuid4()),
        customer_id=test_customer.id,
        user_id=test_user.id,
        channel="email",
        status="scheduled",
        subject="Test Subject",
        content="Test Content",
        scheduled_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(outreach)
    db.commit()
    return outreach

@pytest.fixture
def test_project(db, test_customer):
    from app.project.models.project import Project
    project = Project(
        id=str(uuid.uuid4()),
        customer_id=test_customer.id,
        name="Test Project",
        description="Test Project Description",
        status="active",
        total_value=1000000,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(project)
    db.commit()
    return project

@pytest.fixture
def mock_settings():
    return {
        "PROJECT_NAME": "Real Estate CRM",
        "VERSION": "1.0.0",
        "API_V1_STR": "/api/v1",
        "BACKEND_CORS_ORIGINS": ["http://localhost:3000"],
        "SECRET_KEY": "test_secret_key",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "DATABASE_URL": test_settings.get_database_url
    } 