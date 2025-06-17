import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db, User
from auth_api import hash_password, authenticate_user, create_access_token, get_current_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserCreate, UserLogin, UserResponse, Token, PasswordChange, Message

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Registration attempt for username: {user.username}, email: {user.email}")
    
    try:
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
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered successfully: {user.username} (ID: {db_user.id})")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
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

@router.post("/change-password", response_model=Message)
def change_password(
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