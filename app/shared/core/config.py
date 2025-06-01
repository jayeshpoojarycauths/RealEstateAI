from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator, EmailStr, PostgresDsn
import secrets
from functools import lru_cache
import json
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Real Estate CRM"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_HOSTS: List[str] = ["*"]
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    MAIL_USERNAME: str = "your-email@gmail.com"  # Alias for SMTP_USER
    MAIL_PASSWORD: str = "your-app-password"  # Alias for SMTP_PASSWORD
    MAIL_FROM: str = "your-email@gmail.com"
    MAIL_FROM_NAME: str = "Real Estate CRM"
    MAIL_PORT: int = 587  # Alias for SMTP_PORT
    MAIL_SERVER: str = "smtp.gmail.com"  # Alias for SMTP_HOST
    MAIL_TLS: bool = True  # Alias for SMTP_TLS
    MAIL_SSL: bool = False
    MAIL_STARTTLS: bool = True
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True
    MAIL_DEFAULT_SENDER: str = "your-email@gmail.com"
    MAIL_MAX_EMAILS: Optional[int] = None
    MAIL_ASCII_ATTACHMENTS: bool = False
    MAIL_SUPPRESS_SEND: bool = False
    MAIL_DEBUG: bool = False
    
    # SMS
    SMS_PROVIDER: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None

    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # MFA
    MFA_ISSUER: str = "Real Estate CRM"
    MFA_TOKEN_EXPIRE_MINUTES: int = 5
    MFA_BACKUP_CODES_COUNT: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "app.log"

    # Cache
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # Scraping
    SCRAPER_PROXY_URL: str = ""
    SCRAPE_INTERVAL_HOURS: int = 24

    # Database pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # 30 minutes
    DB_ECHO: bool = False

    # ElevenLabs TTS Settings
    ELEVENLABS_API_KEY: str
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    ELEVENLABS_OUTPUT_FORMAT: str = "mp3_44100_128"
    ELEVENLABS_AUDIO_CACHE_DIR: str = "static/audio"  # Directory to store generated audio files

    # Encryption
    ENCRYPTION_KEY: str

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    @property
    def get_database_engine_options(self) -> dict:
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "echo": self.DB_ECHO,
        }

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env file

    def __init__(self, **kwargs):
        env_file = kwargs.pop("_env_file", ".env")
        if env_file is None:
            # If _env_file is None, don't load from .env file
            kwargs["_env_file"] = None
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

# Only create settings instance if not in alembic environment
if not os.environ.get("ALEMBIC_RUNNING"):
    @lru_cache()
    def get_settings() -> Settings:
        return Settings()

    settings = get_settings()
    print("CORS origins:", settings.BACKEND_CORS_ORIGINS) 