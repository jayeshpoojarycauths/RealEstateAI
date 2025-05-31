from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.shared.core.security.jwt import get_current_user, get_current_customer
from app.core.config import settings
import time
from typing import Optional

security = HTTPBearer()

class SecurityMiddleware:
    def __init__(self):
        self.rate_limit = {}  # Simple in-memory rate limiting

    async def __call__(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip in self.rate_limit:
            if current_time - self.rate_limit[client_ip]["last_request"] < 1:  # 1 second cooldown
                self.rate_limit[client_ip]["count"] += 1
                if self.rate_limit[client_ip]["count"] > settings.RATE_LIMIT_PER_SECOND:
                    raise HTTPException(status_code=429, detail="Too many requests")
            else:
                self.rate_limit[client_ip] = {"count": 1, "last_request": current_time}
        else:
            self.rate_limit[client_ip] = {"count": 1, "last_request": current_time}

        # JWT Authentication
        try:
            auth = await security(request)
            user = get_current_user(auth.credentials)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            request.state.user = user
            request.state.customer = get_current_customer(auth.credentials)
        except HTTPException:
            # Allow unauthenticated access to public endpoints
            if not request.url.path.startswith("/api/v1/public"):
                raise

        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

security_middleware = SecurityMiddleware() 