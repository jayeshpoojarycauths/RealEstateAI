from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.models import Customer, User, Role, Permission
from uuid import uuid4

def init_db(db: Session) -> None:
    # Create customers
    customer1 = Customer(
        id=uuid4(),
        name="Real Estate Firm A"
    )
    customer2 = Customer(
        id=uuid4(),
        name="Real Estate Firm B"
    )
    db.add(customer1)
    db.add(customer2)
    db.commit()

    # Create permissions
    permissions = [
        Permission(
            id=uuid4(),
            action="create",
            resource="leads"
        ),
        Permission(
            id=uuid4(),
            action="read",
            resource="leads"
        ),
        Permission(
            id=uuid4(),
            action="update",
            resource="leads"
        ),
        Permission(
            id=uuid4(),
            action="delete",
            resource="leads"
        ),
    ]
    for permission in permissions:
        db.add(permission)
    db.commit()

    # Create roles for customer1
    admin_role = Role(
        id=uuid4(),
        name="admin",
        description="Administrator role",
        customer_id=customer1.id
    )
    agent_role = Role(
        id=uuid4(),
        name="agent",
        description="Real estate agent role",
        customer_id=customer1.id
    )
    db.add(admin_role)
    db.add(agent_role)
    db.commit()

    # Assign permissions to roles
    admin_role.permissions = permissions
    agent_role.permissions = [p for p in permissions if p.action in ["create", "read"]]
    db.commit()

    # Create users for customer1
    admin_user = User(
        id=uuid4(),
        email="admin@firma.com",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        customer_id=customer1.id
    )
    agent_user = User(
        id=uuid4(),
        email="agent@firma.com",
        password_hash=get_password_hash("agent123"),
        is_active=True,
        is_superuser=False,
        customer_id=customer1.id
    )
    db.add(admin_user)
    db.add(agent_user)
    db.commit()

    # Assign roles to users
    admin_user.roles = [admin_role]
    agent_user.roles = [agent_role]
    db.commit()

    # Create roles for customer2
    admin_role2 = Role(
        id=uuid4(),
        name="admin",
        description="Administrator role",
        customer_id=customer2.id
    )
    agent_role2 = Role(
        id=uuid4(),
        name="agent",
        description="Real estate agent role",
        customer_id=customer2.id
    )
    db.add(admin_role2)
    db.add(agent_role2)
    db.commit()

    # Assign permissions to roles for customer2
    admin_role2.permissions = permissions
    agent_role2.permissions = [p for p in permissions if p.action in ["create", "read"]]
    db.commit()

    # Create users for customer2
    admin_user2 = User(
        id=uuid4(),
        email="admin@firmb.com",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        customer_id=customer2.id
    )
    agent_user2 = User(
        id=uuid4(),
        email="agent@firmb.com",
        password_hash=get_password_hash("agent123"),
        is_active=True,
        is_superuser=False,
        customer_id=customer2.id
    )
    db.add(admin_user2)
    db.add(agent_user2)
    db.commit()

    # Assign roles to users for customer2
    admin_user2.roles = [admin_role2]
    agent_user2.roles = [agent_role2]
    db.commit() 