import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple
from datetime import datetime
from typing import Dict
from app.shared.core.logging import logger
from datetime import timedelta
from datetime import datetime
from typing import Dict
from app.shared.core.logging import logger
from datetime import timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if a client has exceeded their rate limit.
        
        Args:
            client_id: Client identifier (e.g., IP address)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Initialize or clean up old requests
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if rate limit is exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(
                f"Rate limit exceeded for client {client_id}",
                extra={
                    "client_id": client_id,
                    "requests_in_window": len(self.requests[client_id]),
                    "max_requests": self.max_requests,
                    "window_seconds": self.window_seconds
                }
            )
            return False
        
        # Add new request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> Tuple[int, int]:
        """
        Get the number of remaining requests and reset time.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Tuple of (remaining_requests, seconds_until_reset)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        if client_id not in self.requests:
            return self.max_requests, 0
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        remaining = self.max_requests - len(self.requests[client_id])
        reset_seconds = 0
        
        if self.requests[client_id]:
            oldest_request = min(self.requests[client_id])
            reset_time = oldest_request + timedelta(seconds=self.window_seconds)
            reset_seconds = max(0, int((reset_time - now).total_seconds()))
        
        return remaining, reset_seconds 