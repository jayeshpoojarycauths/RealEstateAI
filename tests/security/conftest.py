import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.shared.core.config import settings
from app.shared.db.base import Base
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.core.security.jwt import jwt_service
from app.shared.core.security import verify_password, get_password_hash

# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db):
    """Create a fresh database session for each test"""
    connection = db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_customer(db_session):
    """Create a test customer"""
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer

@pytest.fixture(scope="function")
def test_user(db_session, test_customer):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        customer_id=test_customer.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin_user(db_session, test_customer):
    """Create a test admin user"""
    user = User(
        email="admin@example.com",
        password_hash="hashed_password",
        is_superuser=True,
        customer_id=test_customer.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_token(test_user):
    """Create a test token"""
    token = jwt_service.create_access_token(test_user, test_user.customer)
    return token

@pytest.fixture(scope="function")
def test_admin_token(test_admin_user):
    """Create a test admin token"""
    token = jwt_service.create_access_token(test_admin_user, test_admin_user.customer)
    return token 