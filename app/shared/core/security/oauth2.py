from fastapi.security import OAuth2PasswordBearer

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

__all__ = ["oauth2_scheme"] 