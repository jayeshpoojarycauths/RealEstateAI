from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String
import base64
from app.shared.core.config import settings
from typing import Union

class EncryptedField(TypeDecorator):
    """SQLAlchemy type for encrypted fields"""
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fernet = Fernet(settings.ENCRYPTION_KEY.encode())

    def process_bind_param(self, value, dialect):
        if value is not None:
            return self._fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is not None:
            return self._fernet.decrypt(value.encode()).decode()

def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()

def encrypt_value(value: str) -> str:
    """Encrypt a string value"""
    if not value:
        return value
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    """Decrypt a string value"""
    if not value:
        return value
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.decrypt(value.encode()).decode()

class EncryptionService:
    def __init__(self):
        self.key = base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0'))
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data using Fernet symmetric encryption."""
        if isinstance(data, str):
            data = data.encode()
        encrypted_data = self.cipher_suite.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet symmetric encryption."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

encryption_service = EncryptionService() 