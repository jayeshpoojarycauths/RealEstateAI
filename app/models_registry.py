"""
This file ensures that all SQLAlchemy models are imported for metadata reflection and relationship resolution.
It is critical for migrations, string-based relationships, and enabling multi-tenancy via the Customer model.
"""

# Import app-specific models
# First import base models
# Then import models that don't have foreign key dependencies
# Then import models that depend on the above
