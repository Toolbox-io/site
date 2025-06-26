import logging
from datetime import timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.requests import Request

from auth_api import hash_password, authenticate_user, create_access_token, get_current_user, verify_password, \
    ACCESS_TOKEN_EXPIRE_MINUTES, validate_password, blacklist_token, security
from database import get_db
from limiter import limiter
from models import UserCreate, UserLogin, UserResponse, Token, PasswordChange, Message, User
from routes.mail import send_mail, render_verify_email_html, render_reset_email_html

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# noinspection PyUnusedLocal
@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")  # Limit registration attempts
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Registration attempt for username: {user.username}, email: {user.email}")

    # Validate password strength
    is_valid, error_message = validate_password(user.password)
    if not is_valid:
        logger.warning(f"Registration failed - weak password for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    db_user = (db
        .query(User)
        .filter(
            User.username == user.username and
            User.email == user.email and
            User.is_verified == 0
        ).first())

    if db_user:
        logger.info("There is a user with the same data, re-registering")
        db.delete(db_user)
        db.commit()
    else:
        # Check if username already exists
        logger.debug(f"Checking if username exists: {user.username}")
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"Registration failed - username already exists: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        logger.debug(f"Checking if email exists: {user.email}")
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Registration failed - email already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Create new user
    logger.debug(f"Creating new user: {user.username}")
    hashed_password = hash_password(user.password)
    # noinspection PyTypeChecker
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    verification_token = str(uuid.uuid4())
    db_user.verification_token = verification_token
    db_user.is_verified = False
    db.commit()
    db.refresh(db_user)
    send_mail(
        str(user.email),
        "Подтвертите ваш email",
        render_verify_email_html(verification_token),
        html=True
    )

    logger.info(f"User registered successfully: {user.username} (ID: {db_user.id})")
    return db_user

# noinspection PyUnusedLocal
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Limit login attempts
def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    logger.info(f"Login attempt for username: {user_credentials.username}")
    
    try:
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        if not user:
            logger.warning(f"Login failed for username: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_verified:
            logger.warning(f"Login failed for unverified user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"User authenticated, creating access token for: {user.username}")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {user.username} (ID: {user.id})")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    logger.debug(f"Getting user info for: {current_user.username} (ID: {current_user.id})")
    return current_user

# noinspection PyUnusedLocal
@router.post("/change-password", response_model=Message)
@limiter.limit("1/minute")
def change_password(
    request: Request,
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    logger.info(f"Password change attempt for user: {current_user.username} (ID: {current_user.id})")
    
    try:
        # Verify current password
        logger.debug(f"Verifying current password for user: {current_user.username}")
        if not verify_password(password_change.current_password, current_user.hashed_password):
            logger.warning(f"Password change failed - incorrect current password for user: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password and update
        logger.debug(f"Hashing new password for user: {current_user.username}")
        new_hashed_password = hash_password(password_change.new_password)
        current_user.hashed_password = new_hashed_password
        db.commit()
        
        logger.info(f"Password changed successfully for user: {current_user.username}")
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during password change: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password change"
        )

@router.get("/health")
def health_check():
    """Health check endpoint for authentication system"""
    logger.debug("Health check request received")
    return {"status": "healthy", "service": "authentication"}

@router.get("/check-auth")
def check_auth_status(current_user: User = Depends(get_current_user)):
    """Check if user is authenticated"""
    logger.debug(f"Auth check for user: {current_user.username}")
    return {"authenticated": True, "user": current_user.username}

@router.get("/user-info", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    logger.debug(f"Getting user info for: {current_user.username}")
    return current_user

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    blacklist_token(token)
    logger.debug("Logout request received, token blacklisted")
    return {"message": "Logged out successfully"}

@router.delete("/delete-account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    logger.info(f"Account deletion request for user: {current_user.username}")
    
    try:
        db.delete(current_user)
        db.commit()
        logger.info(f"Account deleted successfully for user: {current_user.username}")
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )