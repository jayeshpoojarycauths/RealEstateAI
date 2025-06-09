"""
Email communication utilities.
"""

import functools
import time
import logging
import smtplib
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, TypeVar, Callable, TYPE_CHECKING
from contextlib import contextmanager
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Optional imports for different environments
try:
    import hvac
    HAS_VAULT = True
except ImportError:
    HAS_VAULT = False

try:
    from kubernetes import client, config
    HAS_KUBERNETES = True
except ImportError:
    HAS_KUBERNETES = False

from app.shared.core.config import settings
from app.shared.core.exceptions import CommunicationException
from app.shared.core.communication.messages import MessageCode, Messages

if TYPE_CHECKING:
    from app.shared.models.user import User

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Load environment variables from .env file in development
if settings.ENVIRONMENT != "production":
    load_dotenv()

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator for retrying operations with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            raise last_exception
        return wrapper
    return decorator

class SecretsManager:
    """Secure secrets management with support for multiple environments."""
    
    def __init__(self):
        self._secrets = {}
        self._initialized = False
        self._client = None
    
    def initialize(self):
        """Initialize secrets manager based on environment."""
        if settings.ENVIRONMENT == "production":
            if settings.AWS_REGION:
                self._init_aws_secrets()
            elif settings.VAULT_ADDR and HAS_VAULT:
                self._init_vault()
            elif settings.KUBERNETES_SERVICE_HOST and HAS_KUBERNETES:
                self._init_kubernetes_secrets()
            else:
                raise ValueError("No secrets manager configured for production")
        else:
            self._init_env_secrets()
        self._initialized = True
    
    def _init_aws_secrets(self):
        """Initialize AWS Secrets Manager."""
        try:
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            response = client.get_secret_value(
                SecretId=settings.SECRETS_ID
            )
            if 'SecretString' in response:
                self._secrets = eval(response['SecretString'])
            else:
                self._secrets = eval(response['SecretBinary'].decode())
        except ClientError as e:
            logger.error(f"Failed to get AWS secrets: {e}")
            raise
    
    def _init_vault(self):
        """Initialize HashiCorp Vault."""
        if not HAS_VAULT:
            raise ImportError("hvac package is not installed")
        try:
            self._client = hvac.Client(
                url=settings.VAULT_ADDR,
                token=settings.VAULT_TOKEN
            )
            response = self._client.secrets.kv.v2.read_secret_version(
                path=settings.VAULT_PATH
            )
            self._secrets = response['data']['data']
        except Exception as e:
            logger.error(f"Failed to get Vault secrets: {e}")
            raise
    
    def _init_kubernetes_secrets(self):
        """Initialize Kubernetes Secrets."""
        if not HAS_KUBERNETES:
            raise ImportError("kubernetes package is not installed")
        try:
            config.load_incluster_config()
            v1 = client.CoreV1Api()
            secret = v1.read_namespaced_secret(
                name=settings.K8S_SECRET_NAME,
                namespace=settings.K8S_NAMESPACE
            )
            self._secrets = {
                k: v.decode() for k, v in secret.data.items()
            }
        except Exception as e:
            logger.error(f"Failed to get Kubernetes secrets: {e}")
            raise
    
    def _init_env_secrets(self):
        """Initialize from environment variables."""
        required_vars = [
            'MAIL_USERNAME',
            'MAIL_PASSWORD',
            'MAIL_SERVER',
            'MAIL_PORT',
            'MAIL_FROM'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        self._secrets = {
            'smtp_username': os.getenv('MAIL_USERNAME'),
            'smtp_password': os.getenv('MAIL_PASSWORD'),
            'smtp_server': os.getenv('MAIL_SERVER'),
            'smtp_port': os.getenv('MAIL_PORT'),
            'sender_email': os.getenv('MAIL_FROM')
        }
    
    def get_secret(self, key: str) -> str:
        """Get a secret value."""
        if not self._initialized:
            self.initialize()
        value = self._secrets.get(key)
        if value is None:
            raise ValueError(f"Secret {key} not found")
        return value

class SMTPConnectionPool:
    """SMTP connection pool manager."""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self._pool = []
        self._lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """Get an SMTP connection from the pool."""
        connection = None
        try:
            with self._lock:
                if self._pool:
                    connection = self._pool.pop()
                else:
                    connection = self._create_connection()
            yield connection
        finally:
            if connection:
                with self._lock:
                    if len(self._pool) < self.max_connections:
                        self._pool.append(connection)
                    else:
                        connection.quit()
    
    def _create_connection(self):
        """Create a new SMTP connection."""
        secrets = SecretsManager()
        connection = smtplib.SMTP(
            secrets.get_secret('smtp_server'),
            int(secrets.get_secret('smtp_port'))
        )
        connection.starttls()
        connection.login(
            secrets.get_secret('smtp_username'),
            secrets.get_secret('smtp_password')
        )
        return connection

class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.secrets = SecretsManager()
        self.connection_pool = SMTPConnectionPool()
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(smtplib.SMTPException, ConnectionError)
    )
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send an email with retry logic."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.secrets.get_secret('sender_email')
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            with self.connection_pool.get_connection() as server:
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise CommunicationException(f"Failed to send email: {str(e)}")
    
    def send_welcome_email(self, user_id: str, db) -> bool:
        """Send welcome email to a new user."""
        from app.shared.models.user import User
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise CommunicationException("User not found")
        
        subject = Messages.get(MessageCode.WELCOME_EMAIL_SUBJECT)
        body = Messages.get(MessageCode.WELCOME_EMAIL_BODY).format(
            user_name=user.full_name
        )
        
        return self.send_email(user.email, subject, body)
    
    def send_password_reset_email(self, user_id: str, reset_token: str, db) -> bool:
        """Send password reset email."""
        from app.shared.models.user import User
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise CommunicationException("User not found")
        
        subject = Messages.get(MessageCode.PASSWORD_RESET_SUBJECT)
        body = Messages.get(MessageCode.PASSWORD_RESET_BODY).format(
            user_name=user.full_name,
            reset_link=f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        )
        
        return self.send_email(user.email, subject, body)
    
    def send_notification_email(
        self,
        user_id: str,
        notification_type: str,
        data: Dict[str, Any],
        db
    ) -> bool:
        """Send notification email."""
        from app.shared.models.user import User
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise CommunicationException("User not found")
        
        subject = Messages.get(f"{notification_type.upper()}_NOTIFICATION_SUBJECT")
        body = Messages.get(f"{notification_type.upper()}_NOTIFICATION_BODY").format(
            user_name=user.full_name,
            **data
        )
        
        return self.send_email(user.email, subject, body)

# Create a singleton instance
email_service = EmailService()

__all__ = [
    'email_service'
] 