import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse

from db.core import get_db
from limiter import limiter
from models import UserCreate, UserLogin, UserResponse, Token, User
from routes.auth.utils import send_verify_email, validate_password, hash_password, authenticate_user, \
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, security, blacklist_token

logger = logging.getLogger(__name__)

################
# Basic routes #
################
router = APIRouter()

@router.get("/login")
async def login(): return RedirectResponse("/account/login", status_code=308)

@router.get("/register")
async def register(): return RedirectResponse("/account/register", status_code=308)


##############
# API routes #
##############
api_router = APIRouter()

# Core
@api_router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")
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
        User.is_verified == False
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

    send_verify_email(db_user, db)

    logger.info(f"User registered successfully: {user.username} (ID: {db_user.id})")
    return db_user

@api_router.post("/login", response_model=Token)
@limiter.limit("5/minute")
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
        return {"access_token": access_token}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@api_router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    blacklist_token(token)
    logger.debug("Logout request received, token blacklisted")
    return {"message": "Logged out successfully"}

# Information
@api_router.get("/check-auth")
def check_auth_status(current_user: User = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user.username}

@api_router.get("/user-info", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user