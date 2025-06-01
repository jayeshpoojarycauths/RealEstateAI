import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.customer import Customer
from app.models.role import Role
from app.core.security import verify_password

def test_register_user_success(client: TestClient, db_session: Session):
    """Test successful user registration with customer creation."""
    # Test data
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "Test Company",
        "email": "john.doe@testcompany.com",
        "password": "Test@123456"
    }

    # Make registration request
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify response data
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data
    assert "customer_id" in data

    # Verify database records
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert verify_password(user_data["password"], user.hashed_password)
    
    # Verify customer creation
    customer = db_session.query(Customer).filter(Customer.id == user.customer_id).first()
    assert customer is not None
    assert customer.name == user_data["company_name"]
    
    # Verify role assignment
    assert user.role_id is not None
    role = db_session.query(Role).filter(Role.id == user.role_id).first()
    assert role is not None
    assert role.name == "admin"

def test_register_user_duplicate_email(client: TestClient, db_session: Session):
    """Test registration with duplicate email."""
    # Create existing user
    existing_user = User(
        email="existing@test.com",
        first_name="Existing",
        last_name="User",
        hashed_password="hashed_password",
        role_id=1,
        customer_id=1
    )
    db_session.add(existing_user)
    db_session.commit()

    # Attempt registration with same email
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "company_name": "New Company",
        "email": "existing@test.com",
        "password": "Test@123456"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()

def test_register_user_invalid_data(client: TestClient):
    """Test registration with invalid data."""
    # Test with missing required fields
    invalid_data = {
        "first_name": "John",
        "email": "invalid-email",
        "password": "123"  # Too short
    }

    response = client.post("/api/auth/register", json=invalid_data)
    assert response.status_code == 422

def test_register_user_password_validation(client: TestClient):
    """Test password validation during registration."""
    # Test with weak password
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "Test Company",
        "email": "john.doe@testcompany.com",
        "password": "weak"  # Too weak
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]

def test_register_user_customer_creation(client: TestClient, db_session: Session):
    """Test customer creation during registration."""
    user_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "company_name": "New Company Ltd",
        "email": "jane.smith@newcompany.com",
        "password": "Test@123456"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()

    # Verify customer creation
    customer = db_session.query(Customer).filter(Customer.id == data["customer_id"]).first()
    assert customer is not None
    assert customer.name == user_data["company_name"]
    assert customer.created_at is not None
    assert customer.updated_at is not None

def test_register_user_role_assignment(client: TestClient, db_session: Session):
    """Test role assignment during registration."""
    user_data = {
        "first_name": "Admin",
        "last_name": "User",
        "company_name": "Admin Company",
        "email": "admin@admincompany.com",
        "password": "Test@123456"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()

    # Verify user role
    user = db_session.query(User).filter(User.id == data["id"]).first()
    assert user is not None
    assert user.role_id is not None
    
    role = db_session.query(Role).filter(Role.id == user.role_id).first()
    assert role is not None
    assert role.name == "admin" 