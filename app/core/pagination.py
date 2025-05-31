from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field
from math import ceil

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = Field(default=1, ge=1, description="Page number")
    items_per_page: int = Field(default=10, ge=1, le=100, description="Number of items per page")

class PageInfo(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page_info: PageInfo

def paginate(
    items: List[T],
    page: int = 1,
    items_per_page: int = 10
) -> PaginatedResponse[T]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        items_per_page: Number of items per page
        
    Returns:
        PaginatedResponse containing the paginated items and page info
    """
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
    page: Optional[int] = None,
    items_per_page: Optional[int] = None
) -> PaginationParams:
    """
    Get pagination parameters with defaults.
    
    Args:
        page: Optional page number
        items_per_page: Optional items per page
        
    Returns:
        PaginationParams object
    """
    return PaginationParams(
        page=page or 1,
        items_per_page=items_per_page or 10
    ) 