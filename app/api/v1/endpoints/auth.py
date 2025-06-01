from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.models import User, Customer, Role
from app.schemas.auth import Token, TokenPayload, UserRegister, UserResponse
from app.shared.core.sms import send_mfa_code_sms
from datetime import datetime, timedelta
from app.core.config import settings
from app.db.session import get_db
from app.core.email import send_verification_email
from app.core.captcha import verify_captcha
from app.core.security import generate_verification_token
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

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email verification and CAPTCHA.
    """
    try:
        # Verify CAPTCHA if enabled
        if settings.ENABLE_CAPTCHA:
            if not user_data.captcha_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CAPTCHA token is required"
                )
            if not await verify_captcha(user_data.captcha_token):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid CAPTCHA"
                )

        # Check if user already exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Get admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin role not found"
            )

        # Create customer
        customer = Customer(
            name=user_data.company_name,
            status="active"
        )
        db.add(customer)
        db.flush()  # Get customer ID without committing

        # Create user
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=get_password_hash(user_data.password),
            role_id=admin_role.id,
            customer_id=customer.id,
            is_active=False,  # User needs to verify email first
            verification_token=generate_verification_token()
        )
        db.add(user)
        db.flush()  # Get user ID without committing

        # Send verification email
        if settings.ENABLE_EMAIL_VERIFICATION:
            await send_verification_email(
                email_to=user.email,
                token=user.verification_token
            )

        # Commit all changes
        db.commit()
        db.refresh(user)

        logger.info(f"New user registered: {user.email}")

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            customer_id=user.customer_id,
            is_active=user.is_active,
            requires_verification=settings.ENABLE_EMAIL_VERIFICATION
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/verify-email/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user's email address.
    """
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    user.is_active = True
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"} 