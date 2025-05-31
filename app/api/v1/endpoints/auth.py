from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password
from app.models.models import User
from app.schemas.auth import Token, TokenPayload
from app.shared.core.sms import send_mfa_code_sms
from datetime import datetime, timedelta
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger("auth")
logger.setLevel(logging.INFO)

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Accepts either 'email' or 'username' as the login field.
    """
    logger.info(f"[Login Attempt] Username: {form_data.username}")
    # Accept both 'email' and 'username' for login
    login_value = form_data.username
    user = db.query(User).filter((User.email == login_value) | (User.username == login_value)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"[Login Failed] Invalid credentials for: {login_value}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        logger.warning(f"[Login Failed] Inactive user: {login_value}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    logger.info(f"[Login Success] User authenticated: {login_value}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/mfa/send")
async def send_mfa_code(
    phone_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send MFA verification code to user's phone number.
    """
    try:
        code = "123456"  # In production, generate a random code
        result = await send_mfa_code_sms(
            phone_number=phone_number,
            code=code,
            customer_id=current_user.customer_id,
            db=db
        )
        return {
            "status": "success",
            "message": "MFA code sent successfully",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send MFA code: {str(e)}"
        )

@router.post("/mfa/verify")
async def verify_mfa_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify MFA code and generate access token.
    """
    # In production, verify the code against stored code
    if code != "123456":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            current_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 