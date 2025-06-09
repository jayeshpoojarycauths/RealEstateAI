import time
from typing import Dict, Tuple

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.shared.core.config import settings

from .security import security_middleware
from fastapi import Request
from fastapi import HTTPException
from typing import Dict
from fastapi import Request
from fastapi import HTTPException
from typing import Dict


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        
        # Check rate limit
        if client_ip in self.requests and len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Add current request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)

rate_limit_middleware = RateLimitMiddleware

__all__ = ['security_middleware'] 