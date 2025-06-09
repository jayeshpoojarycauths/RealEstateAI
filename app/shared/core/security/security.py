import base64
import hashlib

import pyotp
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from sqlalchemy import func

from app.shared.core.config import settings
from app.shared.core.security.password_utils import get_password_hash, verify_password

# Security constants
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt_value(value: str) -> str:
    """
    Encrypt a value using Fernet symmetric encryption.
    
    Args:
        value: The value to encrypt
        
    Returns:
        str: The encrypted value as a base64 string
    """
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a value that was encrypted using encrypt_value.
    
    Args:
        encrypted_value: The encrypted value as a base64 string
        
    Returns:
        str: The decrypted value
    """
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    f = Fernet(key)
    return f.decrypt(encrypted_value.encode()).decode()

def hash_code(code: str) -> str:
    """
    Hash a code (e.g., backup code) using SHA-256.
    
    Args:
        code: The code to hash
        
    Returns:
        str: The hashed code
    """
    return hashlib.sha256(code.encode()).hexdigest()

def verify_mfa_code(code: str, secret_key: str) -> bool:
    """
    Verify a TOTP code for MFA.
    
    Args:
        code: The TOTP code to verify
        secret_key: The user's TOTP secret key
        
    Returns:
        bool: True if code is valid, False otherwise
    """
    totp = pyotp.TOTP(secret_key)
    return totp.verify(code)

# Export commonly used functions
__all__ = [
    'encrypt_value',
    'decrypt_value',
    'hash_code',
    'verify_mfa_code',
    'verify_password',
    'get_password_hash'
] 