# Python Project Import Guidelines: Avoiding Circular Imports and Duplicates

## 🚨 Critical Rules to Follow

### 1. Import Analysis Before Writing Code
**ALWAYS check before adding any import:**

```python
# Before adding: from your_package.models.user import User
# Ask yourself:
# 1. Does this create a circular dependency?
# 2. Is this import only needed for type hints?
# 3. Can I move this import inside a function?
# 4. Is this already imported elsewhere in the file?
```

### 2. Dependency Direction Rules (Strict Hierarchy)
Respect this hierarchy – lower layers must not import higher layers:

```
├── main.py (top level)
├── routers/ (can import services, models, shared)
├── services/ (can import models, shared - NOT routers)
├── models/ (can import shared/base - NOT services/routers)
├── shared/
│   ├── core/ (minimal dependencies)
│   ├── db/ (DB setup and sessions)
│   └── exceptions/ (custom errors)
```

✅ Rule: Lower layers never import upward.

## 🔍 Pre-Import Checklist
✅ Check if it's already imported (Ctrl+F)

✅ Confirm it's actually needed

✅ Check you're not importing "upward"

✅ Use TYPE_CHECKING for type-only usage

## 📝 Recommended Import Patterns

### 1. Standard Import Order
```python
# Standard library
from datetime import datetime

# Third-party
from fastapi import Depends
from sqlalchemy.orm import Session

# Internal
from your_package.shared.config import settings
from your_package.shared.db.session import get_db

# Conditional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from your_package.models.user import User
```

### 2. Function-Level Imports (Preferred for Models)
```python
def get_user_by_id(user_id: int) -> "User":
    from your_package.models.user import User
    return User.query.get(user_id)
```

### 3. TYPE_CHECKING Pattern
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from your_package.models.user import User

def process_user(user: "User") -> dict:
    from your_package.models.user import User
    return user.to_dict()
```

## 🚫 Patterns to Avoid

### ❌ Model Cross-Imports
```python
# DO NOT DO THIS
# models/user.py
from your_package.models.customer import Customer
```

### ❌ Service Circular Dependencies
```python
# services/auth_service.py
from your_package.services.user_service import UserService

# services/user_service.py
from your_package.services.auth_service import AuthService
```

### ❌ Shared Utilities Importing Business Logic
```python
# shared/logging.py
from your_package.models.user import User  # ❌ Avoid!
```

## 🛠 Avoiding Duplicates

### ✅ Single Source of Truth
```python
# shared/types.py
UserDict = Dict[str, Any]

# everywhere else
from your_package.shared.types import UserDict
```

### ✅ Constants in One File
```python
# shared/constants.py
DEFAULT_PAGE_SIZE = 20

# use everywhere
from your_package.shared.constants import DEFAULT_PAGE_SIZE
```

## 🔍 Search Before Rewriting
```bash
grep -r "def get_user" .
grep -r "class.*Service" .
```

## 🧪 Testing Your Imports

### 1. Validate Imports
```bash
python -c "from your_package.models.user import User; print('OK')"
```

### 2. Detect Circular Imports
```bash
uvicorn your_package.main:app --reload
```
Look for:
- cannot import name 'X' from partially initialized module
- ImportError: cannot import name

## 📋 Code Review Checklist
- [ ] No duplicate imports
- [ ] No circular dependencies
- [ ] TYPE_CHECKING used where needed
- [ ] Models imported functionally
- [ ] Proper import order
- [ ] Constants and types defined centrally
- [ ] Imports are actually used

```bash
# Check for unused imports
autoflake --check --recursive your_package/

# Check import order
isort --check-only your_package/

# Test startup
uvicorn your_package.main:app --reload
```

## 🎯 Design Patterns for FastAPI Projects

### Router Example
```python
from typing import TYPE_CHECKING
from fastapi import APIRouter

if TYPE_CHECKING:
    from your_package.models.user import User

@router.get("/users/{user_id}")
async def get_user(user_id: int) -> "User":
    from your_package.services.user_service import UserService
    return UserService.get_by_id(user_id)
```

### Service Example
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from your_package.models.user import User

class UserService:
    @staticmethod
    def get_by_id(user_id: int) -> "User":
        from your_package.models.user import User
        return ...
```

### Model Example
```python
from sqlalchemy import Column, Integer, String
from your_package.shared.db.base import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
```

## 🚨 Emergency Fix Protocol for Circular Imports
1. 🔥 Comment the import temporarily
2. 🔍 Trace the circular dependency
3. ✂️ Use TYPE_CHECKING
4. 🚪 Move to function-level import
5. ✅ Test startup
6. 🔄 Refactor if needed

💡 Remember: Import discipline avoids technical debt and makes your codebase maintainable and production-ready. 