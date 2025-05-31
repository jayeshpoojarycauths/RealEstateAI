from typing import Optional
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        """Calculate the offset for SQL queries."""
        return (self.page - 1) * self.limit

def get_pagination_params(
    page: Optional[int] = None,
    limit: Optional[int] = None
) -> PaginationParams:
    """
    Get pagination parameters from query parameters.
    """
    return PaginationParams(
        page=page or 1,
        limit=limit or 10
    ) 