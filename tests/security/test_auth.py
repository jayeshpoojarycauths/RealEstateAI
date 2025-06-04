import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.shared.core.security.jwt import jwt_service
from app.shared.core.security.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user
)
from app.models.models import User, Customer

client = TestClient(app)

def test_access_token_expiration():
    """Test that access tokens expire correctly"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Create access token
    token = jwt_service.create_access_token(user, customer)
    
    # Verify token works initially
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Modify token expiration to be in the past
    import jwt
    decoded = jwt.decode(token, options={"verify_signature": False})
    decoded["exp"] = 0
    expired_token = jwt.encode(decoded, "dummy_key", algorithm="HS256")
    
    # Verify expired token is rejected
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

def test_refresh_token_rotation():
    """Test that refresh tokens can be used to get new access tokens"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Create refresh token
    refresh_token = jwt_service.create_refresh_token(user, customer)
    
    # Use refresh token to get new access token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_customer_isolation():
    """Test that users can only access their customer's data"""
    # Create two customers
    customer1 = Customer(id=1, name="Customer 1")
    customer2 = Customer(id=2, name="Customer 2")
    
    # Create users for each customer
    user1 = User(id=1, email="user1@example.com", customer_id=1)
    user2 = User(id=2, email="user2@example.com", customer_id=2)
    
    # Create tokens
    token1 = jwt_service.create_access_token(user1, customer1)
    token2 = jwt_service.create_access_token(user2, customer2)
    
    # User 1 tries to access User 2's data
    response = client.get(
        f"/api/v1/users/{user2.id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 403

def test_rate_limiting():
    """Test that rate limiting works"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    token = jwt_service.create_access_token(user, customer)
    
    # Make multiple requests quickly
    for _ in range(6):  # One more than the limit
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Last request should be rate limited
    assert response.status_code == 429

def test_security_headers():
    """Test that security headers are set correctly"""
    response = client.get("/")
    headers = response.headers
    
    assert "Strict-Transport-Security" in headers
    assert "X-Content-Type-Options" in headers
    assert "X-Frame-Options" in headers
    assert "Content-Security-Policy" in headers
    assert "X-XSS-Protection" in headers
    assert "Permissions-Policy" in headers 