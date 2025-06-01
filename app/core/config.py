from app.shared.core.config import Settings, get_settings
from pydantic_settings import BaseSettings
from typing import Optional

__all__ = ["Settings", "get_settings"]

# Re-export settings for backward compatibility
settings = get_settings()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Real Estate AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    SQLALCHEMY_DATABASE_URL: str
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Features
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_CAPTCHA: bool = True
    
    # reCAPTCHA
    RECAPTCHA_SITE_KEY: Optional[str] = None
    RECAPTCHA_SECRET_KEY: Optional[str] = None
    RECAPTCHA_SCORE_THRESHOLD: float = 0.5
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 