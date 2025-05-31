import pytest
from datetime import datetime
from app.models.audit import AuditLog
from app.models.models import User, Customer

def test_audit_log_creation():
    """Test that audit logs can be created with all required fields"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Create audit log
    audit_log = AuditLog(
        customer_id=customer.id,
        user_id=user.id,
        action="CREATE",
        resource_type="USER",
        resource_id=2,
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0",
        metadata={"details": "User created via API"}
    )
    
    # Verify all fields are set correctly
    assert audit_log.customer_id == customer.id
    assert audit_log.user_id == user.id
    assert audit_log.action == "CREATE"
    assert audit_log.resource_type == "USER"
    assert audit_log.resource_id == 2
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "Mozilla/5.0"
    assert audit_log.metadata == {"details": "User created via API"}
    assert isinstance(audit_log.created_at, datetime)

def test_audit_log_relationships():
    """Test that audit log relationships work correctly"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Create audit log
    audit_log = AuditLog(
        customer_id=customer.id,
        user_id=user.id,
        action="CREATE",
        resource_type="USER",
        resource_id=2
    )
    
    # Verify relationships
    assert audit_log.customer.id == customer.id
    assert audit_log.user.id == user.id

def test_audit_log_metadata():
    """Test that audit log metadata can store complex data"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Complex metadata
    metadata = {
        "action_details": {
            "old_value": "old@email.com",
            "new_value": "new@email.com"
        },
        "system_info": {
            "browser": "Chrome",
            "os": "Windows",
            "version": "91.0"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Create audit log with complex metadata
    audit_log = AuditLog(
        customer_id=customer.id,
        user_id=user.id,
        action="UPDATE",
        resource_type="USER",
        resource_id=2,
        metadata=metadata
    )
    
    # Verify metadata is stored correctly
    assert audit_log.metadata == metadata
    assert audit_log.metadata["action_details"]["old_value"] == "old@email.com"
    assert audit_log.metadata["system_info"]["browser"] == "Chrome"

def test_audit_log_required_fields():
    """Test that required fields are enforced"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Try to create audit log without required fields
    with pytest.raises(Exception):
        AuditLog(
            customer_id=customer.id,
            user_id=user.id
            # Missing action and resource_type
        )

def test_audit_log_repr():
    """Test the string representation of audit logs"""
    # Create test user and customer
    user = User(id=1, email="test@example.com")
    customer = Customer(id=1, name="Test Customer")
    
    # Create audit log
    audit_log = AuditLog(
        customer_id=customer.id,
        user_id=user.id,
        action="CREATE",
        resource_type="USER",
        resource_id=2
    )
    
    # Verify string representation
    expected_repr = f"<AuditLog {audit_log.id}: CREATE USER(2) by User(1) in Customer(1)>"
    assert str(audit_log) == expected_repr 