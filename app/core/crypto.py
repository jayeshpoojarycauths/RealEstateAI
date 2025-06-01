from cryptography.fernet import Fernet
import os
import bcrypt

# Fernet key should be securely stored and rotated as needed
FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY environment variable is not set.")
fernet = Fernet(FERNET_KEY)

def encrypt_value(value: str) -> str:
    """Encrypt a string value using Fernet."""
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(token: str) -> str:
    """Decrypt a Fernet-encrypted string value."""
    return fernet.decrypt(token.encode()).decode()

def hash_code(code: str) -> str:
    """Hash a backup code using bcrypt."""
    return bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()

def verify_code(code: str, hashed: str) -> bool:
    """Verify a backup code against a bcrypt hash."""
    return bcrypt.checkpw(code.encode(), hashed.encode())

"""
MFASettings Security:
- secret_key is encrypted using Fernet before storage.
- backup_codes are hashed with bcrypt; only hashes are stored.
- The Fernet key is managed via environment variable FERNET_KEY.
- Key rotation: To rotate, decrypt all values with the old key, re-encrypt with the new key, and update FERNET_KEY.
- Never log or expose decrypted secrets or backup codes.
""" 