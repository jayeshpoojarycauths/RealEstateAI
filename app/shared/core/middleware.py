
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import RateLimitError
from app.core.redis import get_redis_client
from fastapi import Request
from fastapi import Request


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = get_redis_client()
        self.rate_limits = {
            "default": (100, 60),  # 100 requests per minute
            "auth": (5, 60),      # 5 requests per minute
            "api": (1000, 3600)   # 1000 requests per hour
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client IP
        client_ip = request.client.host
        
        # Determine rate limit based on path
        path = request.url.path
        if path.startswith("/api/v1/auth"):
            limit_key = "auth"
        elif path.startswith("/api/v1"):
            limit_key = "api"
        else:
            limit_key = "default"
            
        # Get rate limit settings
        max_requests, window = self.rate_limits[limit_key]
        
        # Check rate limit
        key = f"rate_limit:{limit_key}:{client_ip}"
        current = self.redis_client.get(key)
        
        if current and int(current) >= max_requests:
            raise RateLimitError(
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window} seconds."
            )
            
        # Increment counter
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        pipe.execute()
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        
        return response

# Create middleware instance
rate_limit_middleware = RateLimitMiddleware 