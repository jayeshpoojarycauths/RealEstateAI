"""
Configuration settings module.
"""

import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, field_validator, Field, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict
from typing import Any
from sqlalchemy import func
from typing import Dict
from typing import Any
from sqlalchemy import func


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # API Settings
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="Real Estate AI")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None)
    POSTGRES_USER: Optional[str] = Field(default=None)
    POSTGRES_PASSWORD: Optional[str] = Field(default=None)
    POSTGRES_SERVER: Optional[str] = Field(default=None)
    POSTGRES_DB: Optional[str] = Field(default=None)
    
    # Email
    MAIL_USERNAME: Optional[str] = Field(default=None)
    MAIL_PASSWORD: Optional[str] = Field(default=None)
    MAIL_SERVER: Optional[str] = Field(default=None)
    MAIL_PORT: Optional[int] = Field(default=None)
    MAIL_FROM: Optional[str] = Field(default=None)
    
    # AWS Settings
    AWS_REGION: Optional[str] = Field(default=None)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    SECRETS_ID: Optional[str] = Field(default=None)
    
    # Vault Settings
    VAULT_ADDR: Optional[str] = Field(default=None)
    VAULT_TOKEN: Optional[str] = Field(default=None)
    VAULT_PATH: Optional[str] = Field(default=None)
    
    # Kubernetes Settings
    K8S_SECRET_NAME: Optional[str] = Field(default=None)
    K8S_NAMESPACE: Optional[str] = Field(default=None)
    
    # Frontend
    FRONTEND_URL: str = Field(default="http://localhost:3000")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(default=[])
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        if all(values.get(key) for key in ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_SERVER', 'POSTGRES_DB']):
            return f"postgresql://{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}@{values['POSTGRES_SERVER']}/{values['POSTGRES_DB']}"
        # Don't default to SQLite, raise an error instead
        raise ValueError("DATABASE_URL or PostgreSQL configuration is required")
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.DATABASE_URL
    
    # Redis
    REDIS_URL: Optional[str] = Field(default=None)
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = Field(default=None)
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None)
    
    # Version
    VERSION: str = "1.0.0"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    MAIL_FROM_NAME: str = "Real Estate AI"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    MAIL_STARTTLS: bool = True
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True
    MAIL_DEFAULT_SENDER: str = "your-email@gmail.com"
    MAIL_MAX_EMAILS: Optional[int] = None
    MAIL_ASCII_ATTACHMENTS: bool = False
    MAIL_SUPPRESS_SEND: bool = False
    MAIL_DEBUG: bool = False
    
    # Features
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_CAPTCHA: bool = True
    
    # reCAPTCHA
    RECAPTCHA_SITE_KEY: Optional[str] = None
    RECAPTCHA_SECRET_KEY: Optional[str] = None
    RECAPTCHA_SCORE_THRESHOLD: float = 0.5
    
    # SMS/Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    SMS_PROVIDER: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None

    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # MFA
    MFA_ISSUER: str = "Real Estate AI"
    MFA_TOKEN_EXPIRE_MINUTES: int = 5
    MFA_BACKUP_CODES_COUNT: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "app.log"

    # Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # Scraping
    SCRAPER_PROXY_URL: str = ""
    SCRAPE_INTERVAL_HOURS: int = 24

    # Database pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # ElevenLabs TTS Settings
    ELEVENLABS_API_KEY: str
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    ELEVENLABS_OUTPUT_FORMAT: str = "mp3_44100_128"
    ELEVENLABS_AUDIO_CACHE_DIR: str = "static/audio"

    # Encryption
    ENCRYPTION_KEY: str

    # Call Settings
    DEFAULT_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice ID
    MAX_CALL_RETRIES: int = 3
    CALL_RETRY_DELAY: int = 60  # seconds
    CALL_RECORDING_ENABLED: bool = True
    CALL_STATUS_CALLBACK_URL: str = "/outreach/call-status"  # Will be combined with API_BASE_URL in property

    # Twilio Call Settings
    TWILIO_CALL_TIMEOUT: int = 30  # seconds
    TWILIO_CALL_MACHINE_DETECTION: str = "DetectMessageEnd"
    TWILIO_CALL_MACHINE_DETECTION_TIMEOUT: int = 30  # seconds
    TWILIO_CALL_MACHINE_DETECTION_SPEECH_THRESHOLD: int = 3000  # milliseconds
    TWILIO_CALL_MACHINE_DETECTION_SPEECH_END_THRESHOLD: int = 1000  # milliseconds
    TWILIO_CALL_MACHINE_DETECTION_SILENCE_TIMEOUT: int = 1000  # milliseconds

    def get_database_url(self) -> str:
        """Get database URL."""
        return self.DATABASE_URL

    @property
    def get_database_engine_options(self) -> dict:
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "echo": self.DB_ECHO,
        }

    @property
    def full_call_status_callback_url(self) -> str:
        """Get the full call status callback URL."""
        return f"{self.API_BASE_URL}{self.CALL_STATUS_CALLBACK_URL}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

# Create settings instance
settings = get_settings()

# Only create settings instance if not in alembic environment
if not os.environ.get("ALEMBIC_RUNNING"):
    @lru_cache()
    def get_settings() -> Settings:
        return Settings()

    settings = get_settings()
    print("CORS origins:", settings.BACKEND_CORS_ORIGINS)

# Re-export settings for backward compatibility
__all__ = ['settings', 'get_settings'] 