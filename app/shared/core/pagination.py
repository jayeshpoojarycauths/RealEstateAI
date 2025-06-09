from math import ceil
from typing import Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = Field(default=1, ge=1, description="Page number")
    items_per_page: int = Field(default=10, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", description="Sort order (asc/desc)")

    @property
    def offset(self) -> int:
        """Calculate the offset for SQL queries."""
        return (self.page - 1) * self.items_per_page

    @property
    def limit(self) -> int:
        """Alias for items_per_page for SQL compatibility."""
        return self.items_per_page

class PageInfo(BaseModel):
    """Information about the current page."""
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with items and page info."""
    items: List[T]
    page_info: PageInfo

def paginate(
    items: List[T],
    page: int = 1,
    items_per_page: int = 10,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> PaginatedResponse[T]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        items_per_page: Number of items per page
        sort_by: Optional field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        PaginatedResponse containing the paginated items and page info
    """
    # Sort items if sort_by is provided
    if sort_by:
        items = sorted(
            items,
            key=lambda x: getattr(x, sort_by, None),
            reverse=sort_order.lower() == "desc"
        )
    
    total_items = len(items)
    total_pages = ceil(total_items / items_per_page)
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    # Calculate start and end indices
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    # Get items for current page
    page_items = items[start_idx:end_idx]
    
    # Create page info
    page_info = PageInfo(
        current_page=page,
        total_pages=total_pages,
        total_items=total_items,
        items_per_page=items_per_page,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    return PaginatedResponse(items=page_items, page_info=page_info)

def get_pagination_params(
    page: Optional[int] = Query(None, ge=1, description="Page number"),
    items_per_page: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc/desc)")
) -> PaginationParams:
    """
    Get pagination parameters with defaults.
    
    Args:
        page: Optional page number
        items_per_page: Optional items per page
        sort_by: Optional field to sort by
        sort_order: Optional sort order
        
    Returns:
        PaginationParams object
    """
    return PaginationParams(
        page=page or 1,
        items_per_page=items_per_page or 10,
        sort_by=sort_by,
        sort_order=sort_order
    )

def get_sql_pagination_params(
    page: Optional[int] = None,
    limit: Optional[int] = None
) -> PaginationParams:
    """
    Get pagination parameters for SQL queries.
    
    Args:
        page: Optional page number
        limit: Optional items per page (SQL-style naming)
        
    Returns:
        PaginationParams object with offset and limit properties
    """
    return PaginationParams(
        page=page or 1,
        items_per_page=limit or 10
    )

__all__ = [
    'PaginationParams',
    'PageInfo',
    'PaginatedResponse',
    'paginate',
    'get_pagination_params',
    'get_sql_pagination_params'
] 