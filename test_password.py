from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The hash from mock_data.sql
stored_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I6e'
test_password = 'password123'

# Test verification
is_valid = pwd_context.verify(test_password, stored_hash)
print(f"Password verification result: {is_valid}")

# Generate a new hash for comparison
new_hash = pwd_context.hash(test_password)
print(f"\nNew hash for 'password123': {new_hash}")
print(f"Verification with new hash: {pwd_context.verify(test_password, new_hash)}") 