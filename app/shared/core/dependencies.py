from app.shared.core.security.auth import (get_current_active_user,
                                           get_current_superuser,
                                           get_current_user)
from app.shared.core.infrastructure.deps import (get_current_customer,
                                               get_current_active_customer)
from app.shared.db.session import get_db

# Re-export auth dependencies
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_current_customer",
    "get_current_active_customer"
] 