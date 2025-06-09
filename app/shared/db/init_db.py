from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.shared.core.security import get_password_hash
from app.shared.models.customer import Customer
from app.shared.models.user import Permission, Role, User
from app.shared.core.config import settings
from app.shared.db.base_class import Base
from app.scraping.models.scraping import ScrapingConfig

def create_tables():
    """Create all database tables."""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)

def init_db(db: Session) -> None:
    """Initialize the database with required data."""
    # Create default roles
    roles = [
        Role(name="admin", description="Administrator"),
        Role(name="manager", description="Manager"),
        Role(name="agent", description="Real Estate Agent"),
        Role(name="user", description="Regular User")
    ]
    
    for role in roles:
        if not db.query(Role).filter(Role.name == role.name).first():
            db.add(role)
    
    db.commit()
    
    # Create default permissions
    permissions = [
        Permission(name="manage_users", description="Can manage users"),
        Permission(name="manage_roles", description="Can manage roles"),
        Permission(name="manage_leads", description="Can manage leads"),
        Permission(name="manage_projects", description="Can manage projects"),
        Permission(name="view_analytics", description="Can view analytics"),
        Permission(name="manage_settings", description="Can manage settings")
    ]
    
    for permission in permissions:
        if not db.query(Permission).filter(Permission.name == permission.name).first():
            db.add(permission)
    
    db.commit()

    # Create customers
    customer1 = Customer(
        name="Real Estate Firm A",
        email="contact@firma.com",
        phone="123-456-7890",
        address="123 Main St"
    )
    customer2 = Customer(
        name="Real Estate Firm B",
        email="contact@firmb.com",
        phone="098-765-4321",
        address="456 Oak St"
    )
    db.add(customer1)
    db.add(customer2)
    db.commit()

    # Create users for customer1
    admin_user = User(
        email="admin@firma.com",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        customer_id=customer1.id
    )
    agent_user = User(
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
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    agent_role = db.query(Role).filter(Role.name == "agent").first()
    
    admin_user.roles = [admin_role]
    agent_user.roles = [agent_role]
    db.commit()

    # Create users for customer2
    admin_user2 = User(
        email="admin@firmb.com",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        customer_id=customer2.id
    )
    agent_user2 = User(
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
    admin_user2.roles = [admin_role]
    agent_user2.roles = [agent_role]
    db.commit() 