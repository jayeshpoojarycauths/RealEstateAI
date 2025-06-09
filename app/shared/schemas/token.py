from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None  # For token type (access, refresh, etc.)
    jti: Optional[str] = None  # JWT ID for token tracking 