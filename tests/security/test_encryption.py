import pytest
from app.core.security.encryption import (
    EncryptedField,
    encrypt_value,
    decrypt_value,
    generate_encryption_key
)

def test_encryption_decryption():
    """Test that values can be encrypted and decrypted correctly"""
    # Generate a new key
    key = generate_encryption_key()
    
    # Test values
    test_values = [
        "sensitive@email.com",
        "123-45-6789",  # SSN
        "+1-555-123-4567",  # Phone
        "123 Main St, Anytown, USA"  # Address
    ]
    
    for value in test_values:
        # Encrypt
        encrypted = encrypt_value(value, key)
        assert encrypted != value  # Ensure value is actually encrypted
        
        # Decrypt
        decrypted = decrypt_value(encrypted, key)
        assert decrypted == value  # Ensure value is recovered correctly

def test_encrypted_field():
    """Test the SQLAlchemy EncryptedField type"""
    # Create a test field
    field = EncryptedField()
    
    # Test values
    test_values = [
        "sensitive@email.com",
        "123-45-6789",
        "+1-555-123-4567",
        "123 Main St, Anytown, USA"
    ]
    
    for value in test_values:
        # Test process_bind_param (encryption)
        encrypted = field.process_bind_param(value, None)
        assert encrypted != value  # Ensure value is encrypted
        
        # Test process_result_value (decryption)
        decrypted = field.process_result_value(encrypted, None)
        assert decrypted == value  # Ensure value is recovered correctly

def test_encryption_key_rotation():
    """Test that encryption works with key rotation"""
    # Generate two different keys
    key1 = generate_encryption_key()
    key2 = generate_encryption_key()
    
    # Encrypt with first key
    value = "sensitive@email.com"
    encrypted = encrypt_value(value, key1)
    
    # Try to decrypt with second key (should fail)
    with pytest.raises(Exception):
        decrypt_value(encrypted, key2)
    
    # Decrypt with original key (should succeed)
    decrypted = decrypt_value(encrypted, key1)
    assert decrypted == value

def test_encrypted_field_null_values():
    """Test that EncryptedField handles null values correctly"""
    field = EncryptedField()
    
    # Test None value
    assert field.process_bind_param(None, None) is None
    assert field.process_result_value(None, None) is None
    
    # Test empty string
    assert field.process_bind_param("", None) == ""
    assert field.process_result_value("", None) == ""

def test_encryption_performance():
    """Test encryption/decryption performance"""
    import time
    
    # Generate key
    key = generate_encryption_key()
    
    # Test value
    value = "sensitive@email.com"
    
    # Measure encryption time
    start_time = time.time()
    for _ in range(1000):
        encrypt_value(value, key)
    encryption_time = time.time() - start_time
    
    # Measure decryption time
    encrypted = encrypt_value(value, key)
    start_time = time.time()
    for _ in range(1000):
        decrypt_value(encrypted, key)
    decryption_time = time.time() - start_time
    
    # Ensure operations complete within reasonable time
    assert encryption_time < 1.0  # Less than 1 second for 1000 operations
 